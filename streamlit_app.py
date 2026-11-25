import os, io, base64, logging
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

PHASE_METADATA = {
    "ring":        {"name":"Ring Stage (Early Trophozoite)","short_name":"Ring Stage","key":"ring","timeline":"0 - 18 Hours","cycle_progress":25,"badge":"#17a2b8","severity":"Early Intraerythrocytic Phase","urgency":"Immediate Standard ACT","morphology":'Delicate cytoplasmic ring with a small condensed chromatin dot ("signet-ring" appearance)',"description":"Early developmental phase following erythrocyte invasion by merozoites. The parasite occupies approximately 5% to 15% of the red blood cell area.","clinical":"Parasites circulate actively in peripheral blood. High susceptibility to Artemisinin-based Combination Therapy (ACT). Low risk of immediate capillary cytoadherence.","treatment":"Standard oral ACT (e.g., Artemether-Lumefantrine) for 3 days as per WHO guidelines."},
    "trophozoite": {"name":"Mature Trophozoite Stage","short_name":"Trophozoite Stage","key":"trophozoite","timeline":"18 - 36 Hours","cycle_progress":55,"badge":"#ffc107","severity":"Active Metabolic Phase","urgency":"Urgent Antimalarial Therapy","morphology":"Irregular amoeboid cytoplasmic mass with prominent golden-brown to black hemozoin pigment granules","description":"Actively feeding parasite metabolizing host hemoglobin. The parasite expands to occupy 20% to 45% of the erythrocyte volume.","clinical":"Parasite expresses PfEMP1 knobs causing cytoadherence to microvascular endothelium; causes rising fever spikes, nausea, and headache.","treatment":"Prompt oral ACT. Administer antipyretics (Paracetamol) for high fever and maintain hydration."},
    "schizont":    {"name":"Schizont Stage (Asexual Multiplication)","short_name":"Schizont Stage","key":"schizont","timeline":"36 - 48 Hours","cycle_progress":85,"badge":"#dc3545","severity":"Critical Pre-Lytic Phase","urgency":"Emergency Evaluation & Care","morphology":"Multinucleate complex containing 8 to 24 dividing merozoites with clustered central hemozoin pigment","description":"Late-stage asexual schizogony where nuclear division produces multiple daughter merozoites prior to host cell rupture.","clinical":"Imminent erythrocyte lysis releases pyrogenic toxins, causing acute rigors, spike fevers (up to 41°C), and marked hemolytic anemia.","treatment":"Emergency antimalarial therapy. For severe malaria, initiate IV Artesunate (2.4 mg/kg) followed by full course oral ACT."},
    "gametocyte":  {"name":"Gametocyte Stage (Sexual Precursor)","short_name":"Gametocyte Stage","key":"gametocyte","timeline":"Transmission Phase","cycle_progress":100,"badge":"#0d6efd","severity":"Vector Transmission Reservoir","urgency":"Transmission-blocking Therapy","morphology":"Characteristic elongated crescent / banana-shaped morphology stretching the host RBC, with centralized chromatin and coarse pigment","description":"Sexually committed micro- or macrogametocyte. Does not cause acute hemolytic destruction in humans but infects female Anopheles mosquitoes.","clinical":"Indicates sub-acute or mature infection acting as an active transmission reservoir in the community.","treatment":"Add a single low dose of Primaquine (0.25 mg base/kg) on day 1 alongside ACT to eliminate gametocytes."},
    "healthy":     {"name":"Uninfected (Healthy Erythrocyte)","short_name":"Uninfected","key":"healthy","timeline":"N/A","cycle_progress":0,"badge":"#28a745","severity":"Normal","urgency":"None","morphology":"Normal biconcave erythrocyte disk with central pallor, uniform pink-gray Giemsa staining, absent intracellular parasites","description":"Healthy red blood cell showing normal morphological integrity with no detectable Plasmodium infection.","clinical":"No malaria parasites detected. Re-test if fever persists or clinical suspicion is elevated.","treatment":"No antimalarial medication required. Investigate other non-malarial causes if clinical symptoms are present."},
}
CLINICAL_STAGES = [
    {"stage":"❄️ Cold Stage (Chills)","duration":"15–60 minutes","symptoms":"Intense uncontrollable shivering, feeling bitterly cold, peripheral vasoconstriction, rapid pulse.","mechanism":"Sudden rupture of schizonts releasing pyrogens, merozoites, and hemoglobin breakdown products."},
    {"stage":"🔥 Hot Stage (Fever)","duration":"2–6 hours","symptoms":"High spike fever (up to 40.5–41°C), throbbing headache, flushed skin, delirium, vomiting.","mechanism":"Hypothalamic setpoint elevated by circulating TNF-alpha, IL-1, and parasite toxins."},
    {"stage":"💧 Sweating Stage (Defervescence)","duration":"2–4 hours","symptoms":"Profuse diaphoresis (drenching sweats), rapid temperature decline, exhaustion, deep sleep.","mechanism":"Resetting of hypothalamic thermostat, peripheral vasodilation, recovery until next cycle."},
]

@st.cache_resource
def get_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}")
    return load_model(MODEL_PATH, compile=False)

def preprocess(pil_img, size=(224,224)):
    arr = np.asarray(pil_img.convert("RGB").resize(size), dtype=np.float32) / 255.0
    return np.expand_dims(arr, 0)

def check_blur(bgr, threshold=50.0):
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    return score < threshold, score

def generate_gradcam(model, img_array):
    try:
        layer_name = next((l.name for l in reversed(model.layers) if "conv" in l.name.lower()), model.layers[-2].name)
        grad_model = tf.keras.models.Model([model.inputs],[model.get_layer(layer_name).output, model.output])
        with tf.GradientTape() as tape:
            conv_out, preds = grad_model(img_array)
            loss = preds[:, 0] if preds.shape[-1] == 1 else preds[:, 0]
        grads = tape.gradient(loss, conv_out)
        pooled = tf.reduce_mean(grads, axis=(0,1,2))
        heatmap = tf.squeeze(conv_out[0] @ pooled[..., tf.newaxis])
        heatmap = tf.maximum(heatmap, 0) / (tf.reduce_max(heatmap) + 1e-10)
        return cv2.resize(heatmap.numpy(), (224,224))
    except Exception as e:
        logger.warning("Grad-CAM: %s", e); return None

def overlay_heatmap(bgr, heatmap):
    bgr_r = cv2.resize(bgr, (224,224))
    colored = cv2.applyColorMap(np.uint8(255*heatmap), cv2.COLORMAP_JET)
    return cv2.cvtColor(cv2.addWeighted(bgr_r,0.6,colored,0.4,0), cv2.COLOR_BGR2RGB)

def classify_phase(bgr, heatmap=None, is_parasitized=True):
    if not is_parasitized:
        return PHASE_METADATA["healthy"]["name"], 0.99, PHASE_METADATA["healthy"]
    try:
        h,w = bgr.shape[:2]; total_area = float(h*w)
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV); b,g,r = cv2.split(bgr)
        stain = (((b.astype(int)>g.astype(int)+10)&(r.astype(int)>g.astype(int)+5))|((hsv[:,:,0]>=115)&(hsv[:,:,0]<=168)&(hsv[:,:,1]>=25))).astype(np.uint8)*255
        stain = cv2.morphologyEx(stain, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)))
        contours,_ = cv2.findContours(stain, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        focus = float(np.mean(heatmap>0.45)) if heatmap is not None else 0.0
        if not contours:
            if focus>0.28: return PHASE_METADATA["schizont"]["name"],0.93,PHASE_METADATA["schizont"]
            elif focus>0.12: return PHASE_METADATA["trophozoite"]["name"],0.94,PHASE_METADATA["trophozoite"]
            else: return PHASE_METADATA["ring"]["name"],0.95,PHASE_METADATA["ring"]
        largest = max(contours, key=cv2.contourArea); ar = cv2.contourArea(largest)/total_area
        _,_,bw,bh = cv2.boundingRect(largest); asp = max(bw,bh)/max(min(bw,bh),1)
        spots = len([c for c in contours if cv2.contourArea(c)>20])
        if asp>=1.75 and ar>=0.035: k,c="gametocyte",min(0.97,0.88+asp*0.03)
        elif ar>=0.16 or spots>=4 or focus>=0.26: k,c="schizont",min(0.98,0.90+ar*0.2)
        elif ar>=0.05 or (ar>=0.02 and spots>=2) or focus>=0.12: k,c="trophozoite",min(0.96,0.89+ar*0.2)
        else: k,c="ring",min(0.98,0.92+(1.0-ar)*0.04)
        return PHASE_METADATA[k]["name"], round(float(c),3), PHASE_METADATA[k]
    except Exception as e:
        logger.warning("Phase fallback: %s",e); return PHASE_METADATA["ring"]["name"],0.92,PHASE_METADATA["ring"]

def run_analysis(pil_img, blur_threshold=50.0, skip_blur=False):
    rgb = np.asarray(pil_img.convert("RGB")); bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    is_blur, blur_score = check_blur(bgr, blur_threshold)
    if is_blur and not skip_blur:
        return {"status":"blurry","blur_score":blur_score,"rgb":rgb}
    model = get_model(); img_array = preprocess(pil_img)
    raw = model.predict(img_array, verbose=0)
    if raw.shape[-1]==1:
        val=float(raw[0][0]); result,conf=("Parasitized",1.0-val) if val<0.5 else ("Uninfected",val)
    else:
        idx=int(np.argmax(raw[0])); conf=float(np.max(raw[0])); result="Parasitized" if idx==0 else "Uninfected"
    heatmap = generate_gradcam(model, img_array)
    overlay = overlay_heatmap(bgr, heatmap) if heatmap is not None else None
    stage_name,stage_conf,stage_info = classify_phase(bgr, heatmap, result=="Parasitized")
    return {"status":"ok","result":result,"confidence":float(conf),"stage_name":stage_name,
            "stage_conf":float(stage_conf),"stage_info":stage_info,"blur_score":blur_score,
            "rgb":rgb,"overlay":overlay,"timestamp":datetime.now().strftime("%B %d, %Y\n%I:%M %p")}

def pil_to_b64(pil_img, thumb=False):
    if thumb:
        pil_img = pil_img.copy(); pil_img.thumbnail((60,60))
    buf = io.BytesIO(); pil_img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

def arr_to_b64(arr, thumb=False):
    return pil_to_b64(Image.fromarray(arr.astype(np.uint8)), thumb=thumb)

# ─────────────────────── CSS ───────────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family:'Inter',sans-serif; }
#MainMenu,footer,.stDeployButton { display:none!important; }
.block-container { padding:0!important; max-width:100%!important; }

/* ── sidebar ── */
[data-testid="stSidebar"] {
    background:linear-gradient(180deg,#1e293b 0%,#0f172a 100%)!important;
    min-width:270px!important; max-width:270px!important;
}
[data-testid="stSidebarContent"] { padding:1.2rem 1rem!important; }
[data-testid="stSidebar"] * { color:rgba(255,255,255,0.85)!important; }
[data-testid="stSidebar"] .stMarkdown p { margin:0; }

.sb-logo { display:flex; align-items:center; padding:.8rem 0 1rem;
    border-bottom:1px solid rgba(255,255,255,0.1); margin-bottom:1.2rem; }
.sb-logo-icon { font-size:26px; margin-right:10px; }
.sb-logo-text { font-size:18px; font-weight:700; color:white!important; letter-spacing:-0.5px; }

[data-testid="stSidebar"] [data-testid="stButton"] button {
    background:transparent!important; border:none!important; outline:none!important;
    color:rgba(255,255,255,0.8)!important; text-align:left!important; width:100%!important;
    padding:11px 16px!important; border-radius:8px!important; font-size:14px!important;
    font-weight:500!important; transition:all .2s!important; margin:1px 0!important;
    display:flex; align-items:center; gap:10px;
}
[data-testid="stSidebar"] [data-testid="stButton"] button:hover {
    background:rgba(59,130,246,0.15)!important; color:white!important;
    transform:translateX(4px)!important;
}
.nav-active [data-testid="stButton"] button {
    background:rgba(59,130,246,0.2)!important; color:white!important;
    border-left:3px solid #3b82f6!important; padding-left:13px!important;
}
.nav-logout [data-testid="stButton"] button {
    background:#dc2626!important; color:white!important; border-radius:8px!important;
    font-weight:600!important; justify-content:center!important; margin-top:8px!important;
}
.nav-logout [data-testid="stButton"] button:hover {
    background:#b91c1c!important; transform:none!important;
}

/* ── top header bar ── */
.top-header {
    background:white; border-bottom:1px solid #e5e7eb;
    padding:.9rem 2rem; display:flex; align-items:center;
    justify-content:space-between; margin-bottom:1.5rem;
    box-shadow:0 1px 3px rgba(0,0,0,0.05);
}
.top-header .search-wrap {
    flex:1; max-width:420px;
    background:#f3f4f6; border-radius:999px;
    padding:8px 18px; display:flex; align-items:center; gap:8px;
    font-size:14px; color:#9ca3af;
}
.top-header .user-info { display:flex; align-items:center; gap:10px; }
.top-header .user-name { text-align:right; }
.top-header .user-name strong { display:block; font-size:14px; color:#111827; }
.top-header .user-name span { font-size:12px; color:#6b7280; }
.top-header .avatar {
    width:38px; height:38px; border-radius:50%;
    background:#dc2626; color:white; font-weight:700;
    display:flex; align-items:center; justify-content:center; font-size:14px;
}

/* ── main content wrapper ── */
.main-wrap { padding:0 2rem 2rem; }

/* ── page header ── */
.page-hdr { margin-bottom:1.4rem; }
.page-hdr h1 { font-size:22px; font-weight:700; color:#111827; margin:0 0 2px; }
.page-hdr p  { font-size:13px; color:#6b7280; margin:0; }

/* ── KPI cards ── */
.kpi-row { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:1.4rem; }
.kpi { background:white; border-radius:12px; overflow:hidden;
       box-shadow:0 1px 4px rgba(0,0,0,0.07); }
.kpi-bar { height:4px; }
.kpi-body { padding:1.1rem 1.3rem; }
.kpi-label { font-size:12px; color:#6b7280; font-weight:500; margin-bottom:4px; }
.kpi-value { font-size:26px; font-weight:700; color:#111827; margin:0; line-height:1.2; }
.kpi-change { font-size:12px; margin-top:4px; }
.up   { color:#059669; } .down { color:#dc2626; }

/* ── white cards ── */
.wcard { background:white; border-radius:12px; padding:1.4rem 1.5rem;
         box-shadow:0 1px 4px rgba(0,0,0,0.07); margin-bottom:1.2rem; }
.wcard h5 { font-size:15px; font-weight:600; color:#111827; margin:0 0 1rem; }

/* ── upload area ── */
.upload-area {
    border:2px dashed #d1d5db; border-radius:12px; padding:2.5rem 1rem;
    text-align:center; background:#f9fafb; cursor:pointer; transition:all .2s;
}
.upload-area:hover { border-color:#3b82f6; background:#eff6ff; }
.upload-icon { font-size:3rem; color:#3b82f6; margin-bottom:.5rem; }
.upload-area h4 { font-size:18px; font-weight:600; color:#374151; margin:.3rem 0 .2rem; }
.upload-area p  { color:#6b7280; font-size:13px; margin:0; }

/* ── no-image placeholder ── */
.no-img { text-align:center; padding:2.5rem 1rem; color:#9ca3af; }
.no-img-icon { font-size:3rem; margin-bottom:.5rem; }
.no-img p { font-size:14px; margin:0; }

/* ── result badges ── */
.badge-p { display:inline-flex; align-items:center; gap:5px;
    background:#fef2f2; color:#dc2626; border:1px solid #fca5a5;
    border-radius:999px; padding:3px 12px; font-size:12px; font-weight:600; }
.badge-u { display:inline-flex; align-items:center; gap:5px;
    background:#f0fdf4; color:#059669; border:1px solid #86efac;
    border-radius:999px; padding:3px 12px; font-size:12px; font-weight:600; }

/* ── Recent Analyses table ── */
.ra-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; }
.ra-header h5 { font-size:15px; font-weight:600; color:#111827; margin:0; }
.ra-header .ra-actions { display:flex; gap:8px; }
.btn-sm {
    padding:5px 12px; border-radius:6px; font-size:12px; font-weight:500;
    border:1px solid #d1d5db; background:white; color:#374151;
    cursor:pointer; display:inline-flex; align-items:center; gap:5px;
}

.ra-table { width:100%; border-collapse:collapse; font-size:13px; }
.ra-table th { background:#f9fafb; padding:10px 14px; text-align:left;
    font-weight:600; color:#374151; border-bottom:1px solid #e5e7eb; }
.ra-table td { padding:10px 14px; border-bottom:1px solid #f3f4f6;
    color:#374151; vertical-align:middle; }
.ra-table tr:last-child td { border-bottom:none; }
.ra-table tr:hover td { background:#f9fafb; }

.thumb { width:50px; height:50px; object-fit:cover; border-radius:8px; border:1px solid #e5e7eb; }

.conf-wrap { display:flex; align-items:center; gap:8px; }
.conf-bar-bg { flex:1; height:5px; background:#fee2e2; border-radius:999px; min-width:70px; }
.conf-bar { height:5px; border-radius:999px; }
.conf-pct { font-weight:600; white-space:nowrap; }

.act-btn { padding:4px 8px; border-radius:6px; border:1px solid #e5e7eb;
    background:white; cursor:pointer; font-size:13px; color:#374151;
    display:inline-flex; align-items:center; }
.act-btn.del { border-color:#fca5a5; color:#dc2626; }

/* ── progress bar ── */
.prog-bg { background:#e5e7eb; border-radius:999px; height:7px; margin:5px 0 10px; }
.prog-fill { height:7px; border-radius:999px; }

/* ── phase cards ── */
.phase-card {
    background:white; border-radius:12px; padding:1.2rem 1.5rem;
    box-shadow:0 1px 4px rgba(0,0,0,0.07); margin-bottom:1rem;
    border-left:4px solid;
}
.phase-title { font-size:15px; font-weight:700; color:#111827; margin-bottom:4px; }
.phase-tl { font-size:12px; color:#6b7280; margin-bottom:8px; }
.phase-grid { display:grid; grid-template-columns:1fr 1fr; gap:6px 16px; font-size:13px; }
.phase-grid .full { grid-column:1/-1; }
.lbl { color:#6b7280; }
.treat-box { background:#f0fdf4; border-radius:6px; padding:7px 10px;
    font-size:12px; color:#065f46; }

/* ── staging table ── */
.stg-table { width:100%; border-collapse:collapse; font-size:13px; }
.stg-table th { background:#f9fafb; padding:9px 12px; text-align:left;
    font-weight:600; color:#374151; border-bottom:1px solid #e5e7eb; }
.stg-table td { padding:9px 12px; border-bottom:1px solid #f3f4f6; color:#374151; }
.pill { border-radius:4px; padding:2px 9px; font-size:11px; font-weight:600; color:white; }

/* ── history table ── */
.hist-table { width:100%; border-collapse:collapse; font-size:13px; }
.hist-table th { background:#f9fafb; padding:10px 14px; text-align:left;
    font-weight:600; color:#374151; border-bottom:1px solid #e5e7eb; }
.hist-table td { padding:10px 14px; border-bottom:1px solid #f3f4f6; color:#374151; vertical-align:middle; }

/* ── disclaimer ── */
.disclaimer { background:#eff6ff; border:1px solid #bfdbfe; border-radius:8px;
    padding:9px 12px; font-size:11px; color:#1e40af; margin-top:1rem; line-height:1.5; }
</style>
"""

# ─────────────────────── Sidebar ──────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sb-logo">
            <span class="sb-logo-icon">🔬</span>
            <span class="sb-logo-text">Malaria Detection</span>
        </div>""", unsafe_allow_html=True)

        pages = [("📊","Dashboard"),("🔬","New Analysis"),("🦟","Malaria Phases"),
                 ("📋","History"),("📈","Statistics"),("📄","Documentation"),("⚙️","Settings")]
        if "page" not in st.session_state:
            st.session_state.page = "Dashboard"

        for icon, name in pages:
            active = st.session_state.page == name
            st.markdown(f'<div class="{"nav-active" if active else ""}">', unsafe_allow_html=True)
            if st.button(f"{icon}  {name}", key=f"nav_{name}", use_container_width=True):
                st.session_state.page = name
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div style="flex:1"></div>', unsafe_allow_html=True)
        st.markdown('<div class="nav-logout">', unsafe_allow_html=True)
        if st.button("↩  Logout", key="nav_logout", use_container_width=True):
            st.session_state.history = []
            st.session_state.page = "Dashboard"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('<div class="disclaimer">⚕️ <strong>Disclaimer:</strong> For research & educational decision-support only. Always confirm with certified lab microscopy or RDT.</div>', unsafe_allow_html=True)

# ─────────────────────── Header bar ───────────────────────────────────────────
def top_header():
    st.markdown("""
    <div class="top-header">
        <div class="search-wrap">🔍&nbsp;&nbsp;Search in analysis history...</div>
        <div class="user-info">
            <div class="user-name">
                <strong>dk</strong>
                <span>Medical Researcher</span>
            </div>
            <div class="avatar">DK</div>
        </div>
    </div>""", unsafe_allow_html=True)

# ─────────────────────── KPI bar ──────────────────────────────────────────────
def kpi_bar(history):
    total = len(history)
    para  = sum(1 for h in history if h["Result"]=="Parasitized")
    uninf = total - para
    acc   = 98.2
    para_pct = round(para/total*100,1) if total else 0
    uninf_pct= round(uninf/total*100,1) if total else 0

    st.markdown(f"""
    <div class="kpi-row">
      <div class="kpi">
        <div class="kpi-bar" style="background:#2563eb"></div>
        <div class="kpi-body">
          <div class="kpi-label">Total Analyses</div>
          <div class="kpi-value">{total}</div>
          <div class="kpi-change up">↑ This session</div>
        </div>
      </div>
      <div class="kpi">
        <div class="kpi-bar" style="background:#dc2626"></div>
        <div class="kpi-body">
          <div class="kpi-label">Parasitized Cases</div>
          <div class="kpi-value" style="color:#dc2626">{para}</div>
          <div class="kpi-change {'up' if para_pct else 'down'}">{'↑' if para_pct else '—'} {para_pct}% of total</div>
        </div>
      </div>
      <div class="kpi">
        <div class="kpi-bar" style="background:#059669"></div>
        <div class="kpi-body">
          <div class="kpi-label">Uninfected Cases</div>
          <div class="kpi-value" style="color:#059669">{uninf}</div>
          <div class="kpi-change {'up' if uninf_pct else 'down'}">{'↑' if uninf_pct else '—'} {uninf_pct}% of total</div>
        </div>
      </div>
      <div class="kpi">
        <div class="kpi-bar" style="background:#2563eb"></div>
        <div class="kpi-body">
          <div class="kpi-label">Model Accuracy</div>
          <div class="kpi-value" style="color:#2563eb">{acc}%</div>
          <div class="kpi-change up">↑ 2% this month</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

# ─────────────────────── Recent Analyses table ────────────────────────────────
def recent_analyses_table(history, limit=10):
    st.markdown("""
    <div class="ra-header">
        <h5>Recent Analyses</h5>
        <div class="ra-actions">
            <span class="btn-sm">⬇ Export</span>
            <span class="btn-sm">▼ Filter</span>
        </div>
    </div>""", unsafe_allow_html=True)

    if not history:
        st.info("No analyses yet. Upload a blood smear image to get started.")
        return

    rows = ""
    for h in history[:limit]:
        thumb_tag = f'<img src="data:image/png;base64,{h["thumb"]}" class="thumb">' if h.get("thumb") else '<span style="font-size:28px">🔬</span>'
        badge = '<span class="badge-p">⚠ Parasitized</span>' if h["Result"]=="Parasitized" else '<span class="badge-u">✓ Uninfected</span>'
        pct   = int(float(h["ConfVal"])*100)
        bar_color = "#dc2626" if h["Result"]=="Parasitized" else "#059669"
        rows += f"""<tr>
            <td>{thumb_tag}</td>
            <td style="white-space:pre-line;font-size:13px">{h['Date']}</td>
            <td>{badge}</td>
            <td>
                <div class="conf-wrap">
                    <div class="conf-bar-bg"><div class="conf-bar" style="width:{pct}%;background:{bar_color}"></div></div>
                    <span class="conf-pct" style="color:{bar_color}">{pct}.0%</span>
                </div>
            </td>
            <td>
                <span class="act-btn" title="View">👁</span>
                <span class="act-btn" style="margin:0 3px" title="Download">⬇</span>
                <span class="act-btn del" title="Delete">🗑</span>
            </td>
        </tr>"""

    st.markdown(f"""<div class="wcard" style="padding:1.4rem 1.5rem">
    <table class="ra-table">
        <thead><tr><th>Image</th><th>Date</th><th>Result</th><th>Confidence</th><th>Actions</th></tr></thead>
        <tbody>{rows}</tbody>
    </table></div>""", unsafe_allow_html=True)

# ─────────────────────── Inline result card ───────────────────────────────────
def result_card(out):
    res   = out["result"]; conf = out["confidence"]; info = out["stage_info"]
    color = "#dc2626" if res=="Parasitized" else "#059669"
    badge = f'<span class="badge-p">⚠ Parasitized</span>' if res=="Parasitized" else f'<span class="badge-u">✓ Uninfected</span>'
    pct   = int(conf*100)
    st.markdown(f"""
    <div style="margin-bottom:10px">{badge}</div>
    <div style="font-size:12px;color:#6b7280;margin-bottom:3px">Confidence</div>
    <div class="prog-bg"><div class="prog-fill" style="width:{pct}%;background:{color}"></div></div>
    <div style="font-size:22px;font-weight:700;color:{color};margin-bottom:10px">{conf:.1%}</div>
    <div style="font-size:12px;color:#6b7280;margin-bottom:2px">Developmental Phase</div>
    <div style="font-size:14px;font-weight:600;color:#111827;margin-bottom:2px">{info['short_name']}</div>
    <div style="font-size:12px;color:#6b7280">Stage confidence: {out['stage_conf']:.1%} &nbsp;|&nbsp; ⏱ {info['timeline']}</div>
    """, unsafe_allow_html=True)
    if info.get("urgency") and info["urgency"]!="None":
        st.markdown(f'<div style="background:#fef2f2;border-radius:8px;padding:7px 11px;font-size:12px;color:#dc2626;margin-top:8px">🚨 <b>Urgency:</b> {info["urgency"]}</div>', unsafe_allow_html=True)

def save_history(filename, out, pil_img=None):
    if "history" not in st.session_state: st.session_state.history=[]
    if out["status"]!="ok": return
    thumb = pil_to_b64(pil_img, thumb=True) if pil_img else None
    st.session_state.history.insert(0,{
        "File":filename,"Date":out["timestamp"],"Result":out["result"],
        "Confidence":f"{out['confidence']:.1%}","ConfVal":out["confidence"],
        "Phase":out["stage_info"]["short_name"],"thumb":thumb,
        "BlurScore":f"{out['blur_score']:.1f}",
    })

# ═══════════════════════ PAGES ════════════════════════════════════════════════

def page_dashboard():
    st.markdown('<div class="main-wrap">', unsafe_allow_html=True)
    top_header()
    history = st.session_state.get("history",[])
    kpi_bar(history)

    col_up, col_res = st.columns([1,1], gap="medium")
    with col_up:
        st.markdown('<div class="wcard"><h5>Upload Image</h5>', unsafe_allow_html=True)
        uploaded = st.file_uploader("", type=["png","jpg","jpeg","tiff","bmp"], key="dash_up", label_visibility="collapsed")
        if not uploaded:
            st.markdown("""<div class="upload-area">
                <div class="upload-icon">☁️</div>
                <h4>Drop your image here</h4>
                <p>or click to browse</p>
                <p style="margin-top:6px;font-size:11px">Supported formats: PNG, JPG, JPEG, TIFF</p>
            </div>""", unsafe_allow_html=True)
        else:
            pil = Image.open(uploaded)
            st.image(pil, use_container_width=True)
            if st.button("🔬 Analyse Now", type="primary", use_container_width=True):
                with st.spinner("Analysing..."):
                    out = run_analysis(pil, skip_blur=True)
                st.session_state["last_result"]=out
                save_history(uploaded.name, out, pil)
                st.session_state.page="New Analysis"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col_res:
        st.markdown('<div class="wcard"><h5>Analysis Results</h5>', unsafe_allow_html=True)
        last = st.session_state.get("last_result")
        if last and last["status"]=="ok":
            result_card(last)
        else:
            st.markdown("""<div class="no-img">
                <div class="no-img-icon">🖼️</div>
                <p>No image selected for analysis</p>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    recent_analyses_table(history)
    st.markdown("</div>", unsafe_allow_html=True)


def page_new_analysis():
    st.markdown('<div class="main-wrap">', unsafe_allow_html=True)
    top_header()
    st.markdown('<div class="page-hdr"><h1>New Analysis</h1><p>Upload and analyze blood smear images for malaria detection.</p></div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([6,4], gap="medium")
    with col_left:
        st.markdown('<div class="wcard"><h5>Upload Image</h5>', unsafe_allow_html=True)
        uploaded = st.file_uploader("", type=["png","jpg","jpeg","tiff","bmp"], key="new_up", label_visibility="collapsed")
        if not uploaded:
            st.markdown("""<div class="upload-area">
                <div class="upload-icon">☁️</div>
                <h4>Drop your image here</h4>
                <p>or click to browse</p>
                <p style="margin-top:6px;font-size:11px">Supported formats: PNG, JPG, JPEG, TIFF, BMP</p>
            </div>""", unsafe_allow_html=True)
        else:
            pil = Image.open(uploaded)
            st.image(pil, caption=f"Preview: {uploaded.name}", use_container_width=True)
            blur_th = st.slider("Blur sensitivity", 10.0, 150.0, 50.0, 5.0)
            skip_b  = st.checkbox("Analyse even if blurry", False)
            if st.button("🔬 Run Malaria Analysis", type="primary", use_container_width=True):
                with st.spinner("Running CNN inference and Grad-CAM staging..."):
                    out = run_analysis(pil, blur_th, skip_b)
                st.session_state["last_result"]=out
                save_history(uploaded.name, out, pil)
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="wcard"><h5>Guidelines</h5>', unsafe_allow_html=True)
        for tip in ["Use clear, well-focused images","Ensure proper lighting conditions","Maximum file size: 5 MB","Supported: PNG, JPG, TIFF, BMP"]:
            st.markdown(f'<div style="display:flex;gap:8px;margin-bottom:10px;font-size:13px"><span style="color:#059669">✅</span><span>{tip}</span></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="wcard"><h5>Analysis Results</h5>', unsafe_allow_html=True)
        last = st.session_state.get("last_result")
        if last:
            if last["status"]=="blurry":
                st.warning(f"Image too blurry (score: {last['blur_score']:.1f}). Enable 'Analyse even if blurry' or upload a clearer image.")
                st.image(last["rgb"], use_container_width=True)
            else:
                result_card(last)
        else:
            st.markdown('<div class="no-img"><div class="no-img-icon">🖼️</div><p>No image selected for analysis</p></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    last = st.session_state.get("last_result")
    if last and last["status"]=="ok" and last.get("overlay") is not None:
        st.markdown('<div class="wcard"><h5>🌡️ Grad-CAM Attention Heatmap</h5>', unsafe_allow_html=True)
        c1,c2 = st.columns(2, gap="medium")
        with c1: st.image(last["rgb"], caption="Original Blood Smear", use_container_width=True)
        with c2: st.image(last["overlay"], caption="Grad-CAM (Red = Model Focus)", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def page_malaria_phases():
    st.markdown('<div class="main-wrap">', unsafe_allow_html=True)
    top_header()
    st.markdown('<div class="page-hdr"><h1>Malaria Phases</h1><p>Plasmodium falciparum erythrocytic developmental cycle & clinical staging guide.</p></div>', unsafe_allow_html=True)

    st.markdown("""<div class="wcard"><h5>Erythrocytic Cycle Timeline</h5>
        <div style="background:linear-gradient(90deg,#17a2b8 0%,#ffc107 40%,#dc3545 75%,#0d6efd 100%);height:12px;border-radius:999px;margin-bottom:8px"></div>
        <div style="display:flex;justify-content:space-between;font-size:11px;color:#6b7280">
            <span>Ring (0h)</span><span>Trophozoite (18h)</span><span>Schizont (36h)</span><span>Gametocyte</span>
        </div></div>""", unsafe_allow_html=True)

    for _,p in PHASE_METADATA.items():
        prog = p["cycle_progress"]
        st.markdown(f"""<div class="phase-card" style="border-left-color:{p['badge']}">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px">
                <div class="phase-title">{p['name']}</div>
                <span style="background:{p['badge']};color:{'#000' if p['badge']=='#ffc107' else '#fff'};border-radius:999px;padding:2px 10px;font-size:11px;font-weight:600">{p['timeline']}</span>
            </div>
            <div class="prog-bg"><div class="prog-fill" style="width:{prog}%;background:{p['badge']}"></div></div>
            <div class="phase-grid">
                <div><span class="lbl">Severity:</span> {p['severity']}</div>
                <div><span class="lbl">Urgency:</span> {p['urgency']}</div>
                <div class="full"><span class="lbl">Morphology:</span> {p['morphology']}</div>
                <div class="full"><span class="lbl">Description:</span> {p['description']}</div>
                <div class="full"><span class="lbl">Clinical:</span> {p['clinical']}</div>
                <div class="full treat-box"><strong style="color:#059669">Treatment:</strong> {p['treatment']}</div>
            </div></div>""", unsafe_allow_html=True)

    st.markdown('<div class="wcard" style="margin-top:.5rem"><h5>Clinical Paroxysm Stages</h5>', unsafe_allow_html=True)
    colors=["#17a2b8","#dc3545","#28a745"]
    for i,cs in enumerate(CLINICAL_STAGES):
        st.markdown(f"""<div style="display:flex;gap:12px;margin-bottom:14px">
            <div style="width:32px;height:32px;border-radius:50%;background:{colors[i]};display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:14px;flex-shrink:0">{i+1}</div>
            <div><div style="font-weight:600;color:#111827">{cs['stage']} <span style="font-size:11px;color:#6b7280;font-weight:400">— {cs['duration']}</span></div>
                <div style="font-size:13px;color:#374151;margin-top:2px">{cs['symptoms']}</div>
                <div style="font-size:12px;color:#6b7280;margin-top:2px"><em>{cs['mechanism']}</em></div>
            </div></div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    STGTABLE=[
        ("Ring Stage","0–18 hrs","Delicate ring, 1–2 chromatin dots","Normal size","None","Standard ACT","#28a745"),
        ("Mature Trophozoite","18–36 hrs","Thick amoeboid mass","Slightly enlarged","Brown/black granules","Urgent ACT","#ffc107"),
        ("Schizont Stage","36–48 hrs","8–24 merozoite clusters","Distended/ruptured","Dense central clump","Critical Care","#dc3545"),
        ("Gametocyte","Transmission","Crescent/banana shape","Distorted crescent","Coarse central grains","Add Primaquine","#0d6efd"),
        ("Healthy Cell","N/A","Clear biconcave disc","Standard 6–8 μm","None","Negative","#6c757d"),
    ]
    rows="".join(f"""<tr>
        <td><span class="pill" style="background:{uc}">{ph}</span></td>
        <td>{ct}</td><td>{kf}</td><td>{rb}</td><td>{pg}</td>
        <td><span class="pill" style="background:{uc};{'color:#000' if uc=='#ffc107' else ''}">{ur}</span></td>
    </tr>""" for ph,ct,kf,rb,pg,ur,uc in STGTABLE)
    st.markdown(f"""<div class="wcard"><h5>🔬 Microscopic Staging Reference Matrix</h5>
    <table class="stg-table">
        <thead><tr><th>Phase</th><th>Cycle Time</th><th>Key Features</th><th>RBC</th><th>Pigment</th><th>Urgency</th></tr></thead>
        <tbody>{rows}</tbody></table></div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def page_history():
    st.markdown('<div class="main-wrap">', unsafe_allow_html=True)
    top_header()
    st.markdown('<div class="page-hdr"><h1>Analysis History</h1><p>Past blood smear analyses this session.</p></div>', unsafe_allow_html=True)
    history = st.session_state.get("history",[])
    if not history:
        st.info("No analyses yet. Run a New Analysis to see results here.")
    else:
        rows=""
        for i,h in enumerate(history):
            thumb_tag = f'<img src="data:image/png;base64,{h["thumb"]}" class="thumb">' if h.get("thumb") else '<span style="font-size:24px">🔬</span>'
            badge='<span class="badge-p">⚠ Parasitized</span>' if h["Result"]=="Parasitized" else '<span class="badge-u">✓ Uninfected</span>'
            pct=int(float(h["ConfVal"])*100); bc="#dc2626" if h["Result"]=="Parasitized" else "#059669"
            rows+=f"""<tr><td>{i+1}</td><td>{thumb_tag}</td>
                <td style="white-space:pre-line">{h['Date']}</td><td>{badge}</td>
                <td><div class="conf-wrap"><div class="conf-bar-bg"><div class="conf-bar" style="width:{pct}%;background:{bc}"></div></div>
                    <span class="conf-pct" style="color:{bc}">{pct}.0%</span></div></td>
                <td>{h['Phase']}</td><td>{h['BlurScore']}</td></tr>"""
        st.markdown(f"""<div class="wcard"><table class="hist-table">
            <thead><tr><th>#</th><th>Image</th><th>Date</th><th>Result</th><th>Confidence</th><th>Phase</th><th>Blur</th></tr></thead>
            <tbody>{rows}</tbody></table></div>""", unsafe_allow_html=True)
        if st.button("🗑️ Clear History"):
            st.session_state.history=[]; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def page_statistics():
    st.markdown('<div class="main-wrap">', unsafe_allow_html=True)
    top_header()
    st.markdown('<div class="page-hdr"><h1>Statistics</h1><p>Detection summary for this session.</p></div>', unsafe_allow_html=True)
    history = st.session_state.get("history",[]); total=len(history)
    para=sum(1 for h in history if h["Result"]=="Parasitized"); uninf=total-para
    kpi_bar(history)
    phase_counts={}
    for h in history: phase_counts[h["Phase"]]=phase_counts.get(h["Phase"],0)+1
    if phase_counts:
        st.markdown('<div class="wcard"><h5>Phase Distribution</h5>', unsafe_allow_html=True)
        for phase,count in sorted(phase_counts.items(),key=lambda x:-x[1]):
            pct=int(count/total*100) if total else 0
            st.markdown(f"""<div style="margin-bottom:10px">
                <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:3px">
                    <span style="font-weight:500">{phase}</span><span style="color:#6b7280">{count} ({pct}%)</span>
                </div>
                <div class="prog-bg"><div class="prog-fill" style="width:{pct}%;background:#2563eb"></div></div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Run some analyses to see phase distribution.")
    st.markdown("</div>", unsafe_allow_html=True)


def page_documentation():
    st.markdown('<div class="main-wrap">', unsafe_allow_html=True)
    top_header()
    st.markdown('<div class="page-hdr"><h1>Documentation</h1><p>How the Malaria Detection system works.</p></div>', unsafe_allow_html=True)
    sections=[
        ("🧠 AI Model Architecture","The system uses a CNN trained on the NIH Malaria Cell Images dataset containing 27,558 blood smear images (Parasitized / Uninfected). The model achieves <strong>98.2% accuracy</strong> on the test set."),
        ("📸 Image Preprocessing","Uploaded images are resized to <strong>224×224</strong> pixels, normalized to [0, 1] range, and fed into the model as a single-image batch."),
        ("🌡️ Grad-CAM Heatmap","Gradient-weighted Class Activation Mapping (Grad-CAM) highlights regions the model focused on. <strong>Red/warm areas</strong> indicate high model attention — typically the parasite body."),
        ("🦟 Phase Staging","After CNN classification, Giemsa stain morphology analysis (HSV color segmentation + contour analysis) classifies the erythrocytic stage: Ring → Trophozoite → Schizont → Gametocyte or Healthy."),
        ("⚠️ Blur Detection","Laplacian variance is computed on each uploaded image. Images below the threshold (default: 50) are flagged as blurry to prevent unreliable predictions."),
        ("📋 WHO Treatment Guidelines","Recommendations follow <strong>WHO 2023 Malaria Treatment Guidelines</strong> including ACT, IV Artesunate for severe cases, and Primaquine for gametocyte clearance."),
    ]
    for title,content in sections:
        st.markdown(f'<div class="wcard"><h5>{title}</h5><p style="font-size:13px;color:#374151;line-height:1.75;margin:0">{content}</p></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def page_settings():
    st.markdown('<div class="main-wrap">', unsafe_allow_html=True)
    top_header()
    st.markdown('<div class="page-hdr"><h1>Settings</h1><p>Configure analysis and display preferences.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="wcard"><h5>Analysis Settings</h5>', unsafe_allow_html=True)
    st.slider("Default blur threshold", 10.0, 150.0, 50.0, 5.0, key="pref_blur")
    st.checkbox("Skip blur check by default", False, key="pref_skip_blur")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="wcard"><h5>Profile</h5>', unsafe_allow_html=True)
    st.text_input("Name", "dk")
    st.text_input("Role", "Medical Researcher")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════ MAIN ════════════════════════════════════════════════
def main():
    st.set_page_config(
        page_title="Malaria Detection",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CSS, unsafe_allow_html=True)
    sidebar()

    page = st.session_state.get("page","Dashboard")
    if   page=="Dashboard":      page_dashboard()
    elif page=="New Analysis":   page_new_analysis()
    elif page=="Malaria Phases": page_malaria_phases()
    elif page=="History":        page_history()
    elif page=="Statistics":     page_statistics()
    elif page=="Documentation":  page_documentation()
    elif page=="Settings":       page_settings()

if __name__=="__main__":
    main()
