import streamlit as st
import base64
import os
from PIL import Image
import io

def recolor_png(path, hex_color):
    img = Image.open(path).convert("RGBA")
    hex_color = hex_color.replace("#", "")

    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    pixels = img.load()

    for y in range(img.height):
        for x in range(img.width):
            pr, pg, pb, pa = pixels[x, y]
            if pa > 0:
                brightness = (pr + pg + pb) / 3 / 255
                nr = int(r * brightness)
                ng = int(g * brightness)
                nb = int(b * brightness)
                pixels[x, y] = (nr, ng, nb, pa)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

def img_b64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    return ""

def render_navbar():
    st.markdown("""
    <div class="cb-nav" style="font-family:'DM Sans', sans-serif;">
        <div class="cb-brand">
            <span class="cb-brand-name">
                Colour<span style="color:#D77497;">Blueprint</span>
            </span>
            <span class="cb-brand-tag">
                Undertone Analyzer
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
def render_empty_state():
    st.markdown("""
    <div style="
    font-family:'DM Sans', sans-serif;
    text-align:center;
    padding:40px 20px;
    border:2px dashed #E6DADD;
    border-radius:16px;
    background:#FCFAF8;
    margin-top:0px;
    ">
        <span class="material-symbols-rounded" style="font-size:48px; color:#8F7D86;">add_a_photo</span>
        <div style="font-weight:700; margin-top:2px; color:#2F2430; font-size:15px;">Belum Ada Analisis</div>
        <div style="font-size:12px; color:#5E4D56; max-width:280px; margin:4px auto 0 auto; line-height:1.5;">
            Unggah foto pergelangan tangan Anda di panel sebelah kiri untuk melihat hasil analisis di sini.
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_hero_dashboard(
    result,
    vibe_title,
    hero_desc,
    cool_v,
    neut_v,
    warm_v
):

    if result.upper() == "WARM":
        gradient = """
        linear-gradient(
            135deg,
            #E98307 0%,
            #D06A3A 45%,
            #A94A67 100%
        )
        """
        hero_icon = "wb_sunny"

    elif result.upper() == "NEUTRAL":
        gradient = """
        linear-gradient(
            135deg,
            #6B8F87 0%,
            #6E9C95 50%,
            #5E7F8A 100%
        )
        """
        hero_icon = "balance"

    else:
        gradient = """
        linear-gradient(
            135deg,
            #5865A6 0%,
            #5167B8 45%,
            #7B6DC4 100%
        )
        """
        hero_icon = "ac_unit"
        
    st.markdown(
        f"""
        <div class="hero-card" style="
        background:{gradient};
        border-radius:22px;
        padding:14px 20px;
        color:white;
        display:flex;
        align-items:flex-start;
        min-height:200px;
        ">
            <div class="hero-left" style="
            flex:1;
            text-align:center;
            ">
                <span class="material-symbols-rounded"
                style="
                font-size:22px;
                margin-bottom:2ppx;
                color:white;
                ">
                    {hero_icon}
                </span>
                <div style="
                font-size:clamp(36px, 6vw, 52px);
                font-weight:700;
                line-height:1;
                ">
                    {result.upper()}
                </div>
                <div style="
                font-size:20px;
                font-weight:700;
                margin-top:6px;
                ">
                    {vibe_title}
                </div>
                <div style="
                font-size:12px;
                opacity:.92;
                max-width:320px;
                margin:auto;
                margin-top:14px;
                line-height:1.5;
                ">
                    {hero_desc}
                </div>
            </div>
            <div class="hero-divider" style="
            width:1px;
            height:170px;
            background:rgba(255,255,255,.22);
            margin:0 30px;
            ">
            </div>
            <div class="hero-right" style="
            flex:1;
            ">
                <div style="
                font-size:16px;
                font-weight:700;
                margin-bottom:24px;
                display:flex;
                align-items:center;
                gap:8px;
                ">
                    <span class="material-symbols-rounded"
                    style="
                    font-size:18px;
                    ">
                        monitoring
                    </span>
                    Model Confidence
                </div>
                <div style="margin-bottom:16px;">
                    <div style="
                    display:flex;
                    justify-content:space-between;
                    font-size:11px;
                    margin-bottom:6px;
                    ">
                        <span>Cool</span>
                        <span>{cool_v:.1f}%</span>
                    </div>
                    <div style="
                    height:10px;
                    border-radius:10px;
                    background:rgba(255,255,255,.18);
                    overflow:hidden;
                    ">
                        <div style="
                        width:{cool_v}%;
                        background:#8DA2FB;
                        height:100%;
                        ">
                        </div>
                    </div>
                </div>
                <div style="margin-bottom:16px;">
                    <div style="
                    display:flex;
                    justify-content:space-between;
                    font-size:13px;
                    margin-bottom:6px;
                    ">
                        <span>Neutral</span>
                        <span>{neut_v:.1f}%</span>
                    </div>
                    <div style="
                    height:10px;
                    border-radius:10px;
                    background:rgba(255,255,255,.18);
                    overflow:hidden;
                    ">
                        <div style="
                        width:{neut_v}%;
                        background:#6FAE9C;
                        height:100%;
                        ">
                        </div>
                    </div>
                </div>
                <div>
                    <div style="
                    display:flex;
                    justify-content:space-between;
                    font-size:13px;
                    margin-bottom:6px;
                    ">
                        <span>Warm</span>
                        <span>{warm_v:.1f}%</span>
                    </div>
                    <div style="
                    height:10px;
                    border-radius:10px;
                    background:rgba(255,255,255,.18);
                    overflow:hidden;
                    ">
                        <div style="
                        width:{warm_v}%;
                        background:#708238;
                        height:100%;
                        ">
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_outfit_card_premium(
    top_hex,
    outer_hex,
    bottom_hex,
    top_name,
    outer_name,
    bottom_name,
):
    baju_master = recolor_png("assets/Atasan.png", top_hex)
    outer_master = recolor_png("assets/Luaran.png", outer_hex)
    celana_master = recolor_png("assets/Bawahan.png", bottom_hex)

    st.markdown(f"""
    <div style="font-family:'DM Sans', sans-serif; display: flex; flex-direction: column;">
        <div style="display:flex; justify-content:space-between; gap:12px; margin-bottom:12px;">
            <div style="flex:1;text-align:center;">
                <div style="font-size:11px; font-weight:700; margin-bottom:6px; color:#5E4D56;">Atasan</div>
                <div style="
                height:170px;
                display:flex;
                align-items:flex-end;
                justify-content:center;
                ">
                    <img src="data:image/png;base64,{baju_master}"
                    style="
                    max-height:170px;
                    width:auto;
                    ">
                </div>
                <div style="display:flex; justify-content:center; align-items:center; gap:6px; margin-top:8px;">
                    <div style="width:12px; height:12px; border-radius:3px; background:#{top_hex}; border:1px solid rgba(0,0,0,.08);"></div>
                    <span style="font-size:11px; font-weight:600; color:#555;">{top_name}</span>
                </div>
            </div>
            <div style="flex:1;text-align:center;">
                <div style="font-size:11px; font-weight:700; margin-bottom:6px; color:#5E4D56;">Luaran</div>
                <div style="
                height:170px;
                display:flex;
                align-items:flex-end;
                justify-content:center;
                ">
                    <img src="data:image/png;base64,{outer_master}"
                    style="
                    max-height:170px;
                    width:auto;
                    ">
                </div>
                <div style="display:flex; justify-content:center; align-items:center; gap:6px; margin-top:8px;">
                    <div style="width:12px; height:12px; border-radius:3px; background:#{outer_hex}; border:1px solid rgba(0,0,0,.08);"></div>
                    <span style="font-size:11px; font-weight:600; color:#555;">{outer_name}</span>
                </div>
            </div>
            <div style="flex:1;text-align:center;">
                <div style="font-size:11px; font-weight:700; margin-bottom:6px; color:#5E4D56;">Bawahan</div>
                <div style="
                height:170px;
                display:flex;
                align-items:flex-end;
                justify-content:center;
                ">
                    <img src="data:image/png;base64,{celana_master}"
                    style="
                    max-height:170px;
                    width:auto;
                    ">
                </div>
                <div style="display:flex; justify-content:center; align-items:center; gap:6px; margin-top:8px;">
                    <div style="width:12px; height:12px; border-radius:3px; background:#{bottom_hex}; border:1px solid rgba(0,0,0,.08);"></div>
                    <span style="font-size:11px; font-weight:600; color:#555;">{bottom_name}</span>
                </div>
            </div> 
        </div>
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
        margin-bottom:8px;
        ">
        Kombinasi pakaian di atas dipilih untuk membantu
        menampilkan warna kulit secara lebih harmonis.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
def render_analysis_area_premium(crop_b64):

    st.markdown(f"""
    <div style="
    background:white;
    border:1px solid #E9DDE0;
    border-radius:16px;
    padding:18px;
    min-height:180px;
    ">
        <div style="
        display:flex;
        align-items:center;
        gap:8px;
        font-size:14px;
        font-weight:700;
        color:#2F2430;
        margin-bottom:14px;
        ">
            <span class="material-symbols-rounded"
            style="
            color:#D96C8A;
            font-size:20px;
            ">
                crop_free
            </span>
            Detail Analisis
        </div>
        <div style="
        font-size:12px;
        font-weight:600;
        color:#444;
        margin-bottom:10px;
        ">
            Area yang Dianalisis (Crop Otomatis)
        </div>
        <div style="
        display:flex;
        align-items:flex-start;
        gap:18px;
        ">
            <img
                src="data:image/png;base64,{crop_b64}"
                style="
                width:180px;
                height:180px;
                object-fit:cover;
                border-radius:10px;
                border:1px solid #E6DADD;
                "
            >
            <div style="
            flex:1;
            font-size:13px;
            color:#666;
            line-height:1.8;
            padding-top:6px;
            ">
                Area ini adalah hasil <i>crop otomatis</i>
                oleh sistem yang digunakan sebagai
                input model untuk mengklasifikasikan
                <i>skin undertone</i> Anda berdasarkan
                visibilitas warna urat nadi.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)