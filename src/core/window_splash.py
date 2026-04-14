import os
import base64
import webview
import logging
from src.core.paths import SPLASH_1_PATH, SPLASH_2_PATH, SPLASH_3_PATH

log = logging.getLogger("CodeMerger")

def get_splash_html():
    """Generates the animated HTML for the CodeMerger splash screen."""
    def get_b64(path):
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    return f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"
            except Exception: return ""
        return ""

    return f"""
    <body style="background:#1A1A1A; color:#FFFFFF; font-family:'Segoe UI', sans-serif; display:flex; align-items:center; justify-content:center; height:100vh; margin:0; overflow:hidden; user-select:none;">
        <div style="text-align:center;">
            <div style="position:relative; width:64px; height:64px; margin: 0 auto 20px;">
                <img src="{get_b64(SPLASH_1_PATH)}" class="logo logo-1">
                <img src="{get_b64(SPLASH_2_PATH)}" class="logo logo-2">
                <img src="{get_b64(SPLASH_3_PATH)}" class="logo logo-3">
            </div>
            <h1 style="font-weight:100; font-size:28px; letter-spacing:4px; margin:0; color:#eee;">CODEMERGER</h1>
            <div style="margin-top:15px; display:flex; align-items:center; justify-content:center;">
                <div style="width:4px; height:4px; background:#0078D4; border-radius:50%; margin:0 3px; animation: pulse 0.8s infinite ease-in-out;"></div>
                <p style="color:#0078D4; font-size:11px; margin:0; font-weight:bold; letter-spacing:1px; opacity:0.8; text-transform:uppercase;">Initializing Interface</p>
            </div>
        </div>
        <style>
            .logo {{ position: absolute; top: 0; left: 0; width: 64px; height: 64px; opacity: 0; }}
            .logo-1 {{ opacity: 1; }}
            .logo-2 {{ animation: fade-over 0.6s linear forwards 0.3s; }}
            .logo-3 {{ animation: fade-over 0.6s linear forwards 0.6s; }}
            @keyframes fade-over {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
            @keyframes pulse {{ 0%, 100% {{ opacity: 0.3; transform: scale(0.8); }} 50% {{ opacity: 1; transform: scale(1.2); }} }}
        </style>
    </body>
    """

def create_splash_window(m_left, m_top, m_w_phys, m_h_phys, scale):
    """Initializes the frameless splash screen centered on the physical monitor."""
    s_w_log, s_h_log = 400, 280
    s_x_phys = int(m_left + (m_w_phys - (s_w_log * scale)) / 2)
    s_y_phys = int(m_top + (m_h_phys - (s_h_log * scale)) / 2)

    return webview.create_window(
        "CM-Splash", html=get_splash_html(), width=s_w_log, height=s_h_log,
        x=s_x_phys, y=s_y_phys,
        frameless=True, on_top=True, background_color='#1A1A1A',
        hidden=True
    )