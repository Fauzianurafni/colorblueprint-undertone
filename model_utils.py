import streamlit as st
import numpy as np
import cv2

from tensorflow.keras.models import load_model

from config import * 

# =========================================================
# LOAD MODEL (SANGAT RINGKAS SEKARANG)
# =========================================================
@st.cache_resource
def load_all_models():
    model = load_model("models/undertone_model_terbaik.keras", compile=False, safe_mode=False)
    return model

try:
    model = load_all_models()
except Exception as e:
    st.error(f"Gagal memuat model.\nError: {e}")
    st.stop()

classes = CLASSES

# =========================================================
# VALIDASI ULTIMATE: ANTI BENDA GEOMETRIS & FILTER YCrCb
# =========================================================
def validate_wrist_image(img):
    # 1. CEK KONTRAS DASAR
    color_std = np.std(img)
    if color_std < 3.0:
        return False, "Gambar editan digital (warna solid)."

    # 2. CEK GARIS LURUS (ANTI BENDA BUATAN MANUSIA)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=40, minLineLength=40, maxLineGap=5)
    
    if lines is not None and len(lines) > 10:
        return False, "Terdeteksi pola benda mati/sudut lurus (Meja/Layar)."

    # 3. CEK WARNA KULIT
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    img_ycrcb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2YCrCb)
    
    # Rentang warna kulit manusia asli pada YCrCb
    lower_skin = np.array([0, 133, 77], dtype=np.uint8)
    upper_skin = np.array([255, 173, 127], dtype=np.uint8)
    
    skin_mask = cv2.inRange(img_ycrcb, lower_skin, upper_skin)
    
    # Hitung rasio
    skin_ratio = cv2.countNonZero(skin_mask) / skin_mask.size
    
    if skin_ratio < 0.15: 
        return False, "Tidak terdeteksi warna kulit manusia."

    return True, "Lolos"

# =========================================================
# PREDICTION 
# =========================================================
def predict_undertone(pil_image):
    # =====================================================
    # 1. IMAGE PREP & VALIDATION
    # =====================================================
    # PIL image default-nya adalah RGB
    img_rgb = np.array(pil_image)
    
    img_resized = cv2.resize(img_rgb, MODEL_INPUT_SIZE)

    is_valid, msg = validate_wrist_image(img_resized)

    if not is_valid:
        st.toast(f"Ditolak: {msg}", icon="⚠️")
        return ("invalid", 0.0, 0.0, 0.0, 0.0)

    # =====================================================
    # 2. ENHANCEMENT 
    # =====================================================
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    
    # Karena img_resized formatnya RGB, kita ubah RGB ke LAB
    lab = cv2.cvtColor(img_resized, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    
    # Terapkan CLAHE hanya pada channel 'L' (Lightness/Cahaya)
    cl = clahe.apply(l)
    merged = cv2.merge((cl,a,b))
    
    # Kembalikan lagi ke RGB agar untuk dibaca EfficientNet
    enhanced_rgb = cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)

    # =====================================================
    # 3. PREDICTION LANGSUNG! 
    # =====================================================
    cnn_input = enhanced_rgb.astype(np.float32) 
    cnn_input = np.expand_dims(cnn_input, axis=0) 
    
    pred = model.predict(
        cnn_input, 
        verbose=0
        )[0].astype(np.float64)
    
    confidence = float(np.max(pred))

    idx = int(np.argmax(pred))
    
    return (
        classes[idx], 
        confidence, 
        float(pred[0]), 
        float(pred[1]), 
        float(pred[2])
    )