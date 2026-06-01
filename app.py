import streamlit as st
import cv2
import os
import threading
import speech_recognition as sr
import asyncio
import edge_tts
import pygame
import uuid
import time
import psutil 
import json
import base64  
from groq import Groq
from rapidfuzz import process, fuzz
from ultralytics import YOLO

import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- STREAMLIT UI SETUP ---
st.set_page_config(page_title="AeroGuard Master", layout="wide", page_icon="🛫")

def set_background(image_path):
    try:
        with open(image_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            
        st.markdown(
            f"""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Audiowide&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

            .stApp {{
                background-image: url("data:image/jpeg;base64,{b64}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            
            .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp span, .stApp li, .stApp label, .stMarkdown {{
                color: #ffffff !important;
            }}

            /* Force ALL Streamlit wrapper layers around the radio to full width */
            div[data-testid="stRadio"] {{
                width: 100% !important;
                max-width: 100% !important;
                box-sizing: border-box !important;
            }}
            div[data-testid="stRadio"] > div {{
                width: 100% !important;
                max-width: 100% !important;
                box-sizing: border-box !important;
            }}
            div[data-testid="stRadio"] > div > div {{
                width: 100% !important;
                max-width: 100% !important;
                box-sizing: border-box !important;
            }}
            div[data-testid="stRadio"] > div > div > div {{
                width: 100% !important;
                max-width: 100% !important;
                box-sizing: border-box !important;
            }}

            .glass-panel {{
                background-color: rgba(6, 14, 30, 0.65);
                padding: 30px;
                border-radius: 20px;
                border: 1px solid rgba(0, 255, 204, 0.2);
                margin-bottom: 25px;
                box-shadow: 0px 10px 40px rgba(0, 0, 0, 0.8);
                backdrop-filter: blur(15px);
                -webkit-backdrop-filter: blur(15px);
            }}

            .footer {{
                text-align: center;
                padding: 20px;
                margin-top: 50px;
                background-color: rgba(0,0,0,0.6);
                border-top: 1px solid rgba(255,255,255,0.1);
            }}
            
            .glow-card-wrapper {{
                position: relative;
                width: 100%; 
                margin: 0 auto 20px auto;
                transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            }}
            .glow-card-wrapper:hover {{
                transform: translateY(-8px);
            }}
            .glow-card-bg {{
                position: absolute;
                inset: 0;
                opacity: 0.85; 
                border-radius: 40px;
                filter: blur(40px); 
                z-index: 0;
                pointer-events: none;
                transition: all 0.4s ease;
            }}
            .glow-card-wrapper:hover .glow-card-bg {{
                opacity: 1;
                filter: blur(50px);
            }}
            .glow-card-fg {{
                position: relative;
                height: 260px;
                border-radius: 40px;
                z-index: 10;
                border: 8px solid transparent;
                padding: 28px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                text-align: left;
                overflow: hidden; 
            }}
            
            .glow-card-fg::after {{
                content: '';
                position: absolute;
                top: 0;
                left: -150%;
                width: 50%;
                height: 100%;
                background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0) 100%);
                transform: skewX(-25deg);
                animation: shine-sweep 5s infinite;
                z-index: 1;
                pointer-events: none;
            }}
            @keyframes shine-sweep {{
                0% {{ left: -150%; }}
                20% {{ left: 250%; }}
                100% {{ left: 250%; }}
            }}
            
            @keyframes shine-sweep-slow {{
                0% {{ left: -150%; }}
                20% {{ left: 250%; }}
                100% {{ left: 250%; }}
            }}
            
            .cyber-header-box::after {{
                content: '';
                position: absolute;
                top: 0;
                left: -150%;
                width: 50%;
                height: 100%;
                background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0) 100%);
                transform: skewX(-25deg);
                animation: shine-sweep-slow 7s infinite;
                z-index: 1;
                pointer-events: none;
            }}

            .quick-features-box {{
                position: relative;
                padding: 25px;
                border-radius: 20px;
                margin-top: 10px;
                overflow: hidden;
                background: linear-gradient(rgba(15, 15, 20, 0.85), rgba(15, 15, 20, 0.85)) padding-box, 
                            linear-gradient(137deg, #00ffcc 0%, #0061FF 50%, #a200ff 100%) border-box;
                border: 4px solid transparent;
                box-shadow: 0 0 30px rgba(0, 255, 204, 0.25);
            }}

            .quick-features-box::after {{
                content: '';
                position: absolute;
                top: 0;
                left: -150%;
                width: 50%;
                height: 100%;
                background: linear-gradient(to right, rgba(0,255,204,0) 0%, rgba(0,255,204,0.15) 50%, rgba(0,255,204,0) 100%);
                transform: skewX(-25deg);
                animation: shine-sweep-slow 6s infinite 1.5s;
                z-index: 1;
                pointer-events: none;
            }}

            .glow-card-icon {{
                color: rgba(255, 255, 255, 0.9);
                font-size: 32px;
                margin-bottom: 20px;
                position: relative;
                z-index: 2;
            }}
            .glow-card-title {{
                color: #ffffff !important;
                font-weight: 500 !important;
                font-size: 1.25rem !important;
                margin: 0 0 12px 0 !important;
                letter-spacing: -0.5px !important;
                text-shadow: none !important;
                position: relative;
                z-index: 2;
            }}
            .glow-card-desc {{
                color: #9ca3af !important;
                font-size: 14px !important;
                line-height: 1.6 !important;
                margin: 0 !important;
                font-weight: 400 !important;
                text-shadow: none !important;
                position: relative;
                z-index: 2;
            }}

            /* ── PREMIUM CENTERED NAVBAR ── */
            div[data-testid="stRadio"] {{
                display: flex !important;
                justify-content: center !important;
                align-items: center !important;
                width: 100% !important;
                margin-top: 0 !important;
                padding: 0 !important;
            }}

            /* Force the Streamlit block container wrapping the radio to full width */
            div[data-testid="stRadio"] > div {{
                width: 100% !important;
            }}

            div[role="radiogroup"] {{
                display: flex !important;
                flex-direction: row !important;
                justify-content: stretch !important;
                align-items: center !important;
                gap: 10px !important;
                background: linear-gradient(rgba(4, 9, 20, 0.82), rgba(4, 9, 20, 0.82)) padding-box,
                            linear-gradient(137deg, #00ffcc 0%, #00aaff 40%, #a200ff 70%, #ff3366 100%) border-box !important;
                border: 3px solid transparent !important;
                border-radius: 20px !important;
                padding: 10px 14px !important;
                backdrop-filter: blur(18px) !important;
                -webkit-backdrop-filter: blur(18px) !important;
                box-shadow:
                    0 0 0 1px rgba(0, 255, 204, 0.08),
                    0 0 30px rgba(0, 170, 255, 0.25),
                    0 0 60px rgba(162, 0, 255, 0.15),
                    0 8px 32px rgba(0, 0, 0, 0.6) !important;
                width: 100% !important;
                max-width: 100% !important;
                box-sizing: border-box !important;
                margin: 0 0 28px 0 !important;
            }}

            div[role="radiogroup"] > label {{
                background: rgba(11, 19, 32, 0.85) !important;
                color: white !important;
                padding: 12px 0 !important;
                border-radius: 13px !important;
                transition: all 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
                border: 1px solid rgba(0, 170, 255, 0.18) !important;
                cursor: pointer !important;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35) !important;
                margin: 0 !important;
                flex: 1 !important;
                text-align: center !important;
                min-width: 0 !important;
            }}

            div[role="radiogroup"] > label:hover {{
                transform: translateY(-2px) scale(1.02) !important;
                background: rgba(0, 170, 255, 0.1) !important;
                box-shadow: 0 0 18px rgba(0, 255, 204, 0.28), 0 4px 16px rgba(0,0,0,0.4) !important;
                border-color: rgba(0, 255, 204, 0.55) !important;
            }}

            /* Active button per-tab accent colors */
            div[role="radiogroup"] > label:nth-child(1)[data-checked="true"] {{
                background: linear-gradient(135deg, rgba(0,102,204,0.35), rgba(0,30,60,0.6)) !important;
                box-shadow: 0 0 22px rgba(0,170,255,0.5), inset 0 1px 0 rgba(0,200,255,0.2) !important;
                border-color: #00aaff !important;
            }}
            div[role="radiogroup"] > label:nth-child(2)[data-checked="true"] {{
                background: linear-gradient(135deg, rgba(100,0,200,0.35), rgba(30,0,60,0.6)) !important;
                box-shadow: 0 0 22px rgba(162,0,255,0.5), inset 0 1px 0 rgba(180,80,255,0.2) !important;
                border-color: #a200ff !important;
            }}
            div[role="radiogroup"] > label:nth-child(3)[data-checked="true"] {{
                background: linear-gradient(135deg, rgba(0,180,120,0.3), rgba(0,40,30,0.6)) !important;
                box-shadow: 0 0 22px rgba(0,255,204,0.5), inset 0 1px 0 rgba(0,255,200,0.2) !important;
                border-color: #00ffcc !important;
            }}
            div[role="radiogroup"] > label:nth-child(4)[data-checked="true"] {{
                background: linear-gradient(135deg, rgba(200,0,60,0.3), rgba(50,0,20,0.6)) !important;
                box-shadow: 0 0 22px rgba(255,51,102,0.5), inset 0 1px 0 rgba(255,80,120,0.2) !important;
                border-color: #ff3366 !important;
            }}

            div[role="radiogroup"] p {{
                color: #e8f4ff !important;
                font-weight: 600 !important;
                font-size: 14px !important;
                margin: 0 !important;
                letter-spacing: 0.3px !important;
                text-shadow: none !important;
            }}
            div[role="radiogroup"] > label > div:first-of-type {{
                display: none !important;
            }}

            .cyber-header-box {{
                position: relative;
                text-align: center;
                padding: 40px 20px;
                background: linear-gradient(rgba(4, 9, 20, 0.85), rgba(4, 9, 20, 0.85)) padding-box, 
                            linear-gradient(137deg, #00ffcc 0%, #00aaff 50%, #a200ff 100%) border-box;
                border: 4px solid transparent;
                border-radius: 20px;
                margin-bottom: 8px;
                overflow: hidden;
                box-shadow: 0px 0px 40px rgba(0, 170, 255, 0.35);
            }}

            .cyber-title {{
                font-family: 'Audiowide', cursive, sans-serif;
                font-size: 3.8rem !important; 
                margin: 0;
                text-transform: uppercase; 
                color: #e0f7fa !important;
                text-shadow: 0 0 10px #00aaff, 0 0 20px #00aaff, 0 0 30px #00aaff !important;
                position: relative;
                z-index: 2;
                letter-spacing: 2px;
            }}

            .cyber-subtitle {{
                font-family: 'Segoe UI', sans-serif;
                margin: 15px 0 0 0;
                color: #a0e0ff !important;
                font-weight: 300;
                letter-spacing: 4px;
                font-size: 1.2rem;
                text-shadow: 0 0 10px #006699 !important;
                position: relative;
                z-index: 2;
                text-transform: uppercase;
            }}

            /* ANALYTICS KPI CARDS */
            .kpi-card-wrapper {{
                position: relative;
                width: 100%;
                margin: 0 auto 20px auto;
                transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            }}
            .kpi-card-wrapper:hover {{ transform: translateY(-6px); }}
            .kpi-card-bg {{
                position: absolute;
                inset: 0;
                opacity: 0.7;
                border-radius: 24px;
                filter: blur(30px);
                z-index: 0;
                pointer-events: none;
                transition: all 0.4s ease;
            }}
            .kpi-card-wrapper:hover .kpi-card-bg {{ opacity: 1; filter: blur(40px); }}
            .kpi-card-fg {{
                position: relative;
                border-radius: 24px;
                z-index: 10;
                border: 3px solid transparent;
                padding: 22px 20px;
                text-align: center;
                overflow: hidden;
            }}
            .kpi-card-fg::after {{
                content: '';
                position: absolute;
                top: 0;
                left: -150%;
                width: 50%;
                height: 100%;
                background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.12) 50%, rgba(255,255,255,0) 100%);
                transform: skewX(-25deg);
                animation: shine-sweep 6s infinite;
                z-index: 1;
                pointer-events: none;
            }}
            .kpi-value {{
                font-family: 'Audiowide', cursive, sans-serif;
                font-size: 2.2rem !important;
                font-weight: bold !important;
                margin: 0 0 6px 0 !important;
                position: relative;
                z-index: 2;
            }}
            .kpi-label {{
                color: #9ca3af !important;
                font-size: 13px !important;
                letter-spacing: 1.5px !important;
                text-transform: uppercase !important;
                margin: 0 !important;
                position: relative;
                z-index: 2;
            }}
            .kpi-icon {{ font-size: 24px; margin-bottom: 8px; position: relative; z-index: 2; }}

            /* ALERT STATUS STRIP */
            .alert-strip {{
                position: relative;
                display: flex;
                justify-content: space-around;
                padding: 20px 30px;
                background: linear-gradient(rgba(6, 14, 30, 0.80), rgba(6, 14, 30, 0.80)) padding-box,
                            linear-gradient(137deg, #00ffcc 0%, #0061FF 50%, #a200ff 100%) border-box;
                border: 3px solid transparent;
                border-radius: 20px;
                margin-bottom: 25px;
                box-shadow: 0 0 35px rgba(0, 170, 255, 0.25);
                overflow: hidden;
                text-align: center;
                backdrop-filter: blur(15px);
            }}
            .alert-strip::after {{
                content: '';
                position: absolute;
                top: 0; left: -150%; width: 50%; height: 100%;
                background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.08) 50%, rgba(255,255,255,0) 100%);
                transform: skewX(-25deg);
                animation: shine-sweep-slow 8s infinite;
                z-index: 1; pointer-events: none;
            }}

            /* ALERT CARDS */
            .alert-card {{
                position: relative; padding: 20px 22px;
                border-radius: 18px; margin-bottom: 0;
                overflow: hidden; backdrop-filter: blur(12px);
            }}
            .alert-card::after {{
                content: ''; position: absolute;
                top: 0; left: -150%; width: 50%; height: 100%;
                background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0) 100%);
                transform: skewX(-25deg); animation: shine-sweep 5s infinite;
                z-index: 1; pointer-events: none;
            }}
            .alert-card-red {{
                background: linear-gradient(rgba(30, 8, 8, 0.85), rgba(30, 8, 8, 0.85)) padding-box,
                            linear-gradient(137deg, #ff3366 0%, #ff6b35 100%) border-box;
                border: 3px solid transparent; box-shadow: 0 0 25px rgba(255, 51, 102, 0.35);
            }}
            .alert-card-orange {{
                background: linear-gradient(rgba(30, 18, 5, 0.85), rgba(30, 18, 5, 0.85)) padding-box,
                            linear-gradient(137deg, #ff9900 0%, #ffcc00 100%) border-box;
                border: 3px solid transparent; box-shadow: 0 0 25px rgba(255, 153, 0, 0.35);
            }}
            .alert-card-green {{
                background: linear-gradient(rgba(5, 20, 10, 0.85), rgba(5, 20, 10, 0.85)) padding-box,
                            linear-gradient(137deg, #00ffcc 0%, #00ff87 100%) border-box;
                border: 3px solid transparent; box-shadow: 0 0 25px rgba(0, 255, 150, 0.35);
            }}

            /* CHART PANELS */
            .chart-panel {{
                position: relative; padding: 22px; border-radius: 20px; overflow: hidden;
                background: linear-gradient(rgba(6, 14, 30, 0.85), rgba(6, 14, 30, 0.85)) padding-box,
                            linear-gradient(137deg, #00ffcc 0%, #0061FF 50%, #a200ff 100%) border-box;
                border: 3px solid transparent;
                box-shadow: 0 0 30px rgba(0, 97, 255, 0.25); margin-bottom: 20px;
            }}
            .chart-panel::after {{
                content: ''; position: absolute;
                top: 0; left: -150%; width: 50%; height: 100%;
                background: linear-gradient(to right, rgba(0,170,255,0) 0%, rgba(0,170,255,0.12) 50%, rgba(0,170,255,0) 100%);
                transform: skewX(-25deg); animation: shine-sweep-slow 7s infinite 2s;
                z-index: 1; pointer-events: none;
            }}
            .chart-panel-title {{
                color: #00ffcc !important; font-size: 1rem !important;
                font-weight: 600 !important; letter-spacing: 2px !important;
                text-transform: uppercase !important; margin: 0 0 15px 0 !important;
                text-shadow: 0 0 10px rgba(0,255,204,0.4) !important;
                position: relative; z-index: 2;
            }}

            /* DETECTION HISTORY PANEL */
            .history-panel {{
                position: relative; padding: 24px; border-radius: 20px; overflow: hidden;
                background: linear-gradient(rgba(4, 10, 22, 0.92), rgba(4, 10, 22, 0.92)) padding-box,
                            linear-gradient(137deg, #a200ff 0%, #0061FF 50%, #00ffcc 100%) border-box;
                border: 3px solid transparent;
                box-shadow: 0 0 35px rgba(162, 0, 255, 0.3); margin-bottom: 20px;
            }}
            .history-panel::after {{
                content: ''; position: absolute;
                top: 0; left: -150%; width: 50%; height: 100%;
                background: linear-gradient(to right, rgba(162,0,255,0) 0%, rgba(162,0,255,0.1) 50%, rgba(162,0,255,0) 100%);
                transform: skewX(-25deg); animation: shine-sweep-slow 9s infinite 3s;
                z-index: 1; pointer-events: none;
            }}
            .history-panel-title {{
                color: #a200ff !important; font-size: 1rem !important;
                font-weight: 600 !important; letter-spacing: 2px !important;
                text-transform: uppercase !important; margin: 0 0 15px 0 !important;
                text-shadow: 0 0 10px rgba(162,0,255,0.5) !important;
                position: relative; z-index: 2;
            }}
            [data-testid="stDataFrame"] th {{
                background: rgba(162, 0, 255, 0.25) !important;
                color: #c560ff !important; font-weight: 700 !important;
                letter-spacing: 1px !important; text-transform: uppercase !important;
                border-bottom: 2px solid rgba(162,0,255,0.5) !important;
            }}
            [data-testid="stDataFrame"] td {{
                color: #e0e0ff !important;
                background: rgba(10, 15, 30, 0.7) !important;
                border-bottom: 1px solid rgba(0, 97, 255, 0.15) !important;
            }}
            [data-testid="stDataFrame"] tr:hover td {{
                background: rgba(162, 0, 255, 0.15) !important;
            }}

            /* ===== ABOUT PAGE STYLES ===== */
            .glow-section-panel {{
                position: relative;
                padding: 28px;
                border-radius: 20px;
                margin-bottom: 25px;
                overflow: hidden;
                background: linear-gradient(rgba(6, 12, 25, 0.88), rgba(6, 12, 25, 0.88)) padding-box,
                            linear-gradient(137deg, #00ffcc 0%, #0061FF 50%, #a200ff 100%) border-box;
                border: 3px solid transparent;
                box-shadow: 0 0 35px rgba(0, 100, 255, 0.2), 0 0 70px rgba(0, 255, 204, 0.08);
                backdrop-filter: blur(15px);
                -webkit-backdrop-filter: blur(15px);
            }}
            .glow-section-panel::after {{
                content: '';
                position: absolute;
                top: 0; left: -150%; width: 50%; height: 100%;
                background: linear-gradient(to right, rgba(0,255,204,0) 0%, rgba(0,255,204,0.1) 50%, rgba(0,255,204,0) 100%);
                transform: skewX(-25deg);
                animation: shine-sweep-slow 8s infinite 2s;
                z-index: 1; pointer-events: none;
            }}
            .glow-section-title {{
                color: #00ffcc !important;
                font-size: 1.2rem !important; font-weight: 600 !important;
                margin: 0 0 18px 0 !important;
                text-shadow: 0 0 10px rgba(0,255,204,0.5) !important;
                letter-spacing: 1.5px; text-transform: uppercase;
                position: relative; z-index: 2;
            }}

            /* Workflow step */
            .workflow-container {{
                display: flex; align-items: center; justify-content: center;
                flex-wrap: wrap; gap: 0; position: relative; z-index: 2;
            }}
            .workflow-step {{
                display: flex; flex-direction: column; align-items: center;
                text-align: center; padding: 16px 12px; min-width: 110px;
            }}
            .workflow-icon-box {{
                width: 70px; height: 70px;
                border-radius: 50%;
                display: flex; align-items: center; justify-content: center;
                font-size: 28px;
                background: linear-gradient(rgba(6,12,25,0.9), rgba(6,12,25,0.9)) padding-box,
                            linear-gradient(137deg, #00ffcc 0%, #0061FF 100%) border-box;
                border: 2px solid transparent;
                box-shadow: 0 0 20px rgba(0,170,255,0.4);
                margin-bottom: 10px;
                position: relative; z-index: 2;
            }}
            .workflow-label {{
                color: #ffffff !important; font-size: 13px !important;
                font-weight: 600 !important; letter-spacing: 0.5px !important;
                text-shadow: none !important;
                position: relative; z-index: 2;
            }}
            .workflow-arrow {{
                color: #00ffcc; font-size: 28px; padding: 0 4px;
                text-shadow: 0 0 10px rgba(0,255,204,0.6);
                align-self: flex-start; margin-top: 20px;
                position: relative; z-index: 2;
            }}

            /* Tech cards */
            .tech-card-wrapper {{
                position: relative; width: 100%;
                margin: 0 auto 16px auto;
                transition: transform 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            }}
            .tech-card-wrapper:hover {{ transform: translateY(-6px); }}
            .tech-card-bg {{
                position: absolute; inset: 0; opacity: 0.7;
                border-radius: 20px; filter: blur(30px);
                z-index: 0; pointer-events: none;
                transition: all 0.35s ease;
            }}
            .tech-card-wrapper:hover .tech-card-bg {{ opacity: 1; filter: blur(40px); }}
            .tech-card-fg {{
                position: relative; border-radius: 20px; z-index: 10;
                border: 2px solid transparent; padding: 18px 16px;
                text-align: center; overflow: hidden;
            }}
            .tech-card-fg::after {{
                content: ''; position: absolute;
                top: 0; left: -150%; width: 50%; height: 100%;
                background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0) 100%);
                transform: skewX(-25deg); animation: shine-sweep 7s infinite;
                z-index: 1; pointer-events: none;
            }}
            .tech-emoji {{ font-size: 30px; margin-bottom: 8px; display: block; position: relative; z-index: 2; }}
            .tech-name {{
                color: #ffffff !important; font-size: 1rem !important;
                font-weight: 700 !important; margin: 0 0 5px 0 !important;
                position: relative; z-index: 2;
            }}
            .tech-desc {{
                color: #9ca3af !important; font-size: 12px !important;
                line-height: 1.4 !important; margin: 0 !important;
                position: relative; z-index: 2;
            }}

            /* Toggle status indicators */
            .status-toggle-row {{
                display: flex; flex-direction: column; gap: 14px;
                position: relative; z-index: 2;
            }}
            .status-toggle-item {{
                display: flex; align-items: center; justify-content: space-between;
                padding: 14px 20px; border-radius: 14px;
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(0, 255, 204, 0.15);
            }}
            .status-toggle-left {{ display: flex; align-items: center; gap: 12px; }}
            .status-dot-on {{
                width: 12px; height: 12px; border-radius: 50%;
                background: #00ffcc;
                box-shadow: 0 0 8px #00ffcc, 0 0 16px rgba(0,255,204,0.4);
                animation: pulse-dot 2s infinite;
            }}
            .status-dot-off {{
                width: 12px; height: 12px; border-radius: 50%;
                background: #555; border: 1px solid #888;
            }}
            @keyframes pulse-dot {{
                0%, 100% {{ box-shadow: 0 0 8px #00ffcc, 0 0 16px rgba(0,255,204,0.4); }}
                50% {{ box-shadow: 0 0 14px #00ffcc, 0 0 28px rgba(0,255,204,0.6); }}
            }}
            .status-toggle-label {{
                color: #ffffff !important; font-size: 14px !important;
                font-weight: 500 !important;
            }}
            .status-badge-on {{
                background: rgba(0,255,204,0.15); color: #00ffcc;
                border: 1px solid rgba(0,255,204,0.4);
                padding: 4px 14px; border-radius: 20px;
                font-size: 12px; font-weight: 700; letter-spacing: 1px;
            }}
            .status-badge-off {{
                background: rgba(100,100,100,0.15); color: #888;
                border: 1px solid rgba(100,100,100,0.3);
                padding: 4px 14px; border-radius: 20px;
                font-size: 12px; font-weight: 700; letter-spacing: 1px;
            }}

            /* Control action buttons */
            .ctrl-btn {{
                display: inline-flex; align-items: center; gap: 10px;
                width: 100%; padding: 14px 20px; border-radius: 14px;
                border: none; cursor: pointer;
                font-size: 14px; font-weight: 700; letter-spacing: 0.5px;
                text-transform: uppercase; transition: all 0.3s ease;
                margin-bottom: 10px; position: relative; overflow: hidden;
            }}

            /* ══════════════════════════════════════════════════
               NEW ENHANCEMENTS — purely visual, zero logic change
               ══════════════════════════════════════════════════ */

            /* ── Animated scanning line across the whole page ── */
            body::before {{
                content: '';
                position: fixed;
                top: -100%;
                left: 0;
                width: 100%;
                height: 2px;
                background: linear-gradient(90deg, transparent, rgba(0,255,204,0.6), transparent);
                animation: scan-line 8s linear infinite;
                z-index: 9999;
                pointer-events: none;
            }}
            @keyframes scan-line {{
                0%   {{ top: -2px; }}
                100% {{ top: 100%; }}
            }}

            /* ── Corner bracket decorations on header ── */
            .cyber-header-box::before {{
                content: '';
                position: absolute;
                top: 12px; left: 12px;
                width: 30px; height: 30px;
                border-top: 3px solid #00ffcc;
                border-left: 3px solid #00ffcc;
                border-radius: 4px 0 0 0;
                z-index: 3;
            }}
            .header-corner-br {{
                position: absolute;
                bottom: 12px; right: 12px;
                width: 30px; height: 30px;
                border-bottom: 3px solid #a200ff;
                border-right: 3px solid #a200ff;
                border-radius: 0 0 4px 0;
                z-index: 3;
            }}
            .header-corner-tr {{
                position: absolute;
                top: 12px; right: 12px;
                width: 30px; height: 30px;
                border-top: 3px solid #00aaff;
                border-right: 3px solid #00aaff;
                border-radius: 0 4px 0 0;
                z-index: 3;
            }}
            .header-corner-bl {{
                position: absolute;
                bottom: 12px; left: 12px;
                width: 30px; height: 30px;
                border-bottom: 3px solid #ff3366;
                border-left: 3px solid #ff3366;
                border-radius: 0 0 0 4px;
                z-index: 3;
            }}

            /* ── Animated blinking cursor on subtitle ── */
            .cyber-cursor {{
                display: inline-block;
                width: 3px;
                height: 1.2em;
                background: #00ffcc;
                margin-left: 4px;
                vertical-align: middle;
                animation: blink-cursor 1s step-end infinite;
            }}
            @keyframes blink-cursor {{
                0%, 100% {{ opacity: 1; }}
                50%       {{ opacity: 0; }}
            }}

            /* ── Live ticker bar ── */
            .ticker-wrapper {{
                width: 100%;
                overflow: hidden;
                background: linear-gradient(rgba(0,5,15,0.9), rgba(0,5,15,0.9)) padding-box,
                            linear-gradient(90deg, #00ffcc, #0061FF, #a200ff, #ff3366) border-box;
                border: 1px solid transparent;
                border-radius: 10px;
                padding: 10px 0;
                margin-bottom: 20px;
                position: relative;
            }}
            .ticker-track {{
                display: flex;
                width: max-content;
                animation: ticker-scroll 35s linear infinite;
                white-space: nowrap;
            }}
            .ticker-item {{
                font-family: 'Share Tech Mono', monospace;
                font-size: 13px;
                color: #00ffcc;
                padding: 0 40px;
                letter-spacing: 1px;
            }}
            .ticker-item span {{
                color: #ff9900 !important;
                margin-right: 6px;
            }}
            @keyframes ticker-scroll {{
                0%   {{ transform: translateX(0); }}
                100% {{ transform: translateX(-50%); }}
            }}

            /* ── Animated stat counter cards (Home page) ── */
            @keyframes count-up {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to   {{ opacity: 1; transform: translateY(0); }}
            }}
            .stat-counter-card {{
                animation: count-up 0.6s ease forwards;
            }}

            /* ── Mission timer badge ── */
            .mission-timer {{
                font-family: 'Share Tech Mono', monospace;
                font-size: 13px;
                color: #00ffcc;
                background: rgba(0,255,204,0.08);
                border: 1px solid rgba(0,255,204,0.25);
                border-radius: 8px;
                padding: 6px 16px;
                letter-spacing: 2px;
                display: inline-block;
                position: relative; z-index: 2;
                text-shadow: 0 0 8px rgba(0,255,204,0.5);
            }}

            /* ── Hexagonal badge decoration ── */
            .hex-badge {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 36px; height: 36px;
                background: linear-gradient(137deg, #00aaff, #a200ff);
                clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
                font-size: 16px;
                margin-right: 10px;
                flex-shrink: 0;
            }}

            /* ── Animated progress bar ── */
            .progress-bar-track {{
                width: 100%;
                height: 6px;
                background: rgba(255,255,255,0.08);
                border-radius: 3px;
                overflow: hidden;
                margin-top: 8px;
            }}
            .progress-bar-fill {{
                height: 100%;
                border-radius: 3px;
                animation: progress-grow 2s ease-out forwards;
                transform-origin: left;
            }}
            @keyframes progress-grow {{
                from {{ width: 0%; }}
            }}

            /* ── Glowing separator ── */
            .glow-divider {{
                height: 1px;
                background: linear-gradient(90deg, transparent, #00ffcc, #0061FF, #a200ff, transparent);
                margin: 24px 0;
                opacity: 0.5;
            }}

            /* ── Particle dots background on hero ── */
            .particle-dot {{
                position: absolute;
                border-radius: 50%;
                background: rgba(0,255,204,0.4);
                animation: float-particle linear infinite;
            }}
            @keyframes float-particle {{
                0%   {{ transform: translateY(0) scale(1);   opacity: 0.8; }}
                50%  {{ transform: translateY(-20px) scale(1.3); opacity: 0.4; }}
                100% {{ transform: translateY(0) scale(1);   opacity: 0.8; }}
            }}

            /* ── Typewriter text ── */
            .typewriter {{
                overflow: hidden;
                white-space: nowrap;
                border-right: 2px solid #00ffcc;
                width: fit-content;
                animation: type-text 3s steps(40) 0.5s forwards, blink-cursor 0.75s step-end infinite;
                font-family: 'Share Tech Mono', monospace;
                color: #a0e0ff !important;
                font-size: 0.95rem !important;
                letter-spacing: 2px;
                margin: 10px auto 0 auto;
                position: relative; z-index: 2;
            }}
            @keyframes type-text {{
                from {{ width: 0; }}
                to   {{ width: 100%; }}
            }}

            /* ── Pulse ring on status dots ── */
            .pulse-ring {{
                display: inline-block;
                position: relative;
                width: 12px; height: 12px;
            }}
            .pulse-ring::after {{
                content: '';
                position: absolute;
                top: -4px; left: -4px;
                width: 20px; height: 20px;
                border-radius: 50%;
                border: 1px solid #00ffcc;
                animation: ring-expand 2s ease-out infinite;
                opacity: 0;
            }}
            @keyframes ring-expand {{
                0%   {{ transform: scale(0.8); opacity: 0.8; }}
                100% {{ transform: scale(2);   opacity: 0; }}
            }}

            /* ── Version badge ── */
            .version-badge {{
                font-family: 'Share Tech Mono', monospace;
                font-size: 11px;
                color: #a200ff;
                background: rgba(162,0,255,0.1);
                border: 1px solid rgba(162,0,255,0.3);
                border-radius: 20px;
                padding: 3px 12px;
                letter-spacing: 1px;
                display: inline-block;
                position: relative; z-index: 2;
                margin-left: 10px;
            }}

            /* ── Scanline grid overlay ── */
            .scanline-grid {{
                position: absolute;
                inset: 0;
                background-image:
                    linear-gradient(rgba(0,255,204,0.03) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(0,255,204,0.03) 1px, transparent 1px);
                background-size: 40px 40px;
                z-index: 1;
                pointer-events: none;
                border-radius: inherit;
            }}

            /* ── Uptime counter ── */
            .uptime-strip {{
                display: flex;
                align-items: center;
                gap: 24px;
                padding: 14px 24px;
                background: rgba(0,0,0,0.4);
                border-radius: 12px;
                border: 1px solid rgba(0,170,255,0.2);
                margin-bottom: 20px;
                flex-wrap: wrap;
            }}
            .uptime-item {{
                display: flex;
                align-items: center;
                gap: 8px;
                font-family: 'Share Tech Mono', monospace;
                font-size: 13px;
                color: #a0c8ff;
                letter-spacing: 0.5px;
            }}
            .uptime-dot {{
                width: 8px; height: 8px; border-radius: 50%;
                background: #00ffcc;
                box-shadow: 0 0 6px #00ffcc;
                animation: pulse-dot 2s infinite;
                flex-shrink: 0;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.error(f"Background image not found at: {image_path}.")

set_background("bg1.jpeg")

# ── ENHANCED HEADER with corner brackets, typewriter & version badge ──────────
st.markdown("""
    <div class="cyber-header-box">
        <div class="scanline-grid"></div>
        <div class="header-corner-br"></div>
        <div class="header-corner-tr"></div>
        <div class="header-corner-bl"></div>
        <!-- particle dots -->
        <div class="particle-dot" style="width:6px;height:6px;top:20%;left:8%;animation-duration:4s;animation-delay:0s;"></div>
        <div class="particle-dot" style="width:4px;height:4px;top:60%;left:15%;animation-duration:5s;animation-delay:1s;"></div>
        <div class="particle-dot" style="width:5px;height:5px;top:30%;right:10%;animation-duration:6s;animation-delay:0.5s;"></div>
        <div class="particle-dot" style="width:3px;height:3px;top:70%;right:18%;animation-duration:4.5s;animation-delay:2s;"></div>
        <div class="particle-dot" style="width:4px;height:4px;top:15%;left:45%;animation-duration:5.5s;animation-delay:1.5s;background:rgba(162,0,255,0.5);"></div>
        <h1 class="cyber-title">AI-Powered Autonomous Airport Safety Vehicle</h1>
        <h3 class="cyber-subtitle">
            AeroGuard Master
            <span class="version-badge">v2.4.1</span>
            <span class="cyber-cursor"></span>
        </h3>
        <div class="typewriter">INITIALIZING PATROL SYSTEMS — ALL MODULES OPERATIONAL</div>
    </div>
    """, unsafe_allow_html=True)

# ── LIVE TICKER BAR ───────────────────────────────────────────────────────────
st.markdown("""
<div class="ticker-wrapper">
  <div class="ticker-track">
    <span class="ticker-item"><span>●</span> RUNWAY 3L — CLEAR</span>
    <span class="ticker-item"><span>▲</span> DETECTIONS TODAY: 128</span>
    <span class="ticker-item"><span>●</span> AI MODEL: YOLOV8 ACTIVE</span>
    <span class="ticker-item"><span>▲</span> GPS LOCK: CONFIRMED</span>
    <span class="ticker-item"><span>●</span> TAXIWAY B — CLEAR</span>
    <span class="ticker-item"><span>▲</span> ACCURACY: 96.2%</span>
    <span class="ticker-item"><span>●</span> CARGO ZONE — MONITORED</span>
    <span class="ticker-item"><span>▲</span> ALERT LEVEL: NOMINAL</span>
    <span class="ticker-item"><span>●</span> VOICE ENGINE: ONLINE</span>
    <span class="ticker-item"><span>▲</span> RESPONSE TIME: 1.2s</span>
    <!-- duplicate for seamless loop -->
    <span class="ticker-item"><span>●</span> RUNWAY 3L — CLEAR</span>
    <span class="ticker-item"><span>▲</span> DETECTIONS TODAY: 128</span>
    <span class="ticker-item"><span>●</span> AI MODEL: YOLOV8 ACTIVE</span>
    <span class="ticker-item"><span>▲</span> GPS LOCK: CONFIRMED</span>
    <span class="ticker-item"><span>●</span> TAXIWAY B — CLEAR</span>
    <span class="ticker-item"><span>▲</span> ACCURACY: 96.2%</span>
    <span class="ticker-item"><span>●</span> CARGO ZONE — MONITORED</span>
    <span class="ticker-item"><span>▲</span> ALERT LEVEL: NOMINAL</span>
    <span class="ticker-item"><span>●</span> VOICE ENGINE: ONLINE</span>
    <span class="ticker-item"><span>▲</span> RESPONSE TIME: 1.2s</span>
  </div>
</div>
""", unsafe_allow_html=True)

nav_container = st.container()

with nav_container:
    left_space, center_nav, right_space = st.columns([1, 4, 1])

    with center_nav:
        app_mode = st.radio(
            "Select Module:",
            [
                "🏠 Home Page",
                "📹 Live Detection & Monitoring",
                "📊 Alerts & Analytics Page",
                "⚙️ About & System Control Page"
            ],
            horizontal=True,
            label_visibility="collapsed"
        )

@st.cache_resource
def load_ai_model():
    return YOLO('yolov8n.pt')

groq_client = Groq(api_key="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")

# ── THREAD-SAFE SHARED STATE ─────────────────────────────────────────────────
# Uses a module-level dict (created once per interpreter process) plus a Queue
# so the audio daemon thread can push state updates that the vision loop picks
# up each frame — surviving Streamlit's per-rerun script re-execution.
import queue as _queue

if "_aeroguard_state" not in dir():
    _aeroguard_state = {
        "system_status":    "STANDBY - Awaiting Wake Word",
        "latest_command":   "IDLE",
        "intended_trajectory": "IDLE",
        "gps_lat":          40.6413,
        "gps_lon":          -73.7781,
        "last_spoken":      "",          # last verbal response for HUD display
        "voice_active":     False,       # True while audio thread has wake-word
    }
def audio_engine():
    global system_status, latest_command, intended_trajectory # <--- Access memory
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.energy_threshold = 300
    recognizer.pause_threshold = 0.8

# Module-level queues for communication between audio and vision threads
_voice_queue = _queue.Queue()        # audio thread → vision loop updates
_speak_queue = _queue.Queue()        # audio thread → speak requests (UI feedback)

# Convenience aliases so the rest of the code reads naturally
def _get(key):
    return _aeroguard_state[key]

def _set(key, value):
    _aeroguard_state[key] = value

# Legacy global names — kept so any other part of the code that reads them works
system_status      = _aeroguard_state["system_status"]
latest_command     = _aeroguard_state["latest_command"]
intended_trajectory= _aeroguard_state["intended_trajectory"]
gps_lat            = _aeroguard_state["gps_lat"]
gps_lon            = _aeroguard_state["gps_lon"]

VOICE_PROFILE  = "en-IN-NeerjaNeural"
TARGET_CLASSES = [0, 2, 4, 7, 24, 28] 
VIDEO_PLAYLIST = ['test_cargo.f399.mp4', 'test_etihad.f137.mp4', 'test_ramp.f401.mp4']
pygame.mixer.init()

async def generate_audio(text, filename):
    communicate = edge_tts.Communicate(text, VOICE_PROFILE)
    await communicate.save(filename)

def _speak_sync(text):
    unique_audio_file = f"speech_{uuid.uuid4().hex}.mp3"
    print(f"\n🔊 [AEROGUARD]: {text}")
    asyncio.run(generate_audio(text, unique_audio_file))
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    try:
        pygame.mixer.music.load(unique_audio_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
    except Exception:
        pass
    finally:
        if os.path.exists(unique_audio_file):
            try:
                os.remove(unique_audio_file)
            except:
                pass

def speak(text):
    threading.Thread(target=_speak_sync, args=(text,), daemon=True).start()

def extract_intent(spoken_text):
    print(f"\n🧠 [GROQ LLM] >> Analyzing context: '{spoken_text}'...")
    system_prompt = """
    You are the brain of an autonomous airport rover. 
    Analyze the user's command and output a pure JSON object.
    You must extract two things:
    1. "ui_action": MUST be exactly one of: [MOVE_FORWARD, MOVE_BACKWARD, TURN_LEFT, TURN_RIGHT, EMERGENCY_STOP, SLEEP_MODE, IDLE, UNKNOWN].
    2. "verbal_response": A cool, professional, robotic confirmation sentence.
    ONLY output valid JSON. No markdown formatting, no other text.
    """
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": spoken_text}],
            model="llama-3.1-8b-instant",
            temperature=0.0,
        )
        response_text = chat_completion.choices[0].message.content.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()
        return json.loads(response_text)
    except Exception as e:
        print(f"[GROQ ERROR]: {e}")
        return {"ui_action": "UNKNOWN", "verbal_response": "Error reaching LLM server."}

def audio_engine():
    """
    Runs forever in a daemon thread.
    Writes ALL state updates into _aeroguard_state (module-level dict that
    survives Streamlit reruns) AND pushes them onto _voice_queue so the
    vision loop can pick them up immediately within the same frame.
    Also pushes verbal responses onto _speak_queue so the vision loop
    can display on-screen feedback even when it can't call speak() directly.
    """
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = False
    recognizer.energy_threshold = 300
    recognizer.pause_threshold = 0.8
    print("\n🎙️ [AUDIO THREAD] >> Booted and listening in background...")

    def _push(status=None, command=None, trajectory=None, verbal=None):
        """Push a state-change packet onto the queue and into the shared dict."""
        update = {}
        if status is not None:
            _aeroguard_state["system_status"] = status
            update["system_status"] = status
        if command is not None:
            _aeroguard_state["latest_command"] = command
            update["latest_command"] = command
        if trajectory is not None:
            _aeroguard_state["intended_trajectory"] = trajectory
            update["intended_trajectory"] = trajectory
        if verbal is not None:
            _aeroguard_state["last_spoken"] = verbal
            update["last_spoken"] = verbal
        if update:
            _voice_queue.put(update)
        if verbal:
            _speak_queue.put(verbal)

    with sr.Microphone() as source:
        print("🎧 Calibrating microphone for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print(f"✅ Energy Threshold Set To: {recognizer.energy_threshold}")

        while True:
            try:
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=4)
                spoken_text = recognizer.recognize_google(audio).lower()
                print(f"🎤Heard wake audio {spoken_text}")
                if "system online" in spoken_text:
                    _push(status="SYSTEM ONLINE - Awaiting Command",
                          verbal="System online. Diagnostics green. Ready for command.")
                    _aeroguard_state["voice_active"] = True
                    speak("System online. Diagnostics green. Ready for command.")
                    while True:
                        try:
                            audio_cmd = recognizer.listen(source, timeout=10, phrase_time_limit=10)
                            command_text = recognizer.recognize_google(audio_cmd).lower()
                            print(f"🎤 Command detected: {command_text}")
                            command_json = extract_intent(command_text)
                            action   = command_json.get("ui_action", "UNKNOWN")
                            response = command_json.get("verbal_response", "Acknowledged.")
                            print(f"🤖 [LLM] Action={action} | Response={response}")
                            if action == "SLEEP_MODE":
                                _push(status="STANDBY - Awaiting Wake Word",
                                      command="IDLE", trajectory="IDLE",
                                      verbal="Entering standby mode.")
                                _aeroguard_state["voice_active"] = False
                                speak("Entering standby mode.")
                                break
                            elif action != "UNKNOWN":
                                _push(command=action, trajectory=action, verbal=response)
                                speak(response)
                            else:
                                _push(verbal=response)
                                speak(response)
                        except sr.WaitTimeoutError:
                            pass
                        except sr.UnknownValueError:
                            print("❌ Could not understand audio")
                        except sr.RequestError:
                            break
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                print(f"❌ Speech API error: {e}")

def vision_engine():
    st.markdown("### 🎛️ Live Vision Engine Controls")

    if "run_vision" not in st.session_state:
        st.session_state.run_vision = False
    if "use_webcam" not in st.session_state:
        st.session_state.use_webcam = False

    if not st.session_state.run_vision:
        btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 4])
        with btn_col1:
            start_btn = st.button("▶️ START SYSTEM", type="primary", use_container_width=True)
        with btn_col2:
            webcam_toggle = st.toggle("📷 Use Webcam", value=st.session_state.use_webcam)
            st.session_state.use_webcam = webcam_toggle
        stop_btn = False
        if start_btn:
            st.session_state.run_vision = True
            st.rerun()
    else:
        btn_col1, btn_col2 = st.columns([1, 5])
        with btn_col1:
            stop_btn = st.button("🛑 STOP SYSTEM", type="primary", use_container_width=True)
        start_btn = False
        if stop_btn:
            st.session_state.run_vision = False
            st.rerun()

    video_placeholder  = st.empty()
    status_text        = st.empty()
    # ── NEW: live voice-command feedback panel below the video ──
    voice_hud          = st.empty()

    if not st.session_state.run_vision:
        status_text.info("System is offline. Press 'START SYSTEM' to initialize AI and Video Feed.")
        return

    status_text.warning("Initializing AI Models from Cache Memory...")
    model = load_ai_model()

    cap = None
    using_webcam = False

    if st.session_state.use_webcam:
        status_text.warning("🔍 Detecting webcam...")
        test_cap = cv2.VideoCapture(0)
        if test_cap.isOpened():
            ret, _ = test_cap.read()
            if ret:
                cap = test_cap
                using_webcam = True
                status_text.success("📷 Webcam detected — streaming live camera feed.")
            else:
                test_cap.release()
                status_text.warning("⚠️ Webcam found but no frames received. Falling back to video playlist...")
        else:
            test_cap.release()
            status_text.warning("⚠️ No webcam available. Falling back to video playlist...")
            time.sleep(1)

    if not using_webcam:
        valid_playlist = [vid for vid in VIDEO_PLAYLIST if os.path.exists(vid)]
        if not valid_playlist:
            status_text.error("❌ CRITICAL ERROR: No webcam detected and no valid `.mp4` video files found.")
            st.session_state.run_vision = False
            return
        video_index = 0
        cap = cv2.VideoCapture(valid_playlist[video_index])
        status_text.success(f"🎥 Streaming Video Feed: {valid_playlist[video_index]}")

    smooth_x, smooth_y, smooth_radius = 0.0, 0.0, 20.0
    prev_time   = time.time()
    # Tracks the last verbal response shown in the HUD so we only redraw on change
    _last_hud_spoken   = ""
    _last_hud_cmd      = ""
    _last_hud_status   = ""
    _hud_shown_at      = 0.0   # timestamp; fade response text after 6 seconds

    while st.session_state.run_vision:

        # ── DRAIN VOICE QUEUE — pick up every update the audio thread pushed ──
        while not _voice_queue.empty():
            try:
                update = _voice_queue.get_nowait()
                # Merge into the shared state (already done in audio_engine,
                # but draining ensures we notice the change immediately)
                for k, v in update.items():
                    _aeroguard_state[k] = v
            except Exception:
                pass

        # ── READ LIVE STATE — always from the shared dict, never stale globals ──
        latest_command      = _aeroguard_state["latest_command"]
        intended_trajectory = _aeroguard_state["intended_trajectory"]
        system_status       = _aeroguard_state["system_status"]
        gps_lat             = _aeroguard_state["gps_lat"]
        gps_lon             = _aeroguard_state["gps_lon"]
        last_spoken         = _aeroguard_state["last_spoken"]
        voice_active        = _aeroguard_state["voice_active"]

        # ── UPDATE GPS based on current command ──
        if latest_command in ["MOVE_FORWARD", "MOVE_BACKWARD", "TURN_LEFT", "TURN_RIGHT"]:
            _aeroguard_state["gps_lat"] += 0.00002 if latest_command == "MOVE_FORWARD" else -0.00002
            _aeroguard_state["gps_lon"] += 0.00001 if latest_command == "TURN_RIGHT"   else -0.00001
            gps_lat = _aeroguard_state["gps_lat"]
            gps_lon = _aeroguard_state["gps_lon"]

        # ── VIDEO FRAME ──
        success, frame = cap.read()
        if not success:
            if using_webcam:
                status_text.error("📷 Webcam feed lost. Stopping system.")
                st.session_state.run_vision = False
                break
            else:
                video_index = (video_index + 1) % len(valid_playlist)
                cap.release()
                cap = cv2.VideoCapture(valid_playlist[video_index])
                status_text.success(f"🎥 Streaming Video Feed: {valid_playlist[video_index]}")
                continue

        frame = cv2.resize(frame, (1280, 720))
        h, w, _ = frame.shape
        curr_time  = time.time()
        actual_fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
        prev_time  = curr_time

        results         = model(frame, conf=0.5, classes=TARGET_CLASSES, verbose=False)
        annotated_frame = results[0].plot()

        feed_label = "WEBCAM: LIVE FEED" if using_webcam else f"PLAYLIST ({valid_playlist[video_index]})"
        cv2.putText(annotated_frame, f"FEED: {feed_label}",               (20, 30),  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(annotated_frame, f"STATUS: {system_status}",           (20, 65),  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0),   2)
        cv2.putText(annotated_frame, f"LAST CMD: {latest_command.upper()}",(20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        telemetry_y = h - 120
        cv2.putText(annotated_frame, f"FPS: {int(actual_fps)}", (20, telemetry_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
        battery      = psutil.sensors_battery()
        battery_level= battery.percent if battery else 100.0
        power_status = ("[AC]" if battery.power_plugged else "[BATT]") if battery else "[AC]"
        bat_color    = (0, 255, 0) if battery_level > 20 else (0, 0, 255)
        cv2.putText(annotated_frame, f"PWR: {battery_level:.0f}% {power_status}", (20, telemetry_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, bat_color, 2)
        cv2.putText(annotated_frame, f"GPS: {gps_lat:.5f}, {gps_lon:.5f}",        (20, telemetry_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 0), 2)

        # ── VOICE ACTIVE indicator on frame ──
        mic_color = (0, 255, 150) if voice_active else (80, 80, 80)
        mic_label = "🎙 VOICE: ACTIVE" if voice_active else "🎙 VOICE: SAY 'SYSTEM ONLINE'"
        cv2.putText(annotated_frame, mic_label, (w - 520, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, mic_color, 2)

        cx, cy = w // 2, h - 100
        target_x, target_y, target_radius = 0.0, 0.0, 20.0
        hud_color = (150, 150, 150)
        hud_text  = "MOTORS IDLE"
        if latest_command == "MOVE_FORWARD":
            target_y, target_radius, hud_color, hud_text = -40.0, 60.0, (0, 255, 0),   "THROTTLE: FWD"
        elif latest_command == "MOVE_BACKWARD":
            target_y, target_radius, hud_color, hud_text = 40.0,  60.0, (0, 165, 255), "THROTTLE: REV"
        elif latest_command == "TURN_LEFT":
            target_x, target_radius, hud_color, hud_text = -40.0, 60.0, (255, 255, 0), "STEERING: LEFT"
        elif latest_command == "TURN_RIGHT":
            target_x, target_radius, hud_color, hud_text = 40.0,  60.0, (255, 255, 0), "STEERING: RIGHT"
        elif latest_command == "EMERGENCY_STOP":
            target_radius, hud_color, hud_text = 55.0, (0, 0, 255), "BRAKES ENGAGED"

        smooth_x      += (target_x      - smooth_x)      * 0.12
        smooth_y      += (target_y      - smooth_y)      * 0.12
        smooth_radius += (target_radius - smooth_radius)  * 0.12

        if latest_command == "EMERGENCY_STOP":
            cv2.circle(annotated_frame, (cx, cy), int(smooth_radius), (0, 0, 255), -1)
        else:
            cv2.circle(annotated_frame, (cx, cy), int(smooth_radius), (50, 50, 50),    -1)
            cv2.circle(annotated_frame, (cx, cy), int(smooth_radius), (255, 255, 255),  2)
        if abs(smooth_x) > 0.5 or abs(smooth_y) > 0.5:
            cv2.arrowedLine(annotated_frame, (cx, cy), (int(cx + smooth_x), int(cy + smooth_y)), hud_color, 7, tipLength=0.4)
        cv2.putText(annotated_frame, hud_text, (cx - 80, cy - 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, hud_color, 2)

        # ── RADAR ──
        radar_radius = 100
        radar_cx, radar_cy = w - radar_radius - 20, radar_radius + 20
        cv2.circle(annotated_frame, (radar_cx, radar_cy), radar_radius, (0, 30, 0), -1)
        cv2.circle(annotated_frame, (radar_cx, radar_cy), radar_radius, (0, 255, 0),  2)
        cv2.line(annotated_frame, (radar_cx, radar_cy - radar_radius), (radar_cx, radar_cy + radar_radius), (0, 100, 0), 1)
        cv2.line(annotated_frame, (radar_cx - radar_radius, radar_cy), (radar_cx + radar_radius, radar_cy), (0, 100, 0), 1)
        cv2.circle(annotated_frame, (radar_cx, radar_cy), 4, (0, 255, 0), -1)

        path_clear    = True
        evasion_action= None
        threat_name   = ""
        for box in results[0].boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            obj_cx = (x1 + x2) / 2
            obj_cy = y2
            map_x  = int(((obj_cx / w) - 0.5) * (radar_radius * 2))
            map_y  = int(-1 * (radar_radius - ((obj_cy / h) * radar_radius)))
            if (map_x**2 + map_y**2) <= radar_radius**2:
                cv2.circle(annotated_frame, (radar_cx + map_x, radar_cy + map_y), 4, (0, 0, 255), -1)
            if intended_trajectory not in ["IDLE", "EMERGENCY_STOP", "SLEEP_MODE"] and path_clear:
                box_height   = y2 - y1
                height_ratio = box_height / h
                class_id     = int(box.cls[0].item())
                brake_threshold = 0.6 if class_id in [0, 2, 4, 7] else 0.4
                if height_ratio > brake_threshold:
                    path_clear     = False
                    threat_name    = model.names[class_id]
                    screen_center_left  = w * 0.33
                    screen_center_right = w * 0.66
                    if obj_cx < screen_center_left:
                        evasion_action = "TURN_RIGHT"
                    elif obj_cx > screen_center_right:
                        evasion_action = "TURN_LEFT"
                    else:
                        evasion_action = "EMERGENCY_STOP"

        if not path_clear:
            if _aeroguard_state["latest_command"] != evasion_action:
                _aeroguard_state["latest_command"] = evasion_action
                if evasion_action == "EMERGENCY_STOP":
                    msg = f"Critical proximity. Brakes engaged to avoid {threat_name}."
                else:
                    dir_text = "right" if evasion_action == "TURN_RIGHT" else "left"
                    msg = f"Proximity alert. Dodging {dir_text} to avoid {threat_name}."
                _aeroguard_state["last_spoken"] = msg
                speak(msg)
        else:
            if _aeroguard_state["latest_command"] != _aeroguard_state["intended_trajectory"]:
                _aeroguard_state["latest_command"] = _aeroguard_state["intended_trajectory"]
                if _aeroguard_state["intended_trajectory"] not in ["IDLE", "EMERGENCY_STOP", "SLEEP_MODE"]:
                    msg = "Path clear. Resuming original trajectory."
                    _aeroguard_state["last_spoken"] = msg
                    speak(msg)

        video_placeholder.image(annotated_frame, channels="BGR", use_container_width=True)

        # ── VOICE FEEDBACK HUD (Streamlit panel below video) ──
        current_cmd    = _aeroguard_state["latest_command"]
        current_status = _aeroguard_state["system_status"]
        current_spoken = _aeroguard_state["last_spoken"]

        # Only re-render the panel when something actually changed
        state_changed = (current_cmd    != _last_hud_cmd or
                         current_status != _last_hud_status or
                         current_spoken != _last_hud_spoken)
        if current_spoken != _last_hud_spoken:
            _hud_shown_at = time.time()

        if state_changed:
            _last_hud_cmd    = current_cmd
            _last_hud_status = current_status
            _last_hud_spoken = current_spoken

            cmd_color_map = {
                "MOVE_FORWARD":  ("#00ff87", "▲ MOVE FORWARD"),
                "MOVE_BACKWARD": ("#ff9900", "▼ MOVE BACKWARD"),
                "TURN_LEFT":     ("#ffff00", "◄ TURN LEFT"),
                "TURN_RIGHT":    ("#ffff00", "► TURN RIGHT"),
                "EMERGENCY_STOP":("#ff3366", "⛔ EMERGENCY STOP"),
                "IDLE":          ("#9ca3af", "— IDLE"),
                "UNKNOWN":       ("#ff9900", "? UNKNOWN"),
            }
            cmd_hex, cmd_label = cmd_color_map.get(current_cmd, ("#9ca3af", f"— {current_cmd}"))

            voice_status_color = "#00ffcc" if voice_active else "#555555"
            voice_status_text  = "🎙 VOICE ACTIVE — AWAITING COMMAND" if voice_active else "🎙 SAY 'SYSTEM ONLINE' TO ACTIVATE VOICE"

            # Show verbal response for 6 seconds, then clear
            spoken_html = ""
            if current_spoken and (time.time() - _hud_shown_at) < 6.0:
                spoken_html = f"""
                <div style="display:flex;align-items:center;gap:10px;margin-top:10px;
                            background:rgba(0,170,255,0.08);border:1px solid rgba(0,170,255,0.3);
                            border-radius:10px;padding:10px 16px;">
                    <span style="font-size:18px;">🔊</span>
                    <span style="font-family:'Share Tech Mono',monospace;font-size:13px;
                                 color:#a0e0ff;letter-spacing:0.5px;">
                        "{current_spoken}"
                    </span>
                </div>"""

            voice_hud.markdown(f"""
            <div style="
                background: linear-gradient(rgba(4,9,20,0.92), rgba(4,9,20,0.92)) padding-box,
                            linear-gradient(137deg, #00ffcc 0%, #0061FF 50%, #a200ff 100%) border-box;
                border: 2px solid transparent;
                border-radius: 16px;
                padding: 16px 22px;
                margin-top: 10px;
                backdrop-filter: blur(12px);
                box-shadow: 0 0 25px rgba(0,170,255,0.2);
            ">
                <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
                    <!-- Voice status -->
                    <div style="display:flex;align-items:center;gap:10px;">
                        <div style="width:10px;height:10px;border-radius:50%;
                                    background:{voice_status_color};
                                    box-shadow:0 0 8px {voice_status_color};
                                    animation:pulse-dot 2s infinite;"></div>
                        <span style="font-family:'Share Tech Mono',monospace;font-size:13px;
                                     color:{voice_status_color};letter-spacing:1px;">
                            {voice_status_text}
                        </span>
                    </div>
                    <!-- System status -->
                    <div style="font-family:'Share Tech Mono',monospace;font-size:12px;
                                color:#9ca3af;letter-spacing:0.5px;">
                        STATUS: <span style="color:#00aaff;">{current_status}</span>
                    </div>
                    <!-- Active command badge -->
                    <div style="background:rgba(0,0,0,0.4);border:1px solid {cmd_hex};
                                border-radius:8px;padding:6px 16px;">
                        <span style="font-family:'Audiowide',cursive;font-size:14px;
                                     color:{cmd_hex};text-shadow:0 0 8px {cmd_hex}88;
                                     letter-spacing:1px;">
                            CMD: {cmd_label}
                        </span>
                    </div>
                </div>
                {spoken_html}
            </div>
            """, unsafe_allow_html=True)

        time.sleep(0.02)

    if cap:
        cap.release()

# PAGE ROUTING
if app_mode == "🏠 Home Page":

    # ── Uptime strip ──────────────────────────────────────────────────────
    st.markdown("""
    <div class="uptime-strip">
        <div class="uptime-item"><div class="uptime-dot"></div> MISSION UPTIME: <strong style="color:#00ffcc;">04:22:17</strong></div>
        <div class="uptime-item"><div class="uptime-dot" style="background:#00aaff;box-shadow:0 0 6px #00aaff;"></div> LAST PATROL: <strong style="color:#00aaff;">RWY-3L → APRON-A</strong></div>
        <div class="uptime-item"><div class="uptime-dot" style="background:#a200ff;box-shadow:0 0 6px #a200ff;"></div> OBJECTS TRACKED: <strong style="color:#a200ff;">128</strong></div>
        <div class="uptime-item"><div class="uptime-dot" style="background:#ff9900;box-shadow:0 0 6px #ff9900;"></div> ACTIVE ALERTS: <strong style="color:#ff9900;">2</strong></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 💠 System Overview")
    col1, col2, col3, col4 = st.columns(4)
    with col1: 
        st.markdown('''
        <div class="glow-card-wrapper">
            <div class="glow-card-bg" style="background: linear-gradient(137deg, #FF3D77 0%, #FFB1CE 45%, #FF9D3C 100%);"></div>
            <div class="glow-card-fg" style="background: linear-gradient(#1A1A1C, #1A1A1C) padding-box, linear-gradient(137deg, #FF3D77 0%, #FFB1CE 45%, #FF9D3C 100%) border-box;">
                <div><div class="glow-card-icon">🧠</div>
                <h3 class="glow-card-title">AI Model</h3>
                <p class="glow-card-desc">Hardware setup built for power, ensuring durable and silent inference.</p></div>
                <div>
                    <p style="color:#00ffcc !important; font-weight:bold; margin:0 0 6px 0; position:relative; z-index:2;">✅ Active</p>
                    <div class="progress-bar-track"><div class="progress-bar-fill" style="width:92%;background:linear-gradient(90deg,#FF3D77,#FF9D3C);"></div></div>
                </div>
            </div>
        </div>''', unsafe_allow_html=True)
    with col2: 
        st.markdown('''
        <div class="glow-card-wrapper">
            <div class="glow-card-bg" style="background: linear-gradient(137deg, #FFFFFF 0%, #7DD3FC 45%, #06B6D4 100%);"></div>
            <div class="glow-card-fg" style="background: linear-gradient(#1A1A1C, #1A1A1C) padding-box, linear-gradient(137deg, #FFFFFF 0%, #7DD3FC 45%, #06B6D4 100%) border-box;">
                <div><div class="glow-card-icon">📹</div>
                <h3 class="glow-card-title">Camera</h3>
                <p class="glow-card-desc">Studio-grade hub defining every single pixel for optimal clarity.</p></div>
                <div>
                    <p style="color:#00ffcc !important; font-weight:bold; margin:0 0 6px 0; position:relative; z-index:2;">🎥 Online</p>
                    <div class="progress-bar-track"><div class="progress-bar-fill" style="width:100%;background:linear-gradient(90deg,#7DD3FC,#06B6D4);"></div></div>
                </div>
            </div>
        </div>''', unsafe_allow_html=True)
    with col3: 
        st.markdown('''
        <div class="glow-card-wrapper">
            <div class="glow-card-bg" style="background: linear-gradient(137deg, #4361EE 0%, #E0AEFF 45%, #F72585 100%);"></div>
            <div class="glow-card-fg" style="background: linear-gradient(#1A1A1C, #1A1A1C) padding-box, linear-gradient(137deg, #4361EE 0%, #E0AEFF 45%, #F72585 100%) border-box;">
                <div><div class="glow-card-icon">🔊</div>
                <h3 class="glow-card-title">Voice System</h3>
                <p class="glow-card-desc">Dynamic motion algorithms bridging the gap between views and code.</p></div>
                <div>
                    <p style="color:#00ffcc !important; font-weight:bold; margin:0 0 6px 0; position:relative; z-index:2;">🔊 Ready</p>
                    <div class="progress-bar-track"><div class="progress-bar-fill" style="width:88%;background:linear-gradient(90deg,#4361EE,#F72585);"></div></div>
                </div>
            </div>
        </div>''', unsafe_allow_html=True)
    with col4: 
        st.markdown('''
        <div class="glow-card-wrapper">
            <div class="glow-card-bg" style="background: linear-gradient(137deg, #00FF87 0%, #60EFFF 45%, #0061FF 100%);"></div>
            <div class="glow-card-fg" style="background: linear-gradient(#1A1A1C, #1A1A1C) padding-box, linear-gradient(137deg, #00FF87 0%, #60EFFF 45%, #0061FF 100%) border-box;">
                <div><div class="glow-card-icon">🚙</div>
                <h3 class="glow-card-title">AGV Status</h3>
                <p class="glow-card-desc">Real-time locomotion status checking hazard arrays continuously.</p></div>
                <div>
                    <p style="color:#ff3366 !important; font-weight:bold; margin:0 0 6px 0; position:relative; z-index:2;">🚨 Patrol</p>
                    <div class="progress-bar-track"><div class="progress-bar-fill" style="width:76%;background:linear-gradient(90deg,#00FF87,#0061FF);"></div></div>
                </div>
            </div>
        </div>''', unsafe_allow_html=True)

    st.write("")

    # ── Mini stat counters row ────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex; gap:14px; margin-bottom:20px; flex-wrap:wrap;">
        <div class="stat-counter-card" style="flex:1;min-width:140px;background:rgba(0,170,255,0.08);border:1px solid rgba(0,170,255,0.25);border-radius:14px;padding:16px;text-align:center;animation-delay:0.1s;">
            <div style="font-family:'Audiowide',cursive;font-size:2rem;color:#00aaff;text-shadow:0 0 12px rgba(0,170,255,0.6);">128</div>
            <div style="font-size:11px;color:#9ca3af;letter-spacing:1.5px;text-transform:uppercase;margin-top:4px;">Detections</div>
        </div>
        <div class="stat-counter-card" style="flex:1;min-width:140px;background:rgba(0,255,204,0.08);border:1px solid rgba(0,255,204,0.25);border-radius:14px;padding:16px;text-align:center;animation-delay:0.2s;">
            <div style="font-family:'Audiowide',cursive;font-size:2rem;color:#00ffcc;text-shadow:0 0 12px rgba(0,255,204,0.6);">96%</div>
            <div style="font-size:11px;color:#9ca3af;letter-spacing:1.5px;text-transform:uppercase;margin-top:4px;">Accuracy</div>
        </div>
        <div class="stat-counter-card" style="flex:1;min-width:140px;background:rgba(162,0,255,0.08);border:1px solid rgba(162,0,255,0.25);border-radius:14px;padding:16px;text-align:center;animation-delay:0.3s;">
            <div style="font-family:'Audiowide',cursive;font-size:2rem;color:#a200ff;text-shadow:0 0 12px rgba(162,0,255,0.6);">1.2s</div>
            <div style="font-size:11px;color:#9ca3af;letter-spacing:1.5px;text-transform:uppercase;margin-top:4px;">Response</div>
        </div>
        <div class="stat-counter-card" style="flex:1;min-width:140px;background:rgba(255,153,0,0.08);border:1px solid rgba(255,153,0,0.25);border-radius:14px;padding:16px;text-align:center;animation-delay:0.4s;">
            <div style="font-family:'Audiowide',cursive;font-size:2rem;color:#ff9900;text-shadow:0 0 12px rgba(255,153,0,0.6);">24/7</div>
            <div style="font-size:11px;color:#9ca3af;letter-spacing:1.5px;text-transform:uppercase;margin-top:4px;">Uptime</div>
        </div>
        <div class="stat-counter-card" style="flex:1;min-width:140px;background:rgba(255,51,102,0.08);border:1px solid rgba(255,51,102,0.25);border-radius:14px;padding:16px;text-align:center;animation-delay:0.5s;">
            <div style="font-family:'Audiowide',cursive;font-size:2rem;color:#ff3366;text-shadow:0 0 12px rgba(255,51,102,0.6);">3</div>
            <div style="font-size:11px;color:#9ca3af;letter-spacing:1.5px;text-transform:uppercase;margin-top:4px;">Active Zones</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="quick-features-box">
        <h3 style="color: #00ffcc !important; margin-top: 0px; margin-bottom: 15px; font-family: 'Segoe UI', sans-serif; text-shadow: 0 0 10px rgba(0, 255, 204, 0.5); position: relative; z-index: 2;">✨ Quick Features</h3>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;position:relative;z-index:2;">
            <div style="display:flex;align-items:flex-start;gap:12px;background:rgba(0,0,0,0.2);border-radius:12px;padding:14px;">
                <div class="hex-badge">🔍</div>
                <div>
                    <p style="margin:0 0 4px 0;color:white;font-weight:700;font-size:14px;">Foreign Object Detection (FOD)</p>
                    <p style="margin:0;color:#9ca3af;font-size:12px;">Identifies debris on runways instantly with 96% accuracy.</p>
                </div>
            </div>
            <div style="display:flex;align-items:flex-start;gap:12px;background:rgba(0,0,0,0.2);border-radius:12px;padding:14px;">
                <div class="hex-badge">👤</div>
                <div>
                    <p style="margin:0 0 4px 0;color:white;font-weight:700;font-size:14px;">Person Detection</p>
                    <p style="margin:0;color:#9ca3af;font-size:12px;">Secures restricted zones with real-time AI surveillance.</p>
                </div>
            </div>
            <div style="display:flex;align-items:flex-start;gap:12px;background:rgba(0,0,0,0.2);border-radius:12px;padding:14px;">
                <div class="hex-badge">🗣️</div>
                <div>
                    <p style="margin:0 0 4px 0;color:white;font-weight:700;font-size:14px;">Voice Feedback</p>
                    <p style="margin:0;color:#9ca3af;font-size:12px;">Issues localized audio warnings automatically via Edge TTS.</p>
                </div>
            </div>
            <div style="display:flex;align-items:flex-start;gap:12px;background:rgba(0,0,0,0.2);border-radius:12px;padding:14px;">
                <div class="hex-badge">⚡</div>
                <div>
                    <p style="margin:0 0 4px 0;color:white;font-weight:700;font-size:14px;">Real-Time Alerts</p>
                    <p style="margin:0;color:#9ca3af;font-size:12px;">Pushes live telemetry to this master dashboard instantly.</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif app_mode == "📹 Live Detection & Monitoring":
    vision_engine()

elif app_mode == "📊 Alerts & Analytics Page":

    # ALERT STATUS STRIP
    st.markdown("""
    <div class="alert-strip">
        <div style="position:relative; z-index:2;"><h2 style="color: #00ffcc; margin:0; text-shadow: 0 0 15px rgba(0,255,204,0.6);">🟢 SYSTEM SAFE</h2></div>
        <div style="position:relative; z-index:2;"><h2 style="color: #ff9900; margin:0; text-shadow: 0 0 15px rgba(255,153,0,0.6);">⚠️ 2 ACTIVE ALERTS</h2></div>
        <div style="position:relative; z-index:2;"><h2 style="color: #00aaff; margin:0; text-shadow: 0 0 15px rgba(0,170,255,0.6);">📡 AI MONITORING ENABLED</h2></div>
    </div>
    """, unsafe_allow_html=True)

    # ALERT CARDS
    st.markdown('<p style="font-size:1.1rem; font-weight:600; letter-spacing:2px; color:#00ffcc; text-transform:uppercase; margin-bottom:14px;">🚨 Priority Alert Cards</p>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="alert-card alert-card-red">
            <p style="color:#ff3366; font-weight:700; font-size:1rem; margin:0 0 8px 0; position:relative; z-index:2; text-shadow: 0 0 10px rgba(255,51,102,0.5);">🔴 HIGH ALERT</p>
            <p style="color:#ffccd5; margin:0; font-size:0.9rem; position:relative; z-index:2;">Unauthorized personnel detected near Runway 2.</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="alert-card alert-card-orange">
            <p style="color:#ff9900; font-weight:700; font-size:1rem; margin:0 0 8px 0; position:relative; z-index:2; text-shadow: 0 0 10px rgba(255,153,0,0.5);">🟠 MEDIUM ALERT</p>
            <p style="color:#ffe5b0; margin:0; font-size:0.9rem; position:relative; z-index:2;">Unattended luggage detected at Gate 7.</p>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="alert-card alert-card-green">
            <p style="color:#00ffcc; font-weight:700; font-size:1rem; margin:0 0 8px 0; position:relative; z-index:2; text-shadow: 0 0 10px rgba(0,255,204,0.5);">🟢 SAFE ZONE</p>
            <p style="color:#ccfff5; margin:0; font-size:0.9rem; position:relative; z-index:2;">No hazard detected in Cargo Area.</p>
        </div>""", unsafe_allow_html=True)

    st.write("")

    # KPI CARDS
    st.markdown('<p style="font-size:1.1rem; font-weight:600; letter-spacing:2px; color:#00ffcc; text-transform:uppercase; margin-bottom:14px;">📊 Analytics Dashboard</p>', unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown('''
        <div class="kpi-card-wrapper">
            <div class="kpi-card-bg" style="background: linear-gradient(137deg, #00aaff 0%, #0061FF 100%);"></div>
            <div class="kpi-card-fg" style="background: linear-gradient(#0a1520, #0a1520) padding-box, linear-gradient(137deg, #00aaff 0%, #0061FF 100%) border-box; box-shadow: 0 0 25px rgba(0,170,255,0.3);">
                <div class="kpi-icon">🔍</div>
                <div class="kpi-value" style="color: #00aaff; text-shadow: 0 0 15px rgba(0,170,255,0.6);">128</div>
                <p class="kpi-label">Total Detections</p>
                <div class="progress-bar-track" style="margin-top:12px;"><div class="progress-bar-fill" style="width:85%;background:linear-gradient(90deg,#00aaff,#0061FF);"></div></div>
            </div>
        </div>''', unsafe_allow_html=True)
    with k2:
        st.markdown('''
        <div class="kpi-card-wrapper">
            <div class="kpi-card-bg" style="background: linear-gradient(137deg, #00ffcc 0%, #00FF87 100%);"></div>
            <div class="kpi-card-fg" style="background: linear-gradient(#05201a, #05201a) padding-box, linear-gradient(137deg, #00ffcc 0%, #00FF87 100%) border-box; box-shadow: 0 0 25px rgba(0,255,204,0.3);">
                <div class="kpi-icon">🎯</div>
                <div class="kpi-value" style="color: #00ffcc; text-shadow: 0 0 15px rgba(0,255,204,0.6);">96%</div>
                <p class="kpi-label">Accuracy</p>
                <div class="progress-bar-track" style="margin-top:12px;"><div class="progress-bar-fill" style="width:96%;background:linear-gradient(90deg,#00ffcc,#00FF87);"></div></div>
            </div>
        </div>''', unsafe_allow_html=True)
    with k3:
        st.markdown('''
        <div class="kpi-card-wrapper">
            <div class="kpi-card-bg" style="background: linear-gradient(137deg, #a200ff 0%, #E0AEFF 100%);"></div>
            <div class="kpi-card-fg" style="background: linear-gradient(#1a0b2e, #1a0b2e) padding-box, linear-gradient(137deg, #a200ff 0%, #E0AEFF 100%) border-box; box-shadow: 0 0 25px rgba(162,0,255,0.3);">
                <div class="kpi-icon">⚡</div>
                <div class="kpi-value" style="color: #c560ff; text-shadow: 0 0 15px rgba(162,0,255,0.6);">1.2s</div>
                <p class="kpi-label">Response Time</p>
                <div class="progress-bar-track" style="margin-top:12px;"><div class="progress-bar-fill" style="width:95%;background:linear-gradient(90deg,#a200ff,#E0AEFF);"></div></div>
            </div>
        </div>''', unsafe_allow_html=True)
    with k4:
        st.markdown('''
        <div class="kpi-card-wrapper">
            <div class="kpi-card-bg" style="background: linear-gradient(137deg, #ff9900 0%, #ffcc00 100%);"></div>
            <div class="kpi-card-fg" style="background: linear-gradient(#201205, #201205) padding-box, linear-gradient(137deg, #ff9900 0%, #ffcc00 100%) border-box; box-shadow: 0 0 25px rgba(255,153,0,0.3);">
                <div class="kpi-icon">🛡️</div>
                <div class="kpi-value" style="color: #ffcc00; text-shadow: 0 0 15px rgba(255,204,0,0.6);">92%</div>
                <p class="kpi-label">Safe Zones</p>
                <div class="progress-bar-track" style="margin-top:12px;"><div class="progress-bar-fill" style="width:92%;background:linear-gradient(90deg,#ff9900,#ffcc00);"></div></div>
            </div>
        </div>''', unsafe_allow_html=True)

    st.write("")

    # CHARTS
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.markdown('<div class="chart-panel"><p class="chart-panel-title">🍩 Hazard Categories</p>', unsafe_allow_html=True)
        pie_df = pd.DataFrame({"Category": ["FOD", "Luggage", "Personnel"], "Count": [20, 50, 30]})
        fig_pie = px.pie(pie_df, values="Count", names="Category",
            color_discrete_sequence=["#00ffcc", "#0061FF", "#a200ff"], hole=0.45)
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ffffff", margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(font=dict(color="#ffffff", size=13), bgcolor="rgba(0,0,0,0)"), showlegend=True)
        fig_pie.update_traces(textfont_color="#ffffff", marker=dict(line=dict(color='rgba(0,0,0,0.5)', width=2)))
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_chart2:
        st.markdown('<div class="chart-panel"><p class="chart-panel-title">📈 Detection Trend</p>', unsafe_allow_html=True)
        trend_df = pd.DataFrame({"Hour": ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00"], "Detections": [5, 12, 18, 25, 15, 30, 22]})
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=trend_df["Hour"], y=trend_df["Detections"],
            mode="lines+markers",
            line=dict(color="#00aaff", width=3),
            marker=dict(color="#00ffcc", size=8, line=dict(color="#0061FF", width=2)),
            fill="tozeroy", fillcolor="rgba(0, 97, 255, 0.12)", name="Detections"))
        fig_line.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ffffff", margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(gridcolor="rgba(0,170,255,0.1)", color="#9ca3af", showline=True, linecolor="rgba(0,170,255,0.3)"),
            yaxis=dict(gridcolor="rgba(0,170,255,0.1)", color="#9ca3af", showline=True, linecolor="rgba(0,170,255,0.3)"),
            showlegend=False)
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    # DETECTION HISTORY
    st.markdown("""
    <div class="history-panel">
        <p class="history-panel-title">📜 Detection History Log</p>
        <table style="width:100%; border-collapse:collapse; font-family:'Segoe UI',sans-serif; position:relative; z-index:2;">
            <thead>
                <tr style="border-bottom:2px solid rgba(162,0,255,0.5);">
                    <th style="padding:12px 14px; color:#c560ff; font-size:12px; text-transform:uppercase; letter-spacing:1.2px; font-weight:700; text-align:left;">⏱ Time</th>
                    <th style="padding:12px 14px; color:#c560ff; font-size:12px; text-transform:uppercase; letter-spacing:1.2px; font-weight:700; text-align:left;">⚠ Hazard Type</th>
                    <th style="padding:12px 14px; color:#c560ff; font-size:12px; text-transform:uppercase; letter-spacing:1.2px; font-weight:700; text-align:left;">📍 Zone</th>
                    <th style="padding:12px 14px; color:#c560ff; font-size:12px; text-transform:uppercase; letter-spacing:1.2px; font-weight:700; text-align:left;">🎯 Confidence</th>
                    <th style="padding:12px 14px; color:#c560ff; font-size:12px; text-transform:uppercase; letter-spacing:1.2px; font-weight:700; text-align:left;">📋 Status</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom:1px solid rgba(0,97,255,0.15); transition:background 0.2s;">
                    <td style="padding:12px 14px; color:#e0e0ff; font-size:14px;">10:45:12</td>
                    <td style="padding:12px 14px; color:#e0e0ff; font-size:14px;">FOD Debris</td>
                    <td style="padding:12px 14px; color:#e0e0ff; font-size:14px;">Runway 3L</td>
                    <td style="padding:12px 14px; color:#e0e0ff; font-size:14px;">96%</td>
                    <td style="padding:12px 14px; font-size:14px;"><span style="color:#00ffcc; font-weight:600;">✅ Resolved</span></td>
                </tr>
                <tr style="border-bottom:1px solid rgba(0,97,255,0.15); background:rgba(162,0,255,0.05);">
                    <td style="padding:12px 14px; color:#e0e0ff; font-size:14px;">11:20:03</td>
                    <td style="padding:12px 14px; color:#e0e0ff; font-size:14px;">Unattended Luggage</td>
                    <td style="padding:12px 14px; color:#e0e0ff; font-size:14px;">Gate 7</td>
                    <td style="padding:12px 14px; color:#e0e0ff; font-size:14px;">88%</td>
                    <td style="padding:12px 14px; font-size:14px;"><span style="color:#ff9900; font-weight:600;">🔄 Pending</span></td>
                </tr>
                <tr style="border-bottom:1px solid rgba(0,97,255,0.15);">
                    <td style="padding:12px 14px; color:#e0e0ff; font-size:14px;">11:55:44</td>
                    <td style="padding:12px 14px; color:#e0e0ff; font-size:14px;">Unauthorized Personnel</td>
                    <td style="padding:12px 14px; color:#e0e0ff; font-size:14px;">Taxiway B</td>
                    <td style="padding:12px 14px; color:#e0e0ff; font-size:14px;">94%</td>
                    <td style="padding:12px 14px; font-size:14px;"><span style="color:#00ffcc; font-weight:600;">✅ Resolved</span></td>
                </tr>
                <tr style="border-bottom:1px solid rgba(0,97,255,0.15); background:rgba(162,0,255,0.05);">
                    <td style="padding:12px 14px; color:#e0e0ff; font-size:14px;">12:10:08</td>
                    <td style="padding:12px 14px; color:#e0e0ff; font-size:14px;">FOD Debris</td>
                    <td style="padding:12px 14px; color:#e0e0ff; font-size:14px;">Apron A</td>
                    <td style="padding:12px 14px; color:#e0e0ff; font-size:14px;">91%</td>
                    <td style="padding:12px 14px; font-size:14px;"><span style="color:#00ffcc; font-weight:600;">✅ Resolved</span></td>
                </tr>
                <tr>
                    <td style="padding:12px 14px; color:#e0e0ff; font-size:14px;">13:02:51</td>
                    <td style="padding:12px 14px; color:#e0e0ff; font-size:14px;">Vehicle Obstruction</td>
                    <td style="padding:12px 14px; color:#e0e0ff; font-size:14px;">Runway 2R</td>
                    <td style="padding:12px 14px; color:#e0e0ff; font-size:14px;">87%</td>
                    <td style="padding:12px 14px; font-size:14px;"><span style="color:#ff9900; font-weight:600;">🔄 Pending</span></td>
                </tr>
            </tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

elif app_mode == "⚙️ About & System Control Page":

    # ── SECTION 1: PROJECT OVERVIEW ──────────────────────────────────────
    st.markdown("""
    <div class="glow-section-panel">
        <p class="glow-section-title">📘 Project Overview</p>
        <p style="color:#a0c8ff !important; font-size:15px; line-height:1.8; margin:0 0 18px 0; position:relative; z-index:2;">
            <b style="color:#00ffcc;">AeroGuard</b> is an AI-powered autonomous ground vehicle designed to patrol airport tarmacs, runways,
            and cargo zones — eliminating the need for manual visual inspection and dramatically reducing human error in safety-critical environments.
        </p>
        <div style="display:flex; gap:20px; flex-wrap:wrap; position:relative; z-index:2;">
            <div style="flex:1; min-width:220px; background:rgba(0,97,255,0.1); border:1px solid rgba(0,97,255,0.3); border-radius:14px; padding:18px;">
                <p style="color:#00aaff !important; font-weight:700; font-size:13px; text-transform:uppercase; letter-spacing:1px; margin:0 0 10px 0;">⚠️ Problem Statement</p>
                <p style="color:#ccddff !important; font-size:13px; line-height:1.7; margin:0;">Manual airport inspections are slow, error-prone, and expensive. Human fatigue leads to missed hazards like FOD, unattended baggage, and unauthorized personnel — all of which pose severe flight safety risks.</p>
            </div>
            <div style="flex:1; min-width:220px; background:rgba(0,255,204,0.07); border:1px solid rgba(0,255,204,0.25); border-radius:14px; padding:18px;">
                <p style="color:#00ffcc !important; font-weight:700; font-size:13px; text-transform:uppercase; letter-spacing:1px; margin:0 0 10px 0;">🎯 Objectives</p>
                <p style="color:#ccffee !important; font-size:13px; line-height:1.9; margin:0;">
                    ✅ Reduce human error in FOD detection<br>
                    ✅ Enable real-time AI monitoring 24/7<br>
                    ✅ Smart multi-class hazard detection<br>
                    ✅ Voice-guided autonomous response<br>
                    ✅ Compliance with aviation safety protocols
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SECTION 2: WORKFLOW DIAGRAM ──────────────────────────────────────
    st.markdown("""
    <div class="glow-section-panel">
        <p class="glow-section-title">🔄 System Workflow</p>
        <div class="workflow-container">
            <div class="workflow-step">
                <div class="workflow-icon-box">📷</div>
                <span class="workflow-label">Camera<br>Capture</span>
            </div>
            <div class="workflow-arrow">→</div>
            <div class="workflow-step">
                <div class="workflow-icon-box" style="box-shadow: 0 0 20px rgba(162,0,255,0.5); background: linear-gradient(rgba(6,12,25,0.9), rgba(6,12,25,0.9)) padding-box, linear-gradient(137deg, #a200ff 0%, #0061FF 100%) border-box;">🧠</div>
                <span class="workflow-label">AI<br>Detection</span>
            </div>
            <div class="workflow-arrow">→</div>
            <div class="workflow-step">
                <div class="workflow-icon-box" style="box-shadow: 0 0 20px rgba(255,153,0,0.5); background: linear-gradient(rgba(6,12,25,0.9), rgba(6,12,25,0.9)) padding-box, linear-gradient(137deg, #ff9900 0%, #ff3366 100%) border-box;">⚠️</div>
                <span class="workflow-label">Hazard<br>Analysis</span>
            </div>
            <div class="workflow-arrow">→</div>
            <div class="workflow-step">
                <div class="workflow-icon-box" style="box-shadow: 0 0 20px rgba(255,51,102,0.5); background: linear-gradient(rgba(6,12,25,0.9), rgba(6,12,25,0.9)) padding-box, linear-gradient(137deg, #ff3366 0%, #ff9900 100%) border-box;">🔊</div>
                <span class="workflow-label">Voice<br>Alert</span>
            </div>
            <div class="workflow-arrow">→</div>
            <div class="workflow-step">
                <div class="workflow-icon-box" style="box-shadow: 0 0 20px rgba(0,255,204,0.5);">🚙</div>
                <span class="workflow-label">AGV<br>Response</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SECTION 3: TECHNOLOGIES USED ─────────────────────────────────────
    st.markdown('<p class="glow-section-title" style="color:#00ffcc; font-size:1.1rem; font-weight:600; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:16px;">💻 Technologies Used</p>', unsafe_allow_html=True)

    t1, t2, t3, t4, t5, t6 = st.columns(6)
    tech_cards = [
        (t1, "#00aaff", "#0061FF", "#0a1520", "🐍", "Python", "Core language powering all logic & integration"),
        (t2, "#a200ff", "#6600cc", "#0a0015", "👁️", "YOLOv8", "Real-time multi-class object detection model"),
        (t3, "#00ffcc", "#00aa88", "#02100a", "📷", "OpenCV", "Computer vision & video frame processing"),
        (t4, "#ff9900", "#cc6600", "#150a00", "🌊", "Streamlit", "Interactive web dashboard & UI framework"),
        (t5, "#ff3366", "#cc1144", "#150005", "🔊", "Edge TTS", "Neural text-to-speech voice alerts"),
        (t6, "#60EFFF", "#0061FF", "#050f1a", "🤖", "Groq LLM", "NLP command parsing via LLaMA 3.1"),
    ]
    for col, c1, c2, bg, icon, name, desc in tech_cards:
        with col:
            st.markdown(f"""
            <div class="tech-card-wrapper">
                <div class="tech-card-bg" style="background: linear-gradient(137deg, {c1} 0%, {c2} 100%);"></div>
                <div class="tech-card-fg" style="background: linear-gradient({bg}, {bg}) padding-box, linear-gradient(137deg, {c1} 0%, {c2} 100%) border-box; box-shadow: 0 0 20px rgba(0,0,0,0.5);">
                    <span class="tech-emoji">{icon}</span>
                    <p class="tech-name">{name}</p>
                    <p class="tech-desc">{desc}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.write("")

    # ── SECTION 4: SYSTEM CONTROL PANEL ──────────────────────────────────
    st.markdown('<p class="glow-section-title" style="color:#00ffcc; font-size:1.1rem; font-weight:600; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:16px;">⚙️ System Control Panel</p>', unsafe_allow_html=True)

    ctrl_left, ctrl_right = st.columns([1, 1])

    with ctrl_left:
        st.markdown("""
        <div class="glow-section-panel" style="margin-bottom:0;">
            <p class="glow-section-title">🛰️ Live System Status</p>
            <div class="status-toggle-row">
                <div class="status-toggle-item">
                    <div class="status-toggle-left">
                        <div class="pulse-ring"><div class="status-dot-on"></div></div>
                        <span class="status-toggle-label">🧠 AI Engine</span>
                    </div>
                    <span class="status-badge-on">ONLINE</span>
                </div>
                <div class="status-toggle-item">
                    <div class="status-toggle-left">
                        <div class="pulse-ring"><div class="status-dot-on"></div></div>
                        <span class="status-toggle-label">🎥 Camera Feed</span>
                    </div>
                    <span class="status-badge-on">CONNECTED</span>
                </div>
                <div class="status-toggle-item">
                    <div class="status-toggle-left">
                        <div class="pulse-ring"><div class="status-dot-on"></div></div>
                        <span class="status-toggle-label">🔊 Voice System</span>
                    </div>
                    <span class="status-badge-on">ENABLED</span>
                </div>
                <div class="status-toggle-item">
                    <div class="status-toggle-left">
                        <div class="pulse-ring"><div class="status-dot-on"></div></div>
                        <span class="status-toggle-label">📡 Live Monitoring</span>
                    </div>
                    <span class="status-badge-on">ACTIVE</span>
                </div>
                <div class="status-toggle-item">
                    <div class="status-toggle-left">
                        <div class="status-dot-off"></div>
                        <span class="status-toggle-label">🚨 Emergency Mode</span>
                    </div>
                    <span class="status-badge-off">STANDBY</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with ctrl_right:
        st.markdown("""
        <div class="glow-section-panel" style="margin-bottom:0;">
            <p class="glow-section-title">🕹️ Control Actions</p>
        """, unsafe_allow_html=True)

        st.markdown('<p style="color:#9ca3af; font-size:12px; margin:0 0 14px 0; position:relative; z-index:2; letter-spacing:0.5px;">Execute system-level commands from this panel.</p>', unsafe_allow_html=True)

        b1, b2 = st.columns(2)
        with b1:
            if st.button("🔄 Restart AI", use_container_width=True, type="primary"):
                st.toast("🔄 AI Engine restarting...", icon="🔄")
            if st.button("🗑️ Reset Detection Logs", use_container_width=True, type="primary"):
                st.toast("🗑️ Detection logs cleared.", icon="✅")
        with b2:
            if st.button("🚨 Enable Emergency Mode", use_container_width=True, type="primary"):
                st.toast("🚨 Emergency mode activated!", icon="🚨")
                speak("Emergency mode activated. All systems on high alert.")
            if st.button("⏹️ Shutdown System", use_container_width=True, type="primary"):
                st.toast("⏹️ Shutdown command sent.", icon="⏹️")
                speak("Initiating system shutdown. Goodbye.")

        st.markdown('<div style="margin-top:18px; position:relative; z-index:2;">', unsafe_allow_html=True)
        st.subheader("")
        st.markdown('<p style="color:#00ffcc; font-size:12px; letter-spacing:1px; text-transform:uppercase; margin:10px 0 6px 0;">🔊 Broadcast Message</p>', unsafe_allow_html=True)
        custom_message = st.text_input("Message:", "Warning. Please clear the path for the autonomous vehicle.", label_visibility="collapsed")
        if st.button("📢 Broadcast Audio", use_container_width=True, type="primary"):
            st.info(f"Broadcasting: '{custom_message}'")
            speak(custom_message)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    with st.expander("⚙️ Advanced Settings", expanded=False):
        st.subheader("AI Vision Parameters")
        confidence = st.slider("YOLO Confidence Threshold (%)", min_value=10, max_value=100, value=50, step=5)
        st.subheader("Rover Kinematics")
        speed = st.slider("Max Patrol Speed (km/h)", min_value=1, max_value=15, value=5)
        st.subheader("Network")
        st.text_input("Master Control IP Address", value="192.168.1.105")
        st.button("Save Configuration", type="primary")

    st.markdown("""
    <div class="glow-section-panel" style="background: linear-gradient(rgba(4,9,20,0.9), rgba(4,9,20,0.9)) padding-box, linear-gradient(137deg, #a200ff 0%, #0061FF 50%, #00ffcc 100%) border-box; box-shadow: 0 0 30px rgba(162,0,255,0.2);">
        <p class="glow-section-title" style="color:#a200ff !important; text-shadow: 0 0 10px rgba(162,0,255,0.5) !important;">👩‍💻 Team Information</p>
        <div style="display:flex; gap:20px; flex-wrap:wrap; position:relative; z-index:2;">
            <div style="flex:1; min-width:180px;">
                <p style="color:#9ca3af !important; font-size:12px; text-transform:uppercase; letter-spacing:1px; margin:0 0 4px 0;">Lead Developer</p>
                <p style="color:#ffffff !important; font-size:15px; font-weight:600; margin:0 0 16px 0;">Poulymi Samanta, Jayanti Jana, Ronit Das, Puskar Mondal</p>
                <p style="color:#9ca3af !important; font-size:12px; text-transform:uppercase; letter-spacing:1px; margin:0 0 4px 0;">Institution</p>
                <p style="color:#ffffff !important; font-size:15px; font-weight:600; margin:0;">National Skill Training Institute Howrah</p>
            </div>
            <div style="flex:1; min-width:180px;">
                <p style="color:#9ca3af !important; font-size:12px; text-transform:uppercase; letter-spacing:1px; margin:0 0 4px 0;">Contact</p>
                <p style="color:#00ffcc !important; font-size:15px; font-weight:600; margin:0 0 16px 0;">support@aeroguard.com</p>
                <p style="color:#9ca3af !important; font-size:12px; text-transform:uppercase; letter-spacing:1px; margin:0 0 4px 0;">Project Type</p>
                <p style="color:#ffffff !important; font-size:15px; font-weight:600; margin:0;">Capstone / Final Year Project</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if 'system_booted' not in st.session_state:
        print("\n" + "="*50)
        print("🚀 INITIATING AEROGUARD MASTER LAUNCH SEQUENCE")
        print("="*50)
        for file in os.listdir('.'):
            if file.startswith("speech_") and file.endswith(".mp3"):
                try:
                    os.remove(file)
                except:
                    pass
        audio_thread = threading.Thread(target=audio_engine, daemon=True)
        audio_thread.start()
        st.session_state.system_booted = True

st.markdown("""
    <div class="footer">
        <p style="margin: 0; font-family: 'Share Tech Mono', monospace; font-size: 13px; letter-spacing: 1px;">
            <span style="color:#00ffcc;">●</span> &nbsp;
            <b>Team:</b> AeroGuard &nbsp;|&nbsp; 
            <b>College:</b> National Skill Training Institute Howrah &nbsp;|&nbsp; 
            <b>Contact:</b> support@aeroguard.com &nbsp;|&nbsp;
            <span style="color:#a200ff;">v2.4.1</span>
        </p>
    </div>
    """, unsafe_allow_html=True)