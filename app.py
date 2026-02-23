import streamlit as st
import streamlit_antd_components as sac

# 1. 페이지 전체 설정
st.set_page_config(layout="wide", page_title="위드인천에너지 수처리 모니터링")

# --- 사이드바 레이아웃 컨테이너 설정 (상/하단 분리) ---
sidebar_top = st.sidebar.container()
st.sidebar.markdown("<div style='height: 55vh;'></div>", unsafe_allow_html=True) # 하단으로 밀어내기 위한 여백
sidebar_bottom = st.sidebar.container()

# --- 테마 선택 (사진과 동일한 해/달 아이콘 토글 적용) ---
with sidebar_bottom:
    # `theme_selector`가 session_state에 없으면 0으로 초기화합니다.
    if 'theme_selector' not in st.session_state:
        st.session_state.theme_selector = 0

    # sac.segmented는 st.session_state.theme_selector 값을 사용하고 업데이트합니다.
    sac.segmented(
        items=[
            sac.SegmentedItem(icon='sun'),  # 0번: 해 (화이트 모드)
            sac.SegmentedItem(icon='moon'), # 1번: 달 (다크 모드)
        ],
        align='start',
        size='sm',
        radius='lg',
        return_index=True,
        key='theme_selector'
    )

# session_state에 저장된 인덱스를 바탕으로 테마 이름을 결정합니다.
theme_selection = "다크 모드" if st.session_state.theme_selector == 1 else "화이트 모드"

# --- 테마별 시인성 최적화 설정 (레이아웃 수치는 절대 고정) ---
if theme_selection == "다크 모드":
    bg_color = "#000000"      # 전체 배경: 검정
    box_bg = "#e0e0e0"       # 박스 내부: 연회색 (눈 보호용)
    border_color = "#00d4ff" # 테두리: 하늘색
    title_color = "#000000"   # 박스 내부 제목 글자: 검정
    data_color = "#1a1c24"    # 박스 내부 수치 글자
    sub_header_color = "#ffffff" # 배경 위 소제목: 흰색
    metric_val = "#ffffff"    # 하단 메트릭: 흰색
    sidebar_title_color = "#000000" # 다크모드 사이드바 제목: 검정
    
    # ★ 다크모드 전용: 강렬한 네온 효과 유지 ★
    flow_color = "#00ffff" # 형광 시안색 입자
    flow_glow = "0 0 8px #00ffff" # 강한 네온 빛 번짐 효과
    
else:
    bg_color = "#ffffff"      # 전체 배경: 흰색
    box_bg = "#1a1c24"       # 박스 내부: 검정
    border_color = "#4e9af1" # 테두리: 파란색
    title_color = "#fffd8d"   # 박스 내부 제목 글자: 노란색
    data_color = "#ffffff"    # 박스 내부 수치 글자: 흰색
    sub_header_color = "#000000" # 배경 위 소제목: 검정
    metric_val = "#000000"    # 하단 메트릭: 검정
    sidebar_title_color = "#000000" # 화이트모드에서도 검정 유지
    
    # ★ 화이트모드 전용: 눈이 편안한 소프트 효과 적용 ★
    flow_color = "#4e9af1" # 부드러운 파란색 입자 (테두리색과 통일)
    flow_glow = "none"    # 네온 빛 번짐 효과 완전 제거

# --- CSS 스타일 정의 (수치 및 구조 절대 고정) ---
# 설정된 flow_color, flow_glow 변수가 CSS에 적용됩니다.
st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color}; }}
    .main {{ background-color: {bg_color}; }}
    
    h1, h2, h3 {{ color: {sub_header_color} !important; }}
    
    /* st.divider() 구분선 시인성 강제 확보 */
    hr {{
        border: none !important;
        border-top: 2px solid {sub_header_color} !important;
        opacity: 0.3 !important;
    }}
    
    /* 탭(작은 제목) 글자색 강제 동기화 */
    button[data-baseweb="tab"] span, button[data-baseweb="tab"] div, button[data-baseweb="tab"] p {{
        color: {sub_header_color} !important;
    }}
    
    /* 슬라이더 라벨(예상 평균 ST LOAD) 글자색 강제 동기화 */
    .stSlider p {{
        color: {sub_header_color} !important;
    }}
    
    .process-container {{
        background-color: {box_bg};
        border: 2px solid {border_color};
        border-radius: 10px;
        padding: 0px 10px;
        text-align: center;
        height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        position: relative;
        z-index: 10;
    }}

    @keyframes pulse-glow {{
        0% {{ box-shadow: 0 0 5px #00d4ff; border-color: #00d4ff; }}
        50% {{ box-shadow: 0 0 15px #00d4ff; border-color: #ffffff; }}
        100% {{ box-shadow: 0 0 5px #00d4ff; border-color: #00d4ff; }}
    }}
    .running-glow {{ animation: pulse-glow 2s infinite ease-in-out; }}

    /* 유량 배관 애니메이션 (테마별 변수 적용) */
    @keyframes flow-h {{ from {{ background-position: 0 0; }} to {{ background-position: 24px 0; }} }}
    @keyframes flow-v-upward {{ from {{ background-position: 0 24px; }} to {{ background-position: 0 0; }} }}
    @keyframes flow-v-downward {{ from {{ background-position: 0 0; }} to {{ background-position: 0 24px; }} }}

    .line-h-flow {{ 
        width: 100%; height: 4px; margin-top: 54px; position: relative; 
        background: radial-gradient(circle, {flow_color} 40%, transparent 70%); /* 변수 적용 */
        background-size: 24px 4px; animation: flow-h 0.6s linear infinite; z-index: 1;
        box-shadow: {flow_glow}; /* 변수 적용 */
        border-radius: 2px;
    }}
    
    .line-angle-rd {{ width: 100%; height: 110px; position: relative; z-index: 1; }}
    .line-angle-rd::before {{
        content: ''; position: absolute; top: 54px; left: 0; width: 100%; height: 4px;
        background: radial-gradient(circle, {flow_color} 40%, transparent 70%); /* 변수 적용 */
        background-size: 24px 4px; animation: flow-h 0.6s linear infinite;
        box-shadow: {flow_glow}; /* 변수 적용 */
        border-radius: 2px;
    }}
    .line-angle-rd::after {{ display: none; }} 

    .line-h-solid {{ width: 100%; height: 2px; margin-top: 54px; background-color: #334155; position: relative; z-index: 1; }}
    .flow-data-box {{ background-color: #002b36; border: 1px solid #00d4ff; border-radius: 4px; padding: 1px 5px; font-size: 0.75rem; font-weight: bold; color: #ffffff; }}
    .manifold-anchor {{ width: 100%; height: 110px; position: relative; z-index: 1; }}
    
    .path-up-center {{ position: absolute; bottom: 50%; left: 0; width: 100%; height: 110px; z-index: 1; }}
    .path-up-center .vertical {{ 
        position: absolute; left: 0; bottom: 20px; width: 4px; height: 80%; 
        background: radial-gradient(circle, {flow_color} 40%, transparent 70%);  /* 변수 적용 */
        background-size: 4px 24px; animation: flow-v-upward 0.6s linear infinite; 
        box-shadow: {flow_glow}; /* 변수 적용 */
        border-radius: 2px;
    }}
    .path-up-center .horizontal {{ 
        position: absolute; left: 0; top: 0; width: 100%; height: 4px; 
        background: radial-gradient(circle, {flow_color} 40%, transparent 70%);  /* 변수 적용 */
        background-size: 24px 4px; animation: flow-h 0.6s linear infinite; 
        box-shadow: {flow_glow}; /* 변수 적용 */
        border-radius: 2px;
    }}
    
    .path-down-center-solid {{ position: absolute; top: 50%; left: 0; width: 100%; height: 110px; z-index: 1; }}
    .path-down-center-solid .vertical {{ position: absolute; left: 0; top: 33px; width: 2px; height: 70%; background-color: #334155; }}
    .path-down-center-solid .horizontal {{ position: absolute; left: 0; bottom: 0; width: 100%; height: 2px; background-color: #334155; }}

    .outlet-v-down {{ 
        position: absolute; right: 0; top: -54px; width: 4px; height: 130%; 
        background: radial-gradient(circle, {flow_color} 40%, transparent 70%);  /* 변수 적용 */
        background-size: 4px 24px; animation: flow-v-downward 0.6s linear infinite; 
        box-shadow: {flow_glow}; /* 변수 적용 */
        border-radius: 2px;
    }}
    .outlet-v-up {{ 
        position: absolute; right: 0; top: -54px; width: 4px; height: 130%; 
        background: radial-gradient(circle, {flow_color} 40%, transparent 70%);  /* 변수 적용 */
        background-size: 4px 24px; animation: flow-v-upward 0.6s linear infinite; 
        box-shadow: {flow_glow}; /* 변수 적용 */
        border-radius: 2px;
    }}
    .outlet-v-solid {{ position: absolute; right: 0; top: 55px; width: 2px; height: 140%; background-color: #334155; }}

    .basin-visual {{ 
        width: 100%; height: 110px; background-color: {box_bg}; border: 2px solid {border_color}; 
        position: relative; display: flex; align-items: center; justify-content: flex-start; 
        border-radius: 10px; z-index: 10; flex-direction: column; padding-top: 15px;
    }}
    .basin-water {{ position: absolute; bottom: 0; width: 100%; background: linear-gradient(180deg, #00d4ff 0%, #005f73 100%); opacity: 0.6; }}

    .sub-header-final {{ color: {sub_header_color} !important; font-size: 1.2rem; font-weight: bold; margin: 15px 0; padding-bottom: 5px; border-bottom: 3px solid #4e9af1; display: inline-block; }}
    .data-box {{ background-color: #002b36; border: 1px solid #00d4ff !important; border-radius: 4px; padding: 2px 6px; font-size: 0.75rem; font-weight: bold; }}
    
    /* 메트릭 시인성 극대화 */
    [data-testid="stMetricLabel"] * {{ font-size: 1.3rem !important; font-weight: 900 !important; color: {sub_header_color} !important; }}
    [data-testid="stMetricValue"] {{ font-size: 2.5rem !important; font-weight: 900 !important; color: {metric_val} !important; }}

    .alarm-label {{
        position: absolute; width: 30px; text-align: center; z-index: 20; 
        color: #ff4b4b; border: 2px solid #ff4b4b; border-radius: 4px; 
        padding: 1px 0px; font-size: 0.7rem; font-weight: bold;
    }}
</style>
""", unsafe_allow_html=True)

def render_tank(name, value, unit, pct):
    st.markdown(f"""
        <div style="display:flex; flex-direction:column; align-items:center; width:100%;">
            <div style="width:105px; height:16px; background:radial-gradient(ellipse at center, #999 0%, #444 100%); border-radius:50%; margin-bottom:-8px; z-index:11;"></div>
            <div style="width:105px; height:100px; background:linear-gradient(90deg, #3a3d40 0%, #6d7175 45%, #8e9296 50%, #6d7175 55%, #3a3d40 100%); border-radius:0 0 8px 8px; position:relative; display:flex; align-items:center; justify-content:center; box-shadow:inset 0 -5px 15px rgba(0,0,0,0.4); z-index:10;">
                <div style="position:absolute; left:10px; bottom:10px; width:10px; height:75px; background:rgba(0,0,0,0.3); border-radius:2px;">
                    <div style="position:absolute; bottom:0; width:100%; height:{pct}%; background:#00d4ff;"></div>
                </div>
                <div style="z-index:10; text-align:center; margin-left:12px;">
                    <div style="color:white; font-size:0.8rem; font-weight:800; line-height:1.1; margin-bottom:4px;">{name}</div>
                    <div style="color:#eee; font-size:0.7rem; font-weight:bold; background:rgba(0,0,0,0.4); padding:1px 6px; border-radius:8px;">{value}{unit}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<h2 style='color: #00d4ff;'>🟢 위드인천에너지 수처리 공정 모니터링</h2>", unsafe_allow_html=True)
st.divider()

col_left, col_right = st.columns([0.6, 0.4], gap="large")

# 1. 순수제조계통
with col_left:
    st.markdown("### 1. 순수제조계통")
    pure_tabs = st.tabs([" 1-1) 이온교환수지", " 1-2) R.O System"])
    with pure_tabs[0]:
        st.markdown("<div class='sub-header-final'>1-1) 이온교환수지</div>", unsafe_allow_html=True)
        ix_r = [1.2, 0.4, 1.0, 0.4, 1.0, 0.5, 1.1]
        ra = st.columns(ix_r)
        with ra[2]: st.markdown(f"<div class='process-container running-glow'><div style='color:{title_color}; font-size:1.1rem; font-weight:bold;'>Train A</div><div style='color:#888; font-size:0.8rem;'>2B3T</div><div class='data-box' style='color:#00d4ff; margin-top:5px;'>0.2μS/cm</div></div>", unsafe_allow_html=True)
        with ra[3]: st.markdown("<div class='line-h-flow'></div>", unsafe_allow_html=True)
        with ra[4]: st.markdown(f"<div class='process-container running-glow'><div style='color:{title_color}; font-size:1.1rem; font-weight:bold;'>Train A</div><div style='color:#888; font-size:0.8rem;'>MBP</div><div class='data-box' style='color:#00d4ff; margin-top:5px;'>0.06μS/cm</div></div>", unsafe_allow_html=True)
        with ra[5]: st.markdown("""<div style='position:absolute; width:150%; text-align:center; bottom:0px; z-index:25;'><div class='flow-data-box'> 9 m³/h</div></div><div class='line-h-flow'></div>""", unsafe_allow_html=True)
        rm = st.columns(ix_r)
        with rm[0]: st.markdown(f"""<div class="basin-visual"><div class="basin-water" style="height: 65%;"></div><div style="z-index:15; color:{title_color}; font-size:1.1rem; font-weight:bold; margin-bottom:5px;">Raw Water Basin</div><div style="z-index:15; color:#eee; font-size:0.7rem; font-weight:bold; background:rgba(0,0,0,0.4); padding:1px 6px; border-radius:8px;">3,000 mm</div></div>""", unsafe_allow_html=True)
        with rm[1]: st.markdown("<div class='manifold-anchor'><div class='path-up-center'><div class='vertical'></div><div class='horizontal'></div></div><div class='path-down-center-solid'><div class='vertical'></div><div class='horizontal'></div></div></div>", unsafe_allow_html=True)
        with rm[5]: st.markdown("""<div class='manifold-anchor'><div style='position:absolute; top:0; left:0; width:100%; height:50%;'><div class='outlet-v-down' style='top:-50px; height:150%;'></div></div><div style='position:absolute; bottom:0; left:0; width:100%; height:70%;'><div class='outlet-v-solid' style='height:100%;'></div></div></div>""", unsafe_allow_html=True)
        with rm[6]: render_tank("DEMI TANK", "8,000", "mm", 80)
        rb = st.columns(ix_r)
        with rb[2]: st.markdown(f"<div class='process-container'><div style='color:{title_color}; font-size:1.1rem; font-weight:bold;'>Train B</div><div style='color:#888; font-size:0.8rem;'>2B3T</div><div class='data-box' style='color:#00d4ff; margin-top:5px;'> - μS/cm</div></div>", unsafe_allow_html=True)
        with rb[3]: st.markdown("<div class='line-h-solid'></div>", unsafe_allow_html=True)
        with rb[4]: st.markdown(f"<div class='process-container'><div style='color:{title_color}; font-size:1.1rem; font-weight:bold;'>Train B</div><div style='color:#888; font-size:0.8rem;'>MBP</div><div class='data-box' style='color:#00d4ff; margin-top:5px;'> - μS/cm</div></div>", unsafe_allow_html=True)
        with rb[5]: st.markdown("""<div style='position:absolute; width:150%; text-align:center; top:65px; z-index:25;'><div class='flow-data-box'> 0 m³/h</div></div><div class='line-h-solid'></div>""", unsafe_allow_html=True)
    with pure_tabs[1]:
        st.markdown("<div class='sub-header-final'>1-2) R.O System</div>", unsafe_allow_html=True)
        st.markdown("<div style='height: 125px;'></div>", unsafe_allow_html=True)
        ro_r = [1.2, 0.4, 1.0, 0.4, 1.0, 0.5, 1.1]
        rr = st.columns(ro_r)
        with rr[0]: st.markdown(f"""<div class="basin-visual"><div class="basin-water" style="height: 50%;"></div><div style="z-index:15; color:{title_color}; font-size:1.1rem; font-weight:bold; margin-bottom:5px;">Raw Water Basin</div><div style="z-index:15; color:#eee; font-size:0.7rem; font-weight:bold; background:rgba(0,0,0,0.4); padding:1px 6px; border-radius:8px;">3,000 mm</div></div>""", unsafe_allow_html=True)
        with rr[1]: st.markdown("<div class='line-h-flow'></div>", unsafe_allow_html=True)
        with rr[2]: st.markdown(f"<div class='process-container running-glow'><div style='color:{title_color}; font-size:1.1rem; font-weight:bold; line-height:1.2;'>Micro & Carbon<br>Filter</div></div>", unsafe_allow_html=True)
        with rr[3]: st.markdown("<div class='line-h-flow'></div>", unsafe_allow_html=True)
        with rr[4]: st.markdown(f"<div class='process-container running-glow'><div style='color:{title_color}; font-size:1.1rem; font-weight:bold;'>R.O Units</div><div class='data-box' style='color:#00d4ff; margin-top:5px;'>7 µS/cm</div></div>", unsafe_allow_html=True)
        with rr[5]: st.markdown("""<div style='position:relative; height:110px;'><div style='position:absolute; width:130%; text-align:center; bottom:70px; white-space: nowrap; z-index:25;'><div class='flow-data-box'>6 m³/h</div></div><div class='line-h-flow'></div></div>""", unsafe_allow_html=True)
        
        with rr[6]: 
            ro_tank_current = 1500  # 원하시는 현재 수위(mm)를 여기에 입력하세요.
            ro_tank_max = 2250
            ro_tank_pct = (ro_tank_current / ro_tank_max) * 100
            ro_tank_pct = min(ro_tank_pct, 100) 
            render_tank("R.O TANK", f"{ro_tank_current:,}", "mm", ro_tank_pct)

# 2. DH처리계통
with col_right:
    st.markdown("### 2. DH처리계통")
    dh_tab_main = st.tabs([" 2-1) DH 처리 계통"])
    with dh_tab_main[0]:
        st.markdown("<div class='sub-header-final'>2-1) DH 처리 계통</div>", unsafe_allow_html=True)
        dh_r = [1.0, 0.4, 1.2, 0.4, 1.0]
        dra = st.columns(dh_r)
        with dra[2]: st.markdown(f"""<div class='process-container running-glow'><div style='color:{title_color}; font-size:1.1rem; font-weight:bold;'>Polisher</div><div class='data-box' style='color:#00d4ff; margin-top:5px;'>0.08μS/cm</div></div>""", unsafe_allow_html=True)
        with dra[3]: st.markdown("""<div style='position:absolute; width:200%; text-align:center; bottom:0px; z-index:25;'><div class='flow-data-box'> 80 m³/h</div></div><div class='line-h-flow'></div>""", unsafe_allow_html=True)
        drm = st.columns(dh_r)
        with drm[0]: st.markdown(f"<div class='process-container'><div style='color:#888; font-size:0.8rem;'>공급 (Return)</div></div>", unsafe_allow_html=True)
        with drm[1]: st.markdown("<div class='manifold-anchor'><div class='path-up-center'><div class='vertical'></div><div class='horizontal'></div></div><div class='path-down-center-solid'><div class='vertical'></div><div class='horizontal'></div></div></div>", unsafe_allow_html=True)
        with drm[3]: st.markdown("""<div class='manifold-anchor'><div style='position:absolute; top:0; left:0; width:100%; height:50%;'><div class='outlet-v-down' style='top:-50px; height:150%;'></div></div><div style='position:absolute; bottom:0; left:0; width:100%; height:70%;'><div class='outlet-v-solid' style='height:100%;'></div></div></div>""", unsafe_allow_html=True)
        with drm[4]: st.markdown(f"<div class='process-container'><div style='color:#888; font-size:0.8rem;'>지역 공급</div></div>", unsafe_allow_html=True)
        drb = st.columns(dh_r)
        with drb[2]: st.markdown(f"<div class='process-container'><div style='color:{title_color}; font-size:1.1rem; font-weight:bold;'>AFM</div><div class='data-box' style='color:#00d4ff; margin-top:5px;'> - μS/cm</div></div>", unsafe_allow_html=True)
        with drb[3]: st.markdown("""<div style='position:absolute; width:200%; text-align:center; top:65px; z-index:25;'><div class='flow-data-box'> 0 m³/h</div></div><div class='line-h-solid'></div>""", unsafe_allow_html=True)

# 3. 폐수처리계통
st.divider()
st.markdown("### 3. 폐수처리계통")
ww_r = [1.2, 0.4, 1.2, 0.4, 1.2, 0.4, 1.2, 0.4, 1.2]

w_ra = st.columns(ww_r)
with w_ra[5]: st.markdown("<div class='line-h-flow'></div>", unsafe_allow_html=True)
with w_ra[6]: st.markdown(f"<div class='process-container running-glow'><div style='color:{title_color}; font-size:1.1rem; font-weight:bold;'>Pressure Filter A</div><div style='color:#00ff00; font-size:0.75rem; font-weight:bold;'>RUNNING</div></div>", unsafe_allow_html=True)
with w_ra[7]: st.markdown("<div class='line-h-flow'></div>", unsafe_allow_html=True)

w_rm = st.columns(ww_r)
with w_rm[0]: st.markdown(f"""
    <div class="basin-visual" style="margin-top:-28px;">
        <div class="basin-water" style="height: 70%;"></div>
        <div style="z-index:15; color:{title_color}; font-size:1.1rem; font-weight:bold; margin-bottom:5px;">W/WATER POND</div>
        <div class="alarm-label" style="top:-25px; right:8px; background-color:{box_bg};">H/H</div>
        <div class="alarm-label" style="top:8px; right:8px; background-color:rgba(0,0,0,0.1);">H</div>
        <div class="alarm-label" style="bottom:30px; right:8px; background-color:rgba(0,0,0,0.1);">L</div>
        <div class="alarm-label" style="bottom:8px; right:8px; background-color:rgba(0,0,0,0.1);">L/L</div>
    </div>
    """, unsafe_allow_html=True)
with w_rm[1]: st.markdown("""<div class='manifold-anchor' style='margin-top:-28px;'><div class='line-h-flow' style='margin-top:54px;'></div></div>""", unsafe_allow_html=True)
with w_rm[2]: st.markdown(f"<div class='process-container running-glow' style='margin-top:-28px;'><div style='color:{title_color}; font-size:1.1rem; font-weight:bold;'>Reaction Tank</div><div style='color:{data_color}; font-weight:bold;'>pH : 7.0</div></div>", unsafe_allow_html=True)
with w_rm[3]: st.markdown("<div class='line-h-flow' style='margin-top:26px;'></div>", unsafe_allow_html=True)
with w_rm[4]: st.markdown(f"""
    <div class="basin-visual running-glow" style="margin-top:-28px;">
        <div class="basin-water" style="height: 40%;"></div>
        <div style="z-index:15; color:{title_color}; font-size:1.1rem; font-weight:bold; margin-bottom:5px;">Clarified W. POND</div>
        <div style="z-index:15; color:{data_color}; font-weight:bold;">pH : 7.2</div>
        <div class="alarm-label" style="top:-25px; right:8px; background-color:{box_bg};">H/H</div>
        <div class="alarm-label" style="top:8px; right:8px; background-color:rgba(0,0,0,0.1);">H</div>
        <div class="alarm-label" style="bottom:30px; right:8px; background-color:rgba(0,0,0,0.1);">L</div>
        <div class="alarm-label" style="bottom:8px; right:8px; background-color:rgba(0,0,0,0.1);">L/L</div>
    </div>
    """, unsafe_allow_html=True)
with w_rm[5]: st.markdown("""<div class='manifold-anchor' style='margin-top:-50px;'><div style='position:absolute; top:25px; left:0px; width:100%; height:50%;'><div class='outlet-v-up' style='top:-28px; height:100%; left:0; right:auto;'></div></div><div style='position:absolute; bottom:0; left:0; width:100%; height:60%;'><div class='outlet-v-solid' style='height:100%; left:0; right:auto;'></div></div><div class='path-down-center-solid'><div class='horizontal'></div></div></div>""", unsafe_allow_html=True)
with w_rm[7]: st.markdown("""<div class='manifold-anchor' style='margin-top:-50px;'><div style='position:absolute; top:25px; left:0px; width:100%; height:50%;'><div class='outlet-v-down' style='top:-28px; height:100%;'></div></div><div style='position:absolute; bottom:0; left:0; width:100%; height:60%;'><div class='outlet-v-solid' style='height:100%;'></div></div></div>""", unsafe_allow_html=True)
with w_rm[8]: st.markdown(f"""
    <div class="basin-visual" style="margin-top:-28px;">
        <div class="basin-water" style="height: 60%;"></div>
        <div style="z-index:15; color:{title_color}; font-size:1.1rem; font-weight:bold; margin-bottom:5px;">Filtered Pond</div>
        <div style="z-index:15; color:{data_color}; font-weight:bold;">pH : 7.2</div>
        <div class="alarm-label" style="top:-25px; right:8px; background-color:{box_bg};">H/H</div>
        <div class="alarm-label" style="top:8px; right:8px; background-color:rgba(0,0,0,0.1);">H</div>
        <div class="alarm-label" style="bottom:32px; right:8px; background-color:rgba(0,0,0,0.1);">L</div>
        <div class="alarm-label" style="bottom:8px; right:8px; background-color:rgba(0,0,0,0.1);">L/L</div>
    </div>
    """, unsafe_allow_html=True)

w_rb = st.columns(ww_r)
with w_rb[6]: st.markdown(f"<div class='process-container' style='margin-top:-85px;'><div style='color:{title_color}; font-size:1.1rem; font-weight:bold;'>Pressure Filter B</div><div style='color:#ff4b4b; font-size:0.75rem; font-weight:bold;'>STOPPED</div></div>", unsafe_allow_html=True)
with w_rb[7]: st.markdown("<div style='margin-top:-85px;'><div class='line-h-solid'></div></div>", unsafe_allow_html=True)

# ★ 4. 탈질 계통 ★
st.divider()
st.markdown("### 4. 탈질 계통")

# 변수 사전 정의 (탱크 A, B 레벨)
tank_a_level = 80.1
tank_b_level = 80.5

deni_tabs = st.tabs([" 4-1) 탈질 처리 계통", " 4-2) 암모니아수 입고 예측"])

# 기존 4-1 탭
with deni_tabs[0]:
    st.markdown("<div class='sub-header-final'>4-1) 탈질 처리 계통</div>", unsafe_allow_html=True)
    
    col4_l, col4_m, col4_r = st.columns([0.2, 1.4, 0.8])
    
    with col4_l:
        render_tank("NH4OH Tank A", f"{tank_a_level}", "%", tank_a_level)
        st.markdown("<div style='height: 0px;'></div>", unsafe_allow_html=True)
        render_tank("NH4OH Tank B", f"{tank_b_level}", "%", tank_b_level)

    with col4_m:
        st.markdown("""
            <div style="position: relative; height: 250px; width: 100%;">
                <div class="line-h-solid" style="position: absolute; left: -20px; top: 25px; width: 50px;"></div>
                <div class="line-h-solid" style="position: absolute; left: -20px; top: 150px; width: 50px;"></div>
                <div class="outlet-v-solid" style="position: absolute; left: 30px; top: 79px; height: 62px;"></div>
                <div class="outlet-v-solid" style="position: absolute; left: 30px; top: 143px; height: 63px;"></div>
                <div class="line-h-solid" style="position: absolute; left: 30px; top: 87px; width: 40px;"></div>
                <div class="outlet-v-up" style="position: absolute; left: 70px; top: 25px; height: 119px;"></div>
                <div class="line-h-flow" style="position: absolute; left: 70px; top: -30px; width: 200px;"></div>
                <div style="position: absolute; left: 280px; top: 13px; z-index: 25;">
                    <div class="flow-data-box">120 kg/h</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with col4_r:
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        m_cols = st.columns(2)
        m_cols[0].metric("ST LOAD", "120 MW")
        m_cols[1].metric("ST NOx", "4.5 ppm")

# 4-2 탭: 입고 시기 예측 시뮬레이터
with deni_tabs[1]:
    st.markdown("<div class='sub-header-final'>4-2) ST LOAD 기반 입고 시기 예측</div>", unsafe_allow_html=True)
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    
    sim_col1, sim_col2 = st.columns([0.4, 0.6], gap="large")
    
    with sim_col1:
        st.markdown(f"<h4 style='color: {sub_header_color};'>시뮬레이션 설정</h4>", unsafe_allow_html=True)
        
        # 슬라이더: 예상 ST LOAD (최대 24MW)
        sim_load = st.slider("예상 평균 ST LOAD (MW)", min_value=0, max_value=24, value=24, step=1)
        
        # 산정식: 24MW일 때 125kg/h 소모 -> 1MW당 (125/24) kg/h
        est_usage = sim_load * (125.0 / 24.0)
        
        st.markdown(f"<div style='margin-top:20px; padding:15px; border-radius:10px; border:1px solid {border_color};'>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:{sub_header_color}; font-weight:bold;'>예상 암모니아수 사용량: </span> <span style='color:{sub_header_color}; font-size:1.2rem; font-weight:bold;'>{est_usage:.1f} kg/h</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with sim_col2:
        st.markdown(f"<h4 style='color: {sub_header_color};'>입고 일정 예측 결과</h4>", unsafe_allow_html=True)
        
        # 재고 산출식: (탱크 A 레벨 + 탱크 B 레벨) * 120.55 - 5500
        current_stock = (tank_a_level + tank_b_level) * 120.55 - 5500
        if current_stock < 0:
            current_stock = 0
        
        if est_usage > 0:
            # 예상 소진일 = 현재 재고 / (시간당 소모량 * 24시간)
            days_left = current_stock / (est_usage * 24)
            # 입고 필요 시점 = 전량 소진일 - 안전재고 기간(예: 3일)
            reorder_days = days_left - 3 
        else:
            days_left = 999
            reorder_days = 999
            
        res_col1, res_col2 = st.columns(2)
        res_col1.metric(label="현재 총 재고 추정치", value=f"{current_stock:,.1f} kg")
        
        if days_left != 999:
            res_col2.metric(label="예상 전량 소진일", value=f"{days_left:.1f} 일")
            
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            if reorder_days > 0:
                st.info(f"💡 **안전 재고(3일) 확보를 위해 약 {reorder_days:.1f} 일 후 입고가 필요합니다.**")
            else:
                st.error("🚨 **긴급: 현재 재고가 안전 재고 기준에 미달합니다. 즉시 입고가 필요합니다.**")
        else:
            res_col2.metric(label="예상 전량 소진일", value="-")
            st.success("✅ ST LOAD가 0 MW로 설정되어 암모니아수가 소모되지 않습니다.")

# --- 사이드바 레이아웃 상/하단 분리 ---
with sidebar_top:
    st.markdown(f"<div style='font-size: 1.3rem; font-weight: bold; margin-bottom: 15px; color: {sidebar_title_color} !important;'>📊 시스템 요약</div>", unsafe_allow_html=True)
    st.info("DEMI TANK: 8,000 mm")
    st.success("정상 운전: Train A")
    st.markdown("---")
    st.markdown(f"<p style='color: {sidebar_title_color}; font-weight: bold;'>주요 공정</p>", unsafe_allow_html=True)
    st.info("R.O 생산: 6 m³/h")
    st.info("DH 공급: 80 m³/h")
    st.info("탈질 부하: 120 MW")