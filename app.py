import streamlit as st
import tensorflow as tf
import streamlit.components.v1 as components
import streamlit as st

st.set_page_config(
    page_title="ColourBlueprint",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import tensorflow as tf
import streamlit.components.v1 as components
import io
import base64

from PIL import Image
from PIL import ImageDraw

from model_utils import load_all_models, predict_undertone
from color_data import *
from components import *
from config import *

tf.get_logger().setLevel('ERROR')

model = load_all_models()

with open("style.css") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

# =========================================================
# NAVBAR
# =========================================================
render_navbar()

if st.session_state.get("invalid", False):
    st.markdown(
        """
        <div style="text-align:center; padding-top:80px; padding-bottom:80px; font-family:'DM Sans', sans-serif;">
            <h1>Objek Tidak Terdeteksi</h1>
            <p>Pastikan area crop berisi pergelangan tangan dan warna urat nadi terlihat jelas.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1,1,1])

    with col2:
        if st.button("Upload / Foto Ulang", use_container_width=True, type="primary"):
            st.session_state.invalid = False
            st.session_state.analyzed = False
            st.rerun()

    st.stop()
    
# =========================================================
# FUNGSI POP-UP PANDUAN MELAYANG
# =========================================================
@st.dialog("Panduan Pengambilan Foto")
def tampilkan_popup_panduan():
    st.image(
        "assets/Panduan.png", 
        use_container_width=True
    )
    st.caption("Pastikan Anda mengikuti panduan di atas agar hasil analisis akurat.")

# =========================================================
# MAIN LAYOUT (Split View Kiri-Kanan)
# =========================================================
left_col, right_col = st.columns(
    [1, 2.1],
    gap="small"
)

if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
    
if "camera_file" not in st.session_state:
    st.session_state.camera_file = None

# ---------------------------------------------------------
# KOLOM KIRI: INPUT & PREVIEW AREA
# ---------------------------------------------------------
with left_col:
    with st.container(border=True):
        # 1. JUDUL CARD: UPLOAD FOTO 
        st.markdown("""
        <div style="font-family:'DM Sans', sans-serif; font-size:13px; font-weight:700; color:#2F2430; margin-bottom:12px; display:flex; align-items:center; gap:8px;">
            <span class="material-symbols-rounded" style="color:#C86A87; font-size:20px;">upload_file</span>
            Upload Foto
        </div>
        <div class="cb-step-desc" style="padding-left:0; margin-bottom:8px;">Foto pergelangan tangan dengan pencahayaan alami yang baik.</div>
        """, unsafe_allow_html=True)

        clicked = st.button(
            "📖 Lihat Panduan",
            key="panduan",
            use_container_width=True,
            type="secondary"
        )

        if clicked:
            tampilkan_popup_panduan()
                
        st.markdown(
            "<div style='height:4px'></div>",
            unsafe_allow_html=True
        )

        st.markdown("""
        <hr style="
        border:none;
        border-top:1px solid #E6DADD;
        margin:0;
        ">
        """, unsafe_allow_html=True)

        st.markdown(
            "<div style='height:4px'></div>",
            unsafe_allow_html=True
        )
        
        # =========================================================
        # BELUM ADA FOTO
        # =========================================================
        if (
            st.session_state.uploaded_file is None
            and st.session_state.camera_file is None
        ):

            input_mode = st.radio(
                "Pilih sumber gambar",
                ["Upload", "Kamera"],
                horizontal=True,
                label_visibility="collapsed",
                key="input_mode_v2"
            )

            # ==========================================
            # MODE UPLOAD
            # ==========================================
            if input_mode == "Upload":
                uploaded_file = st.file_uploader(
                    "Upload gambar tangan/pergelangan",
                    type=["jpg", "jpeg", "png"],
                    label_visibility="collapsed"
                )
                if uploaded_file is not None:
                    st.session_state.uploaded_file = uploaded_file
                    st.rerun()

            # ==========================================
            # MODE KAMERA
            # ==========================================
            else:
                camera_file = st.camera_input(
                    "Ambil foto",
                    label_visibility="collapsed"
                )
                if camera_file is not None:
                    st.session_state.camera_file = camera_file
                    st.rerun()

        # =========================================================
        # SUDAH ADA FOTO 
        # =========================================================
        else:
            st.markdown("""
            <div style="background:#F4FBF6; border:1px solid #DCEEDB; padding:12px; border-radius:12px; display:flex; gap:12px; margin-top:12px; margin-bottom:14px; font-family:'DM Sans', sans-serif;">
                <span class="material-symbols-rounded" style="color:#2F8F4E; font-size:22px;">
                    task_alt
                </span>
                <div>
                    <div style="color:#2F8F4E; font-weight:700; font-size:13px;">Foto siap dianalisis</div>
                    <div style="color:#6B7280; font-size:11px; margin-top:2px;">Pastikan pencahayaan alami dan area pergelangan terlihat jelas.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.session_state.uploaded_file is not None:
                image_raw = Image.open(st.session_state.uploaded_file).convert("RGB")
                width, height = image_raw.size
                crop_size = int(min(width, height) * 0.65)
                left = (width - crop_size) // 2
                top = int((height - crop_size) * 0.45)
            else:
                image_raw = Image.open(st.session_state.camera_file).convert("RGB")
                width, height = image_raw.size
                crop_size = int(min(width, height) * 0.65)
                left = (width - crop_size) // 2
                top = (height - crop_size) // 2

            right = left + crop_size
            bottom = top + crop_size

            cropped_image = image_raw.crop((left, top, right, bottom))
            st.image(image_raw, use_container_width=True)

            if st.button("↻ Ganti Foto", use_container_width=True):
                st.session_state.uploaded_file = None
                st.session_state.camera_file = None
                st.session_state.analyzed = False
                st.session_state.pop("result", None)
                st.session_state.pop("cropped_image", None)
                st.rerun()

            if st.button("Analisis Undertone", use_container_width=True, type="primary"):
                with st.spinner("Memeriksa & Menganalisis gambar..."):
                    res, conf, cp, np_prob, wp = predict_undertone(cropped_image)

                    if res == "invalid":
                        st.session_state.invalid = True
                        st.session_state.analyzed = False
                        st.session_state.pop("result", None)
                        st.rerun()
                    else:
                        st.session_state.result = res
                        st.session_state.cool_prob = cp
                        st.session_state.neutral_prob = np_prob
                        st.session_state.warm_prob = wp
                        st.session_state.cropped_image = cropped_image
                        st.session_state.analyzed = True
                        st.rerun()
        
# ---------------------------------------------------------
# KOLOM KANAN: DASHBOARD HASIL 
# ---------------------------------------------------------
with right_col:
    if st.session_state.get('analyzed'):
        result   = st.session_state.result
        cool_v   = st.session_state.cool_prob    * 100
        neut_v   = st.session_state.neutral_prob * 100
        warm_v   = st.session_state.warm_prob    * 100

        if result == "Cool":
            active_colors = COOL_DATA
            icon_hero = "all_inclusive"
            hero_desc = "Hasil analisis menunjukkan dominasi nuansa cool pada tampilan kulit Anda."
            bar_colors = ["#6B7A99", "#A0AEC0", "#C86A87"]
            vibe_title = "Cool Casual"
            top_hex, bottom_hex = "A62649", "4A4E69"
        elif result == "Warm":
            active_colors = WARM_DATA
            icon_hero = "local_fire_department"
            hero_desc = "Hasil analisis menunjukkan dominasi nuansa hangat pada tampilan kulit Anda."
            bar_colors = ["#6B7A99", "#A0AEC0", "#C86A87"]
            vibe_title = "Warm Casual"
            top_hex, bottom_hex = "C86A87", "9D4F68"
        else:
            active_colors = NEUTRAL_DATA
            icon_hero = "all_inclusive"
            hero_desc = "Hasil analisis menunjukkan karakter undertone yang berada di antara warm dan cool."
            bar_colors = ["#6B7A99", "#A0AEC0", "#C86A87"]
            vibe_title = "Neutral Casual"
            top_hex, bottom_hex = "B87D86", "334155"  
        
        render_hero_dashboard(
            result=result,
            vibe_title=vibe_title,
            hero_desc=hero_desc,
            cool_v=cool_v,
            neut_v=neut_v,
            warm_v=warm_v
        )
        
        # =====================================================
        # PENYIAPAN REKOMENDASI OUTFIT
        # =====================================================
        if result == "Warm":
            color_combinations = [
                (
                    [active_colors[4], active_colors[12], active_colors[13]],
                    "Cream Ivory",
                    "Warm Khaki • Camel Brown"
                ),
                (
                    [active_colors[5], active_colors[14], active_colors[13]],
                    "Cream",
                    "Olive Green • Camel Brown"
                ),
                (
                    [active_colors[7], active_colors[13], active_colors[5]],
                    "Warm Beige",
                    "Camel Brown • Cream"
                ),
                (
                    [active_colors[14], active_colors[4], active_colors[9]],
                    "Olive Green",
                    "Cream Ivory • Cedar Brown"
                ),
            ]
            outfit_recommendation = {
                "Atasan": active_colors[4],    # Cream Ivory
                "Luaran": active_colors[12],   # Warm Khaki
                "Bawahan": active_colors[13]   # Camel Brown
            }
        elif result == "Cool":
            color_combinations = [
                (
                    [active_colors[14], active_colors[8], active_colors[2]],
                    "Ice Blue",
                    "Slate Blue • Charcoal Gray"
                ),
                (
                    [active_colors[12], active_colors[2], active_colors[0]],
                    "Silver Gray",
                    "Charcoal Gray • Midnight Black"
                ),
                (
                    [active_colors[6], active_colors[12], active_colors[8]],
                    "Lavender",
                    "Silver Gray • Slate Blue"
                ),
            ]
            outfit_recommendation = {
                "Atasan": active_colors[14],  # Ice Blue
                "Luaran": active_colors[8],   # Slate Blue
                "Bawahan": active_colors[2]   # Charcoal Gray
            }
        else:
            color_combinations = [
                (
                    [active_colors[0], active_colors[3], active_colors[6]],
                    "Off White",
                    "Sage Green • Greige"
                ),
                (
                    [active_colors[11], active_colors[7], active_colors[0]],
                    "Cloud Gray",
                    "Taupe • Off White"
                ),
                (
                    [active_colors[8], active_colors[0], active_colors[6]],
                    "Dusty Rose",
                    "Off White • Greige"
                ),
                (
                    [active_colors[3], active_colors[7], active_colors[11]],
                    "Sage Green",
                    "Taupe • Cloud Gray"
                ),
            ]
            outfit_recommendation = {
                "Atasan": active_colors[0],  # Off White
                "Luaran": active_colors[3],  # Sage Green
                "Bawahan": active_colors[6]  # Greige
            }
        # =====================================================
        # BARIS 3: PALETTE SYSTEM | OUTFIT VISUALIZER
        # =====================================================
        palette_col, outfit_col = st.columns([1.4, 1.2], gap="medium")

        # --- PALETTE COMPONENT ---
        with palette_col:
            st.markdown('<div class="equal-height-card">', unsafe_allow_html=True)
            with st.container(border=True):
                # 4. JUDUL CARD: REKOMENDASI PALET WARNA (SERAGAM 14PX)
                st.markdown("""
                <div style="font-family:'DM Sans', sans-serif; font-size:14px; font-weight:700; color:#2F2430; margin-bottom:20px; display:flex; align-items:center; gap:8px;">
                    <span class="material-symbols-rounded" style="color:#C86A87; font-size:20px;">palette</span>
                    Rekomendasi Palet Warna
                </div>
                """, unsafe_allow_html=True)
                st.markdown(
                    "<div style='height:12px;'></div>",
                    unsafe_allow_html=True
                )

                items_html = "".join([
                    f'<div class="premium-palette-item">'
                    f'<div class="premium-palette-swatch" style="background:#{color["hex"]};"></div>'
                    f'<div class="premium-palette-label">{color["nama"]}</div>'
                    f'</div>'
                    for color in active_colors
                ])
                full_palette_html = f'<div class="premium-palette-grid">{items_html}</div>'
                st.markdown(
                    full_palette_html,
                    unsafe_allow_html=True
                )

                st.markdown("""
                <div style="
                background:#FCFAF8;
                border:1px solid #E6DADD;
                border-radius:10px;
                padding:10px;
                font-size:11px;
                text-align:center;
                color:#5E4D56;
                line-height:1.6;
                margin-top:18px;
                margin-bottom:2px;
                ">
                Warna-warna di atas dipilih khusus untuk
                menonjolkan karakter undertone Anda.
                </div>
                """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)
        
        # --- OUTFIT RECOM COMPONENT ---
        with outfit_col:
            st.markdown('<div class="equal-height-card">', unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown("""
                <div style="font-family:'DM Sans', sans-serif; font-size:14px; font-weight:700; color:#2F2430; margin-bottom:16px; display:flex; align-items:center; gap:6px;">
                    <span class="material-symbols-rounded" style="color:#C86A87; font-size:20px;">checkroom</span>
                    Rekomendasi Warna Busana
                </div>
                """, unsafe_allow_html=True)
                
                render_outfit_card_premium(
                    top_hex=outfit_recommendation["Atasan"]["hex"],
                    outer_hex=outfit_recommendation["Luaran"]["hex"],
                    bottom_hex=outfit_recommendation["Bawahan"]["hex"],
                    top_name=outfit_recommendation["Atasan"]["nama"],
                    outer_name=outfit_recommendation["Luaran"]["nama"],
                    bottom_name=outfit_recommendation["Bawahan"]["nama"],
                )
            st.markdown('</div>', unsafe_allow_html=True)

        # =====================================================
        # BARIS 4: SUGGESTED COLOR COMBINATIONS
        # =====================================================
        with st.container(border=True):
            # 6. JUDUL CARD: KOMBINASI WARNA YANG DISARANKAN (SERAGAM 14PX)
            st.markdown("""
            <div style="font-family:'DM Sans', sans-serif; font-size:14px; font-weight:700; color:#2F2430; margin-bottom:16px; display:flex; align-items:center; gap:8px;">
                <span class="material-symbols-rounded" style="color:#C86A87; font-size:20px;">auto_awesome</span>
                Kombinasi Warna yang Disarankan
            </div>
            """, unsafe_allow_html=True)
            
            combo_cols = st.columns(len(color_combinations))
            for i, (colors, line1, line2) in enumerate(color_combinations):
                with combo_cols[i]:
                    st.markdown(f"""
                        <div style="font-family:'DM Sans', sans-serif; background:#FAF7F5; border:1px solid #F0E7E2; border-radius:12px; padding:10px; text-align:center; min-height:90px;">
                            <div style="display:flex; justify-content:center; margin-bottom:8px;">
                                <div style="width:18px; height:18px; border-radius:50%; background:#{colors[0]["hex"]}; margin-left:-4px; border:2px solid white;"></div>
                                <div style="width:18px; height:18px; border-radius:50%; background:#{colors[1]["hex"]}; margin-left:-4px; border:2px solid white;"></div>
                                <div style="width:18px; height:18px; border-radius:50%; background:#{colors[2]["hex"]}; margin-left:-4px; border:2px solid white;"></div>
                            </div>
                            <div style="font-size:10px; font-weight:600; color:#555; line-height:1.4;">{line1}<br>{line2}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
            st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
        
        # =====================================================
        # BARIS 5: DETAIL ANALISIS
        # =====================================================

        buffer = io.BytesIO()

        st.session_state.cropped_image.save(
            buffer,
            format="PNG"
        )

        crop_b64 = base64.b64encode(
            buffer.getvalue()
        ).decode()

        render_analysis_area_premium(
            crop_b64
        )    
             
    else:
        render_empty_state()