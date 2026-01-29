import streamlit as st
import pandas as pd
import os

# 앱 페이지 설정
st.set_page_config(page_title="신촌 스크린 골프 동호회", layout="wide", page_icon="⛳")
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

# 1. 데이터 파일 경로 및 초기화
DB_FILE = "golf_data_backup.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=['연도', '월', '이름', '전월스코어', '전월불참', '당월스코어', '당월불참'])

def save_data(df):
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')

if 'golf_data' not in st.session_state:
    st.session_state.golf_data = load_data()

# --- 관리자 로그인 세션 관리 ---
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# --- 사이드바: 설정 및 관리자 로그인 ---
with st.sidebar:
    st.title("⚙️ 설정 및 관리")
    
    # [관리자 로그인 섹션]
    if not st.session_state.admin_logged_in:
        st.subheader("🔐 관리자 로그인")
        password = st.text_input("비밀번호 입력", type="password")
        if st.button("로그인"):
            if password == "1234":
                st.session_state.admin_logged_in = True
                st.success("관리자 인증 성공!")
                st.rerun()
            else:
                st.error("비밀번호가 틀렸습니다.")
    else:
        st.success("✅ 관리자 모드 가동 중")
        if st.button("로그아웃"):
            st.session_state.admin_logged_in = False
            st.rerun()

    st.divider()
    
    # [조회 설정]
    st.subheader("🔍 조회 대상 선택")
    view_year = st.selectbox("조회 연도", [f"{year}년" for year in range(2026, 2031)])
    view_month = st.selectbox("조회 월", [f"{i}월" for i in range(1, 13)])
    
    # [데이터 입력 - 관리자 전용]
    if st.session_state.admin_logged_in:
        st.divider()
        st.subheader("📝 새 기록 추가")
        with st.form("score_form", clear_on_submit=True):
            name = st.text_input("회원 성함")
            c_abs1, c_abs2 = st.columns(2)
            is_p_abs = c_abs1.checkbox("전월 불참")
            is_c_abs = c_abs2.checkbox("당월 불참")
            p_score = st.number_input("전월 스코어", 0, 150, 80)
            c_score = st.number_input("당월 스코어", 0, 150, 80)
            submit = st.form_submit_button("기록 저장하기")

        if submit and name:
            new_entry = pd.DataFrame({
                '연도': [view_year], '월': [view_month], '이름': [name], 
                '전월스코어': [0 if is_p_abs else p_score], '전월불참': [is_p_abs],
                '당월스코어': [0 if is_c_abs else c_score], '당월불참': [is_c_abs]
            })
            df = st.session_state.golf_data
            mask = (df['연도'] == view_year) & (df['월'] == view_month) & (df['이름'] == name)
            st.session_state.golf_data = pd.concat([df[~mask], new_entry], ignore_index=True)
            save_data(st.session_state.golf_data)
            st.rerun()

# --- 메인 대시보드 ---
st.title(f"⛳ {view_year} {view_month} 리더보드")

all_data = st.session_state.golf_data
filtered_idx = all_data[(all_data['연도'] == view_year) & (all_data['월'] == view_month)].index
df_filtered = all_data.loc[filtered_idx].copy()

if not df_filtered.empty:
    df_filtered['calc_improvement'] = df_filtered.apply(
        lambda x: x['전월스코어'] - x['당월스코어'] if (not x['전월불참'] and not x['당월불참']) else -999, axis=1
    )
    
    # 🏆 시상 결과
    participants = df_filtered[df_filtered['당월불참'] == False]
    if not participants.empty:
        st.subheader("🏆 이달의 시상")
        col_w, col_e, col_d = st.columns([1, 1, 1])
        
        winner = participants.loc[participants['당월스코어'].idxmin()]
        with col_w:
            d_val = None if winner['전월불참'] else f"{int(winner['calc_improvement'])}타 개선"
            st.metric("🥇 메달리스트", winner['이름'], delta=d_val)
            
        valid_effort = participants[participants['전월불참'] == False]
        if not valid_effort.empty:
            effort_man = valid_effort.loc[valid_effort['calc_improvement'].idxmax()]
            with col_e:
                st.metric("👏 노력상", effort_man['이름'], delta=f"{int(effort_man['calc_improvement'])}타 개선")
        
        with col_d:
            csv = df_filtered.to_csv(index=False).encode('utf-8-sig')
            st.write("") 
            st.download_button("📥 엑셀 다운로드", csv, f"신촌골프_{view_year}_{view_month}.csv", "text/csv")

    st.divider()
    
    # 📋 리더보드 표시
    if st.session_state.admin_logged_in:
        st.subheader("📝 스코어 관리 (관리자 수정 모드)")
        edit_cols = ['이름', '전월스코어', '전월불참', '당월스코어', '당월불참']
        edited_df = st.data_editor(
            df_filtered[edit_cols].sort_values(by='당월스코어'),
            column_config={
                "전월스코어": st.column_config.NumberColumn("전월", format="%d타"),
                "당월스코어": st.column_config.NumberColumn("당월", format="%d타"),
            },
            use_container_width=True, hide_index=True, key="admin_editor"
        )
        if not edited_df.equals(df_filtered[edit_cols].sort_values(by='당월스코어')):
            for i in range(len(edited_df)):
                name_val = edited_df.iloc[i]['이름']
                target_idx = all_data[(all_data['연도'] == view_year) & (all_data['월'] == view_month) & (all_data['이름'] == name_val)].index
                all_data.loc[target_idx, edit_cols] = edited_df.iloc[i].values
            save_data(all_data)
            st.rerun()
    else:
        st.subheader("📋 전체 순위표 (조회 전용)")
        display_df = df_filtered.sort_values(by='당월스코어').reset_index(drop=True)
        display_df.index += 1
        display_df['전월'] = display_df.apply(lambda x: "불참" if x['전월불참'] else f"{int(x['전월스코어'])}타", axis=1)
        display_df['당월'] = display_df.apply(lambda x: "불참" if x['당월불참'] else f"{int(x['당월스코어'])}타", axis=1)
        display_df['개선'] = display_df.apply(lambda x: f"{int(x['calc_improvement'])}타" if (not x['전월불참'] and not x['당월불참']) else "N/A", axis=1)
        st.table(display_df[['이름', '전월', '당월', '개선']])
else:
    st.info("조회된 데이터가 없습니다.")
