import streamlit as st
import pandas as pd
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

# --- ✨ 시각화 폰트 설정 (Streamlit 클라우드 한글 깨짐 100% 방어) ---
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
        plt.rcParams['axes.unicode_minus'] = False
        sns.set_theme(style='whitegrid', font=font_name, font_scale=1.0)
    except:
        import platform
        if platform.system() == 'Darwin': plt.rc('font', family='AppleGothic')
        elif platform.system() == 'Windows': plt.rc('font', family='Malgun Gothic')
        plt.rcParams['axes.unicode_minus'] = False

set_korean_font()

# --- [디자인 요소] 커스텀 CSS ---
# ✨ 사이드바 메뉴 디자인 강제 적용 (업데이트된 Streamlit 구조에 맞게 강화)
st.markdown("""
    <style>
    h1, h2, h3, h4, h5, h6, p, label, span, div, button, input, select, textarea, li, th, td {
        font-family: 'KakaoBigSans-ExtraBold', 'Pretendard', 'Malgun Gothic', sans-serif;
    }
    svg, [data-baseweb="icon"], .material-icons { font-family: inherit !important; }

    .badge-green { background-color: #dcfce7; color: #166534; padding: 4px 10px; border-radius: 12px; font-size: 0.85em; font-weight: bold; margin-right: 5px; }
    .badge-red { background-color: #fee2e2; color: #991b1b; padding: 4px 10px; border-radius: 12px; font-size: 0.85em; font-weight: bold; margin-right: 5px; }
    .badge-blue { background-color: #e0e7ff; color: #3730a3; padding: 4px 10px; border-radius: 12px; font-size: 0.85em; font-weight: bold; margin-right: 5px; border: 1px solid #c7d2fe; }
    .badge-gray { background-color: #f1f5f9; color: #475569; padding: 4px 10px; border-radius: 12px; font-size: 0.85em; font-weight: bold; margin-right: 5px; }
    .card-title { font-size: 1.4em; font-weight: 800; color: #1e293b; margin-bottom: 0.2em; }
    .card-desc { font-size: 0.95em; color: #64748b; margin-bottom: 1em; }
    .recruit-period { font-size: 0.85em; color: #b45309; background-color: #fef3c7; padding: 5px 10px; border-radius: 5px; font-weight: bold; display: inline-block; margin-bottom: 10px; }
    .schedule-table { width: 100%; border-collapse: collapse; font-size: 0.9em; text-align: center; margin-bottom: 10px; }
    .schedule-table th { border: 1px solid #cbd5e1; padding: 8px; background-color: #f1f5f9; font-weight: bold; color: #334155; }
    .schedule-table td { border: 1px solid #cbd5e1; padding: 8px; color: #1e293b; vertical-align: top; }
    .schedule-table td.task-content { text-align: left; }
    
    /* ✨ 잃어버렸던 사이드바 컬러 버튼 디자인 복구! */
    [data-testid="stSidebar"] { background-color: #261633 !important; }
    [data-testid="stSidebarUserContent"] { padding-left: 1rem !important; padding-right: 1rem !important; padding-top: 3rem !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label { 
        width: 100%; min-height: 65px; margin: 0 0 12px 0; padding: 10px 20px; cursor: pointer; border-radius: 12px; display: flex; justify-content: flex-start; align-items: center; transition: all 0.2s ease; 
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child div { background-color: transparent !important; border-color: rgba(255,255,255,0.6) !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(1) { background-color: #5c358f !important; } 
    [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(2) { background-color: #c13945 !important; } 
    [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(3) { background-color: #2b7a78 !important; } 
    [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-child(4) { background-color: #e68128 !important; } 
    [data-testid="stSidebar"] div[role="radiogroup"] > label p { font-size: 1.3rem !important; font-weight: 900 !important; color: #ffffff !important; margin: 0 !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover { transform: scale(1.03); filter: brightness(1.15); box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
    
    /* 리포트 카드 디자인 */
    .report-box { border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; margin-top: 10px; background-color: #f8fafc; }
    .pos-text { color: #059669; font-weight: 600; margin-bottom: 5px;}
    .neg-text { color: #dc2626; font-weight: 600; margin-bottom: 5px;}
    .info-text { color: #475569; font-weight: 500;}
    
    /* 가족 CRM 카드 디자인 */
    .crm-card { border: 1px solid #cbd5e1; border-radius: 12px; padding: 20px; background: #ffffff; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-bottom: 20px; border-left: 6px solid #2b7a78; }
    .crm-title { font-size: 1.3em; font-weight: 900; color: #1e293b; margin-bottom: 5px; }
    .crm-meta { font-size: 0.9em; color: #64748b; margin-bottom: 15px; }
    .crm-history-box { background-color: #f8fafc; padding: 15px; border-radius: 8px; border: 1px dashed #e2e8f0; }
    .crm-child-name { font-weight: 800; color: #334155; margin-top: 5px; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

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
    if sd and ed and sd != ed: return f"[{sd} ~ {ed}] "
    elif sd and sd != "-": return f"[{sd}] "
    return ""

def safe_key(text): return re.sub(r'[\.\$#\[\]/]', '_', text)

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
    except:
        return False

# ==============================================================
# ✨ [데이터베이스 연결 로직]
# ==============================================================
today_str = datetime.now().strftime("%Y-%m-%d")

# 🚨 [중요] 선생님의 파이어베이스 주소 입력
FIREBASE_URL = "https://youth-canvas-default-rtdb.firebaseio.com/data.json"

def load_data():
    try:
        response = requests.get(FIREBASE_URL)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, dict) and 'programs' in data: 
                if 'parents' not in data: data['parents'] = []
                if 'settings' not in data: data['settings'] = {"recruit_start": "2026-01-01", "recruit_end": "2026-12-31"}
                if 'terms' not in data['settings']: data['settings']['terms'] = {"super": "최고관리자", "admin": "선생님", "user": "학생", "parent": "학부모"}
                if 'ui' not in data['settings']:
                    data['settings']['ui'] = {
                        "brand_title": "Youth Canvas", "brand_subtitle": "청소년의 꿈을 그리는 공간",
                        "menu1": "찾아보기 (탐색)", "menu2": "나의 이야기", "menu3": "👨‍👩‍👧 학부모 공간", "menu4": "관계자 외 출입금지",
                        "page1_title": "✨ 지금 뜨고 있는 활동", "page2_title": "🙋 나의 활동 진행도", "page3_title": "🔒 관리자 전용 포털"
                    }
                return data
    except Exception as e: st.error(f"🚨 연결 오류: {e}")
    return {"programs": [], "users": [], "parents": [], "admins": [{"name": "마스터", "pin": "0000", "role": "super", "programs": []}], "settings": {"recruit_start": "2026-01-01", "recruit_end": "2026-12-31", "terms": {"super": "최고관리자", "admin": "선생님", "user": "학생", "parent": "학부모"}, "ui": {"brand_title": "Youth Canvas", "brand_subtitle": "청소년의 꿈을 그리는 공간", "menu1": "찾아보기 (탐색)", "menu2": "나의 이야기", "menu3": "👨‍👩‍👧 학부모 공간", "menu4": "관계자 외 출입금지", "page1_title": "✨ 지금 뜨고 있는 활동", "page2_title": "🙋 나의 활동 진행도", "page3_title": "🔒 관리자 전용 포털"}}}

def save_data(data):
    try:
        res = requests.put(FIREBASE_URL, json=data)
        if res.status_code == 200: return True
        else: st.error(f"🚨 저장 실패: {res.status_code}"); return False
    except Exception as e: st.error("🚨 인터넷 문제로 저장되지 않았습니다."); return False
# ==============================================================

if 'db' not in st.session_state: st.session_state['db'] = load_data()
db = st.session_state['db']

if 'settings' not in db: db['settings'] = {}
if 'terms' not in db['settings']: db['settings']['terms'] = {"super": "최고관리자", "admin": "선생님", "user": "학생", "parent": "학부모"}
if 'ui' not in db['settings']: db['settings']['ui'] = {"brand_title": "Youth Canvas", "brand_subtitle": "청소년의 꿈을 그리는 공간", "menu1": "찾아보기 (탐색)", "menu2": "나의 이야기", "menu3": "👨‍👩‍👧 학부모 공간", "menu4": "관계자 외 출입금지", "page1_title": "✨ 지금 뜨고 있는 활동", "page2_title": "🙋 나의 활동 진행도", "page3_title": "🔒 관리자 전용 포털"}

T_SUPER = db['settings']['terms']['super']
T_ADMIN = db['settings']['terms']['admin']
T_USER = db['settings']['terms']['user']
T_PARENT = db['settings']['terms']['parent']

UI = db['settings']['ui']

menu_list = [UI['menu1'], UI['menu2'], UI['menu3'], UI['menu4']]
if 'menu_option' not in st.session_state or st.session_state.menu_option not in menu_list: 
    st.session_state.menu_option = UI['menu1']

def change_page(page_name): 
    st.session_state.menu_option = page_name; st.rerun()

with st.sidebar:
    st.markdown(f"<div style='margin-bottom: 2rem; padding: 0 10px;'><div style='font-size: 3.2rem; font-weight: 900; color: #ffffff; line-height: 1.1; margin-bottom: 0.3rem; letter-spacing: -1px;'>{UI['brand_title']}</div><div style='font-size: 1.6rem; font-weight: 800; color: #ffce31; letter-spacing: -0.5px;'>{UI['brand_subtitle']}</div></div>", unsafe_allow_html=True)
    menu = st.radio("메뉴 이동", menu_list, index=menu_list.index(st.session_state.menu_option), label_visibility="collapsed")
    st.write(""); st.write("")
    if st.button("🔄 서버 최신 데이터 동기화", use_container_width=True):
        st.session_state['db'] = load_data(); st.toast("✅ 동기화 완료!"); time.sleep(1); st.rerun()
st.session_state.menu_option = menu

# =========================================================
# [페이지 1] 메인 대시보드
# =========================================================
if st.session_state.menu_option == UI['menu1']:
    st.markdown(f"## {UI['page1_title']}")
    st.write("") 
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
                
                if not is_recruiting_period: status_badge = "<span class='badge-gray'>⏳ 기간종료</span>"
                elif is_all_full: status_badge = "<span class='badge-red'>🔴 모집마감</span>"
                else: status_badge = "<span class='badge-green'>🟢 모집중</span>"
                    
                st.markdown(f"{status_badge}", unsafe_allow_html=True)
                st.markdown(f"<div class='card-title' style='border-left: 5px solid {prog.get('color', '#4f46e5')}; padding-left: 8px;'>{prog['title']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='recruit-period'>🗓️ 모집 기간: {p_r_start} ~ {p_r_end}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='card-desc'>{prog['desc']}</div>", unsafe_allow_html=True)
                
                clean_url = fix_youtube_url(prog.get('video'))
                if clean_url: st.video(clean_url)
                
                tags_html = "".join([f"<span class='badge-blue'>#{r}</span> " for r, _ in roles_list])
                if tags_html: st.markdown(f"<div style='margin-bottom: 15px;'>{tags_html}</div>", unsafe_allow_html=True)
                
                grouped_tasks = defaultdict(list)
                for role, tasks in prog.get('roles_workflow', {}).items():
                    for t in tasks:
                        label = get_date_label(t)
                        date_val = label if label else "일정 미정"
                        
                        # ✨ [세부 일정 줄바꿈 완벽 수정] 쉼표 대신 <br> 태그와 띄어쓰기로 깔끔하게 정렬
                        sub_texts = [stask['desc'] for stask in t.get('subtasks', [])]
                        if sub_texts:
                            subs_html = "<br>".join([f"&nbsp;&nbsp;└ {desc}" for desc in sub_texts])
                            task_display = f"<b>{t['task']}</b><br><span style='color:#64748b; font-size:0.9em;'>{subs_html}</span>"
                        else:
                            task_display = f"<b>{t['task']}</b>"
                            
                        grouped_tasks[date_val].append({"role": role, "task": task_display})
                
                if grouped_tasks:
                    def sort_by_number(d):
                        nums = re.findall(r'\d+', d)
                        return (0, int(nums[0]), d) if nums else (1, 0, d)
                    sorted_dates = sorted(grouped_tasks.keys(), key=sort_by_number)
                    max_roles_in_a_day = max([len(tasks) for tasks in grouped_tasks.values()] + [0])
                    
                    with st.expander("📅 전체 일정 요약 보기"):
                        html_table = "<table class='schedule-table'><tr><th>일정</th>"
                        for _ in range(max_roles_in_a_day): html_table += "<th>역할</th><th>내용</th>"
                        html_table += "</tr>"
                        for d in sorted_dates:
                            html_table += f"<tr><td style='font-weight:bold;'>{d}</td>"
                            tasks_on_date = grouped_tasks[d]
                            for i in range(max_roles_in_a_day):
                                if i < len(tasks_on_date): html_table += f"<td>{tasks_on_date[i]['role']}</td><td class='task-content'>{tasks_on_date[i]['task']}</td>"
                                else: html_table += "<td></td><td></td>"
                            html_table += "</tr>"
                        html_table += "</table>"
                        st.markdown(html_table, unsafe_allow_html=True)

                st.write(f"**현재 참여 인원** ({total_curr}/{total_cap}명)")
                st.progress(total_curr/total_cap if total_cap > 0 else 0)
                
                can_apply = is_recruiting_period and not is_all_full
                if st.button("🚀 이 프로그램 지원하기", key=f"apply_{idx}", use_container_width=True, type="primary", disabled=not can_apply):
                    st.session_state['selected_prog_from_main'] = prog['title']; change_page(UI['menu2'])

# =========================================================
# [페이지 2-1] 청소년 전용 페이지 
# =========================================================
elif st.session_state.menu_option == UI['menu2']:
    st.markdown(f"## {UI['page2_title']}")
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
                    colA, colB = st.columns(2)
                    user_name = colA.text_input(f"{T_USER} 이름 (실명 입력)")
                    user_pin = colB.text_input("나만의 접속 비밀번호 (숫자 4자리)", type="password", max_chars=4)
                    selected_prog_title = st.selectbox("참여할 프로그램", active_programs, index=default_idx)
                    selected_prog_data = next(p for p in db['programs'] if p['title'] == selected_prog_title)
                    
                    role_options = []
                    for r, cap in selected_prog_data.get('roles_capacity', {}).items():
                        curr = sum(1 for u in db['users'] if u['program'] == selected_prog_title and u['role'] == r)
                        role_options.append(f"{r} ({curr}/{cap}명) - {'지원가능' if curr < cap else '마감'}")
                    selected_role_strs = st.multiselect("희망 역할 (여러 개 동시 선택 가능)", role_options)
                    
                    if st.button("✨ 최종 지원하기", use_container_width=True, type="primary"):
                        if not user_name or not user_pin: st.error("이름과 비밀번호를 모두 입력하세요.")
                        elif not selected_role_strs: st.error("희망 역할을 하나 이상 선택해주세요.")
                        elif any("마감" in r for r in selected_role_strs): st.error("마감된 역할이 포함되어 있습니다.")
                        else:
                            added_count = 0
                            for r_str in selected_role_strs:
                                actual_role = r_str.split(" (")[0]
                                my_tasks = copy.deepcopy(selected_prog_data['roles_workflow'][actual_role])
                                for t in my_tasks: t['score'] = 0; t['comment'] = ""
                                db['users'].append({"name": user_name, "pin": user_pin, "program": selected_prog_title, "role": actual_role, "workflow": my_tasks, "messages": [], "parent_messages": [], "alias": "", "attendance": {}})
                                added_count += 1
                            if save_data(db): st.success("🎉 지원 완료!"); time.sleep(1); st.rerun()
                            else:
                                for _ in range(added_count): db['users'].pop()

    with tab2:
        with st.container(border=True):
            col_id, col_pw, col_btn = st.columns([4, 4, 2])
            search_name = col_id.text_input(f"{T_USER} 이름", placeholder="예: 권해리")
            search_pin = col_pw.text_input("비밀번호 (4자리)", type="password")
            login_attempt = col_btn.button("접속하기", use_container_width=True)
            
            if login_attempt or (search_name and search_pin):
                my_data = [u for u in db['users'] if u['name'] == search_name and u.get('pin', '0000') == search_pin]
                if my_data:
                    st.divider()
                    st.markdown(f"### 🌟 **{search_name}**님의 맞춤형 대시보드")
                    
                    s_chart_options = [
                        "막대 그래프 (프로그램별 성취도) [추천]", 
                        "도넛 차트 (나의 종합 출결 비율)", 
                        "라인 그래프 (성취도 변화 추이)"
                    ]
                    selected_s_charts = st.multiselect("📊 보고 싶은 차트를 선택하세요 (다중 선택 가능):", s_chart_options, default=s_chart_options)
                    st.write("")
                    
                    summary_rows = []
                    total_t_all = 0
                    total_d_all = 0
                    all_scores = []
                    att_counts = {'출석': 0, '지각': 0, '결석': 0, '병결': 0}
                    trend_data = []
                    
                    for d in my_data:
                        t_items = 0
                        d_items = 0
                        s_list = []
                        
                        for t in d['workflow']:
                            t_items += 1
                            d_items += 1 if t.get('done') else 0
                            if t.get('score', 0) > 0:
                                s_list.append(t.get('score'))
                                sd, _ = get_date_range(t)
                                if sd and re.match(r'\d{4}-\d{2}-\d{2}', sd):
                                    trend_data.append({"날짜": sd, "프로그램": d['program'], "점수": t['score']})
                            for stask in t.get('subtasks', []):
                                t_items += 1
                                d_items += 1 if stask.get('done') else 0
                                
                        pct = int((d_items/t_items)*100) if t_items > 0 else 0
                        avg_s = sum(s_list)/len(s_list) if s_list else 0
                        
                        for d_key, att_info in d.get('attendance', {}).items():
                            if is_active_role_period(d, d_key):
                                st_val = att_info.get('status')
                                if st_val in att_counts:
                                    att_counts[st_val] += 1
                                
                        total_t_all += t_items
                        total_d_all += d_items
                        all_scores.extend(s_list)
                        
                        summary_rows.append({
                            "프로그램": d['program'],
                            "역할": d['role'],
                            "진행률(%)": pct,
                            "평균 성취도": avg_s
                        })
                    
                    df_summ = pd.DataFrame(summary_rows)
                    
                    # ✨ [학생 차트] SVG 포맷 및 아담한 사이즈(6x4) 적용
                    if "막대 그래프 (프로그램별 성취도) [추천]" in selected_s_charts and not df_summ.empty:
                        with st.container(border=True):
                            st.markdown("##### 📊 프로그램별 달성률 및 성취도 (막대 그래프)")
                            fig_s1, (ax_s1, ax_s2) = plt.subplots(1, 2, figsize=(10, 4))
                            sns.barplot(data=df_summ, x='프로그램', y='진행률(%)', ax=ax_s1, palette='mako')
                            ax_s1.set_ylim(0, 100); ax_s1.tick_params(axis='x', rotation=15)
                            sns.barplot(data=df_summ, x='프로그램', y='평균 성취도', ax=ax_s2, palette='flare')
                            ax_s2.set_ylim(0, 100); ax_s2.tick_params(axis='x', rotation=15)
                            st.pyplot(fig_s1, format="svg", use_container_width=True)
                            plt.close(fig_s1)
                            
                            if df_summ['진행률(%)'].max() == 0 and df_summ['평균 성취도'].max() == 0:
                                st.info("📉 진행된 목표나 평가가 없습니다. 활동을 시작해보세요!")
                            else:
                                top_prog = df_summ.loc[df_summ['진행률(%)'].idxmax()]
                                st.markdown(f"<div class='report-box'><div class='pos-text'>🟢 긍정적 시그널: '{top_prog['프로그램']}'의 달성률이 {top_prog['진행률(%)']}%로 가장 높습니다! 꾸준한 성실함을 칭찬합니다.</div></div>", unsafe_allow_html=True)

                    if "도넛 차트 (나의 종합 출결 비율)" in selected_s_charts:
                        with st.container(border=True):
                            st.markdown("##### 🍩 나의 종합 출결 비율 (도넛 차트)")
                            total_att = sum(att_counts.values())
                            if total_att == 0:
                                st.info("📉 기록된 출결 데이터가 없습니다.")
                            else:
                                labels = [k for k, v in att_counts.items() if v > 0]
                                sizes = [v for v in att_counts.values() if v > 0]
                                colors = ['#2ECC71', '#FFC107', '#E74C3C', '#9B59B6'][:len(labels)]
                                
                                fig_d, ax_d = plt.subplots(figsize=(6, 4))
                                ax_d.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90, pctdistance=0.85, wedgeprops=dict(width=0.4, edgecolor='w'))
                                ax_d.text(0, 0, f"총 {total_att}일", ha='center', va='center', fontsize=12, fontweight='bold')
                                st.pyplot(fig_d, format="svg", use_container_width=True)
                                plt.close(fig_d)
                                
                                bad_att = att_counts['지각'] + att_counts['결석']
                                if bad_att == 0:
                                    st.markdown("<div class='report-box'><div class='pos-text'>🟢 긍정적 시그널: 지각과 결석이 단 한 번도 없습니다! 완벽한 출석률입니다.</div></div>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<div class='report-box'><div class='neg-text'>🔴 주의 요망: 지각/결석이 총 {bad_att}회 있습니다. 성실한 참여를 위해 출결 관리에 신경 써주세요.</div></div>", unsafe_allow_html=True)

                    if "라인 그래프 (성취도 변화 추이)" in selected_s_charts:
                        with st.container(border=True):
                            st.markdown("##### 📈 시간 흐름별 성취도 변화 추이 (라인 그래프)")
                            if len(trend_data) < 2:
                                st.info("📉 성취도 점수가 2건 이상 누적되어야 추이 그래프를 볼 수 있습니다.")
                            else:
                                df_trend = pd.DataFrame(trend_data).sort_values(by="날짜")
                                fig_l, ax_l = plt.subplots(figsize=(8, 4))
                                sns.lineplot(data=df_trend, x='날짜', y='점수', hue='프로그램', marker='o', ax=ax_l)
                                ax_l.set_ylim(0, 105); ax_l.tick_params(axis='x', rotation=45)
                                st.pyplot(fig_l, format="svg", use_container_width=True)
                                plt.close(fig_l)
                                
                                first_score = df_trend['점수'].iloc[0]
                                last_score = df_trend['점수'].iloc[-1]
                                if last_score > first_score:
                                    st.markdown("<div class='report-box'><div class='pos-text'>🟢 긍정적 시그널: 최근 성취도 점수가 과거에 비해 상승하는 추세입니다. 아주 잘하고 있습니다!</div></div>", unsafe_allow_html=True)
                                elif last_score < first_score:
                                    st.markdown("<div class='report-box'><div class='neg-text'>🔴 주의 요망: 최근 성취도가 다소 하락했습니다. 어려운 점이 있다면 선생님과 편하게 상의해 보세요.</div></div>", unsafe_allow_html=True)
                                else:
                                    st.markdown("<div class='report-box'><div class='info-text'>ℹ️ 꾸준한 성적을 유지하고 있습니다.</div></div>", unsafe_allow_html=True)

                    st.divider()
                    st.markdown("### 🔍 개별 프로그램 세부 리포트")
                    for u_idx, data in enumerate(my_data):
                        with st.expander(f"📁 {data['program']} ({data['role']}) 상세 보기", expanded=False):
                            st.write("")
                            tasks = data['workflow']
                            total_items = 0; done_items = 0
                            for t in tasks:
                                total_items += 1; done_items += 1 if t.get('done') else 0
                                for stask in t.get('subtasks', []): total_items += 1; done_items += 1 if stask.get('done') else 0
                            pct = int((done_items/total_items)*100) if total_items > 0 else 0
                            
                            st.metric("활동 달성률 (체크리스트)", f"{pct}%", f"{done_items} / {total_items} 완료")
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
                elif login_attempt: st.error("정보가 일치하지 않습니다.")

# =========================================================
# [페이지 2-2] 학부모 전용 라운지
# =========================================================
elif st.session_state.menu_option == UI['menu3']:
    st.markdown(f"## {UI['menu3']}")
    st.caption(f"발급받으신 개별 {T_PARENT} 계정으로 로그인하여 자녀의 성장 기록과 커리큘럼을 확인하세요.")
    
    with st.container(border=True):
        col_id, col_pw, col_btn = st.columns([4, 4, 2])
        parent_name = col_id.text_input(f"{T_PARENT} 성함", placeholder="예: 권해리 어머니")
        parent_pin = col_pw.text_input(f"{T_PARENT} 전용 비밀번호 (4자리)", type="password")
        login_attempt = col_btn.button("로그인", use_container_width=True)
        
        if login_attempt or (parent_name and parent_pin):
            my_parent_data = [p for p in db['parents'] if p['name'] == parent_name and p['pin'] == parent_pin]
            
            if my_parent_data:
                p_info = my_parent_data[0]
                st.success(f"환영합니다, **{p_info['name']}**님! 😊")
                linked_students = p_info.get('linked_students', [])
                
                if not linked_students:
                    st.info(f"아직 연결된 정보가 없습니다. 기관에 문의해주세요.")
                else:
                    p_summary_rows = []
                    att_counts_total = {'출석': 0, '지각': 0, '결석': 0, '병결': 0}
                    trend_data_p = []
                    
                    for s_info in linked_students:
                        s_record = next((u for u in db['users'] if u['name'] == s_info['name'] and u['program'] == s_info['program']), None)
                        if s_record:
                            tasks = s_record['workflow']
                            t_items, d_items, s_list = 0, 0, []
                            for t in tasks:
                                t_items += 1
                                d_items += 1 if t.get('done') else 0
                                if t.get('score', 0) > 0: 
                                    s_list.append(t.get('score'))
                                    sd, _ = get_date_range(t)
                                    if sd and re.match(r'\d{4}-\d{2}-\d{2}', sd):
                                        trend_data_p.append({"날짜": sd, "자녀명": s_record['name'], "점수": t['score']})
                                for stask in t.get('subtasks', []):
                                    t_items += 1
                                    d_items += 1 if stask.get('done') else 0
                                    
                            pct = int((d_items/t_items)*100) if t_items > 0 else 0
                            avg_s = sum(s_list)/len(s_list) if s_list else 0
                            
                            s_att = {'출석': 0, '지각': 0, '결석': 0, '병결': 0}
                            for d_key, att_info in s_record.get('attendance', {}).items():
                                if is_active_role_period(s_record, d_key):
                                    st_val = att_info.get('status')
                                    if st_val in s_att:
                                        s_att[st_val] += 1
                                        att_counts_total[st_val] += 1
                                    
                            p_summary_rows.append({
                                "자녀명": s_record['name'],
                                "프로그램": s_record['program'],
                                "라벨": f"{s_record['name']}\n({s_record['program']})", 
                                "진행률(%)": pct,
                                "평균 성취도": avg_s,
                                "결석_지각": s_att['결석'] + s_att['지각']
                            })

                    tab_names = ["🌟 자녀 종합 대시보드"] + [f"👦👧 {s['name']} ({s['program']})" for s in linked_students]
                    parent_tabs = st.tabs(tab_names)
                    
                    with parent_tabs[0]:
                        if not p_summary_rows:
                            st.warning("데이터를 불러올 수 있는 연결된 자녀가 없습니다.")
                        else:
                            st.markdown(f"### 🌟 **{p_info['name']}**님의 자녀 종합 대시보드")
                            
                            p_chart_options = [
                                "막대 그래프 (자녀별 성취도/진행률) [추천]", 
                                "도넛 차트 (자녀 통합 출결 비율)", 
                                "라인 그래프 (자녀별 성취도 추이)"
                            ]
                            selected_p_charts = st.multiselect("📊 보고 싶은 차트를 선택하세요:", p_chart_options, default=p_chart_options)
                            st.write("")
                            df_p_summ = pd.DataFrame(p_summary_rows)
                            
                            # ✨ [학부모 차트] SVG 포맷 및 반응형 사이즈 적용
                            if "막대 그래프 (자녀별 성취도/진행률) [추천]" in selected_p_charts and not df_p_summ.empty:
                                p_col1, p_col2 = st.columns(2)
                                with p_col1:
                                    with st.container(border=True):
                                        st.markdown(f"##### 📊 자녀별 프로그램 진행률 (막대 그래프)")
                                        fig_p1, ax_p1 = plt.subplots(figsize=(6, 4))
                                        sns.barplot(data=df_p_summ, x='라벨', y='진행률(%)', ax=ax_p1, palette='mako')
                                        ax_p1.set_ylim(0, 100); ax_p1.tick_params(axis='x', rotation=15)
                                        st.pyplot(fig_p1, format="svg", use_container_width=True)
                                        plt.close(fig_p1)
                                        
                                        if df_p_summ['진행률(%)'].max() == 0:
                                            st.info("📉 진행된 과업이 없습니다.")
                                        else:
                                            top_prog = df_p_summ.loc[df_p_summ['진행률(%)'].idxmax()]
                                            st.markdown(f"<div class='report-box'><div class='pos-text'>🟢 긍정적 시그널: {top_prog['자녀명']} {T_USER}의 활동이 {top_prog['진행률(%)']}%로 가장 활발합니다.</div></div>", unsafe_allow_html=True)
                                            
                                with p_col2:
                                    with st.container(border=True):
                                        st.markdown(f"##### 📊 자녀별 평균 성취도 (막대 그래프)")
                                        fig_p2, ax_p2 = plt.subplots(figsize=(6, 4))
                                        sns.barplot(data=df_p_summ, x='라벨', y='평균 성취도', ax=ax_p2, palette='flare')
                                        ax_p2.set_ylim(0, 100); ax_p2.tick_params(axis='x', rotation=15)
                                        st.pyplot(fig_p2, format="svg", use_container_width=True)
                                        plt.close(fig_p2)
                                        
                                        if df_p_summ['평균 성취도'].max() == 0:
                                            st.info("📉 평가 점수가 없습니다.")
                                        else:
                                            top_s = df_p_summ.loc[df_p_summ['평균 성취도'].idxmax()]
                                            low_s_df = df_p_summ[(df_p_summ['평균 성취도'] > 0) & (df_p_summ['평균 성취도'] < 60)]
                                            pos_msg = f"<div class='pos-text'>🟢 긍정적 시그널: {top_s['자녀명']} {T_USER}의 성취도가 {top_s['평균 성취도']:.1f}점으로 뛰어납니다.</div>"
                                            neg_msg = f"<div class='neg-text'>🔴 주의 요망: {', '.join(low_s_df['자녀명'].unique())} {T_USER}의 성취도 보완이 필요합니다.</div>" if not low_s_df.empty else ""
                                            st.markdown(f"<div class='report-box'>{pos_msg}{neg_msg}</div>", unsafe_allow_html=True)
                            
                            if "도넛 차트 (자녀 통합 출결 비율)" in selected_p_charts:
                                with st.container(border=True):
                                    st.markdown("##### 🍩 자녀 통합 종합 출결 비율 (도넛 차트)")
                                    total_att_p = sum(att_counts_total.values())
                                    if total_att_p == 0:
                                        st.info("📉 기록된 출결 데이터가 없습니다.")
                                    else:
                                        labels = [k for k, v in att_counts_total.items() if v > 0]
                                        sizes = [v for v in att_counts_total.values() if v > 0]
                                        colors = ['#2ECC71', '#FFC107', '#E74C3C', '#9B59B6'][:len(labels)]
                                        
                                        fig_dp, ax_dp = plt.subplots(figsize=(6, 4))
                                        ax_dp.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90, pctdistance=0.85, wedgeprops=dict(width=0.4, edgecolor='w'))
                                        ax_dp.text(0, 0, f"총 {total_att_p}일", ha='center', va='center', fontsize=12, fontweight='bold')
                                        st.pyplot(fig_dp, format="svg", use_container_width=True)
                                        plt.close(fig_dp)
                                        
                                        bad_att_p = att_counts_total['지각'] + att_counts_total['결석']
                                        if bad_att_p == 0:
                                            st.markdown("<div class='report-box'><div class='pos-text'>🟢 긍정적 시그널: 자녀들의 지각/결석이 단 한 번도 없습니다! 훌륭한 출결 관리입니다.</div></div>", unsafe_allow_html=True)
                                        else:
                                            st.markdown(f"<div class='report-box'><div class='neg-text'>🔴 주의 요망: 자녀들의 지각/결석 누적이 총 {bad_att_p}회 입니다. 출결 독려를 부탁드립니다.</div></div>", unsafe_allow_html=True)

                            if "라인 그래프 (자녀별 성취도 추이)" in selected_p_charts:
                                with st.container(border=True):
                                    st.markdown("##### 📈 시간 흐름별 성취도 변화 추이 (라인 그래프)")
                                    if len(trend_data_p) < 2:
                                        st.info("📉 성취도 점수가 2건 이상 누적되어야 추이 그래프를 볼 수 있습니다.")
                                    else:
                                        df_trend_p = pd.DataFrame(trend_data_p).sort_values(by="날짜")
                                        fig_lp, ax_lp = plt.subplots(figsize=(8, 4))
                                        sns.lineplot(data=df_trend_p, x='날짜', y='점수', hue='자녀명', marker='o', ax=ax_lp)
                                        ax_lp.set_ylim(0, 105); ax_lp.tick_params(axis='x', rotation=45)
                                        st.pyplot(fig_lp, format="svg", use_container_width=True)
                                        plt.close(fig_lp)
                                        st.markdown("<div class='report-box'><div class='info-text'>ℹ️ 자녀들의 시간 흐름에 따른 성취도 변화를 직관적으로 비교할 수 있습니다.</div></div>", unsafe_allow_html=True)

                    for idx, s_info in enumerate(linked_students):
                        with parent_tabs[idx + 1]:
                            s_record = next((u for u in db['users'] if u['name'] == s_info['name'] and u['program'] == s_info['program']), None)
                            
                            if s_record:
                                st.markdown(f"### 🏅 [{s_record['program']}] 참가자 **{s_record['name']}**님")
                                st.markdown(f"<span class='badge-blue'>담당 역할: {s_record['role']}</span>", unsafe_allow_html=True)
                                
                                prog_data = next((p for p in db['programs'] if p['title'] == s_record['program']), None)
                                if prog_data:
                                    with st.expander(f"📚 [열람] 프로그램 전체 커리큘럼 보기"):
                                        st.write(f"**프로그램 소개:** {prog_data['desc']}")
                                        st.divider()
                                        st.write(f"**담당 역할 ({s_record['role']}) 상세 일정:**")
                                        for t in prog_data.get('roles_workflow', {}).get(s_record['role'], []):
                                            st.write(f"🔹 **{get_date_label(t)}{t['task']}**")
                                            for stask in t.get('subtasks', []):
                                                st.write(f"  &nbsp;&nbsp;&nbsp;└ {stask['desc']}")
                                
                                st.markdown("#### 📈 우리 아이 성장 리포트")
                                tasks = s_record['workflow']
                                task_names = [t['task'] for t in tasks]
                                task_scores = [t.get('score', 0) for t in tasks]
                                avg_score = sum(task_scores) / len(task_scores) if task_scores else 0
                                
                                total_items = 0; done_items = 0
                                for t in tasks:
                                    total_items += 1; done_items += 1 if t.get('done') else 0
                                    for stask in t.get('subtasks', []): total_items += 1; done_items += 1 if stask.get('done') else 0
                                pct = int((done_items/total_items)*100) if total_items > 0 else 0
                                
                                colR1, colR2 = st.columns(2)
                                colR1.metric("세부 목표 달성률 (체크리스트)", f"{pct}%", f"{done_items} / {total_items} 완료")
                                colR2.metric(f"{T_ADMIN} 종합 성취도 평가", f"{int(avg_score)}점", "100점 만점 기준")

                                st.markdown(f"#### 💌 {T_ADMIN}의 따뜻한 알림장")
                                has_comments = False
                                for t in tasks:
                                    if t.get('comment'):
                                        st.info(f"**[{t['task']}]** {t['comment']}")
                                        has_comments = True
                                if not has_comments: st.write("아직 작성된 코멘트가 없습니다.")
                                st.write("---")

                                st.write("#### ✅ 세부 활동 체크리스트 (열람 전용)")
                                with st.container(border=True):
                                    for t_idx, t in enumerate(tasks):
                                        st.checkbox(f"**{get_date_label(t)}{t['task']}**", value=t.get('done'), key=f"p_chk_{s_record['name']}_{idx}_{t_idx}", disabled=True)
                                        for s_idx, stask in enumerate(t.get('subtasks', [])):
                                            col_empty, col_chk = st.columns([1, 20])
                                            with col_chk:
                                                st.checkbox(f"↳ {stask['desc']}", value=stask.get('done'), key=f"p_chk_sub_{s_record['name']}_{idx}_{t_idx}_{s_idx}", disabled=True)
                                
                                st.write(f"#### 💬 {T_ADMIN}께 메시지 보내기 ({T_USER} 비공개)")
                                chat_box = st.container(border=True, height=250)
                                with chat_box:
                                    if not s_record.get('parent_messages'): st.info("아직 나눈 대화가 없습니다.")
                                    for msg in s_record.get('parent_messages', []):
                                        with st.chat_message("user" if msg['sender'] == 'user' else "assistant"): st.write(msg['content'])
                                with st.form(f"p_chat_form_{s_record['name']}_{idx}", clear_on_submit=True):
                                    c1, c2 = st.columns([8, 2])
                                    msg_input = c1.text_input("메시지 입력", label_visibility="collapsed")
                                    if c2.form_submit_button("전송") and msg_input:
                                        s_record.setdefault('parent_messages', []).append({"sender": "user", "content": f"[{p_info['name']}] {msg_input}"})
                                        if save_data(db): st.rerun()
                            else:
                                st.error(f"[{s_info['name']}] 데이터를 찾을 수 없습니다.")
            else:
                st.error("이름과 비밀번호가 일치하지 않습니다.")

# =========================================================
# [페이지 3] 관리자 페이지
# =========================================================
elif st.session_state.menu_option == UI['menu4']:
    if not st.session_state.get('admin_logged_in', False):
        st.markdown(f"## {UI['page3_title']}")
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
        my_programs = [p['title'] for p in db['programs']] if is_super else admin_info.get('programs', [])

        col_title, col_logout = st.columns([8, 2])
        col_title.markdown(f"## 🛠️ 시설 통합 관리 시스템 <span style='font-size:0.5em; color:gray;'>[{admin_info['name']} 접속중]</span>", unsafe_allow_html=True)
        if col_logout.button("🔓 로그아웃", use_container_width=True): st.session_state['admin_logged_in'] = False; st.rerun()
            
        tab_parent_title = f"👨‍👩‍👧 {T_PARENT} 계정"
        if is_super:
            tab_titles = ["📈 경영 대시보드", "📝 평가/코멘트 작성", "📊 종합 명단", "✅ 출석 관리", "👥 1:1 상담", tab_parent_title, "📝 신규 개설", "🎨 화면 설정", "⚙️ 정보 수정", "🔐 계정 관리"]
        else:
            tab_titles = ["📈 경영 대시보드", "📝 평가/코멘트 작성", "📊 종합 명단", "✅ 출석 관리", "👥 1:1 상담", tab_parent_title, "⚙️ 정보 수정", "🔐 계정 관리"]

        tabs = st.tabs(tab_titles)
        tab_dashboard, tab_eval, tab_overview, tab_attendance, tab_manage_users, tab_parents = tabs[:6]
        
        if is_super:
            tab_create, tab_ui, tab_edit, tab_settings = tabs[6:]
        else:
            tab_edit, tab_settings = tabs[6:]
        
        with tab_dashboard:
            dashboard_title = f"{T_SUPER} 전용" if is_super else f"{admin_info['name']} {T_ADMIN} 전용"
            insight_caller = T_SUPER if is_super else f"{admin_info['name']} {T_ADMIN}"
            
            st.subheader(f"📈 {dashboard_title} 맞춤형 데이터 대시보드")
            users_to_show = [u for u in db['users'] if u['program'] in my_programs]
            
            if not users_to_show: 
                st.info(f"데이터가 부족하여 대시보드를 생성할 수 없습니다. {T_USER}이 등록되고 평가가 진행되어야 합니다.")
            else:
                chart_options = [
                    "막대 그래프 (프로그램별 평균 성취도) [추천]",
                    "도넛 차트 (전체 출결 종합 비율)",
                    "라인 그래프 (시간 흐름별 성취도 추이)",
                    "히트맵 (일자별 출석 밀도 분석)",
                    "산점도 (선생님 피드백 효과 분석) [추천]",
                    "스택 막대 그래프 (출결 상세 비율)"
                ]
                selected_charts = st.multiselect("📊 화면에 띄울 차트를 선택하세요 (다중 선택 가능):", chart_options, default=["막대 그래프 (프로그램별 평균 성취도) [추천]", "산점도 (선생님 피드백 효과 분석) [추천]"])
                st.write("")
                
                dashboard_data = []
                task_data = []
                att_counts_total = {'출석': 0, '지각': 0, '결석': 0, '병결': 0}
                trend_data = []
                heat_data = []
                
                for u in users_to_show:
                    t_scores = [t.get('score', 0) for t in u['workflow']]
                    avg_score = sum(t_scores) / len(t_scores) if t_scores else 0
                    
                    att_counts = 0
                    for d_key, v in u.get('attendance', {}).items():
                        if is_active_role_period(u, d_key):
                            st_val = v.get('status')
                            if st_val == '출석': att_counts += 1
                            if st_val in att_counts_total: att_counts_total[st_val] += 1
                            heat_data.append({"학생명": u['name'], "날짜": d_key, "상태": st_val})
                            
                    comment_counts = sum(1 for t in u['workflow'] if t.get('comment'))
                    
                    dashboard_data.append({
                        "Program": u['program'], "Role": u['role'], "Student": u.get('alias') or u['name'],
                        "AvgScore": avg_score, "Attendance": att_counts, "Comments": comment_counts
                    })
                    
                    for t in u['workflow']:
                        sc = t.get('score', 0)
                        task_data.append({"Program": u['program'], "Task": t['task'], "Score": sc})
                        sd, _ = get_date_range(t)
                        if sc > 0 and sd and re.match(r'\d{4}-\d{2}-\d{2}', sd):
                            trend_data.append({"날짜": sd, "프로그램": u['program'], "점수": sc})
                
                df_dash = pd.DataFrame(dashboard_data)
                df_tasks = pd.DataFrame(task_data)

                # ✨ [관리자 차트] SVG 포맷 및 아담한 사이즈 적용
                if "막대 그래프 (프로그램별 평균 성취도) [추천]" in selected_charts and not df_dash.empty:
                    with st.container(border=True):
                        st.markdown(f"##### 📊 막대 그래프: 프로그램별 평균 성취도 비교")
                        fig1, ax1 = plt.subplots(figsize=(8, 4))
                        sns.barplot(data=df_dash, x='Program', y='AvgScore', ax=ax1, palette='Set2', errorbar=None)
                        ax1.set_ylim(0, 100); ax1.tick_params(axis='x', rotation=15)
                        st.pyplot(fig1, format="svg", use_container_width=True)
                        plt.close(fig1)

                        valid_scores = df_dash[df_dash['AvgScore'] > 0]
                        if valid_scores.empty:
                            st.info("📉 **데이터 부족:** 아직 평가가 충분히 입력되지 않았습니다.")
                        else:
                            top_p = valid_scores.groupby('Program')['AvgScore'].mean().idxmax()
                            top_s = valid_scores.groupby('Program')['AvgScore'].mean().max()
                            low_p = valid_scores.groupby('Program')['AvgScore'].mean().idxmin()
                            low_s = valid_scores.groupby('Program')['AvgScore'].mean().min()
                            st.markdown(f"<div class='report-box'><div class='pos-text'>🟢 긍정적 시그널: '{top_p}' 프로그램이 평균 {top_s:.1f}점으로 가장 우수합니다.</div>" +
                                        (f"<div class='neg-text'>🔴 주의 요망: '{low_p}' 프로그램이 평균 {low_s:.1f}점으로 부진합니다. 원인 파악이 필요합니다.</div></div>" if low_s < 60 else f"<div class='info-text'>ℹ️ 특이사항: 평균 60점 미만인 프로그램은 없습니다.</div></div>"), unsafe_allow_html=True)

                if "도넛 차트 (전체 출결 종합 비율)" in selected_charts:
                    with st.container(border=True):
                        st.markdown(f"##### 🍩 도넛 차트: 시설 전체 {T_USER} 출결 비율")
                        total_att = sum(att_counts_total.values())
                        if total_att == 0:
                            st.info("📉 기록된 출결 데이터가 없습니다.")
                        else:
                            labels = [k for k, v in att_counts_total.items() if v > 0]
                            sizes = [v for v in att_counts_total.values() if v > 0]
                            colors = ['#2ECC71', '#FFC107', '#E74C3C', '#9B59B6'][:len(labels)]
                            
                            fig_d, ax_d = plt.subplots(figsize=(6, 4))
                            ax_d.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90, pctdistance=0.85, wedgeprops=dict(width=0.4, edgecolor='w'))
                            ax_d.text(0, 0, f"총 {total_att}일", ha='center', va='center', fontsize=12, fontweight='bold')
                            st.pyplot(fig_d, format="svg", use_container_width=True)
                            plt.close(fig_d)
                            
                            bad_ratio = ((att_counts_total['지각'] + att_counts_total['결석']) / total_att) * 100
                            if bad_ratio < 10:
                                st.markdown("<div class='report-box'><div class='pos-text'>🟢 긍정적 시그널: 전체 지각/결석 비율이 10% 미만으로 매우 안정적입니다.</div></div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div class='report-box'><div class='neg-text'>🔴 주의 요망: 전체 결석 및 지각 비율이 {bad_ratio:.1f}%에 달합니다. 출결 관리 캠페인이 필요합니다.</div></div>", unsafe_allow_html=True)

                if "라인 그래프 (시간 흐름별 성취도 추이)" in selected_charts:
                    with st.container(border=True):
                        st.markdown(f"##### 📈 라인 그래프: 시간에 따른 프로그램 성과 변화")
                        if len(trend_data) < 2:
                            st.info("📉 성취도 점수가 다양한 날짜에 걸쳐 2건 이상 누적되어야 추이 확인이 가능합니다.")
                        else:
                            df_t = pd.DataFrame(trend_data).sort_values(by="날짜")
                            fig_l, ax_l = plt.subplots(figsize=(10, 4))
                            sns.lineplot(data=df_t, x='날짜', y='점수', hue='프로그램', marker='o', ax=ax_l)
                            ax_l.set_ylim(0, 105); ax_l.tick_params(axis='x', rotation=45)
                            st.pyplot(fig_l, format="svg", use_container_width=True)
                            plt.close(fig_l)
                            st.markdown("<div class='report-box'><div class='info-text'>ℹ️ 선이 우상향하면 성취도가 개선되는 추세이며, 우하향할 경우 학습 난이도 조절이 필요할 수 있습니다.</div></div>", unsafe_allow_html=True)

                if "히트맵 (일자별 출석 밀도 분석)" in selected_charts:
                    with st.container(border=True):
                        st.markdown(f"##### 🔲 히트맵: {T_USER}별 출결 패턴 밀도")
                        if not heat_data:
                            st.info("📉 기록된 출석 데이터가 없어 히트맵을 생성할 수 없습니다.")
                        else:
                            df_h = pd.DataFrame(heat_data)
                            val_map = {'출석': 1, '지각': 0.5, '결석': -1, '병결': -0.5}
                            df_h['NumericStatus'] = df_h['상태'].map(val_map)
                            pivot_h = df_h.pivot_table(index='학생명', columns='날짜', values='NumericStatus', fill_value=0)
                            
                            fig_h, ax_h = plt.subplots(figsize=(10, max(3, len(pivot_h)*0.5)))
                            sns.heatmap(pivot_h, cmap='RdYlGn', cbar=False, linewidths=.5, ax=ax_h)
                            ax_h.set_title("초록색: 출석, 노란색: 지각, 빨간색: 결석", fontsize=10, color='gray')
                            st.pyplot(fig_h, format="svg", use_container_width=True)
                            plt.close(fig_h)
                            st.markdown("<div class='report-box'><div class='info-text'>ℹ️ 붉은색이 연속해서 나타나는 행(특정 학생)이나 열(특정 요일)을 찾아 개별 면담이나 스케줄 보완을 진행하세요.</div></div>", unsafe_allow_html=True)

                if "산점도 (선생님 피드백 효과 분석) [추천]" in selected_charts and not df_dash.empty:
                    with st.container(border=True):
                        st.markdown(f"##### 🎯 산점도: {T_ADMIN} 피드백 빈도와 {T_USER} 성과 상관관계")
                        fig_s, ax_s = plt.subplots(figsize=(8, 4))
                        sns.scatterplot(data=df_dash, x='Comments', y='AvgScore', hue='Program', s=100, ax=ax_s, palette='Set1', alpha=0.8)
                        ax_s.set_xlabel('Number of Comments Given')
                        ax_s.set_ylabel('Average Score')
                        st.pyplot(fig_s, format="svg", use_container_width=True)
                        plt.close(fig_s)

                        valid_sc = df_dash[df_dash['AvgScore'] > 0]
                        if df_dash['Comments'].sum() == 0 or len(valid_sc) < 3:
                            st.info(f"📉 **데이터 부족:** 작성된 코멘트(피드백)가 충분하지 않아 상관관계를 분석할 수 없습니다.")
                        else:
                            corr = df_dash['Comments'].corr(df_dash['AvgScore'])
                            if pd.isna(corr):
                                st.info("📉 **데이터 부족:** 변동성이 부족하여 상관계수를 도출할 수 없습니다.")
                            elif corr >= 0.3:
                                st.markdown(f"<div class='report-box'><div class='pos-text'>🟢 긍정적 시그널: 코멘트 수와 성취도 간에 양의 상관관계(계수: {corr:.2f})가 존재합니다. 피드백이 점수 향상에 기여하고 있습니다.</div></div>", unsafe_allow_html=True)
                            elif corr <= -0.3:
                                st.markdown(f"<div class='report-box'><div class='neg-text'>🔴 주의 요망: 코멘트와 성취도가 역상관(계수: {corr:.2f})을 보입니다. 잔소리성 피드백이 아닌지 코멘트의 질적 점검이 필요합니다.</div></div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div class='report-box'><div class='info-text'>ℹ️ 특이사항: 피드백 횟수와 성적 간에 뚜렷한 패턴이 관찰되지 않았습니다.</div></div>", unsafe_allow_html=True)

                if "스택 막대 그래프 (출결 상세 비율)" in selected_charts:
                    with st.container(border=True):
                        st.markdown(f"##### 📊 스택 막대 그래프: 프로그램별 출결 누적 구성")
                        if not heat_data:
                            st.info("📉 기록된 출석 데이터가 없습니다.")
                        else:
                            df_h = pd.DataFrame(heat_data)
                            prog_map = {u['name']: u['program'] for u in users_to_show}
                            df_h['Program'] = df_h['학생명'].map(prog_map)
                            
                            agg_df = df_h.groupby(['Program', '상태']).size().unstack(fill_value=0)
                            for col in ['출석', '지각', '결석', '병결']:
                                if col not in agg_df.columns: agg_df[col] = 0
                            agg_df = agg_df[['출석', '지각', '결석', '병결']]
                            
                            fig_st, ax_st = plt.subplots(figsize=(10, 4))
                            colors = ['#2ECC71', '#FFC107', '#E74C3C', '#9B59B6']
                            agg_df.plot(kind='bar', stacked=True, ax=ax_st, color=colors, edgecolor='white')
                            ax_st.set_ylabel('Days Count')
                            plt.xticks(rotation=15, ha='right')
                            plt.legend(title='상태', bbox_to_anchor=(1.05, 1), loc='upper left')
                            st.pyplot(fig_st, format="svg", use_container_width=True)
                            plt.close(fig_st)
                            st.markdown("<div class='report-box'><div class='info-text'>ℹ️ 각 막대의 전체 길이는 총 수업일수를 나타내며, 내부 색상 비율을 통해 결석이 유독 많은 프로그램을 쉽게 색출할 수 있습니다.</div></div>", unsafe_allow_html=True)

        with tab_eval:
            st.subheader(f"📝 {T_USER} 주차/과업별 달성도 및 코멘트 평가")
            if not my_programs: st.info("담당 프로그램이 없습니다.")
            else:
                col_sel1, col_sel2 = st.columns([5, 5])
                eval_prog = col_sel1.selectbox("📋 프로그램 선택", my_programs, key="eval_prog")
                prog_users = [(i, u) for i, u in enumerate(db['users']) if u['program'] == eval_prog]
                
                if not prog_users: st.warning(f"신청한 {T_USER}이 없습니다.")
                else:
                    eval_user_options = {f"{u.get('alias') or u['name']} ({u['role']})": i for i, u in prog_users}
                    selected_user_label = col_sel2.selectbox(f"🎓 {T_USER} 선택", list(eval_user_options.keys()))
                    target_idx = eval_user_options[selected_user_label]
                    target_user = db['users'][target_idx]
                    
                    st.write(f"#### 🏅 {target_user['name']} {T_USER} 평가 입력")
                    st.info("💡 각 주차(과업)의 세부 내용을 확인하시고, 이를 종합하여 성취도 점수와 피드백 코멘트를 남겨주세요.")
                    
                    with st.form(f"eval_form_{target_idx}"):
                        for t_idx, t in enumerate(target_user['workflow']):
                            st.markdown(f"**[{t['task']}]** <span style='color:gray; font-size:0.85em;'>*(기간: {get_date_label(t).strip()})*</span>", unsafe_allow_html=True)
                            
                            if t.get('subtasks'):
                                sub_texts = [f"↳ {stask['desc']} {'(✅완료)' if stask.get('done') else '(미완료)'}" for stask in t['subtasks']]
                                st.caption("\n".join(sub_texts))
                            
                            c1, c2 = st.columns([3, 7])
                            new_score = c1.slider("해당 주차 종합 성취도 점수", 0, 100, t.get('score', 0), key=f"score_{target_idx}_{t_idx}")
                            new_comment = c2.text_input(f"{T_PARENT} 전송용 코멘트", value=t.get('comment', ''), placeholder="이 주차의 세부 목표 달성도에 대한 칭찬이나 아쉬운 점을 적어주세요.", key=f"comment_{target_idx}_{t_idx}")
                            st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
                            
                            target_user['workflow'][t_idx]['score'] = new_score
                            target_user['workflow'][t_idx]['comment'] = new_comment
                            
                        if st.form_submit_button("💾 전체 평가 저장하기", type="primary", use_container_width=True):
                            if save_data(db):
                                st.success("평가와 코멘트가 저장되어 리포트에 반영되었습니다!")
                                time.sleep(1)
                                st.rerun()

        with tab_overview:
            st.write("#### 📊 데이터 필터링 및 엑셀(이미지) 추출")
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
                
                fig_table, ax_table = plt.subplots(figsize=(10, max(2, len(df_out) * 0.5 + 1.5)))
                ax_table.axis('tight')
                ax_table.axis('off')
                
                table = ax_table.table(cellText=df_out.values, colLabels=df_out.columns, loc='center', cellLoc='center')
                table.auto_set_font_size(False)
                table.set_fontsize(11)
                table.scale(1.2, 1.8)
                
                for (row, col), cell in table.get_celld().items():
                    if row == 0:
                        cell.set_facecolor('#4f46e5')
                        cell.set_text_props(color='white', weight='bold')
                
                buf = io.BytesIO()
                plt.savefig(buf, format="png", bbox_inches='tight', dpi=300)
                buf.seek(0)
                plt.close(fig_table) 
                
                st.download_button(
                    label="📥 결과 이미지(PNG) 다운로드",
                    data=buf,
                    file_name=f"YouthCanvas_명단_{datetime.now().strftime('%Y%m%d')}.png",
                    mime="image/png",
                    type="primary"
                )
            else: st.info("데이터가 없습니다.")

        with tab_attendance:
            st.subheader("✅ 프로그램별 출석 관리")
            if my_programs:
                att_prog = st.selectbox("📋 출석 체크 프로그램", my_programs, key="att_prog_select")
                pu = [(i, u) for i, u in enumerate(db['users']) if u['program'] == att_prog]
                
                if not pu:
                    st.warning(f"해당 프로그램에 신청한 {T_USER}이 없습니다.")
                else:
                    att_sub1, att_sub2, att_sub3 = st.tabs(["📅 일일 출석 입력", "📊 전체 출석 현황 & 시각화", "✏️ 개별 기록 수정/삭제"])
                    
                    with att_sub1:
                        p_data = next((p for p in db['programs'] if p['title'] == att_prog), None)
                        all_dates = []
                        if p_data:
                            for role, tasks in p_data.get('roles_workflow', {}).items():
                                for t in tasks:
                                    sd, ed = get_date_range(t)
                                    for d_str in [sd, ed]:
                                        if d_str and re.match(r'\d{4}-\d{2}-\d{2}', d_str):
                                            try: all_dates.append(datetime.strptime(d_str, "%Y-%m-%d").date())
                                            except: pass
                        
                        date_kwargs = {}
                        if all_dates:
                            min_d, max_d = min(all_dates), max(all_dates)
                            date_kwargs['min_value'] = min_d
                            date_kwargs['max_value'] = max_d
                            def_d = date.today()
                            if def_d < min_d: def_d = min_d
                            elif def_d > max_d: def_d = max_d
                            date_kwargs['value'] = def_d
                        else:
                            date_kwargs['value'] = date.today()

                        att_date_obj = st.date_input("🗓️ 출석을 기록할 날짜 선택 (프로그램 기간만 선택 가능)", **date_kwargs)
                        att_date = att_date_obj.strftime("%Y-%m-%d")
                        
                        active_pu = []
                        for idx, u in pu:
                            if is_active_role_period(u, att_date):
                                active_pu.append((idx, u))

                        if not active_pu:
                            st.info(f"💡 선택하신 **{att_date}**에 일정이 할당된 역할({T_USER})이 없습니다. 다른 날짜를 선택해 주세요.")
                        else:
                            st.info(f"💡 선택하신 **{att_date}**에 일정이 있는 {T_USER}만 표시됩니다.")
                            with st.form(f"att_form"):
                                att_up = {}
                                h1, h2, h3 = st.columns([3, 3, 4])
                                h1.write(f"**{T_USER}명 (역할)**")
                                h2.write("**상태**")
                                h3.write("**비고**")
                                st.divider()
                                
                                for idx, u in active_pu:
                                    curr_st = u.get('attendance', {}).get(att_date, {}).get('status', '출석')
                                    curr_nt = u.get('attendance', {}).get(att_date, {}).get('note', '')
                                    c1, c2, c3 = st.columns([3, 3, 4])
                                    c1.write(f"**{u.get('alias') or u['name']}**\n<br><span style='color:gray; font-size:0.8em;'>{u['role']}</span>", unsafe_allow_html=True)
                                    ns = c2.selectbox("상태", ["출석", "지각", "결석", "병결"], index=["출석", "지각", "결석", "병결"].index(curr_st), key=f"s_{idx}", label_visibility="collapsed")
                                    nn = c3.text_input("비고", value=curr_nt, key=f"n_{idx}", label_visibility="collapsed")
                                    att_up[idx] = {"status": ns, "note": nn}
                                    
                                st.write("")
                                if st.form_submit_button("💾 출석 저장", type="primary", use_container_width=True):
                                    for idx, ad in att_up.items():
                                        if 'attendance' not in db['users'][idx]: db['users'][idx]['attendance'] = {}
                                        db['users'][idx]['attendance'][att_date] = ad
                                    if save_data(db): 
                                        st.success(f"{att_date} 출석 정보가 성공적으로 저장되었습니다!"); time.sleep(1); st.rerun()

                    with att_sub2:
                        st.markdown(f"#### 🔍 {T_USER}별 종합 출석부 및 시각화")
                        att_records = []
                        for i, u in pu:
                            disp_name = u.get('alias') or u['name']
                            for d_key, info in u.get('attendance', {}).items():
                                if is_active_role_period(u, d_key):
                                    att_records.append({
                                        f"{T_USER}명": f"{disp_name}({u['role']})",
                                        "날짜": d_key,
                                        "상태": info['status'],
                                        "비고": info['note']
                                    })
                        
                        if att_records:
                            df_att = pd.DataFrame(att_records)
                            st.write(f"##### 📅 {T_USER}별 일자별 출석 상세 (유효 기간 한정)")
                            pivot_df = df_att.pivot(index=f"{T_USER}명", columns='날짜', values='상태').fillna('-')
                            pivot_df = pivot_df.reindex(sorted(pivot_df.columns), axis=1) 
                            st.dataframe(pivot_df, use_container_width=True)
                            
                            st.write(f"##### 📊 {T_USER}별 누적 현황 시각화 (스택 막대 그래프)")
                            agg_df = df_att.groupby([f"{T_USER}명", '상태']).size().unstack(fill_value=0)
                            for col in ['출석', '지각', '결석', '병결']:
                                if col not in agg_df.columns: agg_df[col] = 0
                            agg_df = agg_df[['출석', '지각', '결석', '병결']]
                            
                            fig_att, ax_att = plt.subplots(figsize=(10, 4))
                            colors = ['#2ECC71', '#FFC107', '#E74C3C', '#9B59B6']
                            agg_df.plot(kind='bar', stacked=True, ax=ax_att, color=colors, edgecolor='white')
                            ax_att.set_ylabel('Days Count')
                            ax_att.set_xlabel('')
                            plt.xticks(rotation=15, ha='right')
                            plt.legend(title='상태', bbox_to_anchor=(1.05, 1), loc='upper left')
                            st.pyplot(fig_att, format="svg", use_container_width=True)
                            plt.close(fig_att)
                            
                            st.divider()
                            st.markdown(f"#### 🚨 이탈 위험 {T_USER} 자동 리포트 (경고 시스템)")
                            threshold = st.slider("⚠️ 위험 기준 설정 (결석+지각 누적 비율 %)", min_value=10, max_value=100, value=30, step=5)
                            
                            risk_reports = []
                            for student_name, row in agg_df.iterrows():
                                total_days = row.sum()
                                if total_days > 0:
                                    bad_days = row['결석'] + row['지각']
                                    bad_ratio = (bad_days / total_days) * 100
                                    
                                    if bad_ratio >= threshold:
                                        student_records = df_att[df_att[f'{T_USER}명'] == student_name]
                                        recent_notes = student_records[student_records['비고'] != '']['비고'].tail(3).tolist()
                                        note_str = ", ".join(recent_notes) if recent_notes else "특이사항 없음"
                                        
                                        risk_reports.append({
                                            f"{T_USER}명": student_name,
                                            "위험 지수": f"{bad_ratio:.1f}%",
                                            "총 기록일": total_days,
                                            "결석": row['결석'],
                                            "지각": row['지각'],
                                            "최근 비고": note_str
                                        })
                            
                            if risk_reports:
                                st.error(f"**주의 요망!** 설정하신 기준({threshold}%)을 초과하여 집중 관리가 필요한 {T_USER}이 {len(risk_reports)}명 있습니다.")
                                df_risk = pd.DataFrame(risk_reports)
                                st.dataframe(df_risk, use_container_width=True, hide_index=True)
                                
                                report_text = f"단기 이탈 위험 {T_USER} 리포트 (기준: 결석/지각 {threshold}% 이상)\n"
                                report_text += "=" * 40 + "\n"
                                for r in risk_reports:
                                    report_text += f"👤 {r[f'{T_USER}명']}\n"
                                    report_text += f" - 위험 지수: {r['위험 지수']} (총 {r['총 기록일']}일 중 결석 {r['결석']}일, 지각 {r['지각']}일)\n"
                                    report_text += f" - 최근 비고: {r['최근 비고']}\n\n"
                                
                                with st.expander("📄 텍스트 리포트 복사하기"):
                                    st.text_area("아래 내용을 복사하여 카카오톡이나 보고서에 바로 활용하세요.", value=report_text, height=200)
                            else:
                                st.success(f"현재 결석/지각 비율이 {threshold}% 이상인 이탈 위험 {T_USER}이 없습니다. 아주 잘 관리되고 있습니다!")
                                
                        else:
                            st.info("아직 기록된 출석 데이터가 없습니다. [일일 출석 입력] 탭에서 먼저 출석을 기록해 주세요.")
                            
                    with att_sub3:
                        st.markdown(f"#### ✏️ 개별 {T_USER} 출석 기록 수정 및 삭제")
                        
                        att_user_options = {f"{u.get('alias') or u['name']} ({u['role']})": i for i, u in pu}
                        selected_user_label = st.selectbox(f"🎓 수정할 {T_USER} 선택", list(att_user_options.keys()), key="att_edit_user")
                        target_idx = att_user_options[selected_user_label]
                        target_user = db['users'][target_idx]
                        
                        att_history = target_user.get('attendance', {})
                        if not att_history:
                            st.warning(f"이 {T_USER}은 아직 기록된 출석 데이터가 없습니다.")
                        else:
                            sorted_dates = sorted(list(att_history.keys()), reverse=True)
                            selected_date = st.selectbox("🗓️ 수정/삭제할 날짜 선택", sorted_dates, key="att_edit_date")
                            
                            curr_record = att_history[selected_date]
                            
                            with st.form(f"att_edit_form_{target_idx}_{selected_date}"):
                                c1, c2 = st.columns(2)
                                new_status = c1.selectbox("상태", ["출석", "지각", "결석", "병결"], index=["출석", "지각", "결석", "병결"].index(curr_record['status']))
                                new_note = c2.text_input("비고", value=curr_record.get('note', ''))
                                
                                st.write("")
                                col_btn1, col_btn2 = st.columns(2)
                                submit_edit = col_btn1.form_submit_button("💾 이 날짜 기록 수정", type="primary", use_container_width=True)
                                submit_delete = col_btn2.form_submit_button("🗑️ 이 날짜 기록 완전히 삭제", use_container_width=True)
                                
                                if submit_edit:
                                    db['users'][target_idx]['attendance'][selected_date] = {"status": new_status, "note": new_note}
                                    if save_data(db):
                                        st.success(f"{selected_date} 기록이 성공적으로 수정되었습니다!")
                                        time.sleep(1)
                                        st.rerun()
                                        
                                if submit_delete:
                                    del db['users'][target_idx]['attendance'][selected_date]
                                    if save_data(db):
                                        st.success(f"{selected_date} 기록이 완전히 삭제되었습니다!")
                                        time.sleep(1)
                                        st.rerun()

        with tab_manage_users:
            if my_programs:
                sel_p = st.selectbox("프로그램", my_programs, key="m_prog")
                pu = [(i, u) for i, u in enumerate(db['users']) if u['program'] == sel_p]
                if pu:
                    ops = {f"{u.get('alias') or u['name']} ({u['role']})": i for i, u in pu}
                    t_idx = ops[st.selectbox(f"{T_USER} 선택", list(ops.keys()))]
                    tu = db['users'][t_idx]
                    
                    with st.container(border=True):
                        chat_target = st.radio("💬 대화 상대 선택", [f"👦 {T_USER}과 대화", f"👨‍👩‍👧 {T_PARENT}와 대화"], horizontal=True)
                        msg_key = 'messages' if chat_target == f"👦 {T_USER}과 대화" else 'parent_messages'
                        
                        st.divider()
                        if not tu.get(msg_key): st.info("아직 나눈 대화가 없습니다.")
                        for msg in tu.get(msg_key, []):
                            with st.chat_message("assistant" if msg['sender'] == 'admin' else "user"): st.write(msg['content'])
                        
                        with st.form(f"adm_chat_{t_idx}_{msg_key}", clear_on_submit=True):
                            c1, c2 = st.columns([8, 2])
                            ri = c1.text_input("답장", label_visibility="collapsed")
                            if c2.form_submit_button("전송") and ri:
                                tu.setdefault(msg_key, []).append({"sender": "admin", "content": ri})
                                if save_data(db): st.rerun()
                    
                    st.divider()
                    st.write(f"#### ✏️ {T_USER} 정보 수정")
                    with st.form(f"edit_user_form_{t_idx}"):
                        c_u1, c_u2 = st.columns(2)
                        edit_u_name = c_u1.text_input(f"새 {T_USER}명", value=tu['name'])
                        edit_u_pin = c_u2.text_input("새 비밀번호 (4자리 숫자)", value=tu.get('pin', '0000'), max_chars=4)
                        
                        if st.form_submit_button(f"{T_USER} 정보 수정 저장", type="primary"):
                            if edit_u_name and len(edit_u_pin) == 4 and edit_u_pin.isdigit():
                                old_u_name = tu['name']
                                if old_u_name != edit_u_name:
                                    for p in db['parents']:
                                        for s in p.get('linked_students', []):
                                            if s['name'] == old_u_name and s['program'] == tu['program']:
                                                s['name'] = edit_u_name
                                                
                                tu['name'] = edit_u_name
                                tu['pin'] = edit_u_pin
                                if save_data(db):
                                    st.success(f"{T_USER} 정보가 완벽하게 수정되었습니다!")
                                    time.sleep(1)
                                    st.rerun()
                            else:
                                st.error("올바른 이름과 4자리 숫자 비밀번호를 입력하세요.")
                                
                    if st.button(f"❌ {T_USER} 강제 퇴소(삭제)"):
                        db['users'].pop(t_idx); save_data(db); st.rerun()

        with tab_parents:
            st.subheader(f"👨‍👩‍👧 {T_PARENT} 통합 CRM (가족 단위 관리)")
            st.info(f"💡 다둥이(형제/자매)가 등록할 경우, 새로운 {T_PARENT} 계정을 만들지 말고 **기존 계정에서 '수정'을 통해 자녀를 추가**하세요. 장기적인 수강 이력 관리가 가능해집니다.")
            
            if not my_programs:
                st.warning("담당 중인 프로그램이 없습니다.")
            else:
                with st.form("parent_create_form"):
                    st.write(f"**➕ 신규 {T_PARENT} 계정 발급**")
                    col1, col2 = st.columns(2)
                    p_name = col1.text_input(f"{T_PARENT} 대표 이름 (예: 김철수/김영희 어머니)")
                    p_pin = col2.text_input(f"{T_PARENT}용 접속 비밀번호 (숫자 4자리)", type="password", max_chars=4)
                    
                    all_students = [f"{u['name']} - {u['program']} ({u['role']})" for u in db['users'] if u['program'] in my_programs]
                    linked_sts = st.multiselect(f"이 계정과 연결할 {T_USER} 선택 (다둥이 다중 선택 가능)", all_students)
                    
                    if st.form_submit_button(f"새로운 {T_PARENT} 계정 생성", type="primary"):
                        if p_name and len(p_pin) == 4 and p_pin.isdigit() and linked_sts:
                            existing_p = next((p for p in db['parents'] if p['name'] == p_name), None)
                            if existing_p:
                                st.error("이미 존재하는 이름입니다. 정보 수정을 이용해 자녀를 추가해주세요.")
                            else:
                                parsed_students = []
                                for st_str in linked_sts:
                                    s_name = st_str.split(" - ")[0]
                                    s_prog = st_str.split(" - ")[1].split(" (")[0]
                                    parsed_students.append({"name": s_name, "program": s_prog})
                                    
                                db['parents'].append({"name": p_name, "pin": p_pin, "linked_students": parsed_students})
                                if save_data(db):
                                    st.success(f"[{p_name}] 가족 계정이 신규 생성되었습니다!")
                                    time.sleep(1)
                                    st.rerun()
                        else:
                            st.error("이름, 4자리 숫자 비밀번호, 연결할 대상을 모두 올바르게 입력해주세요.")
                            
                if db.get('parents'):
                    st.divider()
                    st.markdown(f"#### 📋 {T_PARENT} 및 가족 수강 이력 카드")
                    
                    for p in db['parents']:
                        children_history = defaultdict(list)
                        first_date = "9999-12-31"
                        
                        for s in p.get('linked_students', []):
                            s_name = s['name']
                            s_prog = s['program']
                            prog_obj = next((pr for pr in db['programs'] if pr['title'] == s_prog), None)
                            
                            if prog_obj:
                                p_st = prog_obj.get('recruit_start', '')
                                p_en = prog_obj.get('recruit_end', '')
                                status_str = "진행중" if p_st <= today_str <= p_en else ("종료" if today_str > p_en else "예정")
                                children_history[s_name].append(f"**{s_prog}** ({p_st} ~ {p_en}) - <span style='color:gray;font-size:0.9em;'>{status_str}</span>")
                                if p_st and p_st < first_date: first_date = p_st
                            else:
                                children_history[s_name].append(f"**{s_prog}** (상세일정 없음)")
                        
                        display_first_date = first_date if first_date != "9999-12-31" else "기록 없음"
                        child_names = list(children_history.keys())
                        child_str = ", ".join(child_names) if child_names else "연결된 데이터 없음"
                        
                        with st.container():
                            st.markdown(f"""
                            <div class='crm-card'>
                                <div style='display:flex; justify-content:space-between; align-items:baseline;'>
                                    <div>
                                        <div class='crm-title'>👨‍👩‍👧 {p['name']}</div>
                                        <div class='crm-meta'><b>연결된 자녀:</b> {child_str}</div>
                                    </div>
                                    <div style='text-align:right;'>
                                        <span class='badge-blue'>최초 등록일: {display_first_date}</span><br>
                                        <span style='font-size:0.85em; color:gray;'>총 누적 수강: {sum(len(v) for v in children_history.values())}건</span>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            if children_history:
                                st.markdown("<div class='crm-history-box'>", unsafe_allow_html=True)
                                for c_name, histories in children_history.items():
                                    st.markdown(f"<div class='crm-child-name'>👦👧 {c_name} 수강 이력</div>", unsafe_allow_html=True)
                                    for h in histories:
                                        st.markdown(f"&nbsp;&nbsp; └ {h}", unsafe_allow_html=True)
                                st.markdown("</div></div>", unsafe_allow_html=True)
                            else:
                                st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.divider()
                    st.write(f"#### ✏️ 기존 {T_PARENT} 정보 수정 (자녀 추가)")
                    p_to_edit_name = st.selectbox(f"수정할 {T_PARENT} 선택", [p['name'] for p in db['parents']])
                    p_to_edit = next(p for p in db['parents'] if p['name'] == p_to_edit_name)
                    
                    with st.form("edit_parent_form"):
                        c1, c2 = st.columns(2)
                        new_p_name = c1.text_input("새 이름", value=p_to_edit['name'])
                        new_p_pin = c2.text_input("새 비밀번호 (4자리 숫자)", value=p_to_edit['pin'], max_chars=4)
                        
                        current_linked = [f"{s['name']} - {s['program']} ({next((u['role'] for u in db['users'] if u['name']==s['name'] and u['program']==s['program']), '알수없음')})" for s in p_to_edit.get('linked_students', [])]
                        valid_current = [x for x in current_linked if x in all_students]
                        
                        new_linked_sts = st.multiselect(f"연결할 {T_USER} 다중 선택 (기존 자녀 + 새 자녀)", all_students, default=valid_current)
                        
                        if st.form_submit_button(f"{T_PARENT} 정보 수정 저장", type="primary"):
                            if new_p_name and len(new_p_pin) == 4 and new_p_pin.isdigit():
                                p_to_edit['name'] = new_p_name
                                p_to_edit['pin'] = new_p_pin
                                
                                parsed_students = []
                                for st_str in new_linked_sts:
                                    s_name = st_str.split(" - ")[0]
                                    s_prog = st_str.split(" - ")[1].split(" (")[0]
                                    parsed_students.append({"name": s_name, "program": s_prog})
                                p_to_edit['linked_students'] = parsed_students
                                
                                if save_data(db):
                                    st.success("수정 완료!")
                                    time.sleep(1)
                                    st.rerun()
                            else:
                                st.error("올바른 값을 입력하세요.")

                    st.divider()
                    st.write(f"#### 🗑️ {T_PARENT} 계정 영구 삭제")
                    del_p = st.selectbox("삭제할 계정 선택", [p['name'] for p in db['parents']], label_visibility="collapsed")
                    if st.button("❌ 선택한 가족 계정 전체 삭제"):
                        db['parents'] = [p for p in db['parents'] if p['name'] != del_p]
                        if save_data(db): st.rerun()

        if is_super:
            with tab_ui:
                st.subheader("🎨 화면 UI 및 텍스트 맞춤 설정")
                st.info("💡 사이드바 메뉴명, 메인 로고, 타이틀 등 화면에 고정된 텍스트와 이모티콘을 기관의 입맛에 맞게 자유롭게 변경하세요.")
                with st.form("ui_setting_form"):
                    st.write("##### 1. 브랜드 & 메인 로고")
                    c1, c2 = st.columns(2)
                    new_brand_title = c1.text_input("메인 로고 (예: Youth Canvas, 청소년수련관)", value=UI.get('brand_title', 'Youth Canvas'))
                    new_brand_sub = c2.text_input("서브 타이틀 (예: 청소년의 꿈을 그리는 공간)", value=UI.get('brand_subtitle', '청소년의 꿈을 그리는 공간'))
                    
                    st.write("##### 2. 좌측 사이드바 메뉴명")
                    c3, c4 = st.columns(2)
                    new_m1 = c3.text_input("메뉴 1 (기본: 찾아보기)", value=UI.get('menu1', '찾아보기 (탐색)'))
                    new_m2 = c4.text_input("메뉴 2 (기본: 나의 이야기)", value=UI.get('menu2', '나의 이야기'))
                    c5, c6 = st.columns(2)
                    new_m3 = c5.text_input("메뉴 3 (기본: 학부모 공간)", value=UI.get('menu3', '👨‍👩‍👧 학부모 공간'))
                    new_m4 = c6.text_input("메뉴 4 (기본: 관계자 외 출입금지)", value=UI.get('menu4', '관계자 외 출입금지'))
                    
                    st.write("##### 3. 페이지별 최상단 메인 제목")
                    c7, c8, c9 = st.columns(3)
                    new_p1 = c7.text_input("메뉴 1 페이지 제목", value=UI.get('page1_title', '✨ 지금 뜨고 있는 활동'))
                    new_p2 = c8.text_input("메뉴 2 페이지 제목", value=UI.get('page2_title', '🙋 나의 활동 진행도'))
                    new_p3 = c9.text_input("메뉴 4 페이지 제목", value=UI.get('page3_title', '🔒 관리자 전용 포털'))
                    
                    if st.form_submit_button("UI 텍스트 저장 및 즉시 적용", type="primary"):
                        db['settings']['ui'] = {
                            "brand_title": new_brand_title,
                            "brand_subtitle": new_brand_sub,
                            "menu1": new_m1,
                            "menu2": new_m2,
                            "menu3": new_m3,
                            "menu4": new_m4,
                            "page1_title": new_p1,
                            "page2_title": new_p2,
                            "page3_title": new_p3
                        }
                        if save_data(db):
                            st.success("화면 텍스트가 성공적으로 변경되었습니다!")
                            time.sleep(1)
                            st.session_state.menu_option = new_m4 
                            st.rerun()

            with tab_create:
                with st.form("create_form"):
                    c1, c2 = st.columns([8, 2])
                    t = c1.text_input("프로그램 명")
                    color = c2.color_picker("색상", "#4f46e5")
                    col_rs, col_re = st.columns(2) 
                    r_s = col_rs.date_input("시작일"); r_e = col_re.date_input("종료일")
                    d = st.text_area("소개"); v = st.text_input("유튜브 링크")
                    w_input = st.text_area("워크플로우 양식 (예: [편집 : 5명]\n2026-04-26 : 1차 편집\n- 컷편집 (세부목표))", height=200)
                    
                    if st.form_submit_button("개설하기", type="primary"):
                        pw = {}; pc = {}; cr = None
                        for line in w_input.split('\n'):
                            line = line.strip()
                            if not line: continue
                            if line.startswith('[') and ']' in line:
                                cr = safe_key(line[1:line.find(']')].split(':')[0].strip())
                                pc[cr] = int(re.sub(r'[^0-9]', '', line.split(':')[1])) if ':' in line else 10
                                pw[cr] = []
                            elif cr and ':' in line and not line.startswith('-'):
                                dt, tk = line.split(':', 1)
                                sd, ed = dt.split('~', 1) if '~' in dt else (dt, dt)
                                pw[cr].append({"start_date": sd.strip(), "end_date": ed.strip(), "task": tk.strip(), "subtasks": [], "done": False, "score":0, "comment":""})
                            elif cr and line.startswith('-'):
                                if pw[cr]: pw[cr][-1]["subtasks"].append({"desc": line[1:].strip(), "done": False})
                        db['programs'].append({"title": t, "desc": d, "video": v, "color": color, "recruit_start": r_s.strftime("%Y-%m-%d"), "recruit_end": r_e.strftime("%Y-%m-%d"), "roles_capacity": pc, "roles_workflow": pw})
                        if not is_super: next(a for a in db['admins'] if a['name'] == admin_info['name']).setdefault('programs', []).append(t)
                        if save_data(db): st.success("개설 완료!"); time.sleep(1); st.rerun()
                        else: db['programs'].pop()

        with tab_edit:
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
                            if sd and ed and sd != ed: initial_w += f"{sd} ~ {ed} : {t['task']}\n"
                            elif sd and sd != "-": initial_w += f"{sd} : {t['task']}\n"
                            else: initial_w += f"{t['task']}\n"
                            for stask in t.get('subtasks', []):
                                initial_w += f"- {stask['desc']}\n"
                        initial_w += "\n"

                    with st.form("edit_form"):
                        colA, colB = st.columns([8, 2])
                        new_t = colA.text_input("프로그램 명", value=p_data['title'])
                        new_color = colB.color_picker("캘린더 색상 변경", value=p_data.get('color', '#4f46e5'))
                        
                        st.write("🗓️ **모집 기간 변경**")
                        colD1, colD2 = st.columns(2)
                        def_start = datetime.strptime(p_data.get('recruit_start', today_str), "%Y-%m-%d")
                        def_end = datetime.strptime(p_data.get('recruit_end', "2026-12-31"), "%Y-%m-%d")
                        new_r_start = colD1.date_input("모집 시작일 수정", value=def_start)
                        new_r_end = colD2.date_input("모집 종료일 수정", value=def_end)

                        new_d = st.text_area("상세 내용", value=p_data['desc'])
                        new_v = st.text_input("유튜브 링크", value=p_data.get('video',''))
                        st.info("세부 목표는 메인 과업 바로 아랫줄에 '-' 기호를 붙여 작성하세요.")
                        new_w = st.text_area("워크플로우 수정 (기간은 물결 ~ 사용)", value=initial_w.strip(), height=300)
                        
                        if st.form_submit_button("수정 내용 저장", type="primary"):
                            pw = {}; pc = {}; cr = None
                            for line in new_w.split('\n'):
                                line = line.strip()
                                if not line: continue
                                if line.startswith('[') and ']' in line:
                                    cr = safe_key(line[1:line.find(']')].split(':')[0].strip())
                                    pc[cr] = int(re.sub(r'[^0-9]', '', line.split(':')[1])) if ':' in line else 10
                                    pw[cr] = []
                                elif cr and ':' in line and not line.startswith('-'):
                                    dt, tk = line.split(':', 1)
                                    sd, ed = dt.split('~', 1) if '~' in dt else (dt, dt)
                                    pw[cr].append({"start_date": sd.strip(), "end_date": ed.strip(), "task": tk.strip(), "subtasks": [], "done": False, "score":0, "comment":""})
                                elif cr and line.startswith('-'):
                                    if pw[cr]: pw[cr][-1]["subtasks"].append({"desc": line[1:].strip(), "done": False})
                            
                            old_title = p_data['title']
                            
                            if new_t != old_title:
                                for a in db['admins']:
                                    if old_title in a.get('programs', []):
                                        a['programs'] = [new_t if x == old_title else x for x in a['programs']]
                                for p in db['parents']:
                                    for s in p.get('linked_students', []):
                                        if s['program'] == old_title:
                                            s['program'] = new_t
                                        
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
                                                            if new_st_dict['desc'] == old_st_dict['desc']:
                                                                new_st_dict['done'] = old_st_dict.get('done', False)
                                        u['workflow'] = new_user_workflow
                            
                            temp_prog = db['programs'][p_idx]
                            db['programs'][p_idx] = {
                                "title": new_t, "desc": new_d, "video": new_v, "color": new_color, 
                                "recruit_start": new_r_start.strftime("%Y-%m-%d"),
                                "recruit_end": new_r_end.strftime("%Y-%m-%d"),
                                "roles_capacity": pc, "roles_workflow": pw
                            }
                            
                            if save_data(db):
                                st.success("수정 완료! 새로운 기능과 데이터가 완벽하게 동기화되었습니다. 보안을 위해 잠시 후 로그아웃됩니다.")
                                time.sleep(2)
                                st.session_state['admin_logged_in'] = False
                                st.rerun()
                            else:
                                db['programs'][p_idx] = temp_prog # 롤백

        with tab_settings:
            with st.form("pin_form"):
                npin = st.text_input("내 계정 새 비밀번호 변경 (4자리)", type="password", max_chars=4)
                if st.form_submit_button("변경 적용"):
                    if len(npin) == 4 and npin.isdigit():
                        adm = next(a for a in db['admins'] if a['name'] == admin_info['name'])
                        op = adm['pin']; adm['pin'] = npin
                        if save_data(db): st.success("변경 완료. 다시 로그인하세요."); time.sleep(1); st.session_state['admin_logged_in'] = False; st.rerun()
                        else: adm['pin'] = op
                    else: st.error("4자리 숫자로 입력해주세요.")
            
            if is_super:
                with st.container(border=True):
                    st.subheader("🔤 맞춤형 호칭 설정 (명칭 변수 변경)")
                    st.info("💡 기관의 성격에 맞게 시스템상에서 사람을 부르는 호칭을 일괄 변경하세요.")
                    with st.form("terms_form"):
                        c1, c2, c3, c4 = st.columns(4)
                        new_t_super = c1.text_input("최고관리자 호칭", value=T_SUPER)
                        new_t_admin = c2.text_input("일반관리자 호칭", value=T_ADMIN)
                        new_t_user = c3.text_input("이용자 호칭", value=T_USER)
                        new_t_parent = c4.text_input("보호자 호칭", value=T_PARENT)
                        
                        if st.form_submit_button("호칭 변경 적용", type="primary"):
                            db['settings']['terms'] = {"super": new_t_super, "admin": new_t_admin, "user": new_t_user, "parent": new_t_parent}
                            if save_data(db):
                                st.success("시스템 호칭이 성공적으로 변경되었습니다!")
                                time.sleep(1)
                                st.rerun()
                
                with st.container(border=True):
                    st.subheader(f"👑 {T_SUPER}: {T_ADMIN} 계정 관리")
                    with st.form("new_admin_form"):
                        st.write(f"**➕ 신규 {T_ADMIN} 계정 생성**")
                        colA, colB = st.columns(2)
                        new_adm_name = colA.text_input(f"이름 (예: 김철수 선생님)")
                        new_adm_pin = colB.text_input("초기 비밀번호 4자리", max_chars=4)
                        all_prog_titles = [p['title'] for p in db['programs']]
                        assign_progs = st.multiselect("담당 프로그램 할당", all_prog_titles)
                        
                        if st.form_submit_button(f"계정 생성", type="primary"):
                            if not new_adm_name or len(new_adm_pin) != 4 or not new_adm_pin.isdigit():
                                st.error("이름과 4자리 숫자 비밀번호를 정확히 입력하세요.")
                            else:
                                db['admins'].append({"name": new_adm_name, "pin": new_adm_pin, "role": "normal", "programs": assign_progs})
                                if save_data(db):
                                    st.success(f"[{new_adm_name}] 계정이 생성되었습니다!"); time.sleep(1); st.rerun()
                                else:
                                    db['admins'].pop()
                    
                    st.write(f"#### 📋 등록된 {T_ADMIN} 목록")
                    df_admins = pd.DataFrame([{"이름": a['name'], "권한": T_SUPER if a['role'] == "super" else T_ADMIN, "담당 프로그램": ", ".join(a.get('programs', [])) if a.get('programs') else "없음/전체"} for a in db['admins']])
                    st.dataframe(df_admins, hide_index=True, use_container_width=True)
                    
                    st.divider()
                    st.write(f"#### ✏️ 기존 {T_ADMIN} 정보 수정")
                    normal_admins = [a['name'] for a in db['admins'] if a['role'] != 'super']
                    if normal_admins:
                        a_to_edit_name = st.selectbox(f"수정할 {T_ADMIN} 선택", normal_admins)
                        a_to_edit = next(a for a in db['admins'] if a['name'] == a_to_edit_name)
                        
                        with st.form("edit_admin_form"):
                            c1, c2 = st.columns(2)
                            new_a_name = c1.text_input("새 이름", value=a_to_edit['name'])
                            new_a_pin = c2.text_input("새 비밀번호 (4자리)", value=a_to_edit['pin'], max_chars=4)
                            
                            valid_progs = [p for p in a_to_edit.get('programs', []) if p in all_prog_titles]
                            new_assign_progs = st.multiselect("담당 프로그램 수정", all_prog_titles, default=valid_progs)
                            
                            if st.form_submit_button("정보 수정 저장", type="primary"):
                                if new_a_name and len(new_a_pin) == 4 and new_a_pin.isdigit():
                                    a_to_edit['name'] = new_a_name
                                    a_to_edit['pin'] = new_a_pin
                                    a_to_edit['programs'] = new_assign_progs
                                    if save_data(db):
                                        st.success("수정 완료!")
                                        time.sleep(1)
                                        st.rerun()
                                else:
                                    st.error("올바른 값을 입력하세요.")

                        st.divider()
                        st.write(f"#### 🗑️ {T_ADMIN} 계정 강제 삭제")
                        col_del1, col_del2 = st.columns([8, 2])
                        admin_to_delete = col_del1.selectbox("삭제할 계정을 선택하세요", normal_admins, label_visibility="collapsed", key="del_admin_select")
                        if col_del2.button("❌ 선택 계정 삭제", type="primary", use_container_width=True):
                            temp_admins = copy.deepcopy(db['admins'])
                            db['admins'] = [a for a in db['admins'] if a['name'] != admin_to_delete]
                            if save_data(db):
                                st.success(f"[{admin_to_delete}] 계정이 성공적으로 삭제되었습니다."); time.sleep(1); st.rerun()
                            else:
                                db['admins'] = temp_admins
                    else:
                        st.info("현재 수정하거나 삭제할 수 있는 일반 계정이 없습니다.")
