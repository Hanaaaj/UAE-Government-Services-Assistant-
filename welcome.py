# welcome.py
import streamlit as st
import time
import base64

def show_welcome_screen():
    st.markdown("""
    <style>
    .stApp{
        background: linear-gradient(
            135deg,
            #022C22 0%,
            #0A5C44 40%,
            #15803D 70%,
            #022C22 100%
        );
    }

    .main-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 85vh;
        padding: 20px;
    }

    .glass-card {
        width: 900px;
        padding: 40px;
        text-align: center;
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-radius: 25px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        animation: fadeIn 1.5s ease-in-out;
    }

    .glass-card h1, .glass-card p, .glass-card div {
        color: #FFFFFF !important;
    }

    .logo {
        width: 220px;
        height: 220px;
        object-fit: contain;
        background-color: #FFFFFF;
        border-radius: 50%;
        border: 3px solid rgba(255, 255, 255, 0.9);
        margin: 0 auto 20px auto;
        display: block;
        padding: 15px;
        animation: logoFloat 2s ease-in-out;
    }

    .typed-title {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin-top: 10px;
        margin-bottom: 20px;
        min-height: 80px;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0px); }
    }

    @keyframes logoFloat {
        0% { opacity: 0; transform: translateY(-20px); }
        100% { opacity: 1; transform: translateY(0px); }
    }
    </style>
    """, unsafe_allow_html=True)

    try:
        with open("LOGO.jpeg", "rb") as f:
            data = f.read()
            encoded_image = base64.b64encode(data).decode()
        image_src = f"data:image/jpeg;base64,{encoded_image}"
    except FileNotFoundError:
        image_src = "LOGO.jpeg"

    container_placeholder = st.empty()
    title = "Welcome to Daleel — دليل "
    typed = ""

    if "animation_done" not in st.session_state:
        for char in title:
            typed += char
            container_placeholder.markdown(
                f"""
                <div class="main-container">
                    <div class="glass-card">
                        <img src="{image_src}" class="logo">
                        <h1 class="typed-title">{typed}</h1>
                        <div style='text-align:center;'>
                            <p style="font-size:16px; color:#D1D5DB; letter-spacing:1px; font-weight: 500;">دليل • Guide</p>
                            <p style="font-size:22px; line-height:1.6; font-weight:300; margin-bottom: 20px;">
                                Your trusted guide to navigating essential services in the UAE.
                            </p>
                            <p style="font-size:16px; color:#D1D5DB; letter-spacing:1px; font-weight: 500;">
                                Visa Services • Driving Licences • Business Services
                            </p>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            time.sleep(0.02)
        st.session_state.animation_done = True
    else:
        container_placeholder.markdown(
            f"""
            <div class="main-container">
                <div class="glass-card">
                    <img src="{image_src}" class="logo">
                    <h1 class="typed-title">{title}</h1>
                    <div style='text-align:center;'>
                        <p style="font-size:16px; color:#D1D5DB; letter-spacing:1px; font-weight: 500;">دليل • Guide</p>
                        <p style="font-size:22px; line-height:1.6; font-weight:300; margin-bottom: 20px;">
                            Your trusted guide to navigating essential services in the UAE.
                        </p>
                        <p style="font-size:16px; color:#D1D5DB; letter-spacing:1px; font-weight: 500;">
                            Visa Services • Driving Licences • Business Services
                        </p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button(" Get Started", use_container_width=True):
            st.session_state.started = True
            st.rerun()
