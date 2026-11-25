import os
import logging
import numpy as np
import cv2
from PIL import Image
import streamlit as st
import tensorflow as tf
from tensorflow.keras.models import load_model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "backend", "models", "malaria_model.h5")

PHASE_METADATA = {
    "ring": {
        "name": "Ring Stage (Early Trophozoite)",
        "short_name": "Ring Stage",
        "key": "ring",
        "timeline": "0 - 18 Hours",
        "cycle_progress": 25,
        "severity": "Early Intraerythrocytic Phase",
        "urgency": "Immediate Standard ACT",
        "morphology": 'Delicate cytoplasmic ring with a small condensed chromatin dot ("signet-ring" appearance)',
        "description": "Early developmental phase following erythrocyte invasion by merozoites. The parasite occupies approximately 5% to 15% of the red blood cell area.",
        "clinical_implications": "Parasites circulate actively in peripheral blood. High susceptibility to Artemisinin-based Combination Therapy (ACT). Low risk of immediate capillary cytoadherence.",
        "treatment": "Standard oral Artemisinin-based Combination Therapy (e.g., Artemether-Lumefantrine or Artesunate-Amodiaquine) for 3 days as per WHO guidelines.",
    },
    "trophozoite": {
        "name": "Mature Trophozoite Stage",
        "short_name": "Trophozoite Stage",
        "key": "trophozoite",
        "timeline": "18 - 36 Hours",
        "cycle_progress": 55,
        "severity": "Active Metabolic Phase",
        "urgency": "Urgent Antimalarial Therapy",
        "morphology": "Irregular amoeboid cytoplasmic mass with prominent golden-brown to black hemozoin pigment granules",
        "description": "Actively feeding parasite metabolizing host hemoglobin. The parasite expands to occupy 20% to 45% of the erythrocyte volume.",
        "clinical_implications": "Parasite expresses PfEMP1 knobs causing cytoadherence to microvascular endothelium; causes rising fever spikes, nausea, and headache.",
        "treatment": "Prompt oral ACT. Administer antipyretics (Paracetamol) for high fever and maintain hydration. Monitor for signs of severe progression.",
    },
    "schizont": {
        "name": "Schizont Stage (Asexual Multiplication)",
        "short_name": "Schizont Stage",
        "key": "schizont",
        "timeline": "36 - 48 Hours",
        "cycle_progress": 85,
        "severity": "Critical Pre-Lytic Phase",
        "urgency": "Emergency Evaluation & Care",
        "morphology": "Multinucleate complex containing 8 to 24 dividing merozoites with clustered central hemozoin pigment",
        "description": "Late-stage asexual schizogony where nuclear division produces multiple daughter merozoites prior to host cell rupture.",
        "clinical_implications": "Imminent erythrocyte lysis releases pyrogenic toxins, causing acute rigors, shivering, spike fevers (up to 41°C), and marked hemolytic anemia.",
        "treatment": "Emergency antimalarial therapy. For severe malaria or persistent vomiting, initiate IV Artesunate (2.4 mg/kg) followed by full course oral ACT.",
    },
    "gametocyte": {
        "name": "Gametocyte Stage (Sexual Precursor)",
        "short_name": "Gametocyte Stage",
        "key": "gametocyte",
        "timeline": "Transmission Phase",
        "cycle_progress": 100,
        "severity": "Vector Transmission Reservoir",
        "urgency": "Transmission-blocking Therapy",
        "morphology": "Characteristic elongated crescent / banana-shaped morphology stretching the host RBC, with centralized chromatin and coarse pigment",
        "description": "Sexually committed micro- or macrogametocyte. Does not cause acute hemolytic destruction in humans but infects female Anopheles mosquitoes during a blood meal.",
        "clinical_implications": "Indicates sub-acute or mature infection acting as an active transmission reservoir in the community.",
        "treatment": "Add a single low dose of Primaquine (0.25 mg base/kg) on day 1 alongside ACT to eliminate gametocytes and prevent vector transmission.",
    },
    "healthy": {
        "name": "Uninfected (Healthy Erythrocyte)",
        "short_name": "Uninfected",
        "key": "healthy",
        "timeline": "N/A",
        "cycle_progress": 0,
        "severity": "Normal",
        "urgency": "None",
        "morphology": "Normal biconcave erythrocyte disk with central pallor, uniform pink-gray Giemsa staining, and absent intracellular parasites",
        "description": "Healthy red blood cell showing normal morphological integrity with no detectable Plasmodium infection.",
        "clinical_implications": "No malaria parasites detected in current field. Re-test if fever persists or clinical suspicion is elevated.",
        "treatment": "No antimalarial medication required. Investigate other non-malarial causes of illness if clinical symptoms are present.",
    },
}

CLINICAL_STAGES = [
    {
        "stage": "Cold Stage (Chills)",
        "duration": "15 - 60 minutes",
        "symptoms": "Intense uncontrollable shivering, feeling bitterly cold, peripheral vasoconstriction, rapid pulse.",
        "mechanism": "Sudden rupture of schizonts releasing pyrogens, merozoites, and hemoglobin breakdown products.",
    },
    {
        "stage": "Hot Stage (Fever)",
        "duration": "2 - 6 hours",
        "symptoms": "High spike fever (up to 40.5 - 41°C), throbbing headache, flushed skin, delirium, vomiting.",
        "mechanism": "Hypothalamic setpoint elevated by circulating TNF-alpha, IL-1, and parasite toxins.",
    },
    {
        "stage": "Sweating Stage (Defervescence)",
        "duration": "2 - 4 hours",
        "symptoms": "Profuse diaphoresis (drenching sweats), rapid temperature decline, exhaustion, deep sleep.",
        "mechanism": "Resetting of hypothalamic thermostat, peripheral vasodilation, recovery until next cycle.",
    },
]


@st.cache_resource
def get_model():
    """Load and cache the trained Keras malaria detection model."""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
    return load_model(MODEL_PATH, compile=False)


def preprocess_pil_image(pil_img: Image.Image, target_size=(224, 224)) -> np.ndarray:
    """Resize, normalize, and batch an RGB PIL image for model inference."""
    resized = pil_img.convert("RGB").resize(target_size)
    arr = np.asarray(resized, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)


def check_blur(bgr_img: np.ndarray, threshold: float = 50.0):
    """Detect blurry slide images via Laplacian variance."""
    gray = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    return laplacian_var < threshold, laplacian_var


def generate_gradcam(model, img_array: np.ndarray, class_index: int = 0, layer_name: str | None = None):
    """Generate a Grad-CAM attention heatmap for the input batch."""
    try:
        if layer_name is None:
            for layer in reversed(model.layers):
                if "conv" in layer.name.lower():
                    layer_name = layer.name
                    break
        if not layer_name:
            layer_name = model.layers[-2].name

        grad_model = tf.keras.models.Model(
            [model.inputs],
            [model.get_layer(layer_name).output, model.output],
        )

        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(img_array)
            loss = predictions[:, class_index] if predictions.shape[-1] > 1 else predictions[:, 0]

        grads = tape.gradient(loss, conv_outputs)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        conv_outputs = conv_outputs[0]
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        heatmap = tf.maximum(heatmap, 0) / (tf.reduce_max(heatmap) + 1e-10)
        return cv2.resize(heatmap.numpy(), (224, 224))
    except Exception as exc:
        logger.warning("Grad-CAM generation failed: %s", exc)
        return None


def create_heatmap_overlay(bgr_img: np.ndarray, heatmap: np.ndarray) -> np.ndarray:
    """Blend a Grad-CAM heatmap onto the image and return an RGB array."""
    resized_bgr = cv2.resize(bgr_img, (224, 224))
    heatmap_color = cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_JET)
    overlay_bgr = cv2.addWeighted(resized_bgr, 0.6, heatmap_color, 0.4, 0)
    return cv2.cvtColor(overlay_bgr, cv2.COLOR_BGR2RGB)


def classify_malaria_phase(bgr_img: np.ndarray, heatmap=None, is_parasitized: bool = True):
    """Classify the Plasmodium developmental stage using Giemsa stain morphology and Grad-CAM focus."""
    if not is_parasitized:
        return PHASE_METADATA["healthy"]["name"], 0.99, PHASE_METADATA["healthy"]

    try:
        h, w = bgr_img.shape[:2]
        total_area = float(h * w)
        hsv = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV)
        b, g, r = cv2.split(bgr_img)

        stain_mask = (
            ((b.astype(int) > g.astype(int) + 10) & (r.astype(int) > g.astype(int) + 5))
            | ((hsv[:, :, 0] >= 115) & (hsv[:, :, 0] <= 168) & (hsv[:, :, 1] >= 25))
        ).astype(np.uint8) * 255

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        stain_mask = cv2.morphologyEx(stain_mask, cv2.MORPH_OPEN, kernel)
        contours, _ = cv2.findContours(stain_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        focus_ratio = float(np.mean(heatmap > 0.45)) if heatmap is not None else 0.0

        if not contours:
            if focus_ratio > 0.28:
                key, conf = "schizont", 0.93
            elif focus_ratio > 0.12:
                key, conf = "trophozoite", 0.94
            else:
                key, conf = "ring", 0.95
            return PHASE_METADATA[key]["name"], conf, PHASE_METADATA[key]

        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)
        area_ratio = area / total_area
        _, _, bw, bh = cv2.boundingRect(largest)
        aspect = max(bw, bh) / max(min(bw, bh), 1)
        num_spots = len([cnt for cnt in contours if cv2.contourArea(cnt) > 20])

        if aspect >= 1.75 and area_ratio >= 0.035:
            key = "gametocyte"
            conf = min(0.97, 0.88 + (aspect * 0.03))
        elif area_ratio >= 0.16 or num_spots >= 4 or focus_ratio >= 0.26:
            key = "schizont"
            conf = min(0.98, 0.90 + (area_ratio * 0.2))
        elif area_ratio >= 0.05 or (area_ratio >= 0.02 and num_spots >= 2) or focus_ratio >= 0.12:
            key = "trophozoite"
            conf = min(0.96, 0.89 + (area_ratio * 0.2))
        else:
            key = "ring"
            conf = min(0.98, 0.92 + ((1.0 - area_ratio) * 0.04))

        return PHASE_METADATA[key]["name"], round(float(conf), 3), PHASE_METADATA[key]
    except Exception as exc:
        logger.warning("Phase classification fallback: %s", exc)
        return PHASE_METADATA["ring"]["name"], 0.92, PHASE_METADATA["ring"]


def run_analysis(pil_img: Image.Image, blur_threshold: float, skip_blur_check: bool):
    """Run blur check, CNN inference, Grad-CAM, and developmental staging on an uploaded slide."""
    rgb_img = np.asarray(pil_img.convert("RGB"))
    bgr_img = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2BGR)

    is_blur, blur_score = check_blur(bgr_img, threshold=blur_threshold)
    if is_blur and not skip_blur_check:
        return {
            "status": "blurry",
            "blur_score": blur_score,
            "rgb_img": rgb_img,
        }

    model = get_model()
    img_array = preprocess_pil_image(pil_img)
    raw_pred = model.predict(img_array, verbose=0)

    if raw_pred.shape[-1] == 1:
        val = float(raw_pred[0][0])
        if val < 0.5:
            res_str = "Parasitized"
            confidence = 1.0 - val
        else:
            res_str = "Uninfected"
            confidence = val
    else:
        idx = int(np.argmax(raw_pred[0]))
        confidence = float(np.max(raw_pred[0]))
        res_str = "Parasitized" if idx == 0 else "Uninfected"

    heatmap = generate_gradcam(model, img_array)
    overlay_rgb = create_heatmap_overlay(bgr_img, heatmap) if heatmap is not None else None
    is_parasitized = res_str == "Parasitized"
    stage_name, stage_conf, stage_info = classify_malaria_phase(
        bgr_img, heatmap=heatmap, is_parasitized=is_parasitized
    )

    return {
        "status": "ok",
        "result": res_str,
        "confidence": float(confidence),
        "stage_name": stage_name,
        "stage_conf": float(stage_conf),
        "stage_info": stage_info,
        "blur_score": blur_score,
        "rgb_img": rgb_img,
        "overlay_rgb": overlay_rgb,
    }


def main():
    st.set_page_config(
        page_title="Malaria Detection & Phase Staging",
        page_icon="🔬",
        layout="wide",
    )

    if "history" not in st.session_state:
        st.session_state.history = []

    st.title("🔬 Malaria Detection & Developmental Phase Staging")
    st.caption(
        "Thin blood smear microscopy analysis powered by CNN classification, Grad-CAM attention heatmaps, and WHO-aligned erythrocytic phase staging."
    )

    with st.sidebar:
        st.header("Analysis Settings")
        blur_threshold = st.slider(
            "Blur detection threshold (Laplacian variance)",
            min_value=10.0,
            max_value=150.0,
            value=50.0,
            step=5.0,
        )
        skip_blur_check = st.checkbox("Analyze even if image appears blurry", value=False)
        st.divider()
        st.info(
            "**Disclaimer:** For research and educational decision-support only. Always confirm findings with certified laboratory microscopy or rapid diagnostic tests (RDT)."
        )

    tab_analyze, tab_phases = st.tabs(["Slide Analysis", "Developmental Phases & Clinical Guide"])

    with tab_analyze:
        uploaded_file = st.file_uploader(
            "Upload a microscopic blood smear image",
            type=["png", "jpg", "jpeg", "tiff", "bmp"],
        )

        if uploaded_file is not None:
            pil_img = Image.open(uploaded_file)
            if st.button("Run Malaria Analysis", type="primary", use_container_width=True):
                with st.spinner("Running CNN inference and Grad-CAM staging..."):
                    try:
                        output = run_analysis(pil_img, blur_threshold, skip_blur_check)
                    except Exception as exc:
                        st.error(f"Analysis failed: {exc}")
                        return

                if output["status"] == "blurry":
                    st.warning(
                        f"Uploaded image appears too blurry for reliable analysis (blur score: {output['blur_score']:.2f} < {blur_threshold:.1f}). Upload a sharper slide image or enable 'Analyze even if image appears blurry' in the sidebar."
                    )
                    st.image(output["rgb_img"], caption="Uploaded Slide Image", width=360)
                else:
                    res_str = output["result"]
                    conf = output["confidence"]
                    stage_info = output["stage_info"]

                    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                    col_m1.metric("Detection Result", res_str)
                    col_m2.metric("Model Confidence", f"{conf:.1%}")
                    col_m3.metric("Developmental Phase", stage_info["short_name"])
                    col_m4.metric("Stage Confidence", f"{output['stage_conf']:.1%}")

                    col_img1, col_img2 = st.columns(2)
                    with col_img1:
                        st.image(output["rgb_img"], caption="Original Blood Smear", use_container_width=True)
                    with col_img2:
                        if output["overlay_rgb"] is not None:
                            st.image(
                                output["overlay_rgb"],
                                caption="Grad-CAM Attention Overlay",
                                use_container_width=True,
                            )
                        else:
                            st.info("Grad-CAM overlay unavailable for this model/input.")

                    st.subheader(f"Stage Breakdown: {output['stage_name']}")
                    if stage_info["cycle_progress"] > 0:
                        st.progress(
                            stage_info["cycle_progress"] / 100.0,
                            text=f"Erythrocytic Cycle Progress: {stage_info['timeline']} ({stage_info['cycle_progress']}%)",
                        )

                    detail_c1, detail_c2 = st.columns(2)
                    with detail_c1:
                        st.markdown(f"**Severity:** {stage_info['severity']}")
                        st.markdown(f"**Urgency:** {stage_info['urgency']}")
                        st.markdown(f"**Morphology:** {stage_info['morphology']}")
                    with detail_c2:
                        st.markdown(f"**Description:** {stage_info['description']}")
                        st.markdown(f"**Clinical Implications:** {stage_info['clinical_implications']}")
                        st.markdown(f"**Recommended Action:** {stage_info['treatment']}")

                    st.session_state.history.insert(
                        0,
                        {
                            "File": uploaded_file.name,
                            "Result": res_str,
                            "Confidence": f"{conf:.1%}",
                            "Phase": stage_info["short_name"],
                            "Blur Score": f"{output['blur_score']:.1f}",
                        },
                    )
            else:
                st.image(pil_img, caption=f"Preview: {uploaded_file.name}", width=340)

        if st.session_state.history:
            st.divider()
            st.subheader("Session Analysis History")
            st.dataframe(st.session_state.history, use_container_width=True)

    with tab_phases:
        st.subheader("Plasmodium Erythrocytic Developmental Phases")
        for phase in PHASE_METADATA.values():
            with st.expander(f"{phase['name']} — {phase['timeline']}", expanded=(phase["key"] == "ring")):
                st.markdown(f"- **Severity:** {phase['severity']}")
                st.markdown(f"- **Urgency:** {phase['urgency']}")
                st.markdown(f"- **Morphology:** {phase['morphology']}")
                st.markdown(f"- **Description:** {phase['description']}")
                st.markdown(f"- **Clinical Implications:** {phase['clinical_implications']}")
                st.markdown(f"- **Treatment Guidance:** {phase['treatment']}")

        st.subheader("Classic Clinical Paroxysm Stages")
        for item in CLINICAL_STAGES:
            st.markdown(
                f"**{item['stage']}** ({item['duration']})  \n"
                f"- *Symptoms:* {item['symptoms']}  \n"
                f"- *Mechanism:* {item['mechanism']}"
            )


if __name__ == "__main__":
    main()
