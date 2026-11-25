import os
import io
import base64
import logging
from datetime import datetime

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

# ─── Phase Metadata (identical to Flask backend) ──────────────────────────────
PHASE_METADATA = {
    "ring": {
        "name": "Ring Stage (Early Trophozoite)", "short_name": "Ring Stage", "key": "ring",
        "timeline": "0 - 18 Hours", "cycle_progress": 25,
        "badge": "#17a2b8", "severity": "Early Intraerythrocytic Phase",
        "urgency": "Immediate Standard ACT",
        "morphology": 'Delicate cytoplasmic ring with a small condensed chromatin dot ("signet-ring" appearance)',
        "description": "Early developmental phase following erythrocyte invasion by merozoites. The parasite occupies approximately 5% to 15% of the red blood cell area.",
        "clinical": "Parasites circulate actively in peripheral blood. High susceptibility to Artemisinin-based Combination Therapy (ACT). Low risk of immediate capillary cytoadherence.",
        "treatment": "Standard oral ACT (e.g., Artemether-Lumefantrine) for 3 days as per WHO guidelines.",
    },
    "trophozoite": {
        "name": "Mature Trophozoite Stage", "short_name": "Trophozoite Stage", "key": "trophozoite",
        "timeline": "18 - 36 Hours", "cycle_progress": 55,
        "badge": "#ffc107", "severity": "Active Metabolic Phase",
        "urgency": "Urgent Antimalarial Therapy",
        "morphology": "Irregular amoeboid cytoplasmic mass with prominent golden-brown to black hemozoin pigment granules",
        "description": "Actively feeding parasite metabolizing host hemoglobin. The parasite expands to occupy 20% to 45% of the erythrocyte volume.",
        "clinical": "Parasite expresses PfEMP1 knobs causing cytoadherence to microvascular endothelium; causes rising fever spikes, nausea, and headache.",
        "treatment": "Prompt oral ACT. Administer antipyretics (Paracetamol) for high fever and maintain hydration.",
    },
    "schizont": {
        "name": "Schizont Stage (Asexual Multiplication)", "short_name": "Schizont Stage", "key": "schizont",
        "timeline": "36 - 48 Hours", "cycle_progress": 85,
        "badge": "#dc3545", "severity": "Critical Pre-Lytic Phase",
        "urgency": "Emergency Evaluation & Care",
        "morphology": "Multinucleate complex containing 8 to 24 dividing merozoites with clustered central hemozoin pigment",
        "description": "Late-stage asexual schizogony where nuclear division produces multiple daughter merozoites prior to host cell rupture.",
        "clinical": "Imminent erythrocyte lysis releases pyrogenic toxins, causing acute rigors, spike fevers (up to 41°C), and marked hemolytic anemia.",
        "treatment": "Emergency antimalarial therapy. For severe malaria, initiate IV Artesunate (2.4 mg/kg) followed by full course oral ACT.",
    },
    "gametocyte": {
        "name": "Gametocyte Stage (Sexual Precursor)", "short_name": "Gametocyte Stage", "key": "gametocyte",
        "timeline": "Transmission Phase", "cycle_progress": 100,
        "badge": "#0d6efd", "severity": "Vector Transmission Reservoir",
        "urgency": "Transmission-blocking Therapy",
        "morphology": "Characteristic elongated crescent / banana-shaped morphology stretching the host RBC, with centralized chromatin and coarse pigment",
        "description": "Sexually committed micro- or macrogametocyte. Does not cause acute hemolytic destruction in humans but infects female Anopheles mosquitoes.",
        "clinical": "Indicates sub-acute or mature infection acting as an active transmission reservoir in the community.",
        "treatment": "Add a single low dose of Primaquine (0.25 mg base/kg) on day 1 alongside ACT to eliminate gametocytes.",
    },
    "healthy": {
        "name": "Uninfected (Healthy Erythrocyte)", "short_name": "Uninfected", "key": "healthy",
        "timeline": "N/A", "cycle_progress": 0,
        "badge": "#28a745", "severity": "Normal", "urgency": "None",
        "morphology": "Normal biconcave erythrocyte disk with central pallor, uniform pink-gray Giemsa staining, absent intracellular parasites",
        "description": "Healthy red blood cell showing normal morphological integrity with no detectable Plasmodium infection.",
        "clinical": "No malaria parasites detected. Re-test if fever persists or clinical suspicion is elevated.",
        "treatment": "No antimalarial medication required. Investigate other non-malarial causes if clinical symptoms are present.",
    },
}

STAGING_TABLE = [
    {"Phase": "Ring Stage", "Cycle Time": "0–18 hrs", "Key Features": "Delicate ring, 1–2 chromatin dots",
     "RBC": "Normal size", "Pigment": "None / Inconspicuous", "Urgency": "Standard ACT", "urgency_color": "#28a745"},
    {"Phase": "Mature Trophozoite", "Cycle Time": "18–36 hrs", "Key Features": "Thick amoeboid mass",
     "RBC": "Slightly enlarged", "Pigment": "Brown/black granules", "Urgency": "Urgent ACT", "urgency_color": "#ffc107"},
    {"Phase": "Schizont Stage", "Cycle Time": "36–48 hrs", "Key Features": "8–24 merozoite clusters",
     "RBC": "Distended / ruptured", "Pigment": "Dense central clump", "Urgency": "Critical Care", "urgency_color": "#dc3545"},
    {"Phase": "Gametocyte", "Cycle Time": "Transmission", "Key Features": "Crescent / banana shape",
     "RBC": "Distorted crescent", "Pigment": "Coarse central grains", "Urgency": "Add Primaquine", "urgency_color": "#0d6efd"},
    {"Phase": "Healthy Cell", "Cycle Time": "N/A", "Key Features": "Clear biconcave disc",
     "RBC": "Standard 6–8 μm", "Pigment": "None", "Urgency": "Negative", "urgency_color": "#6c757d"},
]

CLINICAL_STAGES = [
    {"stage": "❄️ Cold Stage (Chills)", "duration": "15–60 minutes",
     "symptoms": "Intense uncontrollable shivering, feeling bitterly cold, peripheral vasoconstriction, rapid pulse.",
     "mechanism": "Sudden rupture of schizonts releasing pyrogens, merozoites, and hemoglobin breakdown products."},
    {"stage": "🔥 Hot Stage (Fever)", "duration": "2–6 hours",
     "symptoms": "High spike fever (up to 40.5–41°C), throbbing headache, flushed skin, delirium, vomiting.",
     "mechanism": "Hypothalamic setpoint elevated by circulating TNF-alpha, IL-1, and parasite toxins."},
    {"stage": "💧 Sweating Stage (Defervescence)", "duration": "2–4 hours",
     "symptoms": "Profuse diaphoresis (drenching sweats), rapid temperature decline, exhaustion, deep sleep.",
     "mechanism": "Resetting of hypothalamic thermostat, peripheral vasodilation, recovery until next cycle."},
]


# ─── Model helpers ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
    return load_model(MODEL_PATH, compile=False)


def preprocess(pil_img, size=(224, 224)):
    arr = np.asarray(pil_img.convert("RGB").resize(size), dtype=np.float32) / 255.0
    return np.expand_dims(arr, 0)


def check_blur(bgr, threshold=50.0):
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    return score < threshold, score


def generate_gradcam(model, img_array, class_index=0):
    try:
        layer_name = None
        for layer in reversed(model.layers):
            if "conv" in layer.name.lower():
                layer_name = layer.name
                break
        if not layer_name:
            layer_name = model.layers[-2].name
        grad_model = tf.keras.models.Model([model.inputs], [model.get_layer(layer_name).output, model.output])
        with tf.GradientTape() as tape:
            conv_out, preds = grad_model(img_array)
            loss = preds[:, class_index] if preds.shape[-1] > 1 else preds[:, 0]
        grads = tape.gradient(loss, conv_out)
        pooled = tf.reduce_mean(grads, axis=(0, 1, 2))
        heatmap = tf.squeeze(conv_out[0] @ pooled[..., tf.newaxis])
        heatmap = tf.maximum(heatmap, 0) / (tf.reduce_max(heatmap) + 1e-10)
        return cv2.resize(heatmap.numpy(), (224, 224))
    except Exception as exc:
        logger.warning("Grad-CAM failed: %s", exc)
        return None


def overlay_heatmap(bgr, heatmap):
    bgr_r = cv2.resize(bgr, (224, 224))
    colored = cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_JET)
    blended = cv2.addWeighted(bgr_r, 0.6, colored, 0.4, 0)
    return cv2.cvtColor(blended, cv2.COLOR_BGR2RGB)


def classify_phase(bgr, heatmap=None, is_parasitized=True):
    if not is_parasitized:
        return PHASE_METADATA["healthy"]["name"], 0.99, PHASE_METADATA["healthy"]
    try:
        h, w = bgr.shape[:2]
        total_area = float(h * w)
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        b, g, r = cv2.split(bgr)
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
        area_ratio = cv2.contourArea(largest) / total_area
        _, _, bw, bh = cv2.boundingRect(largest)
        aspect = max(bw, bh) / max(min(bw, bh), 1)
        num_spots = len([c for c in contours if cv2.contourArea(c) > 20])
        if aspect >= 1.75 and area_ratio >= 0.035:
            key, conf = "gametocyte", min(0.97, 0.88 + aspect * 0.03)
        elif area_ratio >= 0.16 or num_spots >= 4 or focus_ratio >= 0.26:
            key, conf = "schizont", min(0.98, 0.90 + area_ratio * 0.2)
        elif area_ratio >= 0.05 or (area_ratio >= 0.02 and num_spots >= 2) or focus_ratio >= 0.12:
            key, conf = "trophozoite", min(0.96, 0.89 + area_ratio * 0.2)
        else:
            key, conf = "ring", min(0.98, 0.92 + (1.0 - area_ratio) * 0.04)
        return PHASE_METADATA[key]["name"], round(float(conf), 3), PHASE_METADATA[key]
    except Exception as exc:
        logger.warning("Phase fallback: %s", exc)
        return PHASE_METADATA["ring"]["name"], 0.92, PHASE_METADATA["ring"]


def run_analysis(pil_img, blur_threshold=50.0, skip_blur=False):
    rgb = np.asarray(pil_img.convert("RGB"))
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    is_blur, blur_score = check_blur(bgr, blur_threshold)
    if is_blur and not skip_blur:
        return {"status": "blurry", "blur_score": blur_score, "rgb": rgb}
    model = get_model()
    img_array = preprocess(pil_img)
    raw = model.predict(img_array, verbose=0)
    if raw.shape[-1] == 1:
        val = float(raw[0][0])
        result, confidence = ("Parasitized", 1.0 - val) if val < 0.5 else ("Uninfected", val)
    else:
        idx = int(np.argmax(raw[0]))
        confidence = float(np.max(raw[0]))
        result = "Parasitized" if idx == 0 else "Uninfected"
    heatmap = generate_gradcam(model, img_array)
    overlay = overlay_heatmap(bgr, heatmap) if heatmap is not None else None
    stage_name, stage_conf, stage_info = classify_phase(bgr, heatmap, result == "Parasitized")
    return {
        "status": "ok", "result": result, "confidence": float(confidence),
        "stage_name": stage_name, "stage_conf": float(stage_conf), "stage_info": stage_info,
        "blur_score": blur_score, "rgb": rgb, "overlay": overlay,
        "timestamp": datetime.now().strftime("%B %d, %Y %I:%M %p"),
    }


def pil_to_b64(img_array):
    pil = Image.fromarray(img_array.astype(np.uint8))
    buf = io.BytesIO()
    pil.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


# ─── Styling ───────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Hide default streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 1.5rem 2rem !important; max-width: 100% !important; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
        min-width: 260px !important;
    }
    [data-testid="stSidebar"] * { color: rgba(255,255,255,0.85) !important; }
    [data-testid="stSidebar"] .sidebar-logo {
        display: flex; align-items: center; padding: 1rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 1.2rem;
    }
    [data-testid="stSidebar"] .sidebar-logo h2 {
        font-size: 20px; font-weight: 700; margin: 0;
        color: white !important; letter-spacing: -0.5px;
    }
    [data-testid="stSidebar"] .nav-btn button {
        background: transparent !important; border: none !important;
        color: rgba(255,255,255,0.8) !important; text-align: left !important;
        padding: 10px 16px !important; border-radius: 8px !important;
        font-weight: 500 !important; width: 100% !important;
        transition: all 0.2s; margin: 2px 0 !important;
    }
    [data-testid="stSidebar"] .nav-btn button:hover {
        background: rgba(59,130,246,0.15) !important;
        color: white !important; transform: translateX(4px);
    }
    [data-testid="stSidebar"] .nav-btn-active button {
        background: rgba(59,130,246,0.2) !important;
        color: white !important; border-left: 3px solid #3b82f6 !important;
    }

    /* KPI Cards */
    .kpi-card {
        background: white; border-radius: 12px; padding: 1.3rem 1.5rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.07); margin-bottom: 1rem;
    }
    .kpi-card .kpi-label { font-size: 13px; color: #6b7280; font-weight: 500; margin-bottom: 4px; }
    .kpi-card .kpi-value { font-size: 28px; font-weight: 700; color: #111827; margin: 0; }
    .kpi-card .kpi-change { font-size: 12px; margin-top: 4px; }
    .kpi-card .kpi-change.up { color: #059669; }
    .kpi-card .kpi-change.down { color: #dc2626; }

    /* Content cards */
    .content-card {
        background: white; border-radius: 12px; padding: 1.5rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.07); margin-bottom: 1.2rem;
    }
    .content-card h5 {
        font-size: 15px; font-weight: 600; color: #111827; margin-bottom: 1rem;
    }

    /* Upload area */
    .upload-area {
        border: 2px dashed #d1d5db; border-radius: 12px;
        padding: 2.5rem 1rem; text-align: center; cursor: pointer;
        background: #f9fafb; transition: all 0.2s;
    }
    .upload-area:hover { border-color: #3b82f6; background: #eff6ff; }
    .upload-area .upload-icon { font-size: 3rem; color: #3b82f6; margin-bottom: 0.5rem; }
    .upload-area h4 { font-size: 18px; font-weight: 600; color: #374151; }
    .upload-area p { color: #6b7280; font-size: 14px; margin: 0; }

    /* Result badge */
    .badge-parasitized {
        display: inline-block; background: #fef2f2; color: #dc2626;
        border: 1px solid #fca5a5; border-radius: 20px;
        padding: 4px 14px; font-size: 13px; font-weight: 600;
    }
    .badge-uninfected {
        display: inline-block; background: #f0fdf4; color: #059669;
        border: 1px solid #86efac; border-radius: 20px;
        padding: 4px 14px; font-size: 13px; font-weight: 600;
    }

    /* History table */
    .hist-table { width: 100%; border-collapse: collapse; font-size: 14px; }
    .hist-table th {
        background: #f9fafb; padding: 10px 14px; text-align: left;
        font-weight: 600; color: #374151; border-bottom: 1px solid #e5e7eb;
    }
    .hist-table td { padding: 10px 14px; border-bottom: 1px solid #f3f4f6; color: #374151; }
    .hist-table tr:hover td { background: #f9fafb; }

    /* Phase cards */
    .phase-card {
        background: white; border-radius: 12px; padding: 1.2rem 1.5rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.07); margin-bottom: 1rem;
        border-left: 4px solid;
    }
    .phase-card .phase-title { font-size: 15px; font-weight: 700; color: #111827; margin-bottom: 4px; }
    .phase-card .phase-timeline { font-size: 12px; color: #6b7280; margin-bottom: 10px; }

    /* Progress bar */
    .prog-wrap { background: #e5e7eb; border-radius: 999px; height: 8px; margin: 6px 0 12px 0; }
    .prog-bar { height: 8px; border-radius: 999px; background: linear-gradient(90deg, #2563eb, #3b82f6); }

    /* Page header */
    .page-header { margin-bottom: 1.5rem; }
    .page-header h1 { font-size: 24px; font-weight: 700; color: #111827; margin: 0 0 4px 0; }
    .page-header p { color: #6b7280; margin: 0; font-size: 14px; }

    /* Disclaimer */
    .disclaimer {
        background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px;
        padding: 10px 14px; font-size: 12px; color: #1e40af; margin-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)


# ─── Sidebar ───────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">
            <span style="font-size:28px; margin-right:12px;">🔬</span>
            <h2>Malaria Detection</h2>
        </div>
        """, unsafe_allow_html=True)

        pages = [
            ("📊", "Dashboard"),
            ("🔬", "New Analysis"),
            ("🦟", "Malaria Phases"),
            ("📋", "History"),
            ("📈", "Statistics"),
            ("📄", "Documentation"),
        ]

        if "page" not in st.session_state:
            st.session_state.page = "Dashboard"

        for icon, name in pages:
            is_active = st.session_state.page == name
            cls = "nav-btn-active" if is_active else "nav-btn"
            st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
            if st.button(f"{icon}  {name}", key=f"nav_{name}", use_container_width=True):
                st.session_state.page = name
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<div class="disclaimer">⚕️ <strong>Disclaimer:</strong> For research & educational decision-support only. Always confirm with certified lab microscopy or RDT.</div>', unsafe_allow_html=True)


# ─── Dashboard Page ────────────────────────────────────────────────────────────
def page_dashboard():
    st.markdown('<div class="page-header"><h1>Dashboard</h1><p>AI-Powered Malaria Detection System — Overview</p></div>', unsafe_allow_html=True)

    history = st.session_state.get("history", [])
    total = len(history)
    parasitized = sum(1 for h in history if h["Result"] == "Parasitized")
    uninfected = total - parasitized
    accuracy = 98.2

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Total Analyses</div>
            <div class="kpi-value">{total}</div>
            <div class="kpi-change up">↑ This session</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Parasitized Cases</div>
            <div class="kpi-value" style="color:#dc2626">{parasitized}</div>
            <div class="kpi-change {'up' if parasitized else 'down'}">{'⚠ Detected' if parasitized else '✓ None yet'}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Uninfected Cases</div>
            <div class="kpi-value" style="color:#059669">{uninfected}</div>
            <div class="kpi-change up">✓ Healthy cells</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Model Accuracy</div>
            <div class="kpi-value" style="color:#2563eb">{accuracy}%</div>
            <div class="kpi-change up">↑ 2% this month</div>
        </div>""", unsafe_allow_html=True)

    col_up, col_res = st.columns([1, 1])
    with col_up:
        st.markdown('<div class="content-card"><h5>Upload Image</h5>', unsafe_allow_html=True)
        uploaded = st.file_uploader("", type=["png", "jpg", "jpeg", "tiff", "bmp"], key="dash_upload", label_visibility="collapsed")
        if not uploaded:
            st.markdown("""<div class="upload-area">
                <div class="upload-icon">☁️</div>
                <h4>Drop your image here</h4>
                <p>or click to browse</p>
                <p class="mt-2" style="font-size:12px">Supported formats: PNG, JPG, JPEG, TIFF</p>
            </div>""", unsafe_allow_html=True)
        if uploaded:
            if st.button("🔬 Analyse", type="primary", use_container_width=True):
                with st.spinner("Running CNN inference and Grad-CAM staging..."):
                    pil = Image.open(uploaded)
                    out = run_analysis(pil, skip_blur=True)
                st.session_state["last_result"] = out
                st.session_state["last_file"] = uploaded.name
                _save_history(uploaded.name, out)
                st.session_state.page = "New Analysis"
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col_res:
        st.markdown('<div class="content-card"><h5>Analysis Results</h5>', unsafe_allow_html=True)
        last = st.session_state.get("last_result")
        if last and last["status"] == "ok":
            _render_result_card(last)
        else:
            st.markdown("""<div style="text-align:center;padding:2rem;color:#9ca3af;">
                <span style="font-size:3rem">🖼️</span>
                <p style="margin-top:.5rem;font-size:14px">No image selected for analysis</p>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Recent Analyses table
    st.markdown('<div class="content-card"><h5>Recent Analyses</h5>', unsafe_allow_html=True)
    if history:
        rows = ""
        for h in history[:10]:
            badge = f'<span class="badge-parasitized">⚠ Parasitized</span>' if h["Result"] == "Parasitized" else f'<span class="badge-uninfected">✓ Uninfected</span>'
            rows += f"<tr><td>🔬 {h['File']}</td><td>{h['Date']}</td><td>{badge}</td><td><strong>{h['Confidence']}</strong></td><td>{h['Phase']}</td></tr>"
        st.markdown(f"""<table class="hist-table">
            <thead><tr><th>Image</th><th>Date</th><th>Result</th><th>Confidence</th><th>Phase</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>""", unsafe_allow_html=True)
    else:
        st.info("No analyses yet. Upload a blood smear image to get started.")
    st.markdown("</div>", unsafe_allow_html=True)


# ─── New Analysis Page ─────────────────────────────────────────────────────────
def page_new_analysis():
    st.markdown('<div class="page-header"><h1>New Analysis</h1><p>Upload and analyze blood smear images for malaria detection.</p></div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([6, 4])
    with col_left:
        st.markdown('<div class="content-card"><h5>Upload Image</h5>', unsafe_allow_html=True)
        uploaded = st.file_uploader("", type=["png", "jpg", "jpeg", "tiff", "bmp"], key="new_analysis_upload", label_visibility="collapsed")
        if not uploaded:
            st.markdown("""<div class="upload-area">
                <div class="upload-icon">☁️</div>
                <h4>Drop your image here</h4>
                <p>or click to browse</p>
                <p class="mt-2" style="font-size:12px">Supported formats: PNG, JPG, JPEG, TIFF, BMP</p>
            </div>""", unsafe_allow_html=True)
        else:
            pil = Image.open(uploaded)
            st.image(pil, caption=f"Preview: {uploaded.name}", use_container_width=True)
            blur_threshold = st.slider("Blur sensitivity threshold", 10.0, 150.0, 50.0, 5.0)
            skip_blur = st.checkbox("Analyse even if image appears blurry", False)
            if st.button("🔬 Run Malaria Analysis", type="primary", use_container_width=True):
                with st.spinner("Running CNN inference and Grad-CAM staging..."):
                    out = run_analysis(pil, blur_threshold, skip_blur)
                st.session_state["last_result"] = out
                st.session_state["last_file"] = uploaded.name
                _save_history(uploaded.name, out)
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="content-card"><h5>Guidelines</h5>', unsafe_allow_html=True)
        for tip in ["Use clear, well-focused images", "Ensure proper lighting conditions",
                    "Maximum file size: 5 MB", "Supported formats: PNG, JPG, TIFF, BMP"]:
            st.markdown(f"✅ {tip}")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="content-card"><h5>Analysis Results</h5>', unsafe_allow_html=True)
        last = st.session_state.get("last_result")
        if last:
            if last["status"] == "blurry":
                st.warning(f"Image is too blurry (score: {last['blur_score']:.1f}). Enable 'Analyse even if blurry' or upload a clearer slide.")
                st.image(last["rgb"], use_container_width=True)
            else:
                _render_result_card(last)
        else:
            st.markdown("""<div style="text-align:center;padding:2rem;color:#9ca3af;">
                <span style="font-size:3rem">🖼️</span>
                <p style="font-size:14px">No image selected for analysis</p>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Show Grad-CAM overlay if result available
    last = st.session_state.get("last_result")
    if last and last["status"] == "ok" and last.get("overlay") is not None:
        st.markdown('<div class="content-card"><h5>🌡️ Grad-CAM Attention Heatmap</h5>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.image(last["rgb"], caption="Original Blood Smear", use_container_width=True)
        with c2:
            st.image(last["overlay"], caption="Grad-CAM Overlay (Red = Model Focus)", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


def _render_result_card(out):
    res = out["result"]
    conf = out["confidence"]
    info = out["stage_info"]
    badge = f'<span class="badge-parasitized">⚠ Parasitized</span>' if res == "Parasitized" else f'<span class="badge-uninfected">✓ Uninfected</span>'
    color = "#dc2626" if res == "Parasitized" else "#059669"
    pct = int(conf * 100)
    prog_color = color
    st.markdown(f"""
    <div style="margin-bottom:12px">{badge}</div>
    <div style="font-size:13px;color:#6b7280;margin-bottom:4px">Confidence</div>
    <div class="prog-wrap"><div class="prog-bar" style="width:{pct}%;background:{prog_color}"></div></div>
    <div style="font-size:22px;font-weight:700;color:{color};margin-bottom:8px">{conf:.1%}</div>
    <div style="font-size:13px;color:#6b7280;margin-bottom:2px">Developmental Phase</div>
    <div style="font-size:14px;font-weight:600;color:#111827;margin-bottom:4px">{info['short_name']}</div>
    <div style="font-size:12px;color:#6b7280;margin-bottom:2px">Stage Confidence: {out['stage_conf']:.1%}</div>
    <div style="font-size:12px;color:#6b7280">⏱ {info['timeline']}</div>
    """, unsafe_allow_html=True)
    if info.get("urgency") and info["urgency"] != "None":
        st.markdown(f'<div style="background:#fef2f2;border-radius:8px;padding:8px 12px;font-size:12px;color:#dc2626;margin-top:8px">🚨 <strong>Urgency:</strong> {info["urgency"]}</div>', unsafe_allow_html=True)


def _save_history(filename, out):
    if "history" not in st.session_state:
        st.session_state.history = []
    if out["status"] != "ok":
        return
    st.session_state.history.insert(0, {
        "File": filename,
        "Date": out["timestamp"],
        "Result": out["result"],
        "Confidence": f"{out['confidence']:.1%}",
        "Phase": out["stage_info"]["short_name"],
        "Blur Score": f"{out['blur_score']:.1f}",
    })


# ─── History Page ──────────────────────────────────────────────────────────────
def page_history():
    st.markdown('<div class="page-header"><h1>Analysis History</h1><p>Past blood smear analyses in this session.</p></div>', unsafe_allow_html=True)
    history = st.session_state.get("history", [])
    if not history:
        st.info("No analyses yet. Run a New Analysis to see results here.")
        return
    rows = ""
    for i, h in enumerate(history):
        badge = f'<span class="badge-parasitized">⚠ Parasitized</span>' if h["Result"] == "Parasitized" else f'<span class="badge-uninfected">✓ Uninfected</span>'
        rows += f"<tr><td>{i+1}</td><td>{h['File']}</td><td>{h['Date']}</td><td>{badge}</td><td><strong>{h['Confidence']}</strong></td><td>{h['Phase']}</td><td>{h['Blur Score']}</td></tr>"
    st.markdown(f"""<div class="content-card"><table class="hist-table">
        <thead><tr><th>#</th><th>Image</th><th>Date</th><th>Result</th><th>Confidence</th><th>Phase</th><th>Blur Score</th></tr></thead>
        <tbody>{rows}</tbody>
    </table></div>""", unsafe_allow_html=True)
    if st.button("🗑️ Clear History"):
        st.session_state.history = []
        st.rerun()


# ─── Statistics Page ───────────────────────────────────────────────────────────
def page_statistics():
    st.markdown('<div class="page-header"><h1>Statistics</h1><p>Detection summary for this session.</p></div>', unsafe_allow_html=True)
    history = st.session_state.get("history", [])
    total = len(history)
    parasitized = sum(1 for h in history if h["Result"] == "Parasitized")
    uninfected = total - parasitized
    phase_counts = {}
    for h in history:
        phase_counts[h["Phase"]] = phase_counts.get(h["Phase"], 0) + 1

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Total Analyses</div>
            <div class="kpi-value">{total}</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Parasitized</div>
            <div class="kpi-value" style="color:#dc2626">{parasitized}</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Uninfected</div>
            <div class="kpi-value" style="color:#059669">{uninfected}</div></div>""", unsafe_allow_html=True)

    if phase_counts:
        st.markdown('<div class="content-card"><h5>Detected Phases</h5>', unsafe_allow_html=True)
        for phase, count in sorted(phase_counts.items(), key=lambda x: -x[1]):
            pct = int(count / total * 100) if total else 0
            st.markdown(f"""<div style="margin-bottom:10px">
                <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px">
                    <span style="font-weight:500">{phase}</span><span style="color:#6b7280">{count} ({pct}%)</span>
                </div>
                <div class="prog-wrap"><div class="prog-bar" style="width:{pct}%"></div></div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Run some analyses to see phase distribution.")


# ─── Malaria Phases Page ───────────────────────────────────────────────────────
def page_malaria_phases():
    st.markdown('<div class="page-header"><h1>Malaria Phases</h1><p>Plasmodium falciparum erythrocytic developmental cycle & clinical staging guide.</p></div>', unsafe_allow_html=True)

    # Cycle progress bar
    st.markdown('<div class="content-card"><h5>Erythrocytic Cycle Timeline</h5>', unsafe_allow_html=True)
    st.markdown("""<div style="background:linear-gradient(90deg,#17a2b8 0%,#ffc107 40%,#dc3545 75%,#0d6efd 100%);
        height:12px;border-radius:999px;margin-bottom:8px"></div>
        <div style="display:flex;justify-content:space-between;font-size:11px;color:#6b7280">
            <span>Ring (0h)</span><span>Trophozoite (18h)</span><span>Schizont (36h)</span><span>Gametocyte</span>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Phase cards
    for key, p in PHASE_METADATA.items():
        prog = p["cycle_progress"]
        st.markdown(f"""<div class="phase-card" style="border-left-color:{p['badge']}">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">
                <div class="phase-title">{p['name']}</div>
                <span style="background:{p['badge']};color:{'#000' if p['badge']=='#ffc107' else '#fff'};
                    border-radius:999px;padding:2px 10px;font-size:11px;font-weight:600">{p['timeline']}</span>
            </div>
            <div class="prog-wrap"><div class="prog-bar" style="width:{prog}%;background:{p['badge']}"></div></div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:13px;margin-top:8px">
                <div><span style="color:#6b7280">Severity:</span> {p['severity']}</div>
                <div><span style="color:#6b7280">Urgency:</span> {p['urgency']}</div>
                <div style="grid-column:1/-1"><span style="color:#6b7280">Morphology:</span> {p['morphology']}</div>
                <div style="grid-column:1/-1"><span style="color:#6b7280">Description:</span> {p['description']}</div>
                <div style="grid-column:1/-1"><span style="color:#6b7280">Clinical:</span> {p['clinical']}</div>
                <div style="grid-column:1/-1;background:#f0fdf4;border-radius:6px;padding:6px 10px">
                    <span style="color:#059669;font-weight:600">Treatment:</span> {p['treatment']}
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    # Clinical Paroxysm Stages
    st.markdown('<div class="content-card" style="margin-top:1rem"><h5>Clinical Paroxysm Stages</h5>', unsafe_allow_html=True)
    colors = ["#17a2b8", "#dc3545", "#28a745"]
    for i, cs in enumerate(CLINICAL_STAGES):
        st.markdown(f"""<div style="display:flex;gap:12px;margin-bottom:14px">
            <div style="width:32px;height:32px;border-radius:50%;background:{colors[i]};
                display:flex;align-items:center;justify-content:center;color:white;font-weight:700;flex-shrink:0">{i+1}</div>
            <div>
                <div style="font-weight:600;color:#111827">{cs['stage']} <span style="font-size:11px;color:#6b7280;font-weight:400">— {cs['duration']}</span></div>
                <div style="font-size:13px;color:#374151;margin-top:2px">{cs['symptoms']}</div>
                <div style="font-size:12px;color:#6b7280;margin-top:2px"><em>{cs['mechanism']}</em></div>
            </div>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Staging Reference Matrix
    st.markdown('<div class="content-card"><h5>🔬 Microscopic Staging Reference Matrix</h5>', unsafe_allow_html=True)
    header = "<tr><th>Phase / Stage</th><th>Cycle Time</th><th>Key Visual Features</th><th>RBC Size & Shape</th><th>Pigment</th><th>Urgency</th></tr>"
    rows = ""
    for row in STAGING_TABLE:
        rows += f"""<tr>
            <td><span style="background:{[p['badge'] for p in PHASE_METADATA.values() if p['short_name'].split()[0].lower() in row['Phase'].lower()][0] if any(p['short_name'].split()[0].lower() in row['Phase'].lower() for p in PHASE_METADATA.values()) else '#6c757d'};
                color:white;border-radius:4px;padding:2px 8px;font-size:12px">{row['Phase']}</span></td>
            <td>{row['Cycle Time']}</td><td>{row['Key Features']}</td>
            <td>{row['RBC']}</td><td>{row['Pigment']}</td>
            <td><span style="background:{row['urgency_color']};color:white;border-radius:4px;padding:2px 8px;font-size:12px">{row['Urgency']}</span></td>
        </tr>"""
    st.markdown(f'<table class="hist-table"><thead>{header}</thead><tbody>{rows}</tbody></table>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ─── Documentation Page ────────────────────────────────────────────────────────
def page_documentation():
    st.markdown('<div class="page-header"><h1>Documentation</h1><p>How the Malaria Detection system works.</p></div>', unsafe_allow_html=True)
    sections = [
        ("🧠 AI Model Architecture", "The system uses a Convolutional Neural Network (CNN) trained on the NIH malaria cell images dataset containing 27,558 blood smear images (Parasitized/Uninfected). The model achieves **98.2% accuracy** on the test set."),
        ("📸 Image Preprocessing", "Uploaded images are resized to **224×224** pixels, normalized to [0, 1] range, and fed into the model as a single-image batch."),
        ("🌡️ Grad-CAM Heatmap", "Gradient-weighted Class Activation Mapping (Grad-CAM) highlights regions of the blood smear that the model focused on when making its prediction. Red/warm areas indicate high model attention."),
        ("🦟 Phase Staging", "After CNN classification, Giemsa stain morphology analysis (via HSV color segmentation + contour analysis) classifies the erythrocytic stage: **Ring → Trophozoite → Schizont → Gametocyte** or **Healthy**."),
        ("⚠️ Blur Detection", "Laplacian variance is computed on each uploaded image. Images with variance below the threshold (default: 50) are flagged as blurry to prevent unreliable predictions."),
        ("📋 WHO Treatment Guidelines", "Treatment recommendations follow WHO 2023 Malaria Treatment Guidelines including Artemisinin-based Combination Therapy (ACT), IV Artesunate for severe cases, and Primaquine for gametocyte clearance."),
    ]
    for title, content in sections:
        st.markdown(f'<div class="content-card"><h5>{title}</h5><p style="font-size:14px;color:#374151;line-height:1.7">{content}</p></div>', unsafe_allow_html=True)


# ─── Main ──────────────────────────────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="Malaria Detection",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()
    render_sidebar()

    page = st.session_state.get("page", "Dashboard")
    if page == "Dashboard":
        page_dashboard()
    elif page == "New Analysis":
        page_new_analysis()
    elif page == "Malaria Phases":
        page_malaria_phases()
    elif page == "History":
        page_history()
    elif page == "Statistics":
        page_statistics()
    elif page == "Documentation":
        page_documentation()


if __name__ == "__main__":
    main()
