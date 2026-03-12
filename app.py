import streamlit as st
import pandas as pd
import json
import os
import re
import calendar
import copy
from datetime import datetime, date
from collections import defaultdict
import requests # ✨ Firebase 통신을 위해 필수!

# --- [디자인 요소] 페이지 기본 설정 ---
st.set_page_config(page_title="Youth Canvas | 청소년 활동 플랫폼", page_icon="🎨", layout="wide")

# --- [디자인 요소] 커스텀 CSS ---
st.markdown("""
    <style>
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
    </style>
""", unsafe_allow_html=True)

# --- 유틸리티 함수 ---
def fix_youtube_url(url):
    if not url: return None
    url = url.replace("shorts/", "watch?v=")
    if "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0]
        return f"https://www.youtube.com/watch?v={video_id}"
    if "m.youtube.com" in url:
        return url.replace("m.youtube.com", "www.youtube.com")
    return url

def get_date_range(task_dict):
    if 'start_date' in task_dict and 'end_date' in task_dict:
        return task_dict['start_date'], task_dict['end_date']
    elif 'date' in task_dict:
        d = task_dict['date']
        if '~' in d:
            parts = d.split('~')
            return parts[0].strip(), parts[1].strip()
        return d.strip(), d.strip()
    return "", ""

def get_date_label(task_dict):
    sd, ed = get_date_range(task_dict)
    if sd and ed and sd != ed: return f"[{sd} ~ {ed}] "
    elif sd and sd != "-": return f"[{sd}] "
    return ""

# ==============================================================
# ✨ [데이터베이스 연결 로직 (Firebase 연동)] ✨
# ==============================================================
today_str = datetime.now().strftime("%Y-%m-%d")

# 🚨🚨🚨 [매우 중요] 아래 따옴표 안의 주소를 발급받으신 Firebase 주소로 반드시 변경하세요! 🚨🚨🚨
# (주의: 주소 맨 끝에 반드시 '/data.json' 이라고 적혀 있어야 합니다)
FIREBASE_URL = "https://youth-canvas-default-rtdb.firebaseio.com/data.json"

def load_data():
    try:
        response = requests.get(FIREBASE_URL)
        if response.status_code == 200 and response.json() is not None:
            return response.json()
    except Exception as e:
        st.error(f"데이터베이스 연결 오류: {e}")

    # Firebase에 데이터가 없을 때 뼈대를 만들어 줍니다.
    return {
        "programs": [], "users": [], 
        "admins": [{"name": "마스터", "pin": "0000", "role": "super", "programs": []}],
        "settings": {"recruit_start": "2026-01-01", "recruit_end": "2026-12-31"}
    }

def save_data(data):
    try:
        requests.put(FIREBASE_URL, json=data)
    except Exception as e:
        st.error("데이터 저장에 실패했습니다. 인터넷 연결을 확인해주세요.")
# ==============================================================

if 'db' not in st.session_state: st.session_state['db'] = load_data()
db = st.session_state['db']

# --- 사이드바 및 페이지 이동 ---
if 'menu_option' not in st.session_state: st.session_state.menu_option = "1. 🏠 둘러보기 (메인)"
def change_page(page_name):
    st.session_state.menu_option = page_name
    st.rerun()

with st.sidebar:
    st.markdown("### 🎨 Youth Canvas")
    st.caption("청소년의 꿈을 그리는 공간")
    menu = st.radio(
        "메뉴 이동", 
        ["1. 🏠 둘러보기 (메인)", "2. 🙋 나의 활동 (청소년)", "3. 🛠️ 시설 관리자"],
        index=["1. 🏠 둘러보기 (메인)", "2. 🙋 나의 활동 (청소년)", "3. 🛠️ 시설 관리자"].index(st.session_state.menu_option),
        label_visibility="collapsed"
    )
st.session_state.menu_option = menu

# =========================================================
# [페이지 1] 메인 대시보드
# =========================================================
if st.session_state.menu_option == "1. 🏠 둘러보기 (메인)":
    st.markdown("## ✨ 지금 뜨고 있는 청소년 활동")
    st.write("") 
    
    if not db['programs']: st.info("아직 개설된 프로그램이 없습니다. 관리자 페이지에서 프로그램을 만들어주세요.")
        
    col1, col2 = st.columns(2)
    for idx, prog in enumerate(db['programs']):
        with (col1 if idx % 2 == 0 else col2):
            with st.container(border=True):
                p_r_start = prog.get('recruit_start', today_str)
                p_r_end = prog.get('recruit_end', '2099-12-31')
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
                
                tags_html = ""
                for r, _ in roles_list: tags_html += f"<span class='badge-blue'>#{r}</span> "
                if tags_html: st.markdown(f"<div style='margin-bottom: 15px;'>{tags_html}</div>", unsafe_allow_html=True)
                
                grouped_tasks = defaultdict(list)
                for role, tasks in prog.get('roles_workflow', {}).items():
                    for t in tasks:
                        label = get_date_label(t)
                        date_val = label if label else "일정 미정"
                        
                        sub_texts = [stask['desc'] for stask in t.get('subtasks', [])]
                        if sub_texts:
                            task_display = f"{t['task']} <br><span style='color:gray;font-size:0.85em;'>└ {', '.join(sub_texts)}</span>"
                        else:
                            task_display = t['task']
                            
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
                                if i < len(tasks_on_date):
                                    html_table += f"<td>{tasks_on_date[i]['role']}</td><td class='task-content'>{tasks_on_date[i]['task']}</td>"
                                else: html_table += "<td></td><td></td>"
                            html_table += "</tr>"
                        html_table += "</table>"
                        st.markdown(html_table, unsafe_allow_html=True)
                
                st.write(f"**현재 참여 인원** ({total_curr}/{total_cap}명)")
                st.progress(total_curr/total_cap if total_cap > 0 else 0)
                
                can_apply = is_recruiting_period and not is_all_full
                if st.button("🚀 이 프로그램 지원하기", key=f"apply_{idx}", use_container_width=True, type="primary", disabled=not can_apply):
                    st.session_state['selected_prog_from_main'] = prog['title']
                    change_page("2. 🙋 나의 활동 (청소년)")

# =========================================================
# [페이지 2] 청소년 페이지
# =========================================================
elif st.session_state.menu_option == "2. 🙋 나의 활동 (청소년)":
    st.markdown("## 🙋 나의 활동 보드")
    tab1, tab2 = st.tabs(["📝 신규 프로그램 지원", "🎯 나의 목표 및 진행도 (로그인)"])
    
    with tab1:
        prog_titles = [p['title'] for p in db['programs']]
        if not prog_titles: st.warning("개설된 프로그램이 없습니다.")
        else:
            active_programs = []
            for p in db['programs']:
                p_r_start = p.get('recruit_start', today_str)
                p_r_end = p.get('recruit_end', '2099-12-31')
                if p_r_start <= today_str <= p_r_end: active_programs.append(p['title'])
            
            if not active_programs: st.error("⏳ 현재 모집 중인 프로그램이 없습니다.")
            else:
                default_idx = 0
                if 'selected_prog_from_main' in st.session_state and st.session_state['selected_prog_from_main'] in active_programs:
                    default_idx = active_programs.index(st.session_state['selected_prog_from_main'])

                with st.container(border=True):
                    st.subheader("1단계: 참가자 정보 입력")
                    colA, colB = st.columns(2)
                    user_name = colA.text_input("이름 (실명 입력)")
                    user_pin = colB.text_input("나만의 접속 비밀번호 (숫자 4자리)", type="password", max_chars=4)
                    
                    st.subheader("2단계: 활동 선택")
                    selected_prog_title = st.selectbox("참여할 프로그램", active_programs, index=default_idx)
                    selected_prog_data = next(p for p in db['programs'] if p['title'] == selected_prog_title)
                    
                    role_options = []
                    for r, cap in selected_prog_data.get('roles_capacity', {}).items():
                        curr = sum(1 for u in db['users'] if u['program'] == selected_prog_title and u['role'] == r)
                        role_options.append(f"{r} ({curr}/{cap}명) - {'지원가능' if curr < cap else '마감'}")
                    
                    selected_role_str = st.selectbox("희망 역할", role_options)
                    
                    st.write("")
                    if st.button("✨ 최종 지원하기", use_container_width=True, type="primary"):
                        if not user_name or not user_pin: st.error("이름과 비밀번호를 모두 입력하세요.")
                        elif "마감" in selected_role_str: st.error("정원이 마감되었습니다.")
                        else:
                            actual_role = selected_role_str.split(" (")[0]
                            my_tasks = copy.deepcopy(selected_prog_data['roles_workflow'][actual_role])
                            db['users'].append({"name": user_name, "pin": user_pin, "program": selected_prog_title, "role": actual_role, "workflow": my_tasks, "messages": [], "alias": "", "attendance": {}})
                            save_data(db); st.success("🎉 성공적으로 지원되었습니다! 우측 탭에서 로그인해 확인하세요."); st.rerun()

    with tab2:
        with st.container(border=True):
            col_id, col_pw, col_btn = st.columns([4, 4, 2])
            search_name = col_id.text_input("이름", placeholder="예: 권해리")
            search_pin = col_pw.text_input("비밀번호 (4자리)", type="password")
            
            col_btn.write(""); col_btn.write("")
            login_attempt = col_btn.button("접속하기", use_container_width=True)
            
            if login_attempt or (search_name and search_pin):
                my_data = [u for u in db['users'] if u['name'] == search_name and u.get('pin', '0000') == search_pin]
                if my_data:
                    for data in my_data:
                        st.divider()
                        st.markdown(f"### 🏅 [{data['program']}] 참가자 **{data['name']}**님")
                        st.markdown(f"<span class='badge-blue'>나의 담당 역할: {data['role']}</span>", unsafe_allow_html=True)
                        st.write("")
                        
                        total_items = 0; done_items = 0
                        for t in data['workflow']:
                            total_items += 1
                            if t.get('done'): done_items += 1
                            for stask in t.get('subtasks', []):
                                total_items += 1
                                if stask.get('done'): done_items += 1
                        
                        pct = int((done_items/total_items)*100) if total_items > 0 else 0
                        
                        st.metric("전체 활동 성취율", f"{pct}%", f"{done_items} / {total_items} 개 달성")
                        st.progress(pct / 100)
                        
                        if pct <= 60:
                            st.warning("⚠️ **현재 활동 성취율이 60% 이하입니다.** 어려운 점이 있다면 아래 게시판을 통해 선생님과 소통해 보세요!")
                        else:
                            st.success("🎉 순조롭게 잘 진행되고 있어요! 이대로 끝까지 화이팅!")
                        
                        if data.get('attendance'):
                            st.write("#### 📅 나의 최근 출석 기록")
                            att_df = pd.DataFrame([{"날짜": k, "상태": v['status'], "비고": v['note']} for k, v in data['attendance'].items()]).sort_values("날짜", ascending=False)
                            st.dataframe(att_df, use_container_width=True, hide_index=True)
                        
                        st.write("#### ✅ 세부 활동 체크리스트")
                        with st.container(border=True):
                            changed = False
                            for idx, t in enumerate(data['workflow']):
                                label = f"{get_date_label(t)}{t['task']}"
                                is_done = st.checkbox(f"**{label}**", value=t.get('done'), key=f"chk_{search_name}_{data['program']}_{idx}")
                                if is_done != t.get('done'):
                                    t['done'] = is_done; changed = True
                                
                                for s_idx, stask in enumerate(t.get('subtasks', [])):
                                    col_empty, col_chk = st.columns([1, 20])
                                    with col_chk:
                                        sub_done = st.checkbox(f"↳ {stask['desc']}", value=stask.get('done'), key=f"chk_sub_{search_name}_{data['program']}_{idx}_{s_idx}")
                                        if sub_done != stask.get('done'):
                                            stask['done'] = sub_done; changed = True
                                            
                            if changed: save_data(db); st.rerun()
                        
                        st.write("#### 💬 관리자 1:1 소통 게시판")
                        chat_box = st.container(border=True, height=250)
                        with chat_box:
                            if not data.get('messages'): st.info("아직 나눈 대화가 없습니다.")
                            for msg in data.get('messages', []):
                                with st.chat_message("user" if msg['sender'] == 'user' else "assistant"):
                                    st.write(msg['content'])
                        with st.form(f"chat_form_{data['program']}", clear_on_submit=True):
                            c1, c2 = st.columns([8, 2])
                            msg_input = c1.text_input("메시지 입력", label_visibility="collapsed")
                            if c2.form_submit_button("전송") and msg_input:
                                data.setdefault('messages', []).append({"sender": "user", "content": msg_input})
                                save_data(db); st.rerun()
                elif login_attempt: st.error("정보가 일치하지 않습니다.")

# =========================================================
# [페이지 3] 관리자 페이지
# =========================================================
elif st.session_state.menu_option == "3. 🛠️ 시설 관리자":
    if not st.session_state.get('admin_logged_in', False):
        st.markdown("## 🔒 관리자 전용 포털")
        with st.container(border=True):
            st.info("💡 초기 시스템 세팅: 이름 [ 마스터 ], 비밀번호 [ 0000 ]")
            with st.form("admin_login_form"):
                login_name = st.text_input("관리자 이름")
                login_pin = st.text_input("비밀번호 4자리", type="password", max_chars=4)
                if st.form_submit_button("로그인", type="primary"):
                    matched_admin = next((a for a in db.get('admins', []) if a['name'] == login_name and a['pin'] == login_pin), None)
                    if matched_admin:
                        st.session_state['admin_logged_in'] = True
                        st.session_state['logged_admin'] = matched_admin
                        st.rerun()
                    else: st.error("인증 실패: 정보가 틀렸습니다.")
    
    else:
        admin_info = st.session_state['logged_admin']
        is_super = (admin_info['role'] == 'super')
        my_programs = [p['title'] for p in db['programs']] if is_super else admin_info.get('programs', [])

        col_title, col_logout = st.columns([8, 2])
        col_title.markdown(f"## 🛠️ 시설 통합 관리 시스템 <span style='font-size:0.5em; color:gray;'>[{admin_info['name']} 접속중]</span>", unsafe_allow_html=True)
        if col_logout.button("🔓 로그아웃", use_container_width=True):
            st.session_state['admin_logged_in'] = False; st.rerun()
            
        tab_overview, tab_calendar, tab_attendance, tab_manage_users, tab_create, tab_edit, tab_settings = st.tabs([
            "📊 종합 현황", "📅 통합 캘린더", "✅ 출석 관리", "👥 소통/명단관리", "📝 신규 프로그램", "⚙️ 정보 수정", "🔐 계정/설정"
        ])
        
        with tab_overview:
            users_to_show = [u for u in db['users'] if u['program'] in my_programs]
            if users_to_show:
                st.write("#### 📊 데이터 필터링 및 엑셀 추출")
                with st.container(border=True):
                    col_f1, col_f2, col_f3 = st.columns(3)
                    admin_list = ["전체"] + [a['name'] for a in db['admins'] if a['role'] != 'super']
                    sel_admin = col_f1.selectbox("👤 관리자 담당별", admin_list)
                    
                    allowed_progs_by_admin = my_programs
                    if sel_admin != "전체":
                        target_admin = next((a for a in db['admins'] if a['name'] == sel_admin), None)
                        if target_admin: allowed_progs_by_admin = [p for p in my_programs if p in target_admin.get('programs', [])]
                    
                    prog_list = ["전체"] + list(set([u['program'] for u in users_to_show if u['program'] in allowed_progs_by_admin]))
                    sel_prog = col_f2.selectbox("📋 프로그램별", prog_list)
                    
                    student_list = ["전체"] + list(set([u.get('alias') if u.get('alias') else u['name'] for u in users_to_show]))
                    sel_student = col_f3.selectbox("🎓 학생 이름별", student_list)

                filtered_users = []
                for u in users_to_show:
                    disp_name = u.get('alias') if u.get('alias') else u['name']
                    if u['program'] not in allowed_progs_by_admin: continue
                    if sel_prog != "전체" and u['program'] != sel_prog: continue
                    if sel_student != "전체" and disp_name != sel_student: continue
                    filtered_users.append(u)
                
                if filtered_users:
                    overview_data = []
                    for u in filtered_users:
                        tot_i = 0; don_i = 0
                        for t in u['workflow']:
                            tot_i += 1
                            if t.get('done'): don_i += 1
                            for stask in t.get('subtasks', []):
                                tot_i += 1
                                if stask.get('done'): don_i += 1
                        pct = int((don_i/tot_i)*100) if tot_i > 0 else 0
                        
                        att = u.get('attendance', {})
                        att_counts = {"출석": 0, "지각": 0, "결석": 0, "병결": 0}
                        for date_key, info in att.items():
                            status = info.get('status')
                            if status in att_counts: att_counts[status] += 1
                                
                        managing_admins = [a['name'] for a in db['admins'] if a['role'] != 'super' and u['program'] in a.get('programs', [])]
                        admin_names_str = ", ".join(managing_admins) if managing_admins else "마스터"

                        overview_data.append({
                            "학생명": u.get('alias') if u.get('alias') else u['name'], 
                            "담당 관리자": admin_names_str, "프로그램": u['program'], "역할": u['role'], 
                            "성취율(%)": pct, "출석": att_counts["출석"], "지각": att_counts["지각"], "결석": att_counts["결석"], "병결": att_counts["병결"]
                        })
                    
                    df_out = pd.DataFrame(overview_data).sort_values(by=["프로그램", "학생명"])
                    st.dataframe(df_out, use_container_width=True, hide_index=True)
                    st.write("")
                    csv_data = df_out.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button("📥 필터링된 결과 엑셀(CSV) 파일로 다운로드", data=csv_data, file_name=f"YouthCanvas_종합현황_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", type="primary")
                else: st.warning("선택하신 조건에 맞는 데이터가 없습니다.")
            else: st.info("담당 프로그램에 참여 중인 청소년이 없습니다.")

        with tab_calendar:
            st.subheader("📅 관리자 통합 캘린더")
            event_blocks = []
            for p in db['programs']:
                if p['title'] in my_programs:
                    prog_color = p.get('color', '#4f46e5')
                    for role, tasks in p.get('roles_workflow', {}).items():
                        for t in tasks:
                            sd, ed = get_date_range(t)
                            if sd and ed and re.match(r'\d{4}-\d{2}-\d{2}', sd) and re.match(r'\d{4}-\d{2}-\d{2}', ed):
                                event_blocks.append({"start": sd, "end": ed, "color": prog_color, "title": f"<b>[{p['title'][:5]}]</b> {t['task']}"})
            event_blocks.sort(key=lambda x: (x['start'], x['end']))
            if not event_blocks: st.warning("스케줄이 등록된 프로그램이 없습니다.")
            else:
                all_starts = [b['start'] for b in event_blocks]
                all_starts.sort()
                default_year = int(all_starts[0].split('-')[0])
                default_month = int(all_starts[0].split('-')[1])
                col_y, col_m, _ = st.columns([2, 2, 6])
                selected_year = col_y.selectbox("연도 선택", range(2025, 2031), index=range(2025, 2031).index(default_year))
                selected_month = col_m.selectbox("월 선택", range(1, 13), index=default_month-1)
                cal = calendar.monthcalendar(selected_year, selected_month)
                days_ko = ["월", "화", "수", "목", "금", "토", "일"]
                html_cal = "<table class='cal-table'><tr>"
                for day in days_ko: html_cal += f"<th class='cal-th'>{day}</th>"
                html_cal += "</tr>"
                for week in cal:
                    html_cal += "<tr>"
                    for day_idx, day_num in enumerate(week):
                        if day_num == 0: html_cal += "<td class='cal-td empty'></td>"
                        else:
                            curr_date = f"{selected_year}-{selected_month:02d}-{day_num:02d}"
                            color_text = "#475569"
                            if day_idx == 5: color_text = "#2563eb"
                            elif day_idx == 6: color_text = "#dc2626"
                            html_cal += f"<td class='cal-td'><div class='cal-day-num' style='color:{color_text};'>{day_num}</div>"
                            for eb in event_blocks:
                                if eb['start'] <= curr_date <= eb['end']:
                                    is_start = (curr_date == eb['start']); is_end = (curr_date == eb['end'])
                                    is_week_start = (day_idx == 0); is_week_end = (day_idx == 6)
                                    m_left = "4px" if is_start or is_week_start else "0px"
                                    m_right = "4px" if is_end or is_week_end else "0px"
                                    r_left = "4px" if is_start or is_week_start else "0px"
                                    r_right = "4px" if is_end or is_week_end else "0px"
                                    show_text = is_start or is_week_start
                                    display_text = eb['title'] if show_text else "&nbsp;"
                                    style = f"background-color:{eb['color']}; margin-left:{m_left}; margin-right:{m_right}; border-radius:{r_left} {r_right} {r_right} {r_left};"
                                    html_cal += f"<div class='cal-event' style='{style}'>{display_text}</div>"
                            html_cal += "</td>"
                    html_cal += "</tr>"
                html_cal += "</table>"
                st.markdown(html_cal, unsafe_allow_html=True)

        with tab_attendance:
            st.subheader("✅ 프로그램별 출석 관리")
            if not my_programs: st.info("담당 중인 프로그램이 없습니다.")
            else:
                col_sel1, col_sel2 = st.columns([6, 4])
                att_prog = col_sel1.selectbox("📋 출석을 체크할 프로그램", my_programs, key="att_prog")
                att_date = col_sel2.date_input("🗓️ 날짜 선택", value=datetime.now(), key="att_date")
                att_date_str = att_date.strftime("%Y-%m-%d")

                prog_users_att = [(i, u) for i, u in enumerate(db['users']) if u['program'] == att_prog]
                if not prog_users_att: st.warning("해당 프로그램에 신청한 학생이 없습니다.")
                else:
                    with st.container(border=True):
                        st.write(f"#### 📅 {att_date_str} 출석부")
                        with st.form(f"attendance_form_{att_prog}_{att_date_str}"):
                            h1, h2, h3 = st.columns([3, 3, 4])
                            h1.markdown("**학생명 (역할)**")
                            h2.markdown("**출결 상태**")
                            h3.markdown("**비고 (사유 등)**")
                            st.divider()

                            att_updates = {}
                            for idx, u in prog_users_att:
                                disp_name = u.get('alias') if u.get('alias') else u['name']
                                current_att = u.get('attendance', {}).get(att_date_str, {})
                                curr_status = current_att.get('status', '출석')
                                curr_note = current_att.get('note', '')

                                c1, c2, c3 = st.columns([3, 3, 4])
                                c1.write(f"**{disp_name}**\n<br><span style='color:gray; font-size:0.8em;'>{u['role']}</span>", unsafe_allow_html=True)
                                new_status = c2.selectbox("상태", ["출석", "지각", "결석", "병결"], index=["출석", "지각", "결석", "병결"].index(curr_status), key=f"att_status_{idx}", label_visibility="collapsed")
                                new_note = c3.text_input("비고", value=curr_note, key=f"att_note_{idx}", label_visibility="collapsed", placeholder="상세 사유 입력")
                                att_updates[idx] = {"status": new_status, "note": new_note}

                            st.write("")
                            if st.form_submit_button("💾 출석 데이터 저장하기", type="primary", use_container_width=True):
                                for idx, att_data in att_updates.items():
                                    if 'attendance' not in db['users'][idx]: db['users'][idx]['attendance'] = {}
                                    db['users'][idx]['attendance'][att_date_str] = att_data
                                save_data(db); st.success(f"{att_date_str} 출석 정보가 성공적으로 저장되었습니다!"); st.rerun()

        with tab_manage_users:
            if not my_programs: st.info("담당 중인 프로그램이 없습니다.")
            else:
                selected_prog_manage = st.selectbox("📋 조회할 프로그램 선택", my_programs)
                prog_users_with_idx = [(i, u) for i, u in enumerate(db['users']) if u['program'] == selected_prog_manage]
                
                if prog_users_with_idx:
                    df_prog_users = pd.DataFrame([{
                        "이름": u.get('alias') if u.get('alias') else u['name'], "역할": u['role']
                    } for _, u in prog_users_with_idx])
                    st.dataframe(df_prog_users, use_container_width=True, hide_index=True)
                    
                    st.divider()
                    idx_mapping = {}
                    display_list = []
                    for global_i, u in prog_users_with_idx:
                        disp_name = u.get('alias') if u.get('alias') else u['name']
                        display_str = f"[번호:{global_i}] {disp_name} - {u['role']}"
                        display_list.append(display_str)
                        idx_mapping[display_str] = global_i

                    selected_display = st.selectbox("🔍 상세 관리할 청소년 선택", display_list)
                    
                    if selected_display:
                        target_idx = idx_mapping[selected_display]
                        target_user = db['users'][target_idx]
                        
                        with st.container(border=True):
                            st.write("✏️ **학생 이름 변경 (동명이인 구분용)**")
                            c1, c2 = st.columns([8, 2])
                            current_disp = target_user.get('alias') if target_user.get('alias') else target_user['name']
                            new_alias = c1.text_input("변경할 이름 입력", value=current_disp, label_visibility="collapsed")
                            if c2.button("이름 저장", type="primary", use_container_width=True):
                                db['users'][target_idx]['alias'] = new_alias
                                save_data(db); st.success("관리자 목록의 표시 이름이 변경되었습니다!"); st.rerun()
                                
                        st.write("") 
                        col_info, col_chat = st.columns([1, 1])
                        with col_info:
                            with st.container(border=True):
                                tot_i = 0; don_i = 0
                                for t in target_user['workflow']:
                                    tot_i += 1
                                    if t.get('done'): don_i += 1
                                    for stask in t.get('subtasks', []):
                                        tot_i += 1
                                        if stask.get('done'): don_i += 1
                                pct = int((don_i/tot_i)*100) if tot_i > 0 else 0
                                
                                st.write(f"**[{target_user['name']}] 학생 성취도 ({pct}%)**")
                                if pct <= 60: st.error("🚨 학생의 성취율이 60% 이하입니다. 1:1 상담을 권장합니다.")
                                
                                changed_admin = False
                                for t_idx, t in enumerate(target_user['workflow']):
                                    label = f"{get_date_label(t)}{t['task']}"
                                    is_done = st.checkbox(f"**{label}**", value=t.get('done'), key=f"admin_chk_m_{target_idx}_{t_idx}")
                                    if is_done != t.get('done'):
                                        target_user['workflow'][t_idx]['done'] = is_done; changed_admin = True
                                        
                                    for s_idx, stask in enumerate(t.get('subtasks', [])):
                                        ce, cc = st.columns([1, 20])
                                        with cc:
                                            sub_done = st.checkbox(f"↳ {stask['desc']}", value=stask.get('done'), key=f"admin_chk_s_{target_idx}_{t_idx}_{s_idx}")
                                            if sub_done != stask.get('done'):
                                                stask['done'] = sub_done; changed_admin = True
                                                
                                if changed_admin: save_data(db); st.success("진도 저장됨"); st.rerun()
                                
                                st.write("")
                                if st.button("❌ 이 학생의 신청 취소 (데이터 삭제)", use_container_width=True):
                                    db['users'].pop(target_idx); save_data(db); st.rerun()

                        with col_chat:
                            with st.container(border=True):
                                st.write(f"**💬 1:1 대화방**")
                                admin_chat_box = st.container(height=350)
                                with admin_chat_box:
                                    for msg in target_user.get('messages', []):
                                        with st.chat_message("assistant" if msg['sender'] == 'admin' else "user"):
                                            st.write(msg['content'])
                                with st.form(f"admin_chat_form_{target_idx}", clear_on_submit=True):
                                    c1, c2 = st.columns([7, 3])
                                    reply_input = c1.text_input("답장", label_visibility="collapsed")
                                    if c2.form_submit_button("전송") and reply_input:
                                        target_user.setdefault('messages', []).append({"sender": "admin", "content": reply_input})
                                        save_data(db); st.rerun()

        with tab_create:
            with st.container(border=True):
                with st.form("create_form"):
                    colA, colB = st.columns([8, 2])
                    t = colA.text_input("프로그램 명")
                    prog_color = colB.color_picker("캘린더 색상", "#4f46e5")
                    
                    st.write("🗓️ **모집 기간 설정**")
                    colD1, colD2 = st.columns(2)
                    r_start = colD1.date_input("모집 시작일")
                    r_end = colD2.date_input("모집 종료일")
                    
                    d = st.text_area("프로그램 소개글 (카드에 표시됨)")
                    v = st.text_input("유튜브 링크")
                    st.info("📌 작성 양식 (기간은 물결 ~, 세부 목표는 대시 - 사용)\n[역할명 : 정원]\nYYYY-MM-DD ~ YYYY-MM-DD : 메인 과업\n- 프리미어프로 기초 익히기 (세부 목표 1)\n- 단축키 외우기 (세부 목표 2)")
                    w_input = st.text_area("역할 및 워크플로우 설정", height=250)
                    
                    if st.form_submit_button("프로그램 개설하기", type="primary"):
                        parsed_w = {}; parsed_c = {}; curr_r = None
                        for line in w_input.split('\n'):
                            line = line.strip()
                            if not line: continue
                            if line.startswith('[') and ']' in line:
                                content = line[1:line.find(']')]
                                curr_r = content.split(':')[0].strip()
                                parsed_c[curr_r] = int(re.sub(r'[^0-9]', '', content.split(':')[1])) if ':' in content else 10
                                parsed_w[curr_r] = []
                            elif curr_r and ':' in line and not line.startswith('-') and not line.startswith('*'):
                                dt_part, tk = line.split(':', 1)
                                dt_part = dt_part.strip()
                                if '~' in dt_part:
                                    sd, ed = dt_part.split('~', 1)
                                    parsed_w[curr_r].append({"start_date": sd.strip(), "end_date": ed.strip(), "task": tk.strip(), "subtasks": [], "done": False})
                                else:
                                    parsed_w[curr_r].append({"start_date": dt_part, "end_date": dt_part, "task": tk.strip(), "subtasks": [], "done": False})
                            elif curr_r and (line.startswith('-') or line.startswith('*')):
                                sub_desc = line[1:].strip()
                                if parsed_w[curr_r]: 
                                    parsed_w[curr_r][-1]["subtasks"].append({"desc": sub_desc, "done": False})
                                    
                        db['programs'].append({
                            "title": t, "desc": d, "video": v, "color": prog_color, 
                            "recruit_start": r_start.strftime("%Y-%m-%d"),
                            "recruit_end": r_end.strftime("%Y-%m-%d"),
                            "roles_capacity": parsed_c, "roles_workflow": parsed_w
                        })
                        if not is_super:
                            admin_in_db = next(a for a in db['admins'] if a['name'] == admin_info['name'])
                            admin_in_db.setdefault('programs', []).append(t)
                            st.session_state['logged_admin']['programs'].append(t)
                        save_data(db); st.success("개설 완료!"); st.rerun()

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
                            parsed_w = {}; parsed_c = {}; curr_r = None
                            for line in new_w.split('\n'):
                                line = line.strip()
                                if not line: continue
                                if line.startswith('[') and ']' in line:
                                    content = line[1:line.find(']')]
                                    curr_r = content.split(':')[0].strip()
                                    parsed_c[curr_r] = int(re.sub(r'[^0-9]', '', content.split(':')[1])) if ':' in content else 10
                                    parsed_w[curr_r] = []
                                elif curr_r and ':' in line and not line.startswith('-') and not line.startswith('*'):
                                    dt_part, tk = line.split(':', 1)
                                    dt_part = dt_part.strip()
                                    if '~' in dt_part:
                                        sd, ed = dt_part.split('~', 1)
                                        parsed_w[curr_r].append({"start_date": sd.strip(), "end_date": ed.strip(), "task": tk.strip(), "subtasks": [], "done": False})
                                    else:
                                        parsed_w[curr_r].append({"start_date": dt_part, "end_date": dt_part, "task": tk.strip(), "subtasks": [], "done": False})
                                elif curr_r and (line.startswith('-') or line.startswith('*')):
                                    sub_desc = line[1:].strip()
                                    if parsed_w[curr_r]: 
                                        if "subtasks" not in parsed_w[curr_r][-1]:
                                            parsed_w[curr_r][-1]["subtasks"] = []
                                        parsed_w[curr_r][-1]["subtasks"].append({"desc": sub_desc, "done": False})
                            
                            old_title = p_data['title']
                            
                            if new_t != old_title:
                                for a in db['admins']:
                                    if old_title in a.get('programs', []):
                                        a['programs'] = [new_t if x == old_title else x for x in a['programs']]
                                        
                            for u in db['users']:
                                if u['program'] == old_title:
                                    u['program'] = new_t 
                                    if u['role'] in parsed_w:
                                        new_user_workflow = copy.deepcopy(parsed_w[u['role']])
                                        for new_t_dict in new_user_workflow:
                                            for old_t_dict in u['workflow']:
                                                if new_t_dict['task'] == old_t_dict['task']:
                                                    new_t_dict['done'] = old_t_dict.get('done', False)
                                                    for new_st_dict in new_t_dict.get('subtasks', []):
                                                        for old_st_dict in old_t_dict.get('subtasks', []):
                                                            if new_st_dict['desc'] == old_st_dict['desc']:
                                                                new_st_dict['done'] = old_st_dict.get('done', False)
                                        u['workflow'] = new_user_workflow
                            
                            db['programs'][p_idx] = {
                                "title": new_t, "desc": new_d, "video": new_v, "color": new_color, 
                                "recruit_start": new_r_start.strftime("%Y-%m-%d"),
                                "recruit_end": new_r_end.strftime("%Y-%m-%d"),
                                "roles_capacity": parsed_c, "roles_workflow": parsed_w
                            }
                            save_data(db); st.success("수정 완료 및 학생 데이터 동기화 성공! 보안을 위해 다시 로그인해주세요."); st.session_state['admin_logged_in'] = False; st.rerun()

        with tab_settings:
            with st.container(border=True):
                st.subheader("🔑 내 비밀번호 변경")
                with st.form("change_pin_form"):
                    new_pin = st.text_input("새로운 4자리 비밀번호", type="password", max_chars=4)
                    if st.form_submit_button("변경하기"):
                        if len(new_pin) == 4 and new_pin.isdigit():
                            admin_in_db = next(a for a in db['admins'] if a['name'] == admin_info['name'])
                            admin_in_db['pin'] = new_pin
                            save_data(db)
                            st.success("변경 성공! 다시 로그인해주세요."); st.session_state['admin_logged_in'] = False; st.rerun()
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
                                save_data(db); st.success(f"[{new_adm_name}] 선생님 계정이 생성되었습니다!"); st.rerun()
                    
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
                            db['admins'] = [a for a in db['admins'] if a['name'] != admin_to_delete]
                            save_data(db)
                            st.success(f"[{admin_to_delete}] 계정이 성공적으로 삭제되었습니다.")
                            st.rerun()
                    else:
                        st.info("현재 삭제할 수 있는 일반 선생님(지도사) 계정이 없습니다.")

