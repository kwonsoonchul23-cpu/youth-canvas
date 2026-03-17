import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import re
import calendar
import copy
import time
import urllib.request
import io
from datetime import datetime, date
from collections import defaultdict
import requests 
import matplotlib.pyplot as plt 
import seaborn as sns 
import matplotlib.font_manager as fm

# --- [디자인 요소] 페이지 기본 설정 ---
st.set_page_config(page_title="Youth Canvas | 청소년 활동 플랫폼", page_icon="🎨", layout="wide")

# --- ✨ 시각화 폰트 설정 및 초고해상도(DPI) 세팅 ---
@st.cache_resource
def set_korean_font():
    font_url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
    font_path = "NanumGothic.ttf"
    try:
        if not os.path.exists(font_path):
            urllib.request.urlretrieve(font_url, font_path)
        fm.fontManager.addfont(font_path)
        font_prop = fm.FontProperties(fname=font_path)
        font_name = font_prop.get_name()
        plt.rc('font', family=font_name)
    except:
        import platform
        if platform.system() == 'Darwin': plt.rc('font', family='AppleGothic')
        elif platform.system() == 'Windows': plt.rc('font', family='Malgun Gothic')
    
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['figure.dpi'] = 300  
    sns.set_theme(style='whitegrid', font=plt.rcParams['font.family'], font_scale=1.0)

set_korean_font()

# --- [디자인 요소] 커스텀 CSS ---
st.markdown("""
    <style>
    h1, h2, h3, h4, h5, h6, p, label, span, div, button, input, select, textarea, li, th, td {
        font-family: 'KakaoBigSans-ExtraBold', 'Pretendard', 'Malgun Gothic', sans-serif;
    }
    .badge-green { background-color: #dcfce7; color: #166534; padding: 4px 10px; border-radius: 12px; font-size: 0.85em; font-weight: bold; margin-right: 5px; }
    .badge-red { background-color: #fee2e2; color: #991b1b; padding: 4px 10px; border-radius: 12px; font-size: 0.85em; font-weight: bold; margin-right: 5px; }
    .badge-blue { background-color: #e0e7ff; color: #3730a3; padding: 4px 10px; border-radius: 12px; font-size: 0.85em; font-weight: bold; margin-right: 5px; border: 1px solid #c7d2fe; }
    .card-title { font-size: 1.4em; font-weight: 800; color: #1e293b; margin-bottom: 0.2em; }
    .recruit-period { font-size: 0.85em; color: #b45309; background-color: #fef3c7; padding: 5px 10px; border-radius: 5px; font-weight: bold; display: inline-block; margin-bottom: 10px; }
    .schedule-table { width: 100%; border-collapse: collapse; font-size: 0.9em; text-align: center; margin-bottom: 10px; }
    .schedule-table th { border: 1px solid #cbd5e1; padding: 8px; background-color: #f1f5f9; font-weight: bold; color: #334155; }
    .schedule-table td { border: 1px solid #cbd5e1; padding: 8px; color: #1e293b; vertical-align: top; }
    
    .cal-table { width: 100%; border-collapse: collapse; table-layout: fixed; }
    .cal-th { background: #f8fafc; border: 1px solid #cbd5e1; padding: 10px; text-align: center; font-weight: bold; }
    .cal-td { border: 1px solid #cbd5e1; height: 100px; vertical-align: top; padding: 5px; background: #ffffff; }
    .cal-td.empty { background: #f1f5f9; }
    .cal-day-num { font-weight: bold; color: #475569; text-align: right; }
    .cal-event { color: #ffffff; padding: 2px 5px; margin-bottom: 2px; font-size: 0.75em; border-radius: 3px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }

    [data-testid="stSidebar"] { background-color: #261633 !important; }
    [data-testid="stSidebarUserContent"] { padding-left: 1rem !important; padding-right: 1rem !important; padding-top: 3rem !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label { 
        width: 100%; min-height: 60px; margin: 0 0 10px 0; padding: 10px 15px; cursor: pointer; border-radius: 12px; display: flex; justify-content: flex-start; align-items: center; transition: all 0.2s ease; 
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(1) { background-color: #5c358f !important; } 
    [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(2) { background-color: #3b82f6 !important; } 
    [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(3) { background-color: #c13945 !important; } 
    [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(4) { background-color: #2b7a78 !important; } 
    [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(5) { background-color: #e68128 !important; } 
    [data-testid="stSidebar"] div[role="radiogroup"] > label p { font-size: 1.15rem !important; font-weight: 900 !important; color: #ffffff !important; margin: 0 !important; }
    
    .report-box { border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; margin-top: 10px; background-color: #f8fafc; }
    .pos-text { color: #059669; font-weight: 600; }
    .neg-text { color: #dc2626; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# --- 유틸리티 함수 ---
def fix_youtube_url(url):
    if not url: return None
    url = url.replace("shorts/", "watch?v=")
    if "youtu.be/" in url: return f"https://www.youtube.com/watch?v={url.split('youtu.be/')[1].split('?')[0]}"
    return url

def get_date_range(task_dict):
    if 'start_date' in task_dict and 'end_date' in task_dict: return task_dict['start_date'], task_dict['end_date']
    elif 'date' in task_dict:
        d = task_dict['date']
        if '~' in d: return d.split('~')[0].strip(), d.split('~')[1].strip()
        return d.strip(), d.strip()
    return "", ""

def get_date_label(task_dict):
    sd, ed = get_date_range(task_dict)
    if sd and ed and sd != ed: return f"[{sd} ~ {ed}] "
    elif sd and sd != "-": return f"[{sd}] "
    return ""

def is_active_role_period(u_dict, target_date_str):
    u_dates = []
    for t in u_dict.get('workflow', []):
        sd, ed = get_date_range(t)
        for d_str in [sd, ed]:
            if d_str and re.match(r'\d{4}-\d{2}-\d{2}', d_str):
                try: u_dates.append(datetime.strptime(d_str.strip(), "%Y-%m-%d").date())
                except: pass
    if not u_dates: return True 
    try:
        target_d_obj = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        return min(u_dates) <= target_d_obj <= max(u_dates)
    except: return False

# ==============================================================
# ✨ [데이터베이스 연결 및 에러 방어 로직]
# ==============================================================
FIREBASE_URL = "https://youth-canvas-default-rtdb.firebaseio.com/data.json"

def load_data():
    try:
        response = requests.get(FIREBASE_URL)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, dict) and 'programs' in data: 
                if 'parents' not in data: data['parents'] = []
                if 'payments' not in data: data['payments'] = [] 
                if 'settings' not in data: data['settings'] = {}
                if 'ui' not in data['settings']:
                    data['settings']['ui'] = {
                        "brand_title": "Youth Canvas", "brand_subtitle": "청소년의 꿈을 그리는 공간",
                        "menu1": "🔍 찾아보기 (탐색)", "menu2": "📅 전체 일정", "menu3": "🙋 나의 이야기", 
                        "menu4": "👨‍👩‍👧 학부모 공간", "menu5": "🔒 관리자 전용 포털",
                        "page1_title": "✨ 지금 뜨고 있는 활동", "page2_title": "🗓️ 기관 전체 일정표", 
                        "page3_title": "🙋 나의 활동 진행도", "page4_title": "🔒 관리자 전용 포털"
                    }
                # ✨ 에러 방지: terms 항목이 4개인 경우 5개로 강제 업데이트
                if 'terms' not in data['settings']:
                    data['settings']['terms'] = {"super": "최고관리자", "admin": "선생님", "staff": "행정", "user": "학생", "parent": "학부모"}
                elif len(data['settings']['terms']) < 5:
                    data['settings']['terms']['staff'] = "행정"
                return data
    except: pass
    return {"programs": [], "users": [], "parents": [], "payments": [], "admins": [{"name": "마스터", "pin": "0000", "role": "super", "programs": []}], "settings": {"terms": {"super": "최고관리자", "admin": "선생님", "staff": "행정", "user": "학생", "parent": "학부모"}, "ui": {"brand_title": "Youth Canvas", "brand_subtitle": "청소년의 꿈을 그리는 공간", "menu1": "🔍 찾아보기 (탐색)", "menu2": "📅 전체 일정", "menu3": "🙋 나의 이야기", "menu4": "👨‍👩‍👧 학부모 공간", "menu5": "🔒 관리자 전용 포털", "page1_title": "✨ 지금 뜨고 있는 활동", "page2_title": "🗓️ 기관 전체 일정표", "page3_title": "🙋 나의 활동 진행도", "page4_title": "🔒 관리자 전용 포털"}}}

def save_data(data):
    try: res = requests.put(FIREBASE_URL, json=data); return res.status_code == 200
    except: return False

if 'db' not in st.session_state: st.session_state['db'] = load_data()
db = st.session_state['db']

# ✨ 픽스: .values() 대신 명시적으로 키를 지정하여 NameError 및ValueError 방지
terms = db['settings']['terms']
T_SUPER = terms.get('super', '최고관리자')
T_ADMIN = terms.get('admin', '선생님')
T_STAFF = terms.get('staff', '행정')
T_USER = terms.get('user', '학생')
T_PARENT = terms.get('parent', '학부모')

UI = db['settings']['ui']
menu_list = [UI['menu1'], UI['menu2'], UI['menu3'], UI['menu4'], UI['menu5']]
if 'menu_option' not in st.session_state or st.session_state.menu_option not in menu_list: 
    st.session_state.menu_option = UI['menu1']

with st.sidebar:
    st.markdown(f"<div style='margin-bottom: 2rem; padding: 0 10px;'><div style='font-size: 2.8rem; font-weight: 900; color: #ffffff; line-height: 1.1;'>{UI['brand_title']}</div><div style='font-size: 1.2rem; font-weight: 800; color: #ffce31;'>{UI['brand_subtitle']}</div></div>", unsafe_allow_html=True)
    menu = st.radio("메뉴", menu_list, index=menu_list.index(st.session_state.menu_option), label_visibility="collapsed")
    if st.button("🔄 최신 데이터 동기화", use_container_width=True):
        st.session_state['db'] = load_data(); st.rerun()
st.session_state.menu_option = menu

# =========================================================
# [페이지 1] 찾아보기 (탐색)
# =========================================================
if st.session_state.menu_option == UI['menu1']:
    st.markdown(f"## {UI['page1_title']}")
    if not db['programs']: st.info("프로그램이 없습니다.")
    col1, col2 = st.columns(2)
    for idx, prog in enumerate(db['programs']):
        with (col1 if idx % 2 == 0 else col2):
            with st.container(border=True):
                st.markdown(f"<div class='card-title' style='border-left: 5px solid {prog.get('color', '#4f46e5')}; padding-left: 8px;'>{prog['title']}</div>", unsafe_allow_html=True)
                st.write(prog['desc'])
                clean_url = fix_youtube_url(prog.get('video'))
                if clean_url: st.video(clean_url)
                with st.expander("📅 전체 일정 요약 보기"):
                    grouped_tasks = defaultdict(list)
                    for role, tasks in prog.get('roles_workflow', {}).items():
                        for t in tasks:
                            label = get_date_label(t)
                            sub_texts = [stask['desc'] for stask in t.get('subtasks', [])]
                            subs_html = "<br>".join([f"&nbsp;&nbsp;└ {desc}" for desc in sub_texts])
                            grouped_tasks[label if label else "미정"].append(f"<b>{role}</b>: {t['task']}<br>{subs_html}")
                    html_table = "<table class='schedule-table'><tr><th>일정</th><th>내용</th></tr>"
                    for d, contents in grouped_tasks.items():
                        html_table += f"<tr><td>{d}</td><td style='text-align:left;'>{'<br>'.join(contents)}</td></tr>"
                    st.markdown(html_table + "</table>", unsafe_allow_html=True)
                if st.button("🚀 지원하기", key=f"apply_{idx}", use_container_width=True, type="primary"):
                    st.session_state['selected_prog_from_main'] = prog['title']; change_page(UI['menu3'])

# =========================================================
# [페이지 2] 전체 일정
# =========================================================
elif st.session_state.menu_option == UI['menu2']:
    st.markdown(f"## {UI['page2_title']}")
    now = datetime.now(); c_col1, c_col2 = st.columns([2, 8])
    sel_year = c_col1.selectbox("년도", range(now.year-1, now.year+3), index=1)
    sel_month = c_col2.select_slider("월", range(1, 13), value=now.month)
    cal = calendar.monthcalendar(sel_year, sel_month)
    day_events = defaultdict(list)
    for prog in db['programs']:
        for role, tasks in prog.get('roles_workflow', {}).items():
            for t in tasks:
                sd_str, ed_str = get_date_range(t)
                if not sd_str: continue
                try:
                    sd = datetime.strptime(sd_str, "%Y-%m-%d").date(); ed = datetime.strptime(ed_str, "%Y-%m-%d").date()
                    for d_ord in range(sd.toordinal(), ed.toordinal() + 1):
                        d = date.fromordinal(d_ord)
                        if d.year == sel_year and d.month == sel_month:
                            day_events[d.day].append({"title": f"[{role}] {t['task']}", "color": prog.get('color', '#4f46e5')})
                except: pass
    cols = st.columns(7); days = ["월", "화", "수", "목", "금", "토", "일"]
    for i, day in enumerate(days): cols[i].markdown(f"<div class='cal-th'>{day}</div>", unsafe_allow_html=True)
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0: cols[i].markdown("<div class='cal-td empty'></div>", unsafe_allow_html=True)
            else:
                event_html = "".join([f"<div class='cal-event' style='background:{ev['color']};'>{ev['title']}</div>" for ev in day_events[day]])
                cols[i].markdown(f"<div class='cal-td'><div class='cal-day-num'>{day}</div>{event_html}</div>", unsafe_allow_html=True)

# =========================================================
# [페이지 5] 관리자 전용 포털
# =========================================================
elif st.session_state.menu_option == UI['menu5']:
    if not st.session_state.get('admin_logged_in', False):
        with st.container(border=True):
            with st.form("admin_login"):
                l_name = st.text_input("관리자 이름")
                l_pin = st.text_input("비밀번호", type="password")
                if st.form_submit_button("로그인"):
                    matched = next((a for a in db['admins'] if a['name'] == l_name and a['pin'] == l_pin), None)
                    if matched: st.session_state['admin_logged_in'] = True; st.session_state['logged_admin'] = matched; st.rerun()
                    else: st.error("인증 실패")
    else:
        admin_info = st.session_state['logged_admin']
        is_super = (admin_info['role'] == 'super')
        is_staff = (admin_info['role'] == 'staff')
        is_normal = (admin_info['role'] == 'normal') # ✨ FIX: 변수 정의 완료
        
        col_t, col_l = st.columns([8, 2])
        col_t.subheader(f"🛠️ 시스템 관리 [{admin_info['name']} 접속중]")
        if col_l.button("로그아웃"): st.session_state['admin_logged_in'] = False; st.rerun()
        
        # ✨ 권한별 탭 구성
        if is_super or is_staff:
            t_list = ["📈 경영 대시보드", "💳 행정/재무 관리", "📊 종합 명단", "📝 신규 개설", "⚙️ 정보 수정", "✅ 출석 관리", "👥 1:1 상담", "👨‍👩‍👧 학부모 관리", "🎨 화면 설정", "🔐 계정 관리"]
        else:
            t_list = ["📈 경영 대시보드", "📝 평가/코멘트 작성", "📊 종합 명단", "✅ 출석 관리", "👥 1:1 상담", "🔐 계정 관리"]
            
        tabs = st.tabs(t_list)
        
        # ---------------------------------------------------------
        # 1. 경영 대시보드 (공통)
        with tabs[0]:
            st.write("기관 운영 데이터 분석 결과를 확인합니다.")
            # (차트 시각화 및 AI 리포트 로직... 생략)

        # 2. 행정/재무 관리 (마스터 & 행정)
        if is_super or is_staff:
            with tabs[1]:
                st.subheader("💳 결제 내역 및 재무 인사이트")
                f_tab1, f_tab2 = st.tabs(["입력 및 수정", "데이터 분석 (엑셀/PNG)"])
                
                with f_tab1:
                    with st.form("pay_entry"):
                        c1, c2, c3 = st.columns(3)
                        p_d = c1.date_input("결제일"); p_s = c2.text_input("학생명"); p_c = c3.selectbox("항목", ["수강료", "교재비", "기타"])
                        p_a = c1.number_input("금액", step=1000); p_m = c2.selectbox("수단", ["카드", "현금", "이체"])
                        if st.form_submit_button("내역 저장"):
                            db['payments'].append({"id":str(time.time()), "date":p_d.strftime("%Y-%m-%d"), "student":p_s, "category":p_c, "amount":p_a, "method":p_m})
                            save_data(db); st.success("저장 완료"); st.rerun()

                with f_tab2:
                    # ✨ 마스터 권한 또는 '전체열람' 행정만 접근 가능
                    staff_perm = admin_info.get('staff_permission', 'full') if is_super else admin_info.get('staff_permission', 'entry')
                    if staff_perm == 'full':
                        if db.get('payments'):
                            df_p = pd.DataFrame(db['payments'])
                            # 📥 엑셀(CSV) 다운로드
                            csv = df_p.to_csv(index=False).encode('utf-8-sig')
                            st.download_button("📥 전체 재무 내역 엑셀 다운로드", csv, "finance.csv", "text/csv")
                            
                            # 🖼️ 그래프 PNG 다운로드
                            fig, ax = plt.subplots(figsize=(10,4))
                            df_p.groupby('date')['amount'].sum().plot(kind='bar', ax=ax, color='skyblue')
                            st.pyplot(fig)
                            buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=300); buf.seek(0)
                            st.download_button("📥 매출 그래프 이미지 다운로드", buf, "revenue.png", "image/png")
                        else: st.info("데이터가 없습니다.")
                    else: st.error("🔒 이 기능은 '전체 열람' 권한이 있는 사용자만 볼 수 있습니다.")

            # 3. 종합 명단
            with tabs[2]:
                st.write("전체 학생 명단을 관리하고 이미지로 저장합니다.")
                # (종합명단 로직...)

            # 4. 신규 개설
            with tabs[3]:
                st.write("새로운 프로그램을 등록합니다.")
                # (프로그램 생성 로직...)

            # 5. 정보 수정
            with tabs[4]:
                st.write("기존 프로그램 정보를 수정합니다.")

        # 🔐 계정 관리 (마스터)
        if is_super:
            with tabs[9]:
                st.subheader("직원 권한 수정")
                staffs = [a['name'] for a in db['admins'] if a['role'] == 'staff']
                if staffs:
                    target = st.selectbox("수정할 행정 직원", staffs)
                    adm = next(a for a in db['admins'] if a['name'] == target)
                    new_perm = st.radio("재무 권한", ["entry", "full"], index=0 if adm.get('staff_permission')=='entry' else 1, format_func=lambda x: "단순 입력" if x=="entry" else "전체 열람")
                    if st.button("권한 업데이트"):
                        adm['staff_permission'] = new_perm
                        save_data(db); st.success("변경 완료")
