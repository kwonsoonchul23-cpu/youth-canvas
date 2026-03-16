import streamlit as st
import pandas as pd
import json
import os
import re
import calendar
import copy
import time
import urllib.request
from datetime import datetime, date
from collections import defaultdict
import requests 
import matplotlib.pyplot as plt 
import seaborn as sns 
import matplotlib.font_manager as fm

# --- [디자인 요소] 페이지 기본 설정 ---
st.set_page_config(page_title="Youth Canvas | 청소년 활동 플랫폼", page_icon="🎨", layout="wide")

# --- ✨ [핵심 수정] 시각화 폰트 설정 (Streamlit 클라우드 한글 깨짐 100% 방어) ---
@st.cache_resource
def set_korean_font():
    font_url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
    font_path = "NanumGothic.ttf"
    try:
        # 클라우드에 폰트가 없으면 구글에서 즉시 다운로드
        if not os.path.exists(font_path):
            urllib.request.urlretrieve(font_url, font_path)
        fm.fontManager.addfont(font_path)
        font_prop = fm.FontProperties(fname=font_path)
        font_name = font_prop.get_name()
        plt.rc('font', family=font_name)
        plt.rcParams['axes.unicode_minus'] = False
        sns.set_theme(style='whitegrid', font=font_name, font_scale=1.0)
    except:
        # 혹시 모를 로컬 에러 대비용
        import platform
        if platform.system() == 'Darwin': plt.rc('font', family='AppleGothic')
        elif platform.system() == 'Windows': plt.rc('font', family='Malgun Gothic')
        plt.rcParams['axes.unicode_minus'] = False

set_korean_font()

# --- [디자인 요소] 커스텀 CSS ---
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
    .schedule-table td { border: 1px solid #cbd5e1; padding: 8px; color: #1e293b; }
    .schedule-table td.task-content { text-align: left; }
    .cal-table { width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 0.85em; }
    .cal-th { background: #f8fafc; border: 1px solid #cbd5e1; padding: 10px; text-align: center; color: #334155; font-weight: bold; }
    .cal-td { border: 1px solid #cbd5e1; height: 120px; vertical-align: top; padding: 2px 0px; background: #ffffff; }
    .cal-td.empty { background: #f1f5f9; }
    .cal-day-num { font-weight: bold; color: #475569; margin-bottom: 2px; padding-right: 5px; text-align: right; }
    .cal-event { color: #ffffff; padding: 3px 5px; margin-bottom: 2px; font-size: 0.85em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }

    /* 사이드바 UI 커스텀 */
    [data-testid="stSidebar"] { background-color: #261633 !important; }
    [data-testid="stSidebarUserContent"] { padding-left: 1rem !important; padding-right: 1rem !important; padding-top: 3rem !important; }
    [data-testid="stSidebar"] [data-testid="stRadio"] > div { gap: 10px !important; margin-top: 1rem; }
    [data-testid="stSidebar"] label[data-baseweb="radio"] { width: 100%; height: 75px; margin: 0; padding: 0 20px; cursor: pointer; border-radius: 12px; display: flex; justify-content: flex-start; align-items: center; transition: all 0.2s ease; }
    [data-testid="stSidebar"] label[data-baseweb="radio"] > div:first-child div { background-color: transparent !important; border-color: rgba(255,255,255,0.6) !important; }
    [data-testid="stSidebar"] label[data-baseweb="radio"] > div:nth-child(2) { width: 100%; padding-left: 15px; }
    [data-testid="stSidebar"] label[data-baseweb="radio"] p { font-size: 1.35rem !important; font-weight: 900 !important; color: #ffffff !important; padding: 0 !important; margin: 0 !important; letter-spacing: 0.5px; }
    [data-testid="stSidebar"] label[data-baseweb="radio"]:nth-child(1) { background-color: #5c358f; }
    [data-testid="stSidebar"] label[data-baseweb="radio"]:nth-child(2) { background-color: #c13945; }
    [data-testid="stSidebar"] label[data-baseweb="radio"]:nth-child(3) { background-color: #e68128; }
    [data-testid="stSidebar"] label[data-baseweb="radio"]:hover { transform: scale(1.02); filter: brightness(1.1); }
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
            if data and isinstance(data, dict) and 'programs' in data: return data
    except Exception as e: st.error(f"🚨 연결 오류: {e}")
    return {"programs": [], "users": [], "admins": [{"name": "마스터", "pin": "0000", "role": "super", "programs": []}], "settings": {"recruit_start": "2026-01-01", "recruit_end": "2026-12-31"}}

def save_data(data):
    try:
        res = requests.put(FIREBASE_URL, json=data)
        if res.status_code == 200: return True
        else: st.error(f"🚨 저장 실패: {res.status_code}"); return False
    except Exception as e: st.error("🚨 인터넷 문제로 저장되지 않았습니다."); return False
# ==============================================================

if 'db' not in st.session_state: st.session_state['db'] = load_data()
db = st.session_state['db']

if 'menu_option' not in st.session_state: st.session_state.menu_option = "찾아보기 (탐색)"
def change_page(page_name): st.session_state.menu_option = page_name; st.rerun()

with st.sidebar:
    st.markdown("<div style='margin-bottom: 2rem; padding: 0 10px;'><div style='font-size: 3.2rem; font-weight: 900; color: #ffffff; line-height: 1.1; margin-bottom: 0.3rem; letter-spacing: -1px;'>Youth Canvas</div><div style='font-size: 1.6rem; font-weight: 800; color: #ffce31; letter-spacing: -0.5px;'>청소년의 꿈을 그리는 공간</div></div>", unsafe_allow_html=True)
    menu = st.radio("메뉴 이동", ["찾아보기 (탐색)", "나의 이야기", "관계자 외 출입금지"], index=["찾아보기 (탐색)", "나의 이야기", "관계자 외 출입금지"].index(st.session_state.menu_option), label_visibility="collapsed")
    st.write(""); st.write("")
    if st.button("🔄 서버 최신 데이터 동기화", use_container_width=True):
        st.session_state['db'] = load_data(); st.toast("✅ 동기화 완료!"); time.sleep(1); st.rerun()
st.session_state.menu_option = menu

# =========================================================
# [페이지 1] 메인 대시보드
# =========================================================
if st.session_state.menu_option == "찾아보기 (탐색)":
    st.markdown("## ✨ 지금 뜨고 있는 청소년 활동")
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
                        sub_texts = [stask['desc'] for stask in t.get('subtasks', [])]
                        if sub_texts: task_display = f"{t['task']} <br><span style='color:gray;font-size:0.85em;'>└ {', '.join(sub_texts)}</span>"
                        else: task_display = t['task']
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
                    st.session_state['selected_prog_from_main'] = prog['title']; change_page("나의 이야기")

# =========================================================
# [페이지 2] 청소년/학부모 페이지
# =========================================================
elif st.session_state.menu_option == "나의 이야기":
    st.markdown("## 🙋 나의 활동 및 성장 리포트")
    tab1, tab2 = st.tabs(["📝 신규 프로그램 지원", "🎯 종합 리포트 및 진행도 (로그인)"])
    
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
                    user_name = colA.text_input("이름 (실명 입력)")
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
                                db['users'].append({"name": user_name, "pin": user_pin, "program": selected_prog_title, "role": actual_role, "workflow": my_tasks, "messages": [], "alias": "", "attendance": {}})
                                added_count += 1
                            if save_data(db): st.success("🎉 지원 완료!"); time.sleep(1); st.rerun()
                            else:
                                for _ in range(added_count): db['users'].pop()

    with tab2:
        with st.container(border=True):
            col_id, col_pw, col_btn = st.columns([4, 4, 2])
            search_name = col_id.text_input("이름", placeholder="예: 권해리")
            search_pin = col_pw.text_input("비밀번호 (4자리)", type="password")
            login_attempt = col_btn.button("접속하기", use_container_width=True)
            
            if login_attempt or (search_name and search_pin):
                my_data = [u for u in db['users'] if u['name'] == search_name and u.get('pin', '0000') == search_pin]
                if my_data:
                    for u_idx, data in enumerate(my_data):
                        st.divider()
                        st.markdown(f"### 🏅 [{data['program']}] 참가자 **{data['name']}**님 <span style='font-size:0.6em; color:gray;'>(학부모 열람용)</span>", unsafe_allow_html=True)
                        st.markdown(f"<span class='badge-blue'>담당 역할: {data['role']}</span>", unsafe_allow_html=True)
                        st.write("")
                        
                        st.markdown("#### 📈 우리 아이 성장 리포트")
                        tasks = data['workflow']
                        task_names = [t['task'] for t in tasks]
                        task_scores = [t.get('score', 0) for t in tasks]
                        avg_score = sum(task_scores) / len(task_scores) if task_scores else 0
                        
                        total_items = 0; done_items = 0
                        for t in tasks:
                            total_items += 1; done_items += 1 if t.get('done') else 0
                            for stask in t.get('subtasks', []): total_items += 1; done_items += 1 if stask.get('done') else 0
                        pct = int((done_items/total_items)*100) if total_items > 0 else 0
                        
                        colR1, colR2 = st.columns(2)
                        colR1.metric("활동 달성률 (체크리스트)", f"{pct}%", f"{done_items} / {total_items} 완료")
                        colR2.metric("선생님 종합 성취도 평가", f"{int(avg_score)}점", "100점 만점 기준")
                        
                        if task_scores:
                            df_scores = pd.DataFrame({"성취도 점수": task_scores}, index=task_names)
                            st.line_chart(df_scores, color="#e68128", height=200)

                        st.markdown("#### 💌 선생님의 따뜻한 알림장")
                        has_comments = False
                        for t in tasks:
                            if t.get('comment'):
                                st.info(f"**[{t['task']}]** {t['comment']}")
                                has_comments = True
                        if not has_comments: st.write("아직 작성된 코멘트가 없습니다.")
                        st.write("---")

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

                        st.write("#### 💬 1:1 비밀 소통 게시판")
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
# [페이지 3] 관리자 페이지
# =========================================================
elif st.session_state.menu_option == "관계자 외 출입금지":
    if not st.session_state.get('admin_logged_in', False):
        st.markdown("## 🔒 관리자 전용 포털")
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
            
        tab_dashboard, tab_eval, tab_overview, tab_attendance, tab_manage_users, tab_create, tab_edit, tab_settings = st.tabs([
            "📈 경영 대시보드", "📝 평가/코멘트 작성", "📊 종합 명단", "✅ 출석 관리", "👥 1:1 상담", "📝 신규 개설", "⚙️ 정보 수정", "🔐 계정 관리"
        ])
        
        with tab_dashboard:
            st.subheader("📈 학원장 전용 통합 경영 대시보드")
            users_to_show = [u for u in db['users'] if u['program'] in my_programs]
            
            if not users_to_show: st.info("데이터가 부족하여 대시보드를 생성할 수 없습니다.")
            else:
                dashboard_data = []
                task_data = []
                for u in users_to_show:
                    t_scores = [t.get('score', 0) for t in u['workflow']]
                    avg_score = sum(t_scores) / len(t_scores) if t_scores else 0
                    att_counts = sum(1 for v in u.get('attendance', {}).values() if v.get('status') == '출석')
                    comment_counts = sum(1 for t in u['workflow'] if t.get('comment'))
                    
                    dashboard_data.append({
                        "Program": u['program'], "Role": u['role'], "Student": u.get('alias') or u['name'],
                        "AvgScore": avg_score, "Attendance": att_counts, "Comments": comment_counts
                    })
                    
                    for t in u['workflow']:
                        task_data.append({"Program": u['program'], "Task": t['task'], "Score": t.get('score', 0)})
                
                df_dash = pd.DataFrame(dashboard_data)
                df_tasks = pd.DataFrame(task_data)

                st.markdown("##### 🔍 프로그램별 성과 및 이상치 탐지")
                fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
                sns.barplot(data=df_dash, x='Program', y='AvgScore', ax=ax1, palette='Set2', errorbar=None)
                ax1.set_title('Average Score by Program')
                ax1.set_ylim(0, 100)
                ax1.tick_params(axis='x', rotation=45)
                
                sns.boxplot(data=df_dash, x='Program', y='AvgScore', ax=ax2, palette='pastel')
                ax2.set_title('Score Distribution & Outliers (Risk Detection)')
                ax2.set_ylim(0, 100)
                ax2.tick_params(axis='x', rotation=45)
                st.pyplot(fig1)
                st.info("💡 **원장님 인사이트:** 오른쪽 박스플롯(Boxplot) 아래쪽에 찍힌 점들은 평균 성취도에 한참 못 미치는 **'이탈 위험 학생(이상치)'**입니다. 개별 면담이 필요합니다.")

                st.markdown("##### 🔍 강사 관리 효율성 및 과업 난이도 분석")
                fig2, (ax3, ax4) = plt.subplots(1, 2, figsize=(15, 5))
                sns.scatterplot(data=df_dash, x='Comments', y='AvgScore', hue='Program', s=100, ax=ax3, palette='Set1', alpha=0.8)
                ax3.set_title('Teacher Comments vs Student Score')
                ax3.set_xlabel('Number of Comments Given')
                ax3.set_ylabel('Average Score')
                
                sns.histplot(data=df_tasks, x='Score', bins=10, kde=True, ax=ax4, color='steelblue')
                ax4.set_title('Distribution of All Task Scores (Difficulty)')
                ax4.set_xlabel('Score')
                st.pyplot(fig2)

        with tab_eval:
            st.subheader("📝 학생 종합 평가 및 코멘트 작성")
            if not my_programs: st.info("담당 프로그램이 없습니다.")
            else:
                col_sel1, col_sel2 = st.columns([5, 5])
                eval_prog = col_sel1.selectbox("📋 프로그램 선택", my_programs, key="eval_prog")
                prog_users = [(i, u) for i, u in enumerate(db['users']) if u['program'] == eval_prog]
                
                if not prog_users: st.warning("신청한 학생이 없습니다.")
                else:
                    eval_user_options = {f"{u.get('alias') or u['name']} ({u['role']})": i for i, u in prog_users}
                    selected_user_label = col_sel2.selectbox("🎓 학생 선택", list(eval_user_options.keys()))
                    target_idx = eval_user_options[selected_user_label]
                    target_user = db['users'][target_idx]
                    
                    st.write(f"#### 🏅 {target_user['name']} 학생 과업 평가")
                    with st.form(f"eval_form_{target_idx}"):
                        for t_idx, t in enumerate(target_user['workflow']):
                            st.markdown(f"**[{t['task']}]**")
                            c1, c2 = st.columns([3, 7])
                            new_score = c1.slider("성취도 점수", 0, 100, t.get('score', 0), key=f"score_{target_idx}_{t_idx}")
                            new_comment = c2.text_input("학부모 전송용 코멘트", value=t.get('comment', ''), placeholder="따뜻한 피드백을 적어주세요.", key=f"comment_{target_idx}_{t_idx}")
                            st.write("")
                            target_user['workflow'][t_idx]['score'] = new_score
                            target_user['workflow'][t_idx]['comment'] = new_comment
                            
                        if st.form_submit_button("💾 전체 평가 저장하기", type="primary", use_container_width=True):
                            if save_data(db):
                                st.success("학생 평가와 코멘트가 저장되어 학부모 리포트에 반영되었습니다!")
                                time.sleep(1)
                                st.rerun()

        with tab_overview:
            st.write("#### 📊 데이터 필터링 및 엑셀 추출")
            users_to_show = [u for u in db['users'] if u['program'] in my_programs]
            if users_to_show:
                overview_data = []
                for u in users_to_show:
                    t_scores = [t.get('score', 0) for t in u['workflow']]
                    pct = int(sum(t_scores)/len(t_scores)) if t_scores else 0
                    att_counts = sum(1 for v in u.get('attendance', {}).values() if v.get('status') == '출석')
                    overview_data.append({
                        "학생명": u.get('alias') or u['name'], "프로그램": u['program'], "역할": u['role'], 
                        "평균성취도(점)": pct, "총 출석(일)": att_counts
                    })
                df_out = pd.DataFrame(overview_data).sort_values(by=["프로그램", "학생명"])
                st.dataframe(df_out, use_container_width=True, hide_index=True)
                csv_data = df_out.to_csv(index=False, encoding='utf-8-sig')
                st.download_button("📥 결과 엑셀(CSV) 다운로드", data=csv_data, file_name="명단.csv", mime="text/csv", type="primary")
            else: st.info("데이터가 없습니다.")

        # ✨ [기능 추가 완료] 출석 탭에 3번째 '개별 기록 수정/삭제' 탭 생성
        with tab_attendance:
            st.subheader("✅ 프로그램별 출석 관리")
            if my_programs:
                att_prog = st.selectbox("📋 출석 체크 프로그램", my_programs, key="att_prog_select")
                pu = [(i, u) for i, u in enumerate(db['users']) if u['program'] == att_prog]
                
                if not pu:
                    st.warning("해당 프로그램에 신청한 학생이 없습니다.")
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
                        st.info(f"💡 선택하신 **{att_date}**의 출석을 입력합니다. 이미 기록된 내용이 있다면 아래에 표시됩니다.")
                        
                        with st.form(f"att_form"):
                            att_up = {}
                            h1, h2, h3 = st.columns([3, 3, 4])
                            h1.write("**학생명 (역할)**")
                            h2.write("**상태**")
                            h3.write("**비고**")
                            st.divider()
                            
                            for idx, u in pu:
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
                        st.markdown("#### 🔍 학생별 종합 출석부 및 시각화")
                        att_records = []
                        for i, u in pu:
                            disp_name = u.get('alias') or u['name']
                            for d_key, info in u.get('attendance', {}).items():
                                att_records.append({
                                    "학생명": f"{disp_name}({u['role']})",
                                    "날짜": d_key,
                                    "상태": info['status'],
                                    "비고": info['note']
                                })
                        
                        if att_records:
                            df_att = pd.DataFrame(att_records)
                            st.write("##### 📅 학생별 일자별 출석 상세")
                            pivot_df = df_att.pivot(index='학생명', columns='날짜', values='상태').fillna('-')
                            pivot_df = pivot_df.reindex(sorted(pivot_df.columns), axis=1) 
                            st.dataframe(pivot_df, use_container_width=True)
                            
                            st.write("##### 📊 학생별 누적 현황 시각화")
                            agg_df = df_att.groupby(['학생명', '상태']).size().unstack(fill_value=0)
                            for col in ['출석', '지각', '결석', '병결']:
                                if col not in agg_df.columns: agg_df[col] = 0
                            agg_df = agg_df[['출석', '지각', '결석', '병결']]
                            
                            fig_att, ax_att = plt.subplots(figsize=(12, 6))
                            colors = ['#2ECC71', '#FFC107', '#E74C3C', '#9B59B6']
                            agg_df.plot(kind='bar', stacked=True, ax=ax_att, color=colors, edgecolor='white')
                            ax_att.set_title('Overall Attendance Status per Student', pad=15, fontweight='bold')
                            ax_att.set_ylabel('Days Count')
                            ax_att.set_xlabel('')
                            plt.xticks(rotation=45, ha='right')
                            plt.legend(title='상태', bbox_to_anchor=(1.05, 1), loc='upper left')
                            st.pyplot(fig_att)
                            st.info("💡 **원장님 인사이트:** 빨간색(결석)이나 노란색(지각) 누적 비율이 높은 학생을 한눈에 식별하고 빠르게 학부모 면담을 진행할 수 있습니다.")
                        else:
                            st.info("아직 기록된 출석 데이터가 없습니다. [일일 출석 입력] 탭에서 먼저 출석을 기록해 주세요.")
                            
                    # ✨ 새롭게 추가된 3번째 서브탭: 개별 기록 수정/삭제 기능
                    with att_sub3:
                        st.markdown("#### ✏️ 개별 학생 출석 기록 수정 및 삭제")
                        st.info("특정 학생의 잘못 입력된 과거 출석 기록을 개별적으로 수정하거나 아예 지울 수 있습니다.")
                        
                        att_user_options = {f"{u.get('alias') or u['name']} ({u['role']})": i for i, u in pu}
                        selected_user_label = st.selectbox("🎓 수정할 학생 선택", list(att_user_options.keys()), key="att_edit_user")
                        target_idx = att_user_options[selected_user_label]
                        target_user = db['users'][target_idx]
                        
                        att_history = target_user.get('attendance', {})
                        if not att_history:
                            st.warning("이 학생은 아직 기록된 출석 데이터가 없습니다.")
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
                    t_idx = ops[st.selectbox("학생 선택", list(ops.keys()))]
                    tu = db['users'][t_idx]
                    
                    with st.container(border=True):
                        st.write("💬 1:1 대화방")
                        for msg in tu.get('messages', []):
                            with st.chat_message("assistant" if msg['sender'] == 'admin' else "user"): st.write(msg['content'])
                        with st.form(f"adm_chat_{t_idx}", clear_on_submit=True):
                            c1, c2 = st.columns([8, 2])
                            ri = c1.text_input("답장", label_visibility="collapsed")
                            if c2.form_submit_button("전송") and ri:
                                tu.setdefault('messages', []).append({"sender": "admin", "content": ri})
                                if save_data(db): st.rerun()
                    if st.button("❌ 학생 강제 퇴소(삭제)", type="primary"):
                        db['users'].pop(t_idx); save_data(db); st.rerun()

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
                npin = st.text_input("새 4자리 비밀번호", type="password", max_chars=4)
                if st.form_submit_button("변경"):
                    if len(npin) == 4 and npin.isdigit():
                        adm = next(a for a in db['admins'] if a['name'] == admin_info['name'])
                        op = adm['pin']; adm['pin'] = npin
                        if save_data(db): st.success("변경 완료. 다시 로그인하세요."); time.sleep(1); st.session_state['admin_logged_in'] = False; st.rerun()
                        else: adm['pin'] = op
                    else: st.error("4자리 숫자로 입력해주세요.")
            
            if is_super:
                with st.container(border=True):
                    st.subheader("👑 최고관리자: 선생님 계정 발급")
                    with st.form("new_admin_form"):
                        colA, colB = st.columns(2)
                        new_adm_name = colA.text_input("새 관리자 이름 (예: 김철수 선생님)")
                        new_adm_pin = colB.text_input("초기 비밀번호 4자리", max_chars=4)
                        all_prog_titles = [p['title'] for p in db['programs']]
                        assign_progs = st.multiselect("담당 프로그램 할당", all_prog_titles)
                        
                        if st.form_submit_button("관리자 계정 생성", type="primary"):
                            if not new_adm_name or len(new_adm_pin) != 4 or not new_adm_pin.isdigit():
                                st.error("이름과 4자리 숫자 비밀번호를 정확히 입력하세요.")
                            else:
                                db['admins'].append({"name": new_adm_name, "pin": new_adm_pin, "role": "normal", "programs": assign_progs})
                                if save_data(db):
                                    st.success(f"[{new_adm_name}] 선생님 계정이 생성되었습니다!"); time.sleep(1); st.rerun()
                                else:
                                    db['admins'].pop()
                    
                    st.write("#### 📋 등록된 선생님(관리자) 목록")
                    df_admins = pd.DataFrame([{"이름": a['name'], "권한": "최고관리자" if a['role'] == "super" else "담당 지도사", "담당 프로그램": ", ".join(a.get('programs', [])) if a.get('programs') else "없음/전체"} for a in db['admins']])
                    st.dataframe(df_admins, hide_index=True, use_container_width=True)
                    
                    st.divider()
                    st.write("#### 🗑️ 선생님 계정 강제 삭제")
                    normal_admins = [a['name'] for a in db['admins'] if a['role'] != 'super']
                    if normal_admins:
                        col_del1, col_del2 = st.columns([8, 2])
                        admin_to_delete = col_del1.selectbox("삭제할 계정을 선택하세요", normal_admins, label_visibility="collapsed")
                        if col_del2.button("❌ 계정 삭제", type="primary", use_container_width=True):
                            temp_admins = copy.deepcopy(db['admins'])
                            db['admins'] = [a for a in db['admins'] if a['name'] != admin_to_delete]
                            if save_data(db):
                                st.success(f"[{admin_to_delete}] 계정이 성공적으로 삭제되었습니다."); time.sleep(1); st.rerun()
                            else:
                                db['admins'] = temp_admins
                    else:
                        st.info("현재 삭제할 수 있는 일반 선생님(지도사) 계정이 없습니다.")
