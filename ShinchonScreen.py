import streamlit as st
import pandas as pd
import os

# 앱 페이지 설정
st.set_page_config(page_title="신촌 스크린 골프 동호회", layout="wide", page_icon="⛳")

# --- 모바일용 제목 크기 최적화 (CSS 추가) ---
st.markdown("""
    <style>
    /* 제목(h1) 크기를 스마트폰에서 한 줄로 보이게 조절 */
    @media (max-width: 640px) {
        .main h1 {
            font-size: 1.5rem !important; /* 모바일에서 글자 크기 축소 */
            white-space: nowrap !important; /* 줄바꿈 방지 */
            overflow: hidden;
            text-overflow: ellipsis; /* 너무 길면 끝부분 생략 */
        }
        .stMetric label {
            font-size: 0.8rem !important; /* 시상자 타이틀 크기도 조절 */
        }
    }
    </style>
    """, unsafe_allow_html=True)

# 1. 데이터 파일 경로 및 로드 함수 (이후 로직은 기존과 동일)
DB_FILE = "golf_data_backup.csv"
# ... (이하 기존 코드 동일) ...

# 메인 제목 부분
st.title(f"⛳ {view_year} {view_month} 리더보드")
