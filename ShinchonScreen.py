import streamlit as st
import pandas as pd
import os

# 1. 앱 페이지 설정
st.set_page_config(page_title="신촌 스크린 골프 동호회", layout="wide", page_icon="⛳")

# 2. 초소형 모바일 제목 최적화 (한 줄 고정 강제 CSS)
st.markdown("""
    <style>
    .main h1 {
        white-space: nowrap !important;
        overflow: hidden;
        text-overflow: ellipsis;
        display: block !important;
    }
    @media (max-width: 640px) {
        .main h1 {
            font-size: 0.95rem !important;
            letter-spacing: -0.07rem !important;
        }
        .main h1 span { font-size: 0.95rem !important; }
        [data-testid="stMetricValue"] { font-size: 1.0rem !important; }
        [data-testid="stMetricLabel"] { font-size: 0.7rem !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 로드/저장 함수
DB_FILE = "golf_data_backup.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            # 필요한 기본 컬럼만 필터링하여 로드
            cols = ['연도', '월', '이름', '전월스코어', '전월불참', '당월스코어', '당월불참']
            return df[cols] if set(cols).issubset(df.columns) else df
        except: pass
    return pd.DataFrame(columns=['연도', '월', '이름', '전월스코어', '전월불참', '당월스코어', '당월불참'])

def save_data(df):
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

if 'golf_data' not in st.session_state:
    st.session_state.golf_data = load_data()

if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# 4. 사이드바 구성
with st.sidebar:
    st.title("⚙️ 설정 및 관리")
    if not st.session_state.admin_logged_in:
        pwd = st.text_input("관리자 비번", type="password")
        if st.button("로그인"):
            if pwd == "1234":
                st.session_state.admin_logged_in = True
                st.rerun()
    else:
        if st.button("로그아웃"):
            st.session_state.admin_logged_in = False
            st.rerun()

    st.divider()
    view_year = st.selectbox("조회 연도", [f"{year}년" for year in range(2026, 2031)])
    view_month = st.selectbox("조회 월", [f"{i}월" for i in range(1, 13)])

    if st.session_state.admin_logged_in:
        st.divider()
        with st.form("add_form", clear_on_submit=True):
            st.write("📝 새 기록 추가")
            new_name = st.text_input("회원 성함")
            c1, c2 = st.columns(2)
            p_abs = c1.checkbox("전월불참")
            c_abs = c2.checkbox("당월불참")
            p_sc = st.number_input("전월 스코어", 0, 150, 80)
            c_sc = st.number_input("당월 스코어", 0, 150, 80)
            if st.form_submit_button("저장"):
                if new_name:
                    new_row = pd.DataFrame({
                        '연도': [view_year], '월': [view_month], '이름': [new_name],
                        '전월스코어': [0 if p_abs else p_sc], '전월불참': [p_abs],
                        '당월스코어': [0 if c_abs else c_sc], '당월불참': [c_abs]
                    })
                    df = st.session_state.golf_data
                    mask = (df['연도']==view_year) & (df['월']==view_month) & (df['이름']==new_name)
                    st.session_state.golf_data = pd.concat([df[~mask], new_row], ignore_index=True)
                    save_data(st.session_state.golf_data)
                    st.rerun()

# 5. 메인 화면 출력
st.title(f"⛳ {view_year} {view_month} 리더보드")

all_data = st.session_state.golf_data
df_filtered = all_data[(all_data['연도'] == view_year) & (all_data['월'] == view_month)].copy()

if not df_filtered.empty:
    df_filtered['calc_improvement'] = df_filtered.apply(
        lambda x: x['전월스코어'] - x['당월스코어'] if (not x['전월불참'] and not x['당월불참']) else -999, axis=1
    )
    
    # 시상 결과 요약
    pts = df_filtered[df_filtered['당월불참'] == False]
    if not pts.empty:
        st.subheader("🏆 시상")
        cw, ce = st.columns(2)
        winner = pts.loc[pts['당월스코어'].idxmin()]
        with cw:
            dv = None if winner['전월불참'] else f"{int(winner['calc_improvement'])}타 개선"
            st.metric("🥇 메달리스트", winner['이름'], delta=dv)
        
        ve = pts[pts['전월불참'] == False]
        if not ve.empty:
            eff = ve.loc[ve['calc_improvement'].idxmax()]
            with ce:
                st.metric("👏 노력상", eff['이름'], delta=f"{int(eff['calc_improvement'])}타 개선")
    
    st.divider()

    # 데이터 관리/조회 영역
    if st.session_state.admin_logged_in:
        st.subheader("📝 스코어 관리 (수정 가능)")
        edit_cols = ['이름', '전월스코어', '전월불참', '당월스코어', '당월불참']
        edf = st.data_editor(df_filtered[edit_cols].sort_values('당월스코어'), use_container_width=True, hide_index=True)
        if not edf.equals(df_filtered[edit_cols].sort_values('당월스코어')):
            for i in range(len(edf)):
                row = edf.iloc[i]
                idx = all_data[(all_data['연도']==view_year) & (all_data['월']==view_month) & (all_data['이름']==row['이름'])].index
                all_data.loc[idx, edit_cols] = row.values
            save_data(all_data)
            st.rerun()
    else:
        st.subheader("📋 전체 순위표")
        disp = df_filtered.sort_values('당월스코어').reset_index(drop=True)
        disp.index += 1
        disp['전월'] = disp.apply(lambda x: "불참" if x['전월불참'] else f"{int(x['전월스코어'])}", axis=1)
        disp['당월'] = disp.apply(lambda x: "불참" if x['당월불참'] else f"{int(x['당월스코어'])}", axis=1)
        disp['개선'] = disp.apply(lambda x: f"{int(x['calc_improvement'])}" if (not x['전월불참'] and not x['당월불참']) else "N/A", axis=1)
        st.table(disp[['이름', '전월', '당월', '개선']])

    csv = df_filtered.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 엑셀 다운로드", csv, f"신촌골프_{view_year}_{view_month}.csv", "text/csv")
else:
    st.info("해당 월의 데이터가 없습니다.")
