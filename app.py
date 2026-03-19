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
import urllib.parse
import io
import base64
from datetime import datetime, date
from collections import defaultdict
import requests 
import plotly.express as px
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

# --- [디자인 요소] 커스텀 프리미엄 CSS ---
st.markdown("""
    <style>
    /* 트렌디한 폰트 적용 (Pretendard) */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    html, body, [class*="css"] {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, 'Helvetica Neue', 'Segoe UI', 'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif !important;
        letter-spacing: -0.02em;
    }
    
    /* 앱 전체 배경색 부드럽게 */
    .stApp { background-color: #f8fafc; }
    
    /* ✨ 글래스모피즘 (투명 유리) & 카드 호버 이펙트 */
    div[data-testid="stVerticalBlock"] > div[style*="border"] {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04) !important;
        transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1), box-shadow 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }
    div[data-testid="stVerticalBlock"] > div[style*="border"]:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.08) !important;
    }

    /* ✨ 프리미엄 버튼 디자인 (그라데이션 & 애니메이션) */
    button[kind="primary"] {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        color: white !important;
        font-weight: 800 !important;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(124, 58, 237, 0.5) !important;
        filter: brightness(1.1) !important;
    }

    /* 뱃지 및 기타 텍스트 고급화 */
    .badge-green { background-color: #dcfce7; color: #166534; padding: 6px 12px; border-radius: 20px; font-size: 0.85em; font-weight: 800; margin-right: 5px; box-shadow: 0 2px 4px rgba(22,101,52,0.1); }
    .badge-red { background-color: #fee2e2; color: #991b1b; padding: 6px 12px; border-radius: 20px; font-size: 0.85em; font-weight: 800; margin-right: 5px; box-shadow: 0 2px 4px rgba(153,27,27,0.1);}
    .badge-blue { background-color: #e0e7ff; color: #3730a3; padding: 6px 12px; border-radius: 20px; font-size: 0.85em; font-weight: 800; margin-right: 5px; border: 1px solid #c7d2fe; }
    .badge-gray { background-color: #f1f5f9; color: #475569; padding: 6px 12px; border-radius: 20px; font-size: 0.85em; font-weight: 800; margin-right: 5px; }
    .card-title { font-size: 1.6em; font-weight: 900; color: #0f172a; margin-bottom: 0.3em; letter-spacing:-0.03em;}
    .recruit-period { font-size: 0.85em; color: #b45309; background-color: #fef3c7; padding: 5px 10px; border-radius: 5px; font-weight: bold; display: inline-block; margin-bottom: 10px; }
    
    /* 표 디자인 모던화 */
    .schedule-table { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 0.95em; text-align: left; margin-bottom: 10px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
    .schedule-table th { padding: 16px; background-color: #f8fafc; font-weight: 800; color: #334155; border-bottom: 2px solid #e2e8f0; }
    .schedule-table td { padding: 16px; color: #1e293b; vertical-align: top; border-bottom: 1px solid #f1f5f9; }
    .schedule-table tr:hover td { background-color: #f8fafc; }
    
    .report-box { border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; margin-top: 10px; background-color: #f8fafc; }
    .pos-text { color: #059669; font-weight: 600; margin-bottom: 5px;}
    .neg-text { color: #dc2626; font-weight: 600; margin-bottom: 5px;}
    .info-text { color: #475569; font-weight: 500;}
    
    /* 캘린더 고급화 */
    .cal-table { width: 100%; border-collapse: separate; border-spacing: 4px; table-layout: fixed; }
    .cal-th { background: transparent; padding: 10px; text-align: center; font-weight: 800; color:#64748b; font-size:0.9em; }
    .cal-td { border-radius: 12px; height: 120px; vertical-align: top; padding: 8px; background: #ffffff; box-shadow: 0 2px 5px rgba(0,0,0,0.02); transition: all 0.2s ease; border: 1px solid #f1f5f9;}
    .cal-td:hover { box-shadow: 0 8px 20px rgba(0,0,0,0.06); transform: scale(1.02); z-index:10; }
    .cal-td.empty { background: transparent; box-shadow:none; border:none;}
    .cal-day-num { font-weight: 800; color: #334155; text-align: right; margin-bottom: 6px; font-size:1.1em;}
    .cal-event { color: #ffffff; padding: 4px 8px; margin-bottom: 4px; font-size: 0.8em; border-radius: 6px; font-weight:600; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; box-shadow: 0 2px 4px rgba(0,0,0,0.1); cursor: pointer; transition: filter 0.2s ease; }
    .cal-event:hover { filter: brightness(1.2); }

    /* 사이드바 다크테마 프리미엄화 */
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important; border-right: none !important;}
    [data-testid="stSidebarUserContent"] { padding: 2.5rem 1.5rem !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label { 
        width: 100%; min-height: 64px; margin: 0 0 12px 0; padding: 12px 20px; cursor: pointer; border-radius: 16px; display: flex; justify-content: flex-start; align-items: center; transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); border: 1px solid rgba(255,255,255,0.05);
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(1) { background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important; box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3);} 
    [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(2) { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);} 
    [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(3) { background: linear-gradient(135deg, #ec4899 0%, #db2777 100%) !important; box-shadow: 0 4px 15px rgba(219, 39, 119, 0.3);} 
    [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(4) { background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%) !important; box-shadow: 0 4px 15px rgba(13, 148, 136, 0.3);} 
    [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(5) { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important; box-shadow: 0 4px 15px rgba(217, 119, 6, 0.3);} 
    [data-testid="stSidebar"] div[role="radiogroup"] > label p { font-size: 1.1rem !important; font-weight: 800 !important; color: #ffffff !important; margin: 0 !important; letter-spacing: -0.02em;}
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover { transform: scale(1.04) translateX(5px); filter: brightness(1.15); box-shadow: 0 8px 20px rgba(0,0,0,0.4); }
    </style>
""", unsafe_allow_html=True)

ATT_COLORS = {'출석': '#2ECC71', '지각': '#FFC107', '결석': '#E74C3C', '병결': '#9B59B6'}

# --- 유틸리티 함수 ---
def fix_youtube_url(url):
    if not url: return None
    url = url.replace("shorts/", "watch?v=")
    if "youtu.be/" in url: return f"https://www.youtube.com/watch?v={url.split('youtu.be/')[1].split('?')[0]}"
    if "m.youtube.com" in url: return url.replace("m.youtube.com", "www.youtube.com")
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
    time_str = task_dict.get('time', '')
    label = ""
    if sd and ed and sd != ed: label = f"[{sd} ~ {ed}]"
    elif sd and sd != "-": label = f"[{sd}]"
    if time_str: label += f" ⏱️{time_str}"
    return label + " " if label else ""

def safe_key(text): return re.sub(r'[\.\$#\[\]/]', '_', text)

def extract_date(d_str):
    if not d_str: return None
    m = re.search(r'\d{4}-\d{2}-\d{2}', d_str)
    if m:
        try: return datetime.strptime(m.group(0), "%Y-%m-%d").date()
        except: return None
    return None

def is_active_role_period(u_dict, target_date_str):
    u_dates = []
    for t in u_dict.get('workflow', []):
        sd, ed = get_date_range(t)
        sd_date = extract_date(sd)
        ed_date = extract_date(ed)
        if sd_date: u_dates.append(sd_date)
        if ed_date: u_dates.append(ed_date)
    if not u_dates: return True 
    try:
        target_d_obj = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        return min(u_dates) <= target_d_obj <= max(u_dates)
    except: return False

def clean_str_for_match(text): return re.sub(r'\s+', '', str(text).lower())

# ==============================================================
# ✨ [강력한 데이터 캐싱(최적화) 함수 모음]
# ==============================================================
@st.cache_data(show_spinner=False)
def prep_calendar_events(programs, users, sel_year, sel_month, today_string):
    day_events = defaultdict(list)
    for prog in programs:
        prog_color = prog.get('color', '#4f46e5')
        prog_title_full = prog.get('title', '')
        prog_title_short = prog_title_full[:8] + ".." if len(prog_title_full) > 8 else prog_title_full
        
        p_r_start = prog.get('recruit_start', today_string)
        p_r_end = prog.get('recruit_end', '2099-12-31')
        is_recruiting = (p_r_start <= today_string <= p_r_end)

        total_cap = 0; total_curr = 0
        roles_list = list(prog.get('roles_workflow', {}).items())
        for r, cap in prog.get('roles_capacity', {}).items():
            curr = sum(1 for u in users if u['program'] == prog_title_full and u['role'] == r)
            total_cap += cap; total_curr += curr

        if not is_recruiting: status_str = "대기/마감 (기간 외)"
        elif not roles_list or (total_curr >= total_cap and total_cap > 0): status_str = "모집 마감 (정원 초과)"
        else: status_str = "🟢 모집중"

        for role, tasks in prog.get('roles_workflow', {}).items():
            for t in tasks:
                sd_str, ed_str = get_date_range(t)
                if not sd_str: continue
                sd_date = extract_date(sd_str); ed_date = extract_date(ed_str)
                if sd_date and not ed_date: ed_date = sd_date
                if not sd_date and ed_date: sd_date = ed_date
                
                if sd_date and ed_date:
                    time_info = f"&#10;시간: {t.get('time')}" if t.get('time') else ""
                    tooltip_text = f"[{prog_title_full}]&#10;과업: {t['task']}{time_info}&#10;&#10;상태: {status_str}&#10;모집기간: {p_r_start} ~ {p_r_end}&#10;현재인원: {total_curr} / {total_cap}명&#10;&#10;👉 클릭하여 지원하기"
                    for d_ord in range(sd_date.toordinal(), ed_date.toordinal() + 1):
                        d = date.fromordinal(d_ord)
                        if d.year == sel_year and d.month == sel_month:
                            disp_title = f"[{prog_title_short}] {t['task']}"
                            day_events[d.day].append({"title": disp_title, "color": prog_color, "tooltip": tooltip_text, "prog_name": prog_title_full})
    return day_events

@st.cache_data(show_spinner=False)
def prep_student_dash(my_data):
    summary_rows = []; att_counts = {'출석': 0, '지각': 0, '결석': 0, '병결': 0}; trend_data = []
    for d in my_data:
        t_items = 0; d_items = 0; s_list = []
        for t in d['workflow']:
            t_items += 1; d_items += 1 if t.get('done') else 0
            if t.get('score', 0) > 0:
                s_list.append(t.get('score'))
                sd, _ = get_date_range(t)
                sd_date = extract_date(sd)
                if sd_date: trend_data.append({"날짜": sd_date.strftime("%Y-%m-%d"), "프로그램": d['program'], "점수": t['score']})
        pct = int((d_items/t_items)*100) if t_items > 0 else 0
        avg_s = sum(s_list)/len(s_list) if s_list else 0
        for d_key, att_info in d.get('attendance', {}).items():
            if is_active_role_period(d, d_key):
                st_val = att_info.get('status')
                if st_val in att_counts: att_counts[st_val] += 1
        summary_rows.append({"프로그램": d['program'], "역할": d['role'], "진행률(%)": pct, "평균 성취도": avg_s})
    return pd.DataFrame(summary_rows), att_counts, trend_data

@st.cache_data(show_spinner=False)
def prep_admin_dash(users, my_programs):
    users_to_show = [u for u in users if u['program'] in my_programs]
    dashboard_data = []; task_data = []; att_counts_total = {'출석': 0, '지각': 0, '결석': 0, '병결': 0}; trend_data = []; heat_data = []
    for u in users_to_show:
        t_scores = [t.get('score', 0) for t in u['workflow']]
        avg_score = sum(t_scores) / len(t_scores) if t_scores else 0
        att_counts = 0
        for d_key, v in u.get('attendance', {}).items():
            if is_active_role_period(u, d_key):
                st_val = v.get('status')
                if st_val == '출석': att_counts += 1
                if st_val in att_counts_total: att_counts_total[st_val] += 1
                heat_data.append({"학생명": u['name'], "날짜": d_key, "상태": st_val, "프로그램": u['program']})
        comment_counts = sum(1 for t in u['workflow'] if t.get('comment'))
        dashboard_data.append({"Program": u['program'], "Role": u['role'], "Student": u.get('alias') or u['name'], "AvgScore": avg_score, "Attendance": att_counts, "Comments": comment_counts})
        for t in u['workflow']:
            sc = t.get('score', 0)
            task_data.append({"Program": u['program'], "Task": t['task'], "Score": sc})
            sd, _ = get_date_range(t)
            sd_date = extract_date(sd)
            if sc > 0 and sd_date:
                trend_data.append({"날짜": sd_date.strftime("%Y-%m-%d"), "프로그램": u['program'], "점수": sc})
    return pd.DataFrame(dashboard_data), pd.DataFrame(task_data), att_counts_total, trend_data, heat_data

@st.cache_data(show_spinner=False)
def prep_finance(payments):
    df_pay = pd.DataFrame(payments).sort_values('date', ascending=False) if payments else pd.DataFrame()
    if df_pay.empty: return df_pay, 0, pd.DataFrame(), pd.DataFrame()
    total_rev = df_pay['amount'].sum()
    cat_sum = df_pay.groupby('category')['amount'].sum().reset_index()
    date_sum = df_pay.groupby('date')['amount'].sum().reset_index()
    return df_pay, total_rev, cat_sum, date_sum

# ==============================================================
# ✨ [데이터베이스 연결 로직]
# ==============================================================
# 🚨 [중요] 선생님의 파이어베이스 주소 입력
FIREBASE_URL = "https://youth-canvas-default-rtdb.firebaseio.com/data.json"

def load_data():
    try:
        response = requests.get(FIREBASE_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, dict):
                if 'programs' not in data: data['programs'] = []
                if 'users' not in data: data['users'] = []
                if 'parents' not in data: data['parents'] = []
                if 'payments' not in data: data['payments'] = []
                if 'admins' not in data: data['admins'] = [{"name": "마스터", "pin": "0000", "role": "super", "programs": []}]
                if 'settings' not in data: data['settings'] = {}
                if 'api_keys' not in data['settings']: data['settings']['api_keys'] = {"public_data": ""}
                return data
    except: pass
    return {"programs": [], "users": [], "parents": [], "payments": [], "admins": [{"name": "마스터", "pin": "0000", "role": "super", "programs": []}], "settings": {"api_keys": {"public_data": ""}}}

def save_data(data):
    try: 
        res = requests.put(FIREBASE_URL, json=data, timeout=15)
        if res.status_code == 200: return True
        else:
            st.error(f"🚨 서버 용량 초과 에러(400): 사진이나 영상 용량이 너무 큽니다. 관리자 탭에서 문제가 된 프로그램의 미디어를 삭제해주세요!")
            return False
    except Exception as e: 
        st.error(f"🚨 인터넷 연결이 불안정하거나 데이터가 너무 큽니다.")
        return False

if 'db' not in st.session_state: st.session_state['db'] = load_data()
db = st.session_state['db']

if 'users' not in db: db['users'] = []
if 'programs' not in db: db['programs'] = []
if 'parents' not in db: db['parents'] = []
if 'payments' not in db: db['payments'] = []
if 'admins' not in db: db['admins'] = [{"name": "마스터", "pin": "0000", "role": "super", "programs": []}]

default_terms = {"super": "최고관리자", "admin": "선생님", "staff": "행정", "user": "학생", "parent": "학부모"}
default_ui = {
    "brand_title": "Youth Canvas", "brand_subtitle": "청소년의 꿈을 그리는 공간",
    "menu1": "🔍 찾아보기 (탐색)", "menu2": "📅 전체 일정", "menu3": "🙋 나의 이야기", 
    "menu4": "👨‍👩‍👧 학부모 공간", "menu5": "🔒 관리자 전용 포털",
    "page1_title": "✨ 지금 뜨고 있는 활동", "page2_title": "🗓️ 기관 전체 일정표", 
    "page3_title": "🙋 나의 활동 진행도", "page4_title": "👨‍👩‍👧 학부모 전용 라운지", "page5_title": "🔒 관리자 전용 포털"
}

if 'settings' not in db: db['settings'] = {}
if 'terms' not in db['settings']: db['settings']['terms'] = default_terms
else:
    for k, v in default_terms.items():
        if k not in db['settings']['terms']: db['settings']['terms'][k] = v

if 'ui' not in db['settings']: db['settings']['ui'] = default_ui
else:
    UI_temp = db['settings']['ui']
    if 'menu5' not in UI_temp:
        UI_temp['menu5'] = UI_temp.get('menu4', default_ui['menu5']); UI_temp['menu4'] = UI_temp.get('menu3', default_ui['menu4'])
        UI_temp['menu3'] = UI_temp.get('menu2', default_ui['menu3']); UI_temp['menu2'] = default_ui['menu2']
        UI_temp['page5_title'] = UI_temp.get('page4_title', default_ui['page5_title']); UI_temp['page4_title'] = UI_temp.get('page3_title', default_ui['page4_title'])
        UI_temp['page3_title'] = UI_temp.get('page2_title', default_ui['page3_title']); UI_temp['page2_title'] = default_ui['page2_title']
        save_data(db)
    for k, v in default_ui.items():
        if k not in UI_temp: UI_temp[k] = v

if 'api_keys' not in db['settings']:
    db['settings']['api_keys'] = {"public_data": ""}

T_SUPER, T_ADMIN, T_STAFF, T_USER, T_PARENT = db['settings']['terms']['super'], db['settings']['terms']['admin'], db['settings']['terms']['staff'], db['settings']['terms']['user'], db['settings']['terms']['parent']
UI = db['settings']['ui']
menu_list = [UI['menu1'], UI['menu2'], UI['menu3'], UI['menu4'], UI['menu5']]

try:
    if hasattr(st, 'query_params') and 'target_menu' in st.query_params:
        if st.query_params['target_menu'] == 'apply':
            st.session_state.menu_option = UI['menu3']
            if 'prog' in st.query_params: st.session_state['selected_prog_from_main'] = urllib.parse.unquote(st.query_params['prog'])
        st.query_params.clear()
except: pass

if 'menu_option' not in st.session_state or st.session_state.menu_option not in menu_list: st.session_state.menu_option = UI['menu1']
def change_page(page_name): st.session_state.menu_option = page_name; st.rerun()

with st.sidebar:
    st.markdown(f"<div style='margin-bottom: 2rem; padding: 0 10px;'><div style='font-size: 2.8rem; font-weight: 900; color: #ffffff; line-height: 1.1;'>{UI['brand_title']}</div><div style='font-size: 1.2rem; font-weight: 800; color: #ffce31;'>{UI['brand_subtitle']}</div></div>", unsafe_allow_html=True)
    menu = st.radio("메뉴 이동", menu_list, index=menu_list.index(st.session_state.menu_option), label_visibility="collapsed")
    if st.button("🔄 최신 데이터 동기화", use_container_width=True):
        st.session_state['db'] = load_data(); st.toast("✅ 동기화 완료!"); time.sleep(1); st.rerun()
st.session_state.menu_option = menu

# ✨ 전역으로 '오늘 날짜' 변수를 설정하여 모든 탭에서 활용
today_str = datetime.now().strftime("%Y-%m-%d")

# =========================================================
# [페이지 1] 찾아보기 (탐색)
# =========================================================
if st.session_state.menu_option == UI['menu1']:
    st.markdown(f"## {UI['page1_title']}")
    if not db['programs']: st.info("아직 개설된 프로그램이 없습니다. 관리자 페이지에서 프로그램을 만들어주세요.")
        
    col1, col2 = st.columns(2)
    for idx, prog in enumerate(db['programs']):
        with (col1 if idx % 2 == 0 else col2):
            with st.container(border=True):
                p_r_start = prog.get('recruit_start', today_str); p_r_end = prog.get('recruit_end', '2099-12-31')
                is_recruiting_period = (p_r_start <= today_str <= p_r_end)
                roles_list = list(prog.get('roles_workflow', {}).items())
                is_all_full = True; total_cap = 0; total_curr = 0
                for r, _ in roles_list:
                    cap = prog.get('roles_capacity', {}).get(r, 10)
                    curr = sum(1 for u in db['users'] if u['program'] == prog['title'] and u['role'] == r)
                    total_cap += cap; total_curr += curr
                    if curr < cap: is_all_full = False
                
                if not roles_list: is_all_full = True
                
                if not is_recruiting_period: status_badge = "<span class='badge-gray'>⏳ 기간종료</span>"
                elif is_all_full: status_badge = "<span class='badge-red'>🔴 모집마감</span>"
                else: status_badge = "<span class='badge-green'>🟢 모집중</span>"
                    
                st.markdown(f"{status_badge}", unsafe_allow_html=True)
                st.markdown(f"<div class='card-title' style='border-left: 5px solid {prog.get('color', '#4f46e5')}; padding-left: 8px;'>{prog['title']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='recruit-period'>🗓️ 모집 기간: {p_r_start} ~ {p_r_end}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='card-desc'>{prog['desc']}</div>", unsafe_allow_html=True)
                
                m_type = prog.get('media_type', 'url')
                m_url = prog.get('media_url', prog.get('video', ''))
                
                if m_url:
                    if m_type == 'url':
                        clean_url = fix_youtube_url(m_url)
                        if clean_url: st.video(clean_url)
                    elif m_type == 'image': st.image(m_url, use_container_width=True)
                    elif m_type == 'video': st.video(m_url)
                
                tags_html = "".join([f"<span class='badge-blue'>#{r}</span> " for r, _ in roles_list])
                if tags_html: st.markdown(f"<div style='margin-bottom: 15px;'>{tags_html}</div>", unsafe_allow_html=True)
                
                flat_tasks = []
                for role, tasks in prog.get('roles_workflow', {}).items():
                    for t in tasks:
                        sd, ed = get_date_range(t)
                        date_label = f"{sd} ~ {ed}" if sd and ed and sd != ed else (sd if sd and sd != "-" else "일정 미정")
                        time_val = t.get('time', '')
                        if not time_val: time_val = "-"
                        sub_texts = [stask['desc'] for stask in t.get('subtasks', [])]
                        subs_html = "<br>".join([f"&nbsp;&nbsp;└ {desc}" for desc in sub_texts])
                        task_display = f"<b>{t['task']}</b><br><span style='color:#64748b; font-size:0.9em;'>{subs_html}</span>" if sub_texts else f"<b>{t['task']}</b>"
                        sd_date = extract_date(sd)
                        sort_key = sd_date.strftime("%Y-%m-%d") if sd_date else "9999-12-31"
                        flat_tasks.append({"sort_key": sort_key, "date_label": date_label, "time": time_val, "role": role, "task": task_display})
                
                if flat_tasks:
                    flat_tasks.sort(key=lambda x: x['sort_key'])
                    with st.expander("📅 전체 일정 요약 보기"):
                        html_table = "<table class='schedule-table'><tr><th>일정(날짜)</th><th>시간</th><th>역할</th><th>상세 내용</th></tr>"
                        for ft in flat_tasks: html_table += f"<tr><td style='font-weight:bold; white-space:nowrap;'>{ft['date_label']}</td><td style='white-space:nowrap; color:#b45309;'>{ft['time']}</td><td><span class='badge-blue'>{ft['role']}</span></td><td class='task-content'>{ft['task']}</td></tr>"
                        html_table += "</table>"
                        st.markdown(html_table, unsafe_allow_html=True)

                st.write(f"**현재 참여 인원** ({total_curr}/{total_cap}명)")
                st.progress(total_curr/total_cap if total_cap > 0 else 0)
                
                can_apply = is_recruiting_period and not is_all_full
                if st.button("🚀 이 프로그램 지원하기", key=f"apply_{idx}", use_container_width=True, type="primary", disabled=not can_apply):
                    st.session_state['selected_prog_from_main'] = prog['title']; change_page(UI['menu3'])

# =========================================================
# [페이지 2] ✨ 전체 일정 (독립된 달력 탭)
# =========================================================
elif st.session_state.menu_option == UI['menu2']:
    st.markdown(f"## {UI['page2_title']}")
    st.info("💡 일정을 클릭하면 즉시 수강신청 화면으로 이동합니다!")
    
    now = datetime.now()
    c_col1, c_col2 = st.columns([2, 8])
    sel_year = c_col1.selectbox("년도 선택", range(now.year-1, now.year+3), index=1)
    sel_month = c_col2.select_slider("월 선택", range(1, 13), value=now.month)
    
    cal = calendar.monthcalendar(sel_year, sel_month)
    st.markdown(f"<h3 style='text-align:center; margin-bottom:20px;'>{sel_year}년 {sel_month}월</h3>", unsafe_allow_html=True)
    
    day_events = prep_calendar_events(db['programs'], db['users'], sel_year, sel_month, today_str)

    html_cal = "<table class='cal-table'><tr>"
    days = ["월", "화", "수", "목", "금", "토", "일"]
    for day in days: html_cal += f"<th class='cal-th'>{day}</th>"
    html_cal += "</tr>"
    for week in cal:
        html_cal += "<tr>"
        for day in week:
            if day == 0: html_cal += "<td class='cal-td empty'></td>"
            else:
                events_html = "".join([f"<a href='/?target_menu=apply&prog={urllib.parse.quote(ev['prog_name'])}' target='_self' style='text-decoration: none;'><div class='cal-event' style='background:{ev['color']};' title='{ev['tooltip']}'>{ev['title']}</div></a>" for ev in day_events.get(day, [])])
                html_cal += f"<td class='cal-td'><div class='cal-day-num'>{day}</div>{events_html}</td>"
        html_cal += "</tr>"
    html_cal += "</table>"
    st.markdown(html_cal, unsafe_allow_html=True)

# =========================================================
# [페이지 3] 나의 이야기 (학생 화면)
# =========================================================
elif st.session_state.menu_option == UI['menu3']:
    st.markdown(f"## {UI['page3_title']}")
    tab1, tab2 = st.tabs(["📝 신규 프로그램 지원", "🎯 나의 목표 및 진행도 (로그인)"])
    
    with tab1:
        prog_titles = [p['title'] for p in db['programs']]
        if not prog_titles: st.warning("개설된 프로그램이 없습니다.")
        else:
            active_programs = [p['title'] for p in db['programs'] if p.get('recruit_start', today_str) <= today_str <= p.get('recruit_end', '2099-12-31')]
            if not active_programs: st.error("⏳ 현재 모집 중인 프로그램이 없습니다.")
            else:
                default_idx = active_programs.index(st.session_state['selected_prog_from_main']) if 'selected_prog_from_main' in st.session_state and st.session_state['selected_prog_from_main'] in active_programs else 0
                
                with st.container(border=True):
                    selected_prog_title = st.selectbox("🎯 참여할 프로그램 선택 (먼저 선택해주세요)", active_programs, index=default_idx)
                    selected_prog_data = next(p for p in db['programs'] if p['title'] == selected_prog_title)
                    
                    with st.form("apply_student_form", clear_on_submit=True):
                        st.markdown("##### 📝 신규 지원서 작성")
                        colA, colB = st.columns(2)
                        user_name = colA.text_input(f"👤 {T_USER} 이름 (예: 권해리 어머니, John Doe 등 자유롭게)")
                        user_pin = colB.text_input("🔑 접속 비밀번호 (숫자/문자 무관 4자리)", type="password", max_chars=4)
                        
                        role_options = []
                        for r, cap in selected_prog_data.get('roles_capacity', {}).items():
                            curr = sum(1 for u in db['users'] if u['program'] == selected_prog_title and u['role'] == r)
                            role_options.append(f"{r} || ({curr}/{cap}명) - {'지원가능' if curr < cap else '마감'}")
                        selected_role_strs = st.multiselect("🎭 희망 역할 (여러 개 동시 선택 가능)", role_options, format_func=lambda x: x.replace(" || ", " "))
                        
                        if st.form_submit_button("✨ 최종 지원하기", use_container_width=True, type="primary"):
                            user_name_clean = user_name.strip()
                            user_pin_clean = user_pin.strip()
                            
                            if not user_name_clean or not user_pin_clean: st.error("이름과 비밀번호를 모두 입력하세요.")
                            elif not selected_role_strs: st.error("희망 역할을 하나 이상 선택해주세요.")
                            elif any("마감" in r for r in selected_role_strs): st.error("마감된 역할이 포함되어 있습니다.")
                            else:
                                added_count = 0
                                for r_str in selected_role_strs:
                                    actual_role = r_str.split(" || ")[0]
                                    my_tasks = copy.deepcopy(selected_prog_data.get('roles_workflow', {}).get(actual_role, []))
                                    for t in my_tasks: t['score'] = 0; t['comment'] = ""
                                    db['users'].append({"name": user_name_clean, "pin": user_pin_clean, "program": selected_prog_title, "role": actual_role, "workflow": my_tasks, "messages": [], "parent_messages": [], "alias": "", "attendance": {}})
                                    added_count += 1
                                if save_data(db): 
                                    st.balloons()
                                    st.success("🎉 지원이 완벽하게 완료되었습니다! 위쪽의 [나의 목표 및 진행도] 탭을 눌러 로그인해보세요.")
                                    time.sleep(2); st.rerun()
                                else:
                                    for _ in range(added_count): db['users'].pop()
                                    st.error("🚨 서버 응답 지연: 프로그램에 대용량 이미지가 포함되어 있을 수 있습니다. 관리자에게 문의하세요.")

    with tab2:
        with st.container(border=True):
            with st.form("student_login_form"):
                col_id, col_pw, col_btn = st.columns([4, 4, 2])
                search_name = col_id.text_input(f"{T_USER} 이름", placeholder="예: 홍길동 어머니, John Doe")
                search_pin = col_pw.text_input("비밀번호 (4자리)", type="password")
                login_attempt = col_btn.form_submit_button("접속하기", use_container_width=True)
            
            if login_attempt or (search_name and search_pin):
                s_name_clean = clean_str_for_match(search_name)
                s_pin_clean = str(search_pin).strip()
                my_data = [u for u in db['users'] if clean_str_for_match(u['name']) == s_name_clean and str(u.get('pin', '0000')).strip() == s_pin_clean]
                
                if not my_data and login_attempt: st.error("정보가 일치하지 않습니다. 이름의 띄어쓰기나 비밀번호를 확인해주세요.")
                elif my_data:
                    st.divider()
                    st.markdown(f"### 🌟 **{my_data[0]['name']}**님의 맞춤형 대시보드")
                    st.info("💡 차트의 범례(글씨)를 클릭하면 데이터를 켜고 끌 수 있습니다.")
                    
                    s_chart_options = ["막대 그래프 (프로그램별 성취도) [추천]", "도넛 차트 (나의 종합 출결 비율)", "라인 그래프 (성취도 변화 추이)"]
                    selected_s_charts = st.multiselect("📊 보고 싶은 차트를 선택하세요 (다중 선택 가능):", s_chart_options, default=s_chart_options)
                    
                    df_summ, att_counts, trend_data = prep_student_dash(my_data)
                    
                    if "막대 그래프 (프로그램별 성취도) [추천]" in selected_s_charts and not df_summ.empty:
                        with st.container(border=True):
                            st.markdown("##### 📊 프로그램별 달성률 및 성취도")
                            c1, c2 = st.columns(2)
                            fig_s1 = px.bar(df_summ, x='프로그램', y='진행률(%)', color='프로그램', text='진행률(%)', title='활동 진행률')
                            fig_s1.update_traces(textposition='outside'); fig_s1.update_layout(yaxis=dict(range=[0, 105]), showlegend=False)
                            c1.plotly_chart(fig_s1, use_container_width=True)
                            
                            fig_s2 = px.bar(df_summ, x='프로그램', y='평균 성취도', color='프로그램', text='평균 성취도', title='선생님 평가 성취도')
                            fig_s2.update_traces(texttemplate='%{text:.1f}', textposition='outside'); fig_s2.update_layout(yaxis=dict(range=[0, 105]), showlegend=False)
                            c2.plotly_chart(fig_s2, use_container_width=True)

                            if df_summ['진행률(%)'].max() == 0 and df_summ['평균 성취도'].max() == 0: st.info("📉 진행된 목표나 평가가 없습니다.")
                            else: st.markdown(f"<div class='report-box'><div class='pos-text'>🟢 긍정적 시그널: '{df_summ.loc[df_summ['진행률(%)'].idxmax()]['프로그램']}'의 달성률이 가장 높습니다!</div></div>", unsafe_allow_html=True)

                    if "도넛 차트 (나의 종합 출결 비율)" in selected_s_charts:
                        with st.container(border=True):
                            st.markdown("##### 🍩 나의 종합 출결 비율")
                            total_att = sum(att_counts.values())
                            if total_att == 0: st.info("📉 기록된 출결 데이터가 없습니다.")
                            else:
                                labels = [k for k, v in att_counts.items() if v > 0]
                                sizes = [v for v in att_counts.values() if v > 0]
                                fig_d = px.pie(names=labels, values=sizes, hole=0.4, color=labels, color_discrete_map=ATT_COLORS, title=f"총 {total_att}일 출결 기록")
                                fig_d.update_traces(textposition='inside', textinfo='percent+label')
                                st.plotly_chart(fig_d, use_container_width=True)
                                
                                bad_att = att_counts.get('지각', 0) + att_counts.get('결석', 0)
                                if bad_att == 0: st.markdown("<div class='report-box'><div class='pos-text'>🟢 긍정적 시그널: 지각과 결석이 단 한 번도 없습니다! 완벽한 출석률입니다.</div></div>", unsafe_allow_html=True)
                                else: st.markdown(f"<div class='report-box'><div class='neg-text'>🔴 주의 요망: 지각/결석이 총 {bad_att}회 있습니다. 성실한 참여를 위해 출결 관리에 신경 써주세요.</div></div>", unsafe_allow_html=True)

                    if "라인 그래프 (성취도 변화 추이)" in selected_s_charts:
                        with st.container(border=True):
                            st.markdown("##### 📈 시간 흐름별 성취도 변화 추이")
                            if len(trend_data) < 2: st.info("📉 점수가 2건 이상 누적되어야 추이 그래프를 볼 수 있습니다.")
                            else:
                                df_trend = pd.DataFrame(trend_data).sort_values(by="날짜")
                                fig_l = px.line(df_trend, x='날짜', y='점수', color='프로그램', markers=True)
                                fig_l.update_yaxes(range=[0, 105])
                                st.plotly_chart(fig_l, use_container_width=True)
                                
                                first_score = df_trend.iloc[0]['점수']
                                last_score = df_trend.iloc[-1]['점수']
                                if last_score > first_score: st.markdown(f"<div class='report-box'><div class='pos-text'>🟢 긍정적 시그널: 첫 활동보다 성취도가 상승하고 있습니다! ({first_score}점 ➔ {last_score}점)</div></div>", unsafe_allow_html=True)
                                elif last_score < first_score: st.markdown(f"<div class='report-box'><div class='neg-text'>🔴 주의 요망: 초기보다 성취도가 다소 하락했습니다. ({first_score}점 ➔ {last_score}점)</div></div>", unsafe_allow_html=True)
                                else: st.markdown(f"<div class='report-box'><div class='info-text'>ℹ️ 안정적 시그널: 꾸준한 성적을 유지하고 있습니다.</div></div>", unsafe_allow_html=True)

                    st.divider()
                    st.markdown("### 🔍 개별 프로그램 세부 리포트")
                    for u_idx, data in enumerate(my_data):
                        with st.expander(f"📁 {data['program']} ({data['role']}) 상세 보기", expanded=False):
                            tasks = data['workflow']
                            total_items = 0; done_items = 0
                            for t in tasks:
                                total_items += 1; done_items += 1 if t.get('done') else 0
                                for stask in t.get('subtasks', []): total_items += 1; done_items += 1 if stask.get('done') else 0
                            pct = int((done_items/total_items)*100) if total_items > 0 else 0
                            st.metric("활동 달성률", f"{pct}%", f"{done_items} / {total_items} 완료")
                            st.progress(pct / 100)

                            st.write("#### ✅ 세부 활동 체크리스트")
                            with st.container(border=True):
                                changed = False
                                for idx, t in enumerate(tasks):
                                    is_done = st.checkbox(f"**{get_date_label(t)}{t['task']}**", value=t.get('done'), key=f"chk_{search_name}_{data['program']}_{u_idx}_{idx}")
                                    if is_done != t.get('done'): t['done'] = is_done; changed = True
                                    for s_idx, stask in enumerate(t.get('subtasks', [])):
                                        col_empty, col_chk = st.columns([1, 20])
                                        with col_chk:
                                            sub_done = st.checkbox(f"↳ {stask['desc']}", value=stask.get('done'), key=f"chk_sub_{search_name}_{data['program']}_{u_idx}_{idx}_{s_idx}")
                                            if sub_done != stask.get('done'): stask['done'] = sub_done; changed = True
                                if changed: 
                                    if save_data(db): st.rerun()

                            st.write(f"#### 💬 {T_ADMIN}과 1:1 비밀 소통 게시판 ({T_USER} 전용)")
                            chat_box = st.container(border=True, height=250)
                            with chat_box:
                                if not data.get('messages'): st.info("아직 나눈 대화가 없습니다.")
                                for msg in data.get('messages', []):
                                    with st.chat_message("user" if msg['sender'] == 'user' else "assistant"): st.write(msg['content'])
                            with st.form(f"chat_form_{search_name}_{data['program']}_{u_idx}", clear_on_submit=True):
                                c1, c2 = st.columns([8, 2])
                                msg_input = c1.text_input("메시지 입력", label_visibility="collapsed")
                                if c2.form_submit_button("전송") and msg_input:
                                    data.setdefault('messages', []).append({"sender": "user", "content": msg_input})
                                    if save_data(db): st.rerun()

# =========================================================
# [페이지 4] 학부모 전용 라운지
# =========================================================
elif st.session_state.menu_option == UI['menu4']:
    st.markdown(f"## {UI['page4_title']}")
    st.caption(f"발급받으신 개별 {T_PARENT} 계정으로 로그인하여 자녀의 성장 기록과 커리큘럼을 확인하세요.")
    
    with st.container(border=True):
        with st.form("parent_login_form"):
            col_id, col_pw, col_btn = st.columns([4, 4, 2])
            parent_name = col_id.text_input(f"{T_PARENT} 성함", placeholder="예: 권해리 어머니, John Doe")
            parent_pin = col_pw.text_input(f"{T_PARENT} 전용 비밀번호 (4자리)", type="password")
            login_attempt = col_btn.form_submit_button("로그인", use_container_width=True)
        
        if login_attempt or (parent_name and parent_pin):
            p_name_clean = clean_str_for_match(parent_name)
            p_pin_clean = str(parent_pin).strip()
            
            my_parent_data = [p for p in db['parents'] if clean_str_for_match(p['name']) == p_name_clean and str(p.get('pin', '')).strip() == p_pin_clean]
            
            if not my_parent_data and login_attempt:
                st.error("정보가 일치하지 않습니다.")
            elif my_parent_data:
                p_info = my_parent_data[0]
                st.success(f"환영합니다, **{p_info['name']}**님! 😊")
                linked_students = p_info.get('linked_students', [])
                
                if not linked_students:
                    st.info(f"아직 연결된 정보가 없습니다. 기관에 문의해주세요.")
                else:
                    p_summary_rows = []; att_counts_total = {'출석': 0, '지각': 0, '결석': 0, '병결': 0}; trend_data_p = []
                    for s_info in linked_students:
                        s_record = next((u for u in db['users'] if u['name'] == s_info['name'] and u['program'] == s_info['program']), None)
                        if s_record:
                            tasks = s_record['workflow']
                            t_items, d_items, s_list = 0, 0, []
                            for t in tasks:
                                t_items += 1; d_items += 1 if t.get('done') else 0
                                if t.get('score', 0) > 0: 
                                    s_list.append(t.get('score'))
                                    sd, _ = get_date_range(t)
                                    sd_date = extract_date(sd)
                                    if sd_date: trend_data_p.append({"날짜": sd_date.strftime("%Y-%m-%d"), "자녀명": s_record['name'], "점수": t['score'], "프로그램": s_record['program']})
                                for stask in t.get('subtasks', []): t_items += 1; d_items += 1 if stask.get('done') else 0
                                    
                            pct = int((d_items/t_items)*100) if t_items > 0 else 0
                            avg_s = sum(s_list)/len(s_list) if s_list else 0
                            
                            s_att = {'출석': 0, '지각': 0, '결석': 0, '병결': 0}
                            for d_key, att_info in s_record.get('attendance', {}).items():
                                if is_active_role_period(s_record, d_key):
                                    st_val = att_info.get('status')
                                    if st_val in s_att:
                                        s_att[st_val] += 1
                                        att_counts_total[st_val] += 1
                                    
                            p_summary_rows.append({"자녀명": s_record['name'], "프로그램": s_record['program'], "라벨": f"{s_record['name']}\n({s_record['program']})", "진행률(%)": pct, "평균 성취도": avg_s, "결석_지각": s_att['결석'] + s_att['지각']})

                    tab_names = ["🌟 자녀 종합 대시보드"] + [f"👦👧 {s['name']} ({s['program']})" for s in linked_students]
                    parent_tabs = st.tabs(tab_names)
                    
                    with parent_tabs[0]:
                        if not p_summary_rows: st.warning("데이터가 없습니다.")
                        else:
                            st.markdown(f"### 🌟 자녀 종합 대시보드")
                            p_chart_options = ["막대 그래프 (자녀별 성취도/진행률) [추천]", "도넛 차트 (자녀 통합 출결 비율)", "라인 그래프 (자녀별 성취도 추이)"]
                            selected_p_charts = st.multiselect("📊 보고 싶은 차트를 선택하세요:", p_chart_options, default=p_chart_options)
                            df_p_summ = pd.DataFrame(p_summary_rows)
                            
                            if "막대 그래프 (자녀별 성취도/진행률) [추천]" in selected_p_charts and not df_p_summ.empty:
                                p_col1, p_col2 = st.columns(2)
                                with p_col1:
                                    with st.container(border=True):
                                        st.markdown(f"##### 📊 자녀별 프로그램 진행률")
                                        fig_p1 = px.bar(df_p_summ, x='라벨', y='진행률(%)', color='자녀명', text='진행률(%)')
                                        fig_p1.update_traces(textposition='outside'); fig_p1.update_layout(yaxis=dict(range=[0, 105]), showlegend=False)
                                        st.plotly_chart(fig_p1, use_container_width=True)
                                        if df_p_summ['진행률(%)'].max() > 0: st.markdown(f"<div class='report-box'><div class='pos-text'>🟢 긍정적 시그널: {df_p_summ.loc[df_p_summ['진행률(%)'].idxmax()]['자녀명']} {T_USER}의 활동이 가장 활발합니다.</div></div>", unsafe_allow_html=True)
                                        
                                with p_col2:
                                    with st.container(border=True):
                                        st.markdown(f"##### 📊 자녀별 평균 성취도")
                                        fig_p2 = px.bar(df_p_summ, x='라벨', y='평균 성취도', color='자녀명', text='평균 성취도')
                                        fig_p2.update_traces(texttemplate='%{text:.1f}', textposition='outside'); fig_p2.update_layout(yaxis=dict(range=[0, 105]), showlegend=False)
                                        st.plotly_chart(fig_p2, use_container_width=True)
                                        if df_p_summ['평균 성취도'].max() > 0: st.markdown(f"<div class='report-box'><div class='pos-text'>🟢 긍정적 시그널: {df_p_summ.loc[df_p_summ['평균 성취도'].idxmax()]['자녀명']} {T_USER}의 성취도가 뛰어납니다.</div></div>", unsafe_allow_html=True)
                            
                            if "도넛 차트 (자녀 통합 출결 비율)" in selected_p_charts:
                                with st.container(border=True):
                                    st.markdown("##### 🍩 자녀 통합 종합 출결 비율")
                                    total_att_p = sum(att_counts_total.values())
                                    if total_att_p > 0:
                                        labels = [k for k, v in att_counts_total.items() if v > 0]
                                        sizes = [v for v in att_counts_total.values() if v > 0]
                                        colors = ['#2ECC71', '#FFC107', '#E74C3C', '#9B59B6'][:len(labels)]
                                        fig_dp = px.pie(names=labels, values=sizes, hole=0.4, color=labels, color_discrete_map=ATT_COLORS, title=f"통합 출석일수: {total_att_p}일")
                                        fig_dp.update_traces(textposition='inside', textinfo='percent+label')
                                        st.plotly_chart(fig_dp, use_container_width=True)
                                        bad_att_p = att_counts_total.get('지각', 0) + att_counts_total.get('결석', 0)
                                        if bad_att_p == 0: st.markdown("<div class='report-box'><div class='pos-text'>🟢 긍정적 시그널: 완벽한 출결 관리입니다.</div></div>", unsafe_allow_html=True)
                                        else: st.markdown(f"<div class='report-box'><div class='neg-text'>🔴 주의 요망: 지각/결석 누적 {bad_att_p}회 입니다.</div></div>", unsafe_allow_html=True)
                            
                            if "라인 그래프 (자녀별 성취도 추이)" in selected_p_charts and len(trend_data_p) >= 2:
                                with st.container(border=True):
                                    st.markdown("##### 📈 시간 흐름별 성취도 변화 추이")
                                    df_trend_p = pd.DataFrame(trend_data_p).sort_values(by="날짜")
                                    df_trend_p['분류'] = df_trend_p['자녀명'] + " (" + df_trend_p['프로그램'] + ")"
                                    fig_lp = px.line(df_trend_p, x='날짜', y='점수', color='분류', markers=True)
                                    fig_lp.update_yaxes(range=[0, 105])
                                    st.plotly_chart(fig_lp, use_container_width=True)
                                    
                                    first_score_p = df_trend_p.iloc[0]['점수']
                                    last_score_p = df_trend_p.iloc[-1]['점수']
                                    if last_score_p > first_score_p: st.markdown(f"<div class='report-box'><div class='pos-text'>🟢 긍정적 시그널: 자녀의 성취도가 상승하고 있습니다! ({first_score_p}점 ➔ {last_score_p}점)</div></div>", unsafe_allow_html=True)
                                    elif last_score_p < first_score_p: st.markdown(f"<div class='report-box'><div class='neg-text'>🔴 주의 요망: 자녀의 성취도가 다소 하락했습니다. 격려가 필요합니다. ({first_score_p}점 ➔ {last_score_p}점)</div></div>", unsafe_allow_html=True)
                                    else: st.markdown(f"<div class='report-box'><div class='info-text'>ℹ️ 안정적 시그널: 꾸준한 성적을 유지하고 있습니다.</div></div>", unsafe_allow_html=True)

                    for idx, s_info in enumerate(linked_students):
                        with parent_tabs[idx + 1]:
                            s_record = next((u for u in db['users'] if u['name'] == s_info['name'] and u['program'] == s_info['program']), None)
                            if s_record:
                                st.markdown(f"### 🏅 [{s_record['program']}] 참가자 **{s_record['name']}**님")
                                tasks = s_record['workflow']
                                with st.container(border=True):
                                    for t_idx, t in enumerate(tasks):
                                        st.checkbox(f"**{get_date_label(t)}{t['task']}**", value=t.get('done'), disabled=True, key=f"p_c_{idx}_{t_idx}")
                                chat_box = st.container(border=True, height=250)
                                with chat_box:
                                    for msg in s_record.get('parent_messages', []):
                                        with st.chat_message("user" if msg['sender'] == 'user' else "assistant"): st.write(msg['content'])
                                    with st.form(f"p_chat_{idx}", clear_on_submit=True):
                                        c1, c2 = st.columns([8, 2])
                                        msg_input = c1.text_input("메시지 입력", label_visibility="collapsed")
                                        if c2.form_submit_button("전송") and msg_input:
                                            s_record.setdefault('parent_messages', []).append({"sender": "user", "content": f"[{p_info['name']}] {msg_input}"})
                                            save_data(db); st.rerun()

# =========================================================
# [페이지 5] ✨ 관리자 전용 포털
# =========================================================
elif st.session_state.menu_option == UI['menu5']:
    if not st.session_state.get('admin_logged_in', False):
        st.markdown(f"## {UI['page5_title']}")
        with st.container(border=True):
            st.info("💡 초기 세팅: 이름 [ 마스터 ], 비밀번호 [ 0000 ]")
            with st.form("admin_login_form"):
                login_name = st.text_input("관리자 이름")
                login_pin = st.text_input("비밀번호 4자리", type="password", max_chars=4)
                if st.form_submit_button("로그인", type="primary"):
                    matched_admin = next((a for a in db.get('admins', []) if a['name'] == login_name and a['pin'] == login_pin), None)
                    if matched_admin:
                        st.session_state['admin_logged_in'] = True; st.session_state['logged_admin'] = matched_admin; st.rerun()
                    else: st.error("인증 실패: 정보가 틀렸습니다.")
    else:
        admin_info = st.session_state['logged_admin']
        is_super = (admin_info['role'] == 'super')
        is_staff = (admin_info['role'] == 'staff')
        is_normal = (admin_info['role'] == 'normal')
        
        if is_super or is_staff: my_programs = [p['title'] for p in db['programs']]
        else: my_programs = admin_info.get('programs', [])

        col_title, col_logout = st.columns([8, 2])
        col_title.markdown(f"## 🛠️ 시설 통합 관리 시스템 <span style='font-size:0.5em; color:gray;'>[{admin_info['name']} 접속중]</span>", unsafe_allow_html=True)
        if col_logout.button("🔓 로그아웃", use_container_width=True): st.session_state['admin_logged_in'] = False; st.rerun()
            
        tab_parent_title = f"👨‍👩‍👧 {T_PARENT} 계정"
        
        if is_super:
            tabs = st.tabs(["📈 경영 대시보드", "💳 행정/재무 관리", "📊 종합 명단", "📝 신규 개설", "⚙️ 정보 수정", "📝 평가/코멘트 작성", "✅ 출석 관리", "👥 1:1 상담", tab_parent_title, "🎨 화면 설정", "🔐 계정 관리"])
            tab_dashboard, tab_finance, tab_overview, tab_create, tab_edit, tab_eval, tab_attendance, tab_manage_users, tab_parents, tab_ui, tab_settings = tabs
        elif is_staff:
            tabs = st.tabs(["📈 경영 대시보드", "💳 행정/재무 관리", "📊 종합 명단", "📝 신규 개설", "⚙️ 정보 수정", "📝 평가/코멘트 작성", "✅ 출석 관리", "👥 1:1 상담", tab_parent_title, "🔐 계정 관리"])
            tab_dashboard, tab_finance, tab_overview, tab_create, tab_edit, tab_eval, tab_attendance, tab_manage_users, tab_parents, tab_settings = tabs
        else:
            tabs = st.tabs(["📈 경영 대시보드", "📝 평가/코멘트 작성", "📊 종합 명단", "✅ 출석 관리", "👥 1:1 상담", tab_parent_title, "🔐 계정 관리"])
            tab_dashboard, tab_eval, tab_overview, tab_attendance, tab_manage_users, tab_parents, tab_settings = tabs

        # ---------------------------------------------------------
        # 경영 대시보드
        with tab_dashboard:
            dashboard_title = f"{T_SUPER} 전용" if is_super else f"{admin_info['name']} {T_ADMIN} 전용"
            st.subheader(f"📈 {dashboard_title} 맞춤형 데이터 대시보드")
            df_dash, df_tasks, att_counts_total, trend_data, heat_data = prep_admin_dash(db['users'], my_programs)
            
            if df_dash.empty: 
                st.info(f"데이터가 부족하여 대시보드를 생성할 수 없습니다.")
            else:
                st.info("💡 핫팁: 차트 우측의 **범례(글씨)**를 클릭하여 껐다 켤 수 있으며, **상단의 카메라(📷) 아이콘**을 클릭하면 이미지를 다운로드할 수 있습니다.")
                chart_options = ["막대 그래프 (프로그램별 평균 성취도)", "도넛 차트 (전체 출결 비율)", "라인 그래프 (성취도 추이)", "히트맵 (출결 밀도)", "산점도 (피드백 효과)", "스택 막대 그래프 (출결 상세)"]
                selected_charts = st.multiselect("📊 화면에 띄울 차트를 선택하세요:", chart_options, default=["막대 그래프 (프로그램별 평균 성취도)", "산점도 (피드백 효과)"])
                st.write("")
                
                if "막대 그래프 (프로그램별 평균 성취도)" in selected_charts and not df_dash.empty:
                    with st.container(border=True):
                        st.markdown(f"##### 📊 막대 그래프: 프로그램별 평균 성취도 비교")
                        df_avg = df_dash.groupby('Program')['AvgScore'].mean().reset_index()
                        fig1 = px.bar(df_avg, x='Program', y='AvgScore', color='Program', text='AvgScore', title="프로그램별 전체 평균 점수")
                        fig1.update_traces(texttemplate='%{text:.1f}', textposition='outside'); fig1.update_layout(yaxis=dict(range=[0, 105]))
                        st.plotly_chart(fig1, use_container_width=True)
                        
                        top_p = df_avg.loc[df_avg['AvgScore'].idxmax()]
                        st.markdown(f"<div class='report-box'><div class='pos-text'>🟢 긍정적 시그널: '{top_p['Program']}' 프로그램이 평균 {top_p['AvgScore']:.1f}점으로 가장 우수합니다.</div></div>", unsafe_allow_html=True)

                if "도넛 차트 (전체 출결 비율)" in selected_charts:
                    with st.container(border=True):
                        st.markdown(f"##### 🍩 도넛 차트: 시설 전체 {T_USER} 출결 비율")
                        total_att = sum(att_counts_total.values())
                        if total_att > 0:
                            labels = [k for k, v in att_counts_total.items() if v > 0]
                            sizes = [v for v in att_counts_total.values() if v > 0]
                            colors = ['#2ECC71', '#FFC107', '#E74C3C', '#9B59B6'][:len(labels)]
                            fig_d = px.pie(names=labels, values=sizes, hole=0.4, color=labels, color_discrete_map=ATT_COLORS, title="통합 출석 현황")
                            fig_d.update_traces(textposition='inside', textinfo='percent+label')
                            st.plotly_chart(fig_d, use_container_width=True)
                            
                            bad_ratio = ((att_counts_total.get('지각', 0) + att_counts_total.get('결석', 0)) / total_att) * 100
                            if bad_ratio < 10: st.markdown("<div class='report-box'><div class='pos-text'>🟢 긍정적 시그널: 전체 지각/결석 비율이 10% 미만으로 매우 안정적입니다.</div></div>", unsafe_allow_html=True)
                            else: st.markdown(f"<div class='report-box'><div class='neg-text'>🔴 주의 요망: 전체 결석 및 지각 비율이 {bad_ratio:.1f}%에 달합니다.</div></div>", unsafe_allow_html=True)

                if "라인 그래프 (성취도 추이)" in selected_charts and len(trend_data) >= 2:
                    with st.container(border=True):
                        st.markdown(f"##### 📈 라인 그래프: 시간에 따른 프로그램 성과 변화")
                        df_t = pd.DataFrame(trend_data).sort_values(by="날짜")
                        df_t_avg = df_t.groupby(['날짜', '프로그램'])['점수'].mean().reset_index()
                        fig_l = px.line(df_t_avg, x='날짜', y='점수', color='프로그램', markers=True)
                        fig_l.update_yaxes(range=[0, 105])
                        st.plotly_chart(fig_l, use_container_width=True)
                        
                        first_sc = df_t_avg.iloc[0]['점수']
                        last_sc = df_t_avg.iloc[-1]['점수']
                        if last_sc >= first_sc: st.markdown(f"<div class='report-box'><div class='pos-text'>🟢 긍정적 시그널: 전반적인 성취도가 상승/유지되고 있습니다.</div></div>", unsafe_allow_html=True)
                        else: st.markdown(f"<div class='report-box'><div class='neg-text'>🔴 주의 요망: 최근 전체 성취도가 하락하는 추세입니다. 점검이 필요합니다.</div></div>", unsafe_allow_html=True)

                if "히트맵 (출결 밀도)" in selected_charts and heat_data:
                    with st.container(border=True):
                        st.markdown(f"##### 🔲 히트맵: {T_USER}별 출결 패턴 밀도")
                        df_h = pd.DataFrame(heat_data)
                        val_map = {'출석': 1, '지각': 0.5, '병결': -0.5, '결석': -1}
                        df_h['NumericStatus'] = df_h['상태'].map(val_map)
                        pivot_h = df_h.pivot_table(index='학생명', columns='날짜', values='NumericStatus', fill_value=0)
                        
                        fig_h = px.imshow(pivot_h, labels=dict(x="날짜", y="학생명", color="상태(수치)"), 
                                          x=pivot_h.columns, y=pivot_h.index, aspect="auto", color_continuous_scale="RdYlGn")
                        st.plotly_chart(fig_h, use_container_width=True)
                        
                        bad_days = (df_h['상태'].isin(['결석', '병결'])).sum()
                        if bad_days == 0: st.markdown(f"<div class='report-box'><div class='pos-text'>🟢 긍정적 시그널: 결석이 발생한 날이 없습니다. 훌륭한 참여도입니다.</div></div>", unsafe_allow_html=True)
                        else: st.markdown(f"<div class='report-box'><div class='neg-text'>🔴 주의 요망: 총 {bad_days}건의 결석/병결이 관찰되었습니다. 붉은색이 집중된 인원을 확인하세요.</div></div>", unsafe_allow_html=True)

                if "산점도 (피드백 효과)" in selected_charts and not df_dash.empty:
                    with st.container(border=True):
                        st.markdown(f"##### 🎯 산점도: {T_ADMIN} 피드백 빈도와 {T_USER} 성과 상관관계")
                        fig_s = px.scatter(df_dash, x='Comments', y='AvgScore', color='Program', hover_data=['Student'], size_max=15)
                        fig_s.update_traces(marker=dict(size=12, line=dict(width=1, color='DarkSlateGrey')))
                        st.plotly_chart(fig_s, use_container_width=True)
                        
                        corr = df_dash['Comments'].corr(df_dash['AvgScore'])
                        if pd.isna(corr): st.info("📉 데이터 변동성이 부족하여 상관계수를 도출할 수 없습니다.")
                        elif corr >= 0.3: st.markdown(f"<div class='report-box'><div class='pos-text'>🟢 긍정적 시그널: 피드백(코멘트) 수와 성취도 간에 양의 상관관계(계수: {corr:.2f})가 존재합니다.</div></div>", unsafe_allow_html=True)
                        elif corr <= -0.3: st.markdown(f"<div class='report-box'><div class='neg-text'>🔴 주의 요망: 코멘트와 성취도가 역상관(계수: {corr:.2f})을 보입니다. 피드백의 질적 점검이 필요합니다.</div></div>", unsafe_allow_html=True)
                        else: st.markdown(f"<div class='report-box'><div class='info-text'>ℹ️ 특이사항: 피드백 횟수와 성적 간에 뚜렷한 패턴이 관찰되지 않았습니다.</div></div>", unsafe_allow_html=True)

                if "스택 막대 그래프 (출결 상세)" in selected_charts and heat_data:
                    with st.container(border=True):
                        st.markdown(f"##### 📊 스택 막대 그래프: 프로그램별 출결 누적 구성")
                        df_h = pd.DataFrame(heat_data)
                        agg_df = df_h.groupby(['프로그램', '상태']).size().unstack(fill_value=0).reset_index()
                        for col in ['출석', '지각', '결석', '병결']:
                            if col not in agg_df.columns: agg_df[col] = 0
                        fig_st = px.bar(agg_df, x='프로그램', y=['출석', '지각', '결석', '병결'], title="출결 스택 막대그래프", color_discrete_map=ATT_COLORS)
                        st.plotly_chart(fig_st, use_container_width=True)
                        
                        agg_df['Bad'] = agg_df.get('결석', 0) + agg_df.get('지각', 0)
                        worst_p = agg_df.loc[agg_df['Bad'].idxmax()]
                        if worst_p['Bad'] > 0: st.markdown(f"<div class='report-box'><div class='neg-text'>🔴 주의 요망: '{worst_p['프로그램']}' 프로그램의 지각/결석이 {worst_p['Bad']}건으로 가장 많습니다.</div></div>", unsafe_allow_html=True)
                        else: st.markdown(f"<div class='report-box'><div class='pos-text'>🟢 긍정적 시그널: 지각 및 결석이 발생한 프로그램이 없습니다.</div></div>", unsafe_allow_html=True)

        # ---------------------------------------------------------
        # 행정 및 마스터 탭 모음
        if is_super or is_staff:
            with tab_finance:
                st.subheader(f"💳 {T_STAFF} 및 재무 결제 관리")
                fin_tab1, fin_tab2 = st.tabs(["📝 결제 내역 입력 및 관리", "📈 재무 통계 및 시각화 리포트"])
                
                with fin_tab1:
                    with st.container(border=True):
                        st.markdown("##### ➕ 신규 결제 내역 추가")
                        with st.form("add_payment"):
                            c1, c2, c3 = st.columns(3)
                            p_date = c1.date_input("결제일자")
                            all_u = [f"{u['name']} ({u['program']})" for u in db['users']]
                            p_student = c2.selectbox("결제 확인 대상 (학생)", all_u) if all_u else c2.text_input("결제 학생")
                            p_category = c3.selectbox("결제 항목", ["수강료", "교재비", "간식비", "체험학습비", "물품구입", "기타"])
                            
                            c4, c5, c6 = st.columns(3)
                            p_amount = c4.number_input("결제 금액 (원)", min_value=0, step=1000)
                            p_method = c5.selectbox("결제 수단", ["카드결제", "현금", "계좌이체", "제로페이/지역화폐"])
                            p_note = c6.text_input("비고 (예: 3월 수강료 2회분)")
                            
                            if st.form_submit_button("💾 결제 내역 저장", type="primary"):
                                db['payments'].append({"id": str(time.time()), "date": p_date.strftime("%Y-%m-%d"), "student": p_student, "category": p_category, "amount": p_amount, "method": p_method, "note": p_note, "recorded_by": admin_info['name']})
                                if save_data(db): st.success("저장 완료"); time.sleep(1); st.rerun()
                        
                        st.divider()
                        st.markdown("##### 📋 통합 결제 내역 데이터베이스")
                        if db.get('payments'):
                            df_pay = pd.DataFrame(db['payments']).sort_values('date', ascending=False)
                            csv_data = df_pay.drop(columns=['id']).rename(columns={'date': '결제일', 'student': '학생', 'category': '항목', 'amount': '금액', 'method': '결제수단', 'note': '비고', 'recorded_by': '입력담당자'}).to_csv(index=False).encode('utf-8-sig')
                            st.download_button("📥 전체 결제 내역 엑셀(CSV) 다운로드", data=csv_data, file_name=f"Payments_{today_str}.csv", mime="text/csv")
                            
                            df_pay['amount_fmt'] = df_pay['amount'].apply(lambda x: f"{x:,} 원")
                            st.dataframe(df_pay[['date', 'student', 'category', 'amount_fmt', 'method', 'note', 'recorded_by']].rename(columns={'date': '결제일', 'student': '학생', 'category': '항목', 'amount_fmt': '금액', 'method': '결제수단', 'note': '비고', 'recorded_by': '입력담당자'}), use_container_width=True, hide_index=True)
                            
                            with st.expander("🗑️ 잘못 입력된 결제 내역 삭제"):
                                del_id = st.selectbox("삭제할 내역 선택", df_pay['id'].tolist(), format_func=lambda x: f"{next(p['date'] for p in db['payments'] if p['id']==x)} - {next(p['student'] for p in db['payments'] if p['id']==x)} ({next(p['amount'] for p in db['payments'] if p['id']==x):,}원)")
                                if st.button("❌ 선택 내역 영구 삭제"):
                                    db['payments'] = [p for p in db['payments'] if p['id'] != del_id]
                                    if save_data(db): st.rerun()
                        else: st.info("저장된 결제 내역이 없습니다.")
                
                with fin_tab2:
                    staff_perm = admin_info.get('staff_permission', 'full') if is_super else admin_info.get('staff_permission', 'entry')
                    if staff_perm == 'full':
                        df_pay, total_rev, cat_sum, date_sum = prep_finance(db['payments'])
                        st.markdown("##### 📈 기관 전체 재무 상태 및 매출 분석")
                        if df_pay.empty: st.info("시각화할 결제 데이터가 없습니다.")
                        else:
                            st.metric("💰 누적 총 매출 금액", f"{total_rev:,} 원")
                            f_col1, f_col2 = st.columns(2)
                            with f_col1:
                                with st.container(border=True):
                                    fig_f1 = px.pie(cat_sum, names='category', values='amount', hole=0.4, title="항목별 매출 구성 비율")
                                    fig_f1.update_traces(textinfo='percent+label')
                                    st.plotly_chart(fig_f1, use_container_width=True)
                                    top_cat = cat_sum.loc[cat_sum['amount'].idxmax()]['category']
                                    st.markdown(f"<div class='report-box'><div class='pos-text'>🟢 긍정적 시그널: '{top_cat}' 항목이 전체 매출을 견인하고 있습니다.</div></div>", unsafe_allow_html=True)
                            with f_col2:
                                with st.container(border=True):
                                    fig_f2 = px.bar(date_sum, x='date', y='amount', title="일자별 매출 추이", text='amount')
                                    fig_f2.update_traces(texttemplate='%{text:,}원', textposition='outside')
                                    st.plotly_chart(fig_f2, use_container_width=True)
                                    st.markdown(f"<div class='report-box'><div class='info-text'>ℹ️ 일자별 수입 변동성을 확인하세요.</div></div>", unsafe_allow_html=True)
                    else: st.error("🔒 **접근 제한:** 열람 권한이 부여된 '최고관리자' 또는 '전체 열람 권한 행정직원'만 접근할 수 있습니다.")

            with tab_create:
                st.subheader("➕ 신규 프로그램 개설")
                
                with st.form("create_form"):
                    st.markdown("##### 🎬 1. 미디어 첨부 (선택)")
                    st.warning("🚨 **[필독] 동영상 직접 업로드의 한계 및 대안**\n\n현재 시스템은 무료 텍스트 데이터베이스를 사용 중입니다. 영상(mp4)을 올리면 서버 과부하로 지원자들의 **수강신청이 에러(400)를 내며 튕길 수 있습니다.**\n\n* **해결책:** 유튜브에 영상을 '일부 공개'로 올리신 후 **[유튜브 링크]**란에 붙여넣는 것이 가장 빠르고 안전합니다. (이미지는 1MB 이하만 권장합니다.)")
                    
                    col_m1, col_m2, col_m3 = st.columns(3)
                    new_m_url_input = col_m1.text_input("📺 유튜브 링크 (가장 안전)", placeholder="https://youtu.be/...")
                    img_f = col_m2.file_uploader("🖼️ 이미지 (1MB 이하 필수)", type=['png', 'jpg', 'jpeg'])
                    vid_f = col_m3.file_uploader("🎞️ 동영상 (업로드 차단됨)", type=['mp4', 'mov'], disabled=True)
                            
                    st.divider()
                    st.markdown("##### 📝 2. 프로그램 기본 정보")
                    c1, c2 = st.columns([8, 2])
                    t = c1.text_input("프로그램 명")
                    color = c2.color_picker("색상", "#4f46e5")
                    col_rs, col_re = st.columns(2) 
                    r_s = col_rs.date_input("시작일"); r_e = col_re.date_input("종료일")
                    d = st.text_area("소개")
                    
                    st.markdown("##### 🗓️ 3. 워크플로우 (시간 및 일정)")
                    w_input_placeholder = """[수강생 : 10명]
2026-03-23 (14:00~16:00) : 1차 특강
2026-03-30 (17:30~19:30) : 2차 특강
- 세부 목표 (하이픈으로 시작)"""
                    st.info("💡 **시간은 반드시 소괄호 `( )` 안에 적어주세요!** 그래야 시스템이 정확하게 인식합니다. (예: `2026-03-23 (14:00) : OT`)")
                    w_input = st.text_area("워크플로우 양식", value=w_input_placeholder, height=200)
                    
                    if st.form_submit_button("✨ 최종 개설하기", type="primary"):
                        final_m_url = ""
                        new_m_type = "url"
                        
                        if img_f and img_f.size > 1 * 1024 * 1024:
                            st.error("🚨 이미지 용량이 1MB를 초과합니다! 용량을 줄여서 다시 올려주세요.")
                            st.stop()
                            
                        try:
                            if img_f:
                                new_m_type = "image"
                                final_m_url = f"data:{img_f.type};base64,{base64.b64encode(img_f.read()).decode('utf-8')}"
                            elif new_m_url_input:
                                new_m_type = "url"
                                final_m_url = new_m_url_input
                        except Exception as e:
                            st.error("🚨 파일 변환 중 오류가 발생했습니다.")
                            st.stop()

                        pw = {}; pc = {}; cr = None
                        for line in w_input.split('\n'):
                            line = line.strip()
                            if not line or line.startswith('1. 단일') or line.startswith('2. 날짜') or line.startswith('3. 시간'): continue
                            
                            if line.startswith('['):
                                role_match = re.search(r'\[(.*?)\]', line)
                                if role_match:
                                    role_raw = role_match.group(1)
                                    if ':' in role_raw:
                                        cr = safe_key(role_raw.split(':')[0].strip())
                                        try: pc[cr] = int(re.sub(r'[^0-9]', '', role_raw.split(':')[1]))
                                        except: pc[cr] = 10
                                    else:
                                        cr = safe_key(role_raw.strip())
                                        pc[cr] = 10
                                    pw[cr] = []
                                continue
                            
                            if cr and line.startswith('-'):
                                if pw[cr]: pw[cr][-1]["subtasks"].append({"desc": line[1:].strip(), "done": False})
                            elif cr:
                                match = re.match(r'^([\d\-\s~]+(?:\([^)]+\))?)\s*:\s*(.*)$', line)
                                if match:
                                    dt_part = match.group(1).strip()
                                    tk_part = match.group(2).strip()
                                else:
                                    if ':' in line: parts = line.split(':', 1); dt_part = parts[0].strip(); tk_part = parts[1].strip()
                                    else: dt_part = ""; tk_part = line

                                date_match = re.search(r'\d{4}-\d{2}-\d{2}(?:\s*~\s*\d{4}-\d{2}-\d{2})?', dt_part)
                                time_str = ""; sd = ""; ed = ""
                                if date_match:
                                    date_val = date_match.group(0)
                                    time_str = dt_part.replace(date_val, '').strip(' ()')
                                    if '~' in date_val: sd, ed = [x.strip() for x in date_val.split('~')]
                                    else: sd = date_val.strip(); ed = sd
                                else:
                                    sd = dt_part; ed = dt_part
                                
                                pw[cr].append({"start_date": sd, "end_date": ed, "time": time_str, "task": tk_part, "subtasks": [], "done": False, "score":0, "comment":""})
                                
                        db['programs'].append({"title": t, "desc": d, "video": final_m_url if new_m_type=='url' else '', "media_type": new_m_type, "media_url": final_m_url, "color": color, "recruit_start": r_s.strftime("%Y-%m-%d"), "recruit_end": r_e.strftime("%Y-%m-%d"), "roles_capacity": pc, "roles_workflow": pw})
                        if not is_super: next(a for a in db['admins'] if a['name'] == admin_info['name']).setdefault('programs', []).append(t)
                        if save_data(db): st.success("개설 완료!"); time.sleep(1); st.rerun()
                        else: db['programs'].pop()

            with tab_edit:
                st.subheader("⚙️ 기존 프로그램 정보 수정")
                if not my_programs: st.info("수정 권한이 있는 프로그램이 없습니다.")
                else:
                    with st.container(border=True):
                        edit_title = st.selectbox("⚙️ 수정할 프로그램 선택", my_programs)
                        p_idx = [p['title'] for p in db['programs']].index(edit_title)
                        p_data = db['programs'][p_idx]
                        
                        initial_w = ""
                        for role, tasks in p_data.get('roles_workflow', {}).items():
                            cap = p_data.get('roles_capacity', {}).get(role, 10)
                            initial_w += f"[{role} : {cap}명]\n"
                            for t in tasks:
                                sd, ed = get_date_range(t)
                                time_str = t.get('time', '')
                                date_str = f"{sd}~{ed}" if sd and ed and sd != ed else (sd if sd and sd != "-" else "")
                                if time_str: date_str += f" ({time_str})"
                                if date_str: initial_w += f"{date_str} : {t['task']}\n"
                                else: initial_w += f"{t['task']}\n"
                                for stask in t.get('subtasks', []): initial_w += f"- {stask['desc']}\n"
                            initial_w += "\n"

                        st.markdown("##### 🎬 1. 미디어 첨부 수정")
                        curr_m_type = p_data.get('media_type', 'url')
                        curr_m_url = p_data.get('media_url', p_data.get('video', ''))
                        if curr_m_url:
                            if curr_m_type == 'url': st.info(f"✅ 현재 등록된 링크: {curr_m_url}")
                            elif curr_m_type == 'image': st.info("✅ 현재 이미지가 등록되어 있습니다.")
                            elif curr_m_type == 'video': st.info("✅ 현재 동영상이 등록되어 있습니다.")
                        
                        with st.form("edit_form"):
                            col_m1, col_m2, col_m3 = st.columns(3)
                            new_m_url_input = col_m1.text_input("📺 새 유튜브 링크", value=curr_m_url if curr_m_type == 'url' else "")
                            img_f = col_m2.file_uploader("🖼️ 새 이미지 (1MB 이하 필수)", type=['png', 'jpg', 'jpeg'])
                            vid_f = col_m3.file_uploader("🎞️ 새 동영상 (업로드 차단됨)", type=['mp4', 'mov'], disabled=True)
                            del_media = st.checkbox("🗑️ 등록된 미디어 완전히 삭제하기 (서버 에러 400 발생 시 체크 필수!)")
                            
                            st.divider()
                            st.markdown("##### 📝 2. 프로그램 기본 정보 수정")
                            colA, colB = st.columns([8, 2])
                            new_t = colA.text_input("프로그램 명", value=p_data['title'])
                            new_color = colB.color_picker("캘린더 색상 변경", value=p_data.get('color', '#4f46e5'))
                            colD1, colD2 = st.columns(2)
                            new_r_start = colD1.date_input("모집 시작일 수정", value=datetime.strptime(p_data.get('recruit_start', today_str), "%Y-%m-%d"))
                            new_r_end = colD2.date_input("모집 종료일 수정", value=datetime.strptime(p_data.get('recruit_end', "2026-12-31"), "%Y-%m-%d"))
                            new_d = st.text_area("상세 내용", value=p_data['desc'])
                            
                            st.markdown("##### 🗓️ 3. 워크플로우 수정")
                            st.info("💡 **시간은 반드시 소괄호 `( )` 안에 적어주세요!** (예: `2026-03-23 (14:00) : OT`)")
                            new_w = st.text_area("워크플로우 수정", value=initial_w.strip(), height=300)
                            
                            if st.form_submit_button("✨ 수정 내용 저장", type="primary"):
                                final_m_url = curr_m_url
                                new_m_type = curr_m_type
                                
                                if img_f and img_f.size > 1 * 1024 * 1024:
                                    st.error("🚨 이미지 용량이 1MB를 초과합니다! 용량을 줄여서 다시 올려주세요.")
                                    st.stop()
                                    
                                try:
                                    if del_media:
                                        final_m_url = ""; new_m_type = "url"
                                    elif img_f:
                                        new_m_type = "image"
                                        final_m_url = f"data:{img_f.type};base64,{base64.b64encode(img_f.read()).decode('utf-8')}"
                                    elif new_m_url_input != (curr_m_url if curr_m_type == 'url' else ""):
                                        new_m_type = "url"
                                        final_m_url = new_m_url_input
                                except Exception as e:
                                    st.error("🚨 파일 변환 중 오류가 발생했습니다.")
                                    st.stop()

                                pw = {}; pc = {}; cr = None
                                for line in new_w.split('\n'):
                                    line = line.strip()
                                    if not line or line.startswith('1. 단일') or line.startswith('2. 날짜') or line.startswith('3. 시간'): continue
                                    
                                    if line.startswith('['):
                                        role_match = re.search(r'\[(.*?)\]', line)
                                        if role_match:
                                            role_raw = role_match.group(1)
                                            if ':' in role_raw:
                                                cr = safe_key(role_raw.split(':')[0].strip())
                                                try: pc[cr] = int(re.sub(r'[^0-9]', '', role_raw.split(':')[1]))
                                                except: pc[cr] = 10
                                            else:
                                                cr = safe_key(role_raw.strip())
                                                pc[cr] = 10
                                            pw[cr] = []
                                        continue
                                    
                                    if cr and line.startswith('-'):
                                        if pw[cr]: pw[cr][-1]["subtasks"].append({"desc": line[1:].strip(), "done": False})
                                    elif cr:
                                        match = re.match(r'^([\d\-\s~]+(?:\([^)]+\))?)\s*:\s*(.*)$', line)
                                        if match:
                                            dt_part = match.group(1).strip(); tk_part = match.group(2).strip()
                                        else:
                                            if ':' in line: parts = line.split(':', 1); dt_part = parts[0].strip(); tk_part = parts[1].strip()
                                            else: dt_part = ""; tk_part = line

                                        date_match = re.search(r'\d{4}-\d{2}-\d{2}(?:\s*~\s*\d{4}-\d{2}-\d{2})?', dt_part)
                                        time_str = ""; sd = ""; ed = ""
                                        if date_match:
                                            date_val = date_match.group(0)
                                            time_str = dt_part.replace(date_val, '').strip(' ()')
                                            if '~' in date_val: sd, ed = [x.strip() for x in date_val.split('~')]
                                            else: sd = date_val.strip(); ed = sd
                                        else: sd = dt_part; ed = dt_part
                                        
                                        pw[cr].append({"start_date": sd.strip(), "end_date": ed.strip(), "time": time_str.strip(), "task": tk_part.strip(), "subtasks": [], "done": False, "score":0, "comment":""})
                                
                                old_title = p_data['title']
                                if new_t != old_title:
                                    for a in db['admins']:
                                        if old_title in a.get('programs', []): a['programs'] = [new_t if x == old_title else x for x in a['programs']]
                                    for p in db['parents']:
                                        for s in p.get('linked_students', []):
                                            if s['program'] == old_title: s['program'] = new_t
                                            
                                for u in db['users']:
                                    if u['program'] == old_title:
                                        u['program'] = new_t 
                                        if u['role'] in pw:
                                            new_user_workflow = copy.deepcopy(pw[u['role']])
                                            for new_t_dict in new_user_workflow:
                                                for old_t_dict in u['workflow']:
                                                    if new_t_dict['task'] == old_t_dict['task']:
                                                        new_t_dict['done'] = old_t_dict.get('done', False)
                                                        new_t_dict['score'] = old_t_dict.get('score', 0)
                                                        new_t_dict['comment'] = old_t_dict.get('comment', "")
                                                        for new_st_dict in new_t_dict.get('subtasks', []):
                                                            for old_st_dict in old_t_dict.get('subtasks', []):
                                                                if new_st_dict['desc'] == old_st_dict['desc']: new_st_dict['done'] = old_st_dict.get('done', False)
                                            u['workflow'] = new_user_workflow
                                
                                db['programs'][p_idx] = {"title": new_t, "desc": new_d, "video": final_m_url if new_m_type=='url' else '', "media_type": new_m_type, "media_url": final_m_url, "color": new_color, "recruit_start": new_r_start.strftime("%Y-%m-%d"), "recruit_end": new_r_end.strftime("%Y-%m-%d"), "roles_capacity": pc, "roles_workflow": pw}
                                if save_data(db): st.success("수정 완료!"); time.sleep(2); st.session_state['admin_logged_in'] = False; st.rerun()

        # ---------------------------------------------------------
        # [공통 탭 모음] 종합명단, 평가/코멘트, 출석관리, 상담, 학부모
        with tab_overview:
            st.write("#### 📊 데이터 필터링 및 엑셀 추출")
            users_to_show = [u for u in db['users'] if u['program'] in my_programs]
            if users_to_show:
                overview_data = []
                for u in users_to_show:
                    t_scores = [t.get('score', 0) for t in u['workflow']]
                    pct = int(sum(t_scores)/len(t_scores)) if t_scores else 0
                    
                    att_counts = 0
                    for d_key, v in u.get('attendance', {}).items():
                        if is_active_role_period(u, d_key) and v.get('status') == '출석':
                            att_counts += 1
                            
                    overview_data.append({
                        f"{T_USER}명": u.get('alias') or u['name'], "프로그램": u['program'], "역할": u['role'], 
                        "평균성취도(점)": pct, "총 출석(일)": att_counts
                    })
                df_out = pd.DataFrame(overview_data).sort_values(by=["프로그램", f"{T_USER}명"])
                st.dataframe(df_out, use_container_width=True, hide_index=True)
                
                csv_data = df_out.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 전체 명단 엑셀(CSV) 다운로드", data=csv_data, file_name=f"YouthCanvas_Students_{today_str}.csv", mime="text/csv")
            else: st.info("데이터가 없습니다.")

        with tab_eval:
            st.subheader(f"📝 {T_USER} 주차/과업별 달성도 및 코멘트 평가")
            if not my_programs: st.info("담당 프로그램이 없습니다.")
            else:
                col_sel1, col_sel2 = st.columns([5, 5])
                eval_prog = col_sel1.selectbox("📋 프로그램 선택", my_programs, key="eval_prog")
                prog_users = [(i, u) for i, u in enumerate(db['users']) if u['program'] == eval_prog]
                
                if not prog_users: st.warning(f"신청한 {T_USER}이 없습니다.")
                else:
                    eval_user_options = {f"{u['name']} ({u['role']})": i for i, u in prog_users}
                    selected_user_label = col_sel2.selectbox(f"🎓 {T_USER} 선택", list(eval_user_options.keys()))
                    target_idx = eval_user_options[selected_user_label]
                    target_user = db['users'][target_idx]
                    
                    with st.form(f"eval_form_{target_idx}"):
                        for t_idx, t in enumerate(target_user['workflow']):
                            st.markdown(f"**[{t['task']}]** <span style='color:gray; font-size:0.85em;'>*(기간: {get_date_label(t).strip()})*</span>", unsafe_allow_html=True)
                            if t.get('subtasks'):
                                sub_texts = [f"↳ {stask['desc']} {'(✅완료)' if stask.get('done') else '(미완료)'}" for stask in t['subtasks']]
                                st.caption("\n".join(sub_texts))
                            c1, c2 = st.columns([3, 7])
                            new_score = c1.slider("해당 주차 종합 성취도 점수", 0, 100, t.get('score', 0), key=f"score_{target_idx}_{t_idx}")
                            new_comment = c2.text_input(f"{T_PARENT} 전송용 코멘트", value=t.get('comment', ''), key=f"comment_{target_idx}_{t_idx}")
                            st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
                            target_user['workflow'][t_idx]['score'] = new_score
                            target_user['workflow'][t_idx]['comment'] = new_comment
                        if st.form_submit_button("💾 전체 평가 저장하기", type="primary", use_container_width=True):
                            if save_data(db): st.success("저장 완료!"); time.sleep(1); st.rerun()

        with tab_attendance:
            st.subheader("✅ 프로그램별 출석 관리")
            if my_programs:
                att_prog = st.selectbox("📋 출석 체크 프로그램", my_programs, key="att_prog_select")
                pu = [(i, u) for i, u in enumerate(db['users']) if u['program'] == att_prog]
                if not pu: st.warning(f"신청한 {T_USER}이 없습니다.")
                else:
                    att_sub1, att_sub2, att_sub3 = st.tabs(["📅 일일 출석 입력", "📊 전체 출석 현황 & 시각화", "✏️ 개별 기록 수정/삭제"])
                    with att_sub1:
                        att_date_obj = st.date_input("🗓️ 출석을 기록할 날짜 선택", value=date.today())
                        att_date = att_date_obj.strftime("%Y-%m-%d")
                        active_pu = [(idx, u) for idx, u in pu if is_active_role_period(u, att_date)]
                        if not active_pu: st.info(f"💡 선택하신 **{att_date}**에 일정이 할당된 역할({T_USER})이 없습니다.")
                        else:
                            with st.form(f"att_form"):
                                att_up = {}
                                h1, h2, h3 = st.columns([3, 3, 4])
                                h1.write(f"**{T_USER}명 (역할)**"); h2.write("**상태**"); h3.write("**비고**")
                                st.divider()
                                for idx, u in active_pu:
                                    curr_st = u.get('attendance', {}).get(att_date, {}).get('status', '출석')
                                    curr_nt = u.get('attendance', {}).get(att_date, {}).get('note', '')
                                    c1, c2, c3 = st.columns([3, 3, 4])
                                    c1.write(f"**{u.get('alias') or u['name']}**\n<br><span style='color:gray; font-size:0.8em;'>{u['role']}</span>", unsafe_allow_html=True)
                                    ns = c2.selectbox("상태", ["출석", "지각", "결석", "병결"], index=["출석", "지각", "결석", "병결"].index(curr_st), key=f"s_{idx}", label_visibility="collapsed")
                                    nn = c3.text_input("비고", value=curr_nt, key=f"n_{idx}", label_visibility="collapsed")
                                    att_up[idx] = {"status": ns, "note": nn}
                                if st.form_submit_button("💾 출석 저장", type="primary", use_container_width=True):
                                    for idx, ad in att_up.items():
                                        if 'attendance' not in db['users'][idx]: db['users'][idx]['attendance'] = {}
                                        db['users'][idx]['attendance'][att_date] = ad
                                    if save_data(db): st.success("출석 정보 저장 완료!"); time.sleep(1); st.rerun()

                    with att_sub2:
                        att_records = []
                        for i, u in pu:
                            disp_name = u.get('alias') or u['name']
                            for d_key, info in u.get('attendance', {}).items():
                                if is_active_role_period(u, d_key):
                                    att_records.append({f"{T_USER}명": f"{disp_name}({u['role']})", "날짜": d_key, "상태": info['status'], "비고": info['note']})
                        if att_records:
                            df_att = pd.DataFrame(att_records)
                            pivot_df = df_att.pivot(index=f"{T_USER}명", columns='날짜', values='상태').fillna('-')
                            st.dataframe(pivot_df, use_container_width=True)
                            
                            agg_df = df_att.groupby([f"{T_USER}명", '상태']).size().unstack(fill_value=0).reset_index()
                            for col in ['출석', '지각', '결석', '병결']:
                                if col not in agg_df.columns: agg_df[col] = 0
                            fig_att = px.bar(agg_df, x=f'{T_USER}명', y=['출석', '지각', '결석', '병결'], color_discrete_map=ATT_COLORS, title="학생별 누적 출결 현황")
                            st.plotly_chart(fig_att, use_container_width=True)
                        else: st.info("아직 기록된 출석 데이터가 없습니다.")
                            
                    with att_sub3:
                        att_user_options = {f"{u['name']} ({u['role']})": i for i, u in pu}
                        selected_user_label = st.selectbox(f"🎓 수정할 {T_USER} 선택", list(att_user_options.keys()), key="att_edit_user")
                        target_idx = att_user_options[selected_user_label]
                        target_user = db['users'][target_idx]
                        if not target_user.get('attendance', {}): st.warning("기록이 없습니다.")
                        else:
                            sorted_dates = sorted(list(target_user['attendance'].keys()), reverse=True)
                            selected_date = st.selectbox("🗓️ 날짜 선택", sorted_dates, key="att_edit_date")
                            curr_record = target_user['attendance'][selected_date]
                            with st.form(f"att_edit_form_{target_idx}_{selected_date}"):
                                c1, c2 = st.columns(2)
                                new_status = c1.selectbox("상태", ["출석", "지각", "결석", "병결"], index=["출석", "지각", "결석", "병결"].index(curr_record['status']))
                                new_note = c2.text_input("비고", value=curr_record.get('note', ''))
                                col_btn1, col_btn2 = st.columns(2)
                                if col_btn1.form_submit_button("💾 기록 수정", type="primary", use_container_width=True):
                                    db['users'][target_idx]['attendance'][selected_date] = {"status": new_status, "note": new_note}
                                    if save_data(db): st.rerun()
                                if col_btn2.form_submit_button("🗑️ 기록 삭제", use_container_width=True):
                                    del db['users'][target_idx]['attendance'][selected_date]
                                    if save_data(db): st.rerun()

        with tab_manage_users:
            if my_programs:
                sel_p = st.selectbox("프로그램", my_programs, key="m_prog")
                pu = [(i, u) for i, u in enumerate(db['users']) if u['program'] == sel_p]
                if pu:
                    ops = {f"{u['name']} ({u['role']})": i for i, u in pu}
                    t_idx = ops[st.selectbox(f"{T_USER} 선택", list(ops.keys()))]
                    tu = db['users'][t_idx]
                    with st.container(border=True):
                        chat_target = st.radio("💬 대화 상대 선택", [f"👦 {T_USER}과 대화", f"👨‍👩‍👧 {T_PARENT}와 대화"], horizontal=True)
                        msg_key = 'messages' if chat_target == f"👦 {T_USER}과 대화" else 'parent_messages'
                        if not tu.get(msg_key): st.info("대화가 없습니다.")
                        for msg in tu.get(msg_key, []):
                            with st.chat_message("assistant" if msg['sender'] == 'admin' else "user"): st.write(msg['content'])
                        with st.form(f"adm_chat_{t_idx}_{msg_key}", clear_on_submit=True):
                            c1, c2 = st.columns([8, 2])
                            ri = c1.text_input("답장", label_visibility="collapsed")
                            if c2.form_submit_button("전송") and ri:
                                tu.setdefault(msg_key, []).append({"sender": "admin", "content": ri})
                                if save_data(db): st.rerun()
                    
                    with st.form(f"edit_user_form_{t_idx}"):
                        st.write(f"#### ✏️ {T_USER} 정보 수정")
                        c_u1, c_u2 = st.columns(2)
                        edit_u_name = c_u1.text_input(f"새 {T_USER}명", value=tu['name'])
                        edit_u_pin = c_u2.text_input("새 비밀번호", value=tu.get('pin', '0000'), max_chars=4)
                        if st.form_submit_button("저장", type="primary"):
                            old_u_name = tu['name']
                            if old_u_name != edit_u_name:
                                for p in db['parents']:
                                    for s in p.get('linked_students', []):
                                        if s['name'] == old_u_name and s['program'] == tu['program']: s['name'] = edit_u_name
                            tu['name'] = edit_u_name; tu['pin'] = edit_u_pin
                            if save_data(db): st.rerun()
                    if st.button(f"❌ {T_USER} 강제 퇴소"):
                        db['users'].pop(t_idx); save_data(db); st.rerun()

        with tab_parents:
            st.subheader(f"👨‍👩‍👧 {T_PARENT} 통합 CRM")
            if my_programs:
                with st.form("parent_create_form"):
                    col1, col2 = st.columns(2)
                    p_name = col1.text_input(f"{T_PARENT} 대표 이름")
                    p_pin = col2.text_input(f"비밀번호 (4자리)", type="password", max_chars=4)
                    
                    all_students = [f"{u['name']} || {u['program']} || {u['role']}" for u in db['users'] if u['program'] in my_programs]
                    linked_sts = st.multiselect(f"연결할 {T_USER} 선택", all_students, format_func=lambda x: x.replace(" || ", " - "))
                    
                    if st.form_submit_button(f"새로운 계정 생성", type="primary"):
                        if p_name and len(p_pin) == 4 and linked_sts:
                            parsed_students = []
                            for st_str in linked_sts:
                                parts = st_str.split(" || ")
                                if len(parts) >= 2: parsed_students.append({"name": parts[0], "program": parts[1]})
                            
                            db['parents'].append({"name": p_name, "pin": p_pin, "linked_students": parsed_students})
                            if save_data(db): st.success("계정 생성 완료!"); time.sleep(1); st.rerun()
                            
                if db.get('parents'):
                    for p in db['parents']:
                        children_history = defaultdict(list)
                        for s in p.get('linked_students', []):
                            prog_obj = next((pr for pr in db['programs'] if pr['title'] == s['program']), None)
                            if prog_obj: children_history[s['name']].append(f"**{s['program']}** ({prog_obj.get('recruit_start', '')} ~ {prog_obj.get('recruit_end', '')})")
                        
                        with st.container():
                            st.markdown(f"<div class='crm-card'><div class='crm-title'>👨‍👩‍👧 {p['name']}</div><div class='crm-meta'><b>연결된 자녀:</b> {', '.join(children_history.keys())}</div></div>", unsafe_allow_html=True)
                            if p.get('details'):
                                with st.expander(f"📋 가족 상세 프로필 열람"):
                                    for m_name, d_info in p['details'].items():
                                        st.write(f"**👤 {m_name}** ({d_info.get('relation','')}) | 📞 {d_info.get('phone','')}")
                    
                    st.divider()
                    crm_p_name = st.selectbox(f"상세 정보 관리할 {T_PARENT} 선택", [p['name'] for p in db['parents']])
                    crm_p = next(p for p in db['parents'] if p['name'] == crm_p_name)
                    crm_members = list(dict.fromkeys([crm_p['name']] + [s['name'] for s in crm_p.get('linked_students', [])]))
                    if 'details' not in crm_p: crm_p['details'] = {}
                    
                    with st.form("crm_details_form"):
                        member_tabs = st.tabs([f"👤 {m}" for m in crm_members])
                        updated_details = {}
                        for m_idx, m_name in enumerate(crm_members):
                            with member_tabs[m_idx]:
                                m_detail = crm_p['details'].get(m_name, {})
                                c1, c2 = st.columns(2)
                                rel = c1.text_input("가족관계", value=m_detail.get('relation', ''), key=f"rel_{crm_p_name}_{m_name}")
                                phone = c2.text_input("전화번호", value=m_detail.get('phone', ''), key=f"phone_{crm_p_name}_{m_name}")
                                payment = st.text_input("결제관련", value=m_detail.get('payment', ''), key=f"pay_{crm_p_name}_{m_name}")
                                updated_details[m_name] = {"relation": rel, "phone": phone, "payment": payment}
                        if st.form_submit_button("상세 프로필 저장", type="primary"):
                            crm_p['details'] = updated_details
                            if save_data(db): st.rerun()

                    st.divider()
                    del_p = st.selectbox("삭제할 계정 선택", [p['name'] for p in db['parents']])
                    if st.button("❌ 선택한 가족 계정 전체 삭제"):
                        db['parents'] = [p for p in db['parents'] if p['name'] != del_p]
                        if save_data(db): st.rerun()

        # ---------------------------------------------------------
        # 오직 Super 관리자만 접근 가능한 탭 (UI 화면 설정 / 순서 변경)
        if is_super:
            with tab_ui:
                st.subheader("🎨 화면 UI 텍스트 수정")
                with st.form("ui_form"):
                    c1, c2 = st.columns(2)
                    u1 = c1.text_input("브랜드 이름", value=UI.get('brand_title', 'Youth Canvas'))
                    u1_sub = c2.text_input("서브 타이틀", value=UI.get('brand_subtitle', '청소년의 꿈을 그리는 공간'))
                    
                    c3, c4 = st.columns(2)
                    u2 = c3.text_input("메뉴 1 이름", value=UI.get('menu1', '🔍 찾아보기 (탐색)'))
                    u2_2 = c4.text_input("메뉴 2 (달력) 이름", value=UI.get('menu2', '📅 전체 일정'))
                    c5, c6 = st.columns(2)
                    u3 = c5.text_input("메뉴 3 이름", value=UI.get('menu3', '🙋 나의 이야기'))
                    u4 = c6.text_input("메뉴 4 이름", value=UI.get('menu4', '👨‍👩‍👧 학부모 공간'))
                    u5 = st.text_input("메뉴 5 이름", value=UI.get('menu5', '🔒 관리자 전용 포털'))
                    
                    if st.form_submit_button("저장 및 적용"):
                        UI['brand_title'] = u1; UI['brand_subtitle'] = u1_sub
                        UI['menu1'] = u2; UI['menu2'] = u2_2; UI['menu3'] = u3; UI['menu4'] = u4; UI['menu5'] = u5
                        save_data(db); st.session_state.menu_option = u5; st.rerun()
                        
                st.divider()
                
                st.subheader("🔄 메인 화면 프로그램 노출 순서 변경")
                st.info("💡 [찾아보기] 탭에 표시되는 프로그램의 순서를 위아래로 조정할 수 있습니다.")
                if db.get('programs'):
                    prog_titles = [p['title'] for p in db['programs']]
                    
                    st.write("**현재 노출 순서:**")
                    for i, title in enumerate(prog_titles):
                        st.caption(f"{i+1}. {title}")
                    
                    c_sel, c_up, c_down = st.columns([6, 2, 2])
                    selected_prog_to_move = c_sel.selectbox("순서를 변경할 프로그램 선택", prog_titles, label_visibility="collapsed")
                    
                    if c_up.button("⬆️ 위로 한 칸 이동", use_container_width=True):
                        idx = prog_titles.index(selected_prog_to_move)
                        if idx > 0:
                            db['programs'][idx-1], db['programs'][idx] = db['programs'][idx], db['programs'][idx-1]
                            if save_data(db): st.rerun()
                    
                    if c_down.button("⬇️ 아래로 한 칸 이동", use_container_width=True):
                        idx = prog_titles.index(selected_prog_to_move)
                        if idx < len(db['programs']) - 1:
                            db['programs'][idx+1], db['programs'][idx] = db['programs'][idx], db['programs'][idx+1]
                            if save_data(db): st.rerun()
                else:
                    st.info("개설된 프로그램이 없습니다.")
                    
                st.divider()
                st.subheader("🔑 외부 API 연동 설정")
                st.info("💡 공공데이터포털 등의 외부 서비스 API 키를 입력하여 연동합니다. 여기에 입력된 키는 안전하게 데이터베이스에 저장됩니다.")
                with st.form("api_key_form"):
                    current_key = db['settings'].get('api_keys', {}).get('public_data', '')
                    new_api_key = st.text_input("공공데이터포털 API Key (Decoding/Encoding 무관)", value=current_key, type="password")
                    if st.form_submit_button("API 키 저장 및 적용", type="primary"):
                        if 'api_keys' not in db['settings']:
                            db['settings']['api_keys'] = {}
                        db['settings']['api_keys']['public_data'] = new_api_key
                        if save_data(db):
                            st.success("API 키가 데이터베이스에 안전하게 저장되었습니다!")
                            time.sleep(1)
                            st.rerun()

        # ---------------------------------------------------------
        # 공통 계정 관리 탭
        with tab_settings:
            with st.form("pin_form"):
                npin = st.text_input("내 계정 새 비밀번호 변경 (4자리)", type="password", max_chars=4)
                if st.form_submit_button("변경 적용"):
                    if len(npin) == 4 and npin.isdigit():
                        adm = next(a for a in db['admins'] if a['name'] == admin_info['name'])
                        adm['pin'] = npin
                        if save_data(db): st.success("변경 완료. 다시 로그인하세요."); time.sleep(1); st.session_state['admin_logged_in'] = False; st.rerun()
                    else: st.error("4자리 숫자로 입력해주세요.")
            
            if is_super:
                st.divider()
                st.subheader("💾 전체 시스템 데이터 백업")
                json_string = json.dumps(db, ensure_ascii=False, indent=2)
                st.download_button("📥 데이터 원클릭 백업 (JSON)", file_name=f"Backup_{today_str}.json", mime="application/json", data=json_string, type="primary")
                
                with st.container(border=True):
                    st.subheader("🔤 맞춤형 호칭 설정")
                    with st.form("terms_form"):
                        c1, c2, c3 = st.columns(3)
                        new_t_super = c1.text_input("최고관리자 호칭", value=T_SUPER)
                        new_t_admin = c2.text_input("일반관리자(선생님) 호칭", value=T_ADMIN)
                        new_t_staff = c3.text_input("행정직원 호칭", value=T_STAFF)
                        
                        c4, c5, _ = st.columns(3)
                        new_t_user = c4.text_input("이용자(학생) 호칭", value=T_USER)
                        new_t_parent = c5.text_input("보호자(학부모) 호칭", value=T_PARENT)
                        
                        if st.form_submit_button("호칭 변경 적용", type="primary"):
                            db['settings']['terms'] = {"super": new_t_super, "admin": new_t_admin, "staff": new_t_staff, "user": new_t_user, "parent": new_t_parent}
                            if save_data(db): st.success("호칭 변경 완료!"); time.sleep(1); st.rerun()
                
                with st.container(border=True):
                    st.subheader(f"👑 계정 관리")
                    with st.form("new_admin_form"):
                        colA, colB = st.columns(2)
                        new_adm_name = colA.text_input(f"새 직원 이름")
                        new_adm_pin = colB.text_input("비밀번호 4자리", max_chars=4)
                        role_type = st.radio("계정 유형 선택", [f"{T_ADMIN} (수업/평가)", f"{T_STAFF} (결제/재무)"], horizontal=True)
                        
                        staff_perm = "entry"
                        assign_progs = []
                        if T_STAFF in role_type:
                            staff_perm_label = st.selectbox("행정 권한 수준", ["단순 입력 및 수정", "재무/통계 전체 열람"])
                            staff_perm = "entry" if "단순" in staff_perm_label else "full"
                        else:
                            assign_progs = st.multiselect("담당 프로그램 할당", [p['title'] for p in db['programs']])
                        
                        if st.form_submit_button(f"직원 계정 생성", type="primary"):
                            r_val = "staff" if T_STAFF in role_type else "normal"
                            db['admins'].append({"name": new_adm_name, "pin": new_adm_pin, "role": r_val, "programs": assign_progs, "staff_permission": staff_perm})
                            if save_data(db): st.rerun()
                    
                    df_admins = pd.DataFrame([{"이름": a['name'], "권한 유형": T_SUPER if a['role'] == "super" else (T_STAFF if a['role'] == 'staff' else T_ADMIN), "세부 권한": "전체 열람" if a.get('staff_permission')=='full' else ("단순 입력" if a.get('staff_permission')=='entry' else ", ".join(a.get('programs', [])))} for a in db['admins']])
                    st.dataframe(df_admins, hide_index=True, use_container_width=True)
                    
                    st.divider()
                    normal_admins = [a['name'] for a in db['admins'] if a['role'] != 'super']
                    if normal_admins:
                        a_to_edit_name = st.selectbox("수정할 직원 선택", normal_admins)
                        a_to_edit = next(a for a in db['admins'] if a['name'] == a_to_edit_name)
                        
                        with st.form("edit_admin_form"):
                            c1, c2 = st.columns(2)
                            new_a_name = c1.text_input("새 이름", value=a_to_edit['name'])
                            new_a_pin = c2.text_input("새 비밀번호", value=a_to_edit['pin'], max_chars=4)
                            
                            if a_to_edit['role'] == 'staff':
                                perm_idx = 1 if a_to_edit.get('staff_permission', 'entry') == 'full' else 0
                                staff_perm_label_edit = st.selectbox("행정 권한 수준 수정", ["단순 입력 및 수정", "재무/통계 전체 열람"], index=perm_idx)
                                new_assign_progs = a_to_edit.get('programs', [])
                            else:
                                valid_progs = [p for p in a_to_edit.get('programs', []) if p in [pr['title'] for pr in db['programs']]]
                                new_assign_progs = st.multiselect("담당 프로그램 수정", [pr['title'] for pr in db['programs']], default=valid_progs)
                                staff_perm_label_edit = None
                            
                            if st.form_submit_button("정보 수정 저장", type="primary"):
                                a_to_edit['name'] = new_a_name; a_to_edit['pin'] = new_a_pin
                                if a_to_edit['role'] == 'staff': a_to_edit['staff_permission'] = "full" if "전체" in staff_perm_label_edit else "entry"
                                else: a_to_edit['programs'] = new_assign_progs
                                if save_data(db): st.rerun()

                        del_admin = st.selectbox("삭제할 계정 선택", normal_admins)
                        if st.button("❌ 선택 계정 삭제"):
                            db['admins'] = [a for a in db['admins'] if a['name'] != del_admin]
                            if save_data(db): st.rerun()
