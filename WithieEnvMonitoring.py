import streamlit as st
import streamlit.components.v1 as components
import streamlit_antd_components as sac
import pandas as pd
import base64
import re

# --- 데이터 로드 ---
@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_excel("data.xlsx", sheet_name="Sheet1")

        # 필수 컬럼 존재 여부 확인
        required_columns = ['Tag', 'Value', 'Update Time']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Excel 파일에 필수 컬럼이 누락되었습니다: {', '.join(missing_columns)}. 'Tag', 'Value', 'Update Time' 컬럼이 정확한 이름으로 존재하는지 확인해주세요.")
            return None

        df['Update Time'] = pd.to_datetime(df['Update Time'])
        latest_data = df.sort_values('Update Time').groupby('Tag').last()
        return latest_data
    except FileNotFoundError:
        st.error("⚠️ data.xlsx 파일을 찾을 수 없습니다. app.py와 같은 폴더에 파일이 있는지 확인해주세요.")
        return None
    except PermissionError:
        st.error("🛑 [Permission Denied] 'data.xlsx' 파일에 접근할 수 없습니다. 파일이 다른 프로그램(예: Excel)에서 열려 있는지 확인하고 닫은 후 다시 시도해주세요.")
        return None
    except Exception as e:
        st.error(f"데이터 로딩 중 예상치 못한 오류가 발생했습니다: {e}")
        return None

data = load_data()

def get_value(tag, default_value="-"):
    if data is None:
        return default_value
    try:
        value = data.loc[tag, 'Value']
        return value
    except KeyError:
        return default_value

# --- 이미지 파일을 Base64로 인코딩하는 함수 ---
@st.cache_data
def get_image_as_base64(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        # 이미지를 찾지 못한 경우, 사용자에게 알림
        st.warning(f"CI 로고 파일({path})을 찾을 수 없습니다. 앱과 같은 폴더에 파일이 있는지 확인해주세요.")
        return None


# 1. 페이지 전체 설정
st.set_page_config(layout="wide", page_title="위드인천에너지 수처리 공정 모니터링", initial_sidebar_state="expanded")


# --- 모바일 환경에서 PC 화면 레이아웃(배관 등) 깨짐 방지 ---
# 모바일 브라우저의 viewport를 강제로 PC 화면 너비(1350px)로 고정하여 
# Streamlit의 모바일용 화면 변형(반응형 모드)이 작동하지 않게 만듭니다.
components.html(
    """
    <script>
        try {
            const parentDoc = window.parent.document;
            
            // 1. 모바일 뷰포트 강제 설정 (1350px 고정)
            // 데스크탑 크기(1350px)로 뷰포트를 고정하여 모바일 기기가 억지로 모바일용 화면으로 변환하지 못하게 차단합니다.
            let metaViewport = parentDoc.querySelector('meta[name="viewport"]');
            if (!metaViewport) {
                metaViewport = parentDoc.createElement('meta');
                metaViewport.name = 'viewport';
                parentDoc.head.appendChild(metaViewport);
            }
            metaViewport.setAttribute('content', 'width=650, initial-scale=1.0, minimum-scale=0.3, maximum-scale=5.0, user-scalable=yes');

            // Streamlit의 컬럼이 모바일에서 강제로 100%가 되며 세로로 쌓이는 현상을 방지
            function lockColumnWidths() {
                const columns = parentDoc.querySelectorAll('div[data-testid="column"]');
                columns.forEach((col, idx) => {
                    const inlineWidth = col.style.width;
                    
                    // 100%로 변경되기 전의 원본 비율(예: 60%, 40%)을 메모리(dataset)에 영구 백업
                    if (inlineWidth && !inlineWidth.includes('100%') && !col.dataset.origWidth) {
                        col.dataset.origWidth = inlineWidth;
                    }
                    
                    // 백업된 원본 비율이 있다면 그것을 사용, 없다면 현재 너비 사용
                    const targetWidth = col.dataset.origWidth || inlineWidth;
                    
                    // 원본 PC 비율을 강제로 무한 고정 (!important)
                    if (targetWidth && !targetWidth.includes('100%')) {
                        col.style.setProperty('width', targetWidth, 'important');
                        col.style.setProperty('min-width', targetWidth, 'important');
                        col.style.setProperty('max-width', targetWidth, 'important');
                        col.style.setProperty('flex', '1 1 ' + targetWidth, 'important');
                    }
                });
                
                // 강제로 가로 블록이 세로로 꺾이는 현상(flex-direction: column)을 원천 차단
                const hBlocks = parentDoc.querySelectorAll('div[data-testid="stHorizontalBlock"]');
                hBlocks.forEach(block => {
                    block.style.setProperty('flex-direction', 'row', 'important');
                    block.style.setProperty('flex-wrap', 'nowrap', 'important');
                });
            }
            
            lockColumnWidths();
            // 화면 조작 시에도 영구 고정되도록 감시
            const observer = new MutationObserver(lockColumnWidths);
            observer.observe(parentDoc.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['style', 'class'] });
            
            // --- 2. 모바일용 전체화면(Fullscreen) 토글 버튼 추가 ---
            if (!parentDoc.getElementById('mobile-fs-btn')) {
                const fsBtn = parentDoc.createElement('div');
                fsBtn.id = 'mobile-fs-btn';
                fsBtn.innerHTML = '⛶';
                fsBtn.title = '전체화면 전환';
                Object.assign(fsBtn.style, {
                    display: window.parent.innerWidth <= 768 ? 'block' : 'none',
                    position: 'fixed',
                    bottom: '20px',
                    right: '20px',
                    width: '50px',
                    height: '50px',
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    color: '#00d4ff',
                    border: '2px solid #00d4ff',
                    borderRadius: '50%',
                    zIndex: '9999999',
                    fontSize: '24px',
                    lineHeight: '46px',
                    textAlign: 'center',
                    cursor: 'pointer',
                    boxShadow: '0 0 10px #00d4ff',
                    backdropFilter: 'blur(4px)',
                    transition: 'all 0.3s ease-in-out'
                });

                // 화면 회전 등 크기 변경 시 버튼 표시 여부 감지
                window.parent.addEventListener('resize', () => {
                    fsBtn.style.display = window.parent.innerWidth <= 768 ? 'block' : 'none';
                });

                // 버튼 클릭 시 전체화면 진입/해제 로직
                fsBtn.addEventListener('click', () => {
                    const docEl = parentDoc.documentElement;
                    const isFullscreen = parentDoc.fullscreenElement || parentDoc.webkitFullscreenElement || parentDoc.mozFullScreenElement || parentDoc.msFullscreenElement;
                    
                    if (!isFullscreen) {
                        if (docEl.requestFullscreen) docEl.requestFullscreen();
                        else if (docEl.webkitRequestFullscreen) docEl.webkitRequestFullscreen();
                        else if (docEl.mozRequestFullScreen) docEl.mozRequestFullScreen();
                        else if (docEl.msRequestFullscreen) docEl.msRequestFullscreen();
                        else alert("현재 브라우저/기기에서는 전체화면 API를 지원하지 않습니다. (예: 아이폰 Safari)");
                    } else {
                        if (parentDoc.exitFullscreen) parentDoc.exitFullscreen();
                        else if (parentDoc.webkitExitFullscreen) parentDoc.webkitExitFullscreen();
                        else if (parentDoc.mozCancelFullScreen) parentDoc.mozCancelFullScreen();
                        else if (parentDoc.msExitFullscreen) parentDoc.msExitFullscreen();
                    }
                });
                
                parentDoc.body.appendChild(fsBtn);
            }

        } catch (e) { console.error("Viewport 세팅 실패", e); }
    </script>
    """,
    height=0, width=0
)

# --- 다크 모드 시인성 최적화 설정 (레이아웃 수치는 절대 고정) ---
bg_color = "#000000"      # 전체 배경: 검정
box_bg = "#e0e0e0"       # 박스 내부: 연회색 (눈 보호용)
border_color = "#00d4ff" # 테두리: 하늘색
title_color = "#000000"   # 박스 내부 제목 글자: 검정
data_color = "#1a1c24"    # 박스 내부 수치 글자
sub_header_color = "#ffffff" # 배경 위 소제목: 흰색
metric_val = "#ffffff"    # 하단 메트릭: 흰색
sidebar_title_color = "#ffffff" # 다크모드 사이드바 제목: 흰색
dh_label_color = "#000000"

# 다크모드 st.info() 메시지 박스 시인성 개선
info_style_override = """
    [data-testid="stAlert"][data-kind="info"] {
        background-color: #012A36 !important;
        border: 1px solid #00d4ff !important;
        border-radius: 10px !important;
    }
    [data-testid="stAlert"][data-kind="info"] * {
        color: #FFFFFF !important;
    }
"""

# 다크모드 st.success() 메시지 박스 시인성 개선
success_style_override = """
    [data-testid="stAlert"][data-kind="success"] {
        background-color: #022C17 !important;
        border: 1px solid #2ECC71 !important;
        border-radius: 10px !important;
    }
    [data-testid="stAlert"][data-kind="success"] * {
        color: #FFFFFF !important;
    }
"""

# 다크모드 st.warning() 메시지 박스 시인성 개선
warning_style_override = """
    [data-testid="stAlert"][data-kind="warning"] {
        background-color: #3B2E0A !important;
        border: 1px solid #F1C40F !important;
        border-radius: 10px !important;
    }
    [data-testid="stAlert"][data-kind="warning"] * {
        color: #FFFFFF !important;
    }
"""

# 사이드바 등 메시지 박스 내부 텍스트 강제 좌측 정렬 (모바일에서 텍스트 정렬 틀어짐 방지)
alert_text_align_override = """
    [data-testid="stAlert"] .stMarkdownContainer p {
        text-align: left !important;
        width: 100% !important;
        margin-bottom: 0 !important;
        margin-left: 0 !important;
        padding-left: 0 !important;
    }
    /* 사이드바 전용 커스텀 알림 박스 (들여쓰기 버그 원천 차단용) */
    .sidebar-alert-success {
        background-color: #022C17;
        border: 1px solid #2ECC71;
        border-radius: 10px;
        padding: 14px;
        color: #FFFFFF;
        font-size: 1rem;
        margin-bottom: 1rem;
        line-height: 1.6;
        text-align: left;
    }
    .sidebar-alert-warning {
        background-color: #3B2E0A;
        border: 1px solid #F1C40F;
        border-radius: 10px;
        padding: 14px;
        color: #FFFFFF;
        font-size: 1rem;
        margin-bottom: 1rem;
        line-height: 1.6;
        text-align: left;
    }
"""

# ★ 다크모드 전용: 강렬한 네온 효과 유지 ★
flow_color = "#00ffff" # 형광 시안색 입자
flow_glow = "0 0 8px #00ffff" # 강한 네온 빛 번짐 효과

# --- CSS 스타일 정의 (수치 및 구조 절대 고정) ---
# 설정된 flow_color, flow_glow 변수가 CSS에 적용됩니다.
st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color}; }}

    /* ========================================================
       스크롤바 디자인 커스텀 (다크모드 시인성 확보를 위해 흰색으로 변경)
       ======================================================== */
    ::-webkit-scrollbar {{
        width: 12px;
        height: 12px;
    }}
    ::-webkit-scrollbar-track {{
        background: {bg_color};
    }}
    ::-webkit-scrollbar-thumb {{
        background: #ffffff; /* 스크롤바 색상을 흰색으로 지정 */
        border-radius: 6px;
        border: 2px solid {bg_color}; /* 배경과 어우러지도록 테두리 추가 */
    }}
    * {{
        scrollbar-color: #ffffff {bg_color}; /* Firefox 브라우저 지원용 */
    }}

    /* ========================================================
       창 모드(작은 화면)에서 메인 화면 하단에 가로 스크롤바가 생기도록 강제
       사이드바는 고정되고 메인 화면 영역만 스크롤 가능하도록 설정
       ======================================================== */
    .main, [data-testid="stMain"] {{ 
        background-color: {bg_color};
        overflow-x: auto !important; /* 창이 좁아지면 메인 화면 하단에 스크롤바 생성 */
        }}
    /* 모바일 기기에서도 최상위 컨테이너가 스크롤을 막지 못하도록 전체 강제 오버라이딩 */
    html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"], .main, [data-testid="stMain"] {{ 
        background-color: {bg_color} !important;
        overflow-x: auto !important; 
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch !important; /* iOS 모바일 스크롤 부드럽게 */
    }}
    
    /* ========================================================
       PC 레이아웃 고정 및 모바일 기기 자동 축소(반응형 줌) 적용
       ======================================================== */
    .block-container, [data-testid="stAppViewBlockContainer"], [data-testid="stMainBlockContainer"] {{
        min-width: 650px !important; /* 650px 이하에서도 PC 레이아웃을 유지 (브라우저가 자동 축소) */
        max-width: 100% !important; /* 확장형(Wide) 페이지에 맞게 모니터 해상도 전체 너비를 사용하도록 100% 허용 */
        width: 100% !important;
        padding-left: 0.5rem !important;  /* Streamlit 기본 좌우 여백을 줄여서 잘림 현상 방지 */
        padding-right: 0.5rem !important;
        margin-left: 0 !important; /* 스크롤 시 왼쪽 화면이 잘리는 현상을 방지하기 위해 무조건 왼쪽 정렬 */
        margin-right: auto !important;
    }}
    
    /* 무조건 가로 나열 (세로 모드에서도 세로로 쌓이지 않도록 안전장치 강제) */
    [data-testid="stHorizontalBlock"] {{
        flex-direction: row !important;
        flex-wrap: nowrap !important;
    }}
    [data-testid="column"] {{
        min-width: 0 !important;
    }}
    
    /* 모든 모바일 화면 크기에서 Streamlit의 강제 세로화(컬럼 스택) 원천 차단 */
    @media (max-width: 768px) {{
        [data-testid="stHorizontalBlock"] {{
            flex-direction: row !important;
            flex-wrap: nowrap !important;
        }}
        [data-testid="column"] {{
            width: auto !important;
            flex: 1 1 0% !important;
            min-width: 0 !important;
        }}
    }}
    
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

    /* 체크박스 라벨(Train A/B, Polisher 등) 글자색 강제 동기화 (streamlit 버전 대응) */
    [data-testid="stCheckbox"] p, [data-testid="stCheckbox"] span {{
        color: {sub_header_color} !important;
        font-weight: bold !important;
    }}

    /* 사이드바 하단 고정용 */
    [data-testid="stSidebar"] > div:first-child {{
        display: flex;
        flex-direction: column;
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
        align-items: center; /* 데이터 박스가 너비 전체로 늘어나지 않고 가운데 정렬되도록 강제 */
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
    .flow-data-box {{ 
        background-color: #002b36; 
        border: 1px solid #00d4ff; 
        border-radius: 4px; 
        padding: 2px 8px; 
        font-size: 0.9rem; 
        font-weight: bold; 
        color: #ffffff; 
        display: inline-block; /* 부모 너비(150% 등)로 무작정 늘어나는 현상 방지 */
        white-space: nowrap; /* 글자가 두 줄로 깨지는 현상 원천 차단 */
    }}
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

    .path-up-center-solid {{ position: absolute; bottom: 50%; left: 0; width: 100%; height: 110px; z-index: 1; }}
    .path-up-center-solid .vertical {{ 
        position: absolute; left: 0; bottom: 20px; width: 2px; height: 80%;
        background-color: #334155;
    }}
    .path-up-center-solid .horizontal {{ 
        position: absolute; left: 0; top: 0; width: 100%; height: 2px;
        background-color: #334155;
    }}

    .path-down-center-flow {{ position: absolute; top: 50%; left: 0; width: 100%; height: 110px; z-index: 1; }}
    .path-down-center-flow .vertical {{
        position: absolute; left: 0; top: 33px; width: 4px; height: 70%;
        background: radial-gradient(circle, {flow_color} 40%, transparent 70%);
        background-size: 4px 24px; animation: flow-v-downward 0.6s linear infinite;
        box-shadow: {flow_glow};
        border-radius: 2px;
    }}
    .path-down-center-flow .horizontal {{
        position: absolute; left: 0; bottom: 0; width: 100%; height: 4px;
        background: radial-gradient(circle, {flow_color} 40%, transparent 70%);
        background-size: 24px 4px; animation: flow-h 0.6s linear infinite;
        box-shadow: {flow_glow};
        border-radius: 2px;
    }}

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

    .outlet-v-up-bottom {{ 
        position: absolute; right: 0; top: 55px; width: 4px; height: 130%; 
        background: radial-gradient(circle, {flow_color} 40%, transparent 70%);
        background-size: 4px 24px; animation: flow-v-upward 0.6s linear infinite; 
        box-shadow: {flow_glow};
        border-radius: 2px;
    }}

    .basin-visual {{ 
        width: 100%; height: 110px; background-color: {box_bg}; border: 2px solid {border_color}; 
        position: relative; display: flex; align-items: center; justify-content: flex-start; 
        border-radius: 10px; z-index: 10; flex-direction: column; padding-top: 15px;
    }}
    .basin-water {{ position: absolute; bottom: 0; width: 100%; background: linear-gradient(180deg, #00d4ff 0%, #005f73 100%); opacity: 0.6; }}

    .sub-header-final {{ color: {sub_header_color} !important; font-size: 1.2rem; font-weight: bold; margin: 15px 0; padding-bottom: 5px; border-bottom: 3px solid #4e9af1; display: inline-block; }}
    .data-box {{ 
        background-color: #002b36; 
        border: 1px solid #00d4ff !important; 
        border-radius: 4px; 
        padding: 2px 6px; 
        font-size: 0.75rem; 
        font-weight: bold; 
        display: inline-block; /* 박스가 깔끔하게 내용물 크기만 차지하도록 수정 */
        white-space: nowrap; /* 글자 줄바꿈 차단 */
    }}
    
    /* 메트릭 시인성 극대화 */
    [data-testid="stMetricValue"] {{ font-size: 2.5rem !important; font-weight: 900 !important; }}

    .alarm-label {{
        position: absolute; width: 30px; text-align: center; z-index: 20; 
        color: #ff4b4b; border: 2px solid #ff4b4b; border-radius: 4px; 
        padding: 1px 0px; font-size: 0.7rem; font-weight: bold;
    }}
    {info_style_override}
    {success_style_override}
    {warning_style_override}
    {alert_text_align_override}

    /* 탈질계통 메트릭 전용 커스텀 흰색 클래스 */
    .custom-white-metric .title {{
        font-size: 1.3rem !important;
        font-weight: 900 !important;
        color: #ffffff !important;
    }}
    .custom-white-metric .value {{
        font-size: 2.5rem !important;
        font-weight: 900 !important;
        color: #ffffff !important;
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


# --- 로고 이미지 처리 및 제목 표시 ---
logo_base64 = get_image_as_base64("ci_logo.png")
if logo_base64:
    # 이미지가 있으면 이미지 태그를, 없으면 녹색 동그라미를 사용
    logo_html = f"<img src='data:image/png;base64,{logo_base64}' style='height: 35px; margin-right: 10px;'>"
else:
    logo_html = "🟢"

st.markdown(f"<h2 style='color: #00d4ff; display: flex; align-items: center;'>{logo_html}위드인천에너지 수처리 공정 모니터링</h2>", unsafe_allow_html=True)
st.divider()

# --- Raw Water Basin 수위 계산 ---
raw_water_level_val = get_value('Raw_Water_Basin_Level', '3,000')
try:
    # If it's already a number, use it directly. If it's a string, convert to float.
    if isinstance(raw_water_level_val, str):
        raw_water_level = float(raw_water_level_val.replace(',', ''))
    else:
        raw_water_level = float(raw_water_level_val)
except (ValueError, TypeError):
    raw_water_level = 3000.0

raw_water_max = 4500  # 최대 수위 4,500mm로 가정
raw_water_pct = min((raw_water_level / raw_water_max) * 100, 100)

col_left, col_right = st.columns([0.6, 0.4], gap="large")

# 1. 순수제조계통
with col_left:
    st.markdown("### 1. 순수제조계통")
    pure_tabs = st.tabs([" 1-1) 이온교환수지", " 1-2) R.O System"])
    with pure_tabs[0]:
        st.markdown("<div class='sub-header-final'>1-1) 이온교환수지</div>", unsafe_allow_html=True)
        
        # 데이터 기반으로 Train A/B 가동 상태 결정
        try:
            train_a_running = float(get_value('Train_A_Flow', '9')) > 0
        except (ValueError, TypeError):
            train_a_running = False

        try:
            train_b_running = float(get_value('Train_B_Flow', '9')) > 0
        except (ValueError, TypeError):
            train_b_running = False
        
        st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)

        # Define styles and values based on state
        train_a_glow = "running-glow" if train_a_running else ""
        train_a_pipe = "line-h-flow" if train_a_running else "line-h-solid"
        train_a_flow = f"{get_value('Train_A_Flow', '9')} m³/h" if train_a_running else "0 m³/h"
        
        train_b_glow = "running-glow" if train_b_running else ""
        train_b_pipe = "line-h-flow" if train_b_running else "line-h-solid"
        train_b_flow = f"{get_value('Train_B_Flow', '9')} m³/h" if train_b_running else "0 m³/h"

        # Determine manifold path styles
        path_a_class = "path-up-center" if train_a_running else "path-up-center-solid"
        path_b_class = "path-down-center-flow" if train_b_running else "path-down-center-solid"

        # Determine outlet manifold classes
        outlet_a_pipe_class = "outlet-v-down" if train_a_running else "outlet-v-solid"
        outlet_b_pipe_class = "outlet-v-up-bottom" if train_b_running else "outlet-v-solid"

        # Layout
        ix_r = [1.2, 0.4, 1.0, 0.4, 1.0, 0.5, 1.1]
        ra = st.columns(ix_r)
        with ra[2]: st.markdown(f"<div class='process-container {train_a_glow}'><div style='color:{title_color}; font-size:1.1rem; font-weight:bold;'>Train A</div><div style='color:#888; font-size:0.8rem;'>2B3T</div><div class='data-box' style='color:#00d4ff; margin-top:5px;'>{get_value('Train_A_2B3T_Conductivity', '0.2')}μS/cm</div></div>", unsafe_allow_html=True)
        with ra[3]: st.markdown(f"<div class='{train_a_pipe}'></div>", unsafe_allow_html=True)
        with ra[4]: st.markdown(f"<div class='process-container {train_a_glow}'><div style='color:{title_color}; font-size:1.1rem; font-weight:bold;'>Train A</div><div style='color:#888; font-size:0.8rem;'>MBP</div><div class='data-box' style='color:#00d4ff; margin-top:5px;'>{get_value('Train_A_MBP_Conductivity', '0.06')}μS/cm</div></div>", unsafe_allow_html=True)
        with ra[5]: st.markdown(f"""<div style='position:absolute; width:150%; text-align:center; bottom:0px; z-index:25;'><div class='flow-data-box'> {train_a_flow}</div></div><div class='{train_a_pipe}'></div>""", unsafe_allow_html=True)
        
        rm = st.columns(ix_r)
        with rm[0]: st.markdown(f"""<div class="basin-visual"><div class="basin-water" style="height: {raw_water_pct}%;"></div><div style="z-index:15; color:{title_color}; font-size:1.1rem; font-weight:bold; margin-bottom:5px;">Raw Water Basin</div><div style="z-index:15; color:#eee; font-size:0.7rem; font-weight:bold; background:rgba(0,0,0,0.4); padding:1px 6px; border-radius:8px;">{get_value('Raw_Water_Basin_Level', '3,000')} mm</div></div>""", unsafe_allow_html=True)
        with rm[1]: st.markdown(f"""
            <div class='manifold-anchor'>
                <div class='{path_a_class}'>
                    <div class='vertical'></div>
                    <div class='horizontal'></div>
                </div>
                <div class='{path_b_class}'>
                    <div class='vertical'></div>
                    <div class='horizontal'></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        with rm[5]: st.markdown(f"""
            <div class='manifold-anchor'>
                <div style='position:absolute; top:0; left:0; width:100%; height:50%;'>
                    <div class='{outlet_a_pipe_class}' style='top:-54px; height:150%;'></div>
                </div>
                <div style='position:absolute; bottom:0; left:0; width:100%; height:70%;'>
                    <div class='{outlet_b_pipe_class}' style='height:100%;'></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        with rm[6]: render_tank("DEMI TANK", get_value('DEMI_TANK_Level', '8,000'), "mm", 80)
        
        rb = st.columns(ix_r)
        with rb[2]: st.markdown(f"<div class='process-container {train_b_glow}'><div style='color:{title_color}; font-size:1.1rem; font-weight:bold;'>Train B</div><div style='color:#888; font-size:0.8rem;'>2B3T</div><div class='data-box' style='color:#00d4ff; margin-top:5px;'>{get_value('Train_B_2B3T_Conductivity', '-')} μS/cm</div></div>", unsafe_allow_html=True)
        with rb[3]: st.markdown(f"<div class='{train_b_pipe}'></div>", unsafe_allow_html=True)
        with rb[4]: st.markdown(f"<div class='process-container {train_b_glow}'><div style='color:{title_color}; font-size:1.1rem; font-weight:bold;'>Train B</div><div style='color:#888; font-size:0.8rem;'>MBP</div><div class='data-box' style='color:#00d4ff; margin-top:5px;'>{get_value('Train_B_MBP_Conductivity', '-')} μS/cm</div></div>", unsafe_allow_html=True)
        with rb[5]: st.markdown(f"""<div style='position:absolute; width:150%; text-align:center; top: 70px; z-index:25;'><div class='flow-data-box'> {train_b_flow}</div></div><div class='{train_b_pipe}'></div>""", unsafe_allow_html=True)
    with pure_tabs[1]:
        st.markdown("<div class='sub-header-final'>1-2) R.O System</div>", unsafe_allow_html=True)
        
        # 데이터 기반으로 R.O System 가동 상태 결정
        try:
            ro_running = float(get_value('RO_System_Flow', '6')) > 0
        except (ValueError, TypeError):
            ro_running = False

        st.markdown("<div style='height: 125px;'></div>", unsafe_allow_html=True)

        ro_glow = "running-glow" if ro_running else ""
        ro_pipe = "line-h-flow" if ro_running else "line-h-solid"
        ro_flow = f"{get_value('RO_System_Flow', '6')} m³/h" if ro_running else "0 m³/h"
        
        ro_r = [1.2, 0.4, 1.0, 0.4, 1.0, 0.5, 1.1]
        rr = st.columns(ro_r)
        with rr[0]: st.markdown(f"""<div class="basin-visual"><div class="basin-water" style="height: {raw_water_pct}%;"></div><div style="z-index:15; color:{title_color}; font-size:1.1rem; font-weight:bold; margin-bottom:5px;">Raw Water Basin</div><div style="z-index:15; color:#eee; font-size:0.7rem; font-weight:bold; background:rgba(0,0,0,0.4); padding:1px 6px; border-radius:8px;">{get_value('Raw_Water_Basin_Level', '3,000')} mm</div></div>""", unsafe_allow_html=True)
        with rr[1]: st.markdown(f"<div class='{ro_pipe}'></div>", unsafe_allow_html=True)
        with rr[2]: st.markdown(f"<div class='process-container {ro_glow}'><div style='color:{title_color}; font-size:1.1rem; font-weight:bold; line-height:1.2;'>Micro & Carbon<br>Filter</div></div>", unsafe_allow_html=True)
        with rr[3]: st.markdown(f"<div class='{ro_pipe}'></div>", unsafe_allow_html=True)
        with rr[4]: st.markdown(f"<div class='process-container {ro_glow}'><div style='color:{title_color}; font-size:1.1rem; font-weight:bold;'>R.O Units</div><div class='data-box' style='color:#00d4ff; margin-top:5px;'>{get_value('RO_Units_Conductivity', '7')} µS/cm</div></div>", unsafe_allow_html=True)
        with rr[5]: st.markdown(f"""<div style='position:relative; height:110px;'><div style='position:absolute; width:130%; text-align:center; bottom:70px; white-space: nowrap; z-index:25;'><div class='flow-data-box'>{ro_flow}</div></div><div class='{ro_pipe}'></div></div>""", unsafe_allow_html=True)
        
        with rr[6]: 
            ro_tank_current = float(get_value('RO_TANK_Level', 1500))  # 원하시는 현재 수위(mm)를 여기에 입력하세요.
            ro_tank_max = 2250
            ro_tank_pct = (ro_tank_current / ro_tank_max) * 100
            ro_tank_pct = min(ro_tank_pct, 100) 
            render_tank("R.O TANK", f"{ro_tank_current:,.0f}", "mm", ro_tank_pct)

# 2. DH처리계통
with col_right:
    st.markdown("### 2. DH처리계통")
    dh_tab_main = st.tabs([" DH 처리 계통"])
    with dh_tab_main[0]:
        st.markdown("<div class='sub-header-final'>DH 처리 계통</div>", unsafe_allow_html=True)

        # 데이터 기반으로 Polisher/AFM 가동 상태 결정
        try:
            polisher_running = float(get_value('Polisher_Flow', '80')) > 0
        except (ValueError, TypeError):
            polisher_running = False
        
        try:
            afm_running = float(get_value('AFM_Flow', '80')) > 0
        except (ValueError, TypeError):
            afm_running = False

        st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)

        # Determine state based on selection
        # (The checkbox return values are now directly used)

        # Define styles and values based on state
        polisher_glow = "running-glow" if polisher_running else ""
        polisher_pipe = "line-h-flow" if polisher_running else "line-h-solid"
        polisher_flow = f"{get_value('Polisher_Flow', '80')} m³/h" if polisher_running else "0 m³/h"

        afm_glow = "running-glow" if afm_running else ""
        afm_pipe = "line-h-flow" if afm_running else "line-h-solid"
        afm_flow = f"{get_value('AFM_Flow', '80')} m³/h" if afm_running else "0 m³/h"

        # Determine manifold path styles for DH system
        dh_path_polisher_class = "path-up-center" if polisher_running else "path-up-center-solid"
        dh_path_afm_class = "path-down-center-flow" if afm_running else "path-down-center-solid"

        # Determine outlet manifold classes
        dh_outlet_a_class = "outlet-v-down" if polisher_running else "outlet-v-solid"
        dh_outlet_b_class = "outlet-v-up-bottom" if afm_running else "outlet-v-solid"
        
        # Layout
        dh_r = [1.0, 0.4, 1.2, 0.4, 1.0]
        dra = st.columns(dh_r)
        with dra[2]: st.markdown(f"""<div class='process-container {polisher_glow}'><div style='color:{title_color}; font-size:1.2rem; font-weight:bold;'>Polisher</div><div class='data-box' style='color:#00d4ff; margin-top:5px;'>{get_value('Polisher_Conductivity', '0.08')}μS/cm</div></div>""", unsafe_allow_html=True)
        with dra[3]: st.markdown(f"""<div style='position:absolute; width:200%; text-align:center; bottom:0px; z-index:25;'><div class='flow-data-box'> {polisher_flow}</div></div><div class='{polisher_pipe}'></div>""", unsafe_allow_html=True)
        
        drm = st.columns(dh_r)
        with drm[0]: st.markdown(f"<div class='process-container'><div style='color:{dh_label_color}; font-size:1.1rem; font-weight:bold;'>DH수 Return</div></div>", unsafe_allow_html=True)
        with drm[1]: st.markdown(f"""
            <div class='manifold-anchor'>
                <div class='{dh_path_polisher_class}'>
                    <div class='vertical'></div>
                    <div class='horizontal'></div>
                </div>
                <div class='{dh_path_afm_class}'>
                    <div class='vertical'></div>
                    <div class='horizontal'></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        with drm[3]: st.markdown(f"""
            <div class='manifold-anchor'>
                <div style='position:absolute; top:0; left:0; width:100%; height:50%;'>
                    <div class='{dh_outlet_a_class}' style='top:-54px; height:150%;'></div>
                </div>
                <div style='position:absolute; bottom:0; left:0; width:100%; height:70%;'>
                    <div class='{dh_outlet_b_class}' style='height:100%;'></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        with drm[4]: st.markdown(f"<div class='process-container'><div style='color:{dh_label_color}; font-size:1.1rem; font-weight:bold;'>지역 공급</div></div>", unsafe_allow_html=True)
        
        drb = st.columns(dh_r)
        with drb[2]: st.markdown(f"<div class='process-container {afm_glow}'><div style='color:{title_color}; font-size:1.2rem; font-weight:bold;'>AFM</div><div class='data-box' style='color:#00d4ff; margin-top:5px;'>{get_value('AFM_Conductivity', '-')} μS/cm</div></div>", unsafe_allow_html=True)
        with drb[3]: st.markdown(f"""<div style='position:absolute; width:200%; text-align:center; bottom:-55px; z-index:25;'><div class='flow-data-box'> {afm_flow}</div></div><div class='{afm_pipe}'></div>""", unsafe_allow_html=True)

# 3. 폐수처리계통
st.divider()
st.markdown("### 3. 폐수처리계통")

try:
    is_ww_running = float(get_value('WW_Flow_Rate', '5')) > 0
except (ValueError, TypeError):
    is_ww_running = False

# --- 각 Pond 별 데이터 처리 ---
def get_pond_details(tag_name):
    status = get_value(tag_name, 'Normal')
    if status == 'H/H':
        height = 75  # H 레벨 높이
        active_label = 'H/H'
    else:
        height = 15  # L/L 레벨 높이
        active_label = None
    return height, active_label

ww_pond_height, ww_pond_label = get_pond_details('W_WATER_POND_Level_Status')
clarified_pond_height, clarified_pond_label = get_pond_details('Clarified_W_POND_Level_Status')
filtered_pond_height, filtered_pond_label = get_pond_details('Filtered_Pond_Level_Status')

# --- Pressure Filter 및 가동 상태에 따른 스타일 정의 ---
pressure_filter_status = get_value('Pressure_Filter_Status', 'A').upper()
is_filter_a_running = is_ww_running and (pressure_filter_status == 'A')
is_filter_b_running = is_ww_running and (pressure_filter_status == 'B')

# 공통 가동 상태
ww_flow_class = "line-h-flow" if is_ww_running else "line-h-solid"
ww_glow_class = "running-glow" if is_ww_running else ""
ww_flow_rate = f"{get_value('WW_Flow_Rate', '5')} m³/h" if is_ww_running else "0 m³/h"

# 필터 A 상태
filter_a_status_text = "RUNNING" if is_filter_a_running else "STOPPED"
filter_a_status_color = "#00ff00" if is_filter_a_running else "#ff4b4b"
filter_a_glow = "running-glow" if is_filter_a_running else ""
filter_a_h_pipe = "line-h-flow" if is_filter_a_running else "line-h-solid"
ww_filter_a_in_pipe = "outlet-v-up" if is_filter_a_running else "outlet-v-solid"
ww_filter_a_out_pipe = "outlet-v-down" if is_filter_a_running else "outlet-v-solid"

# 필터 B 상태
filter_b_status_text = "RUNNING" if is_filter_b_running else "STOPPED"
filter_b_status_color = "#00ff00" if is_filter_b_running else "#ff4b4b"
filter_b_glow = "running-glow" if is_filter_b_running else ""
filter_b_h_pipe = "line-h-flow" if is_filter_b_running else "line-h-solid"
ww_filter_b_in_pipe = "outlet-v-down" if is_filter_b_running else "outlet-v-solid"
ww_filter_b_out_pipe = "outlet-v-up" if is_filter_b_running else "outlet-v-solid"

def get_alarm_labels_html(active_label, box_bg, is_filtered_pond=False):
    """선택된 레벨에 해당하는 알람 라벨의 HTML만 생성합니다."""
    if not active_label:
        return ""

    l_position = "32px" if is_filtered_pond else "30px"
    
    labels = {
        "H/H": f'<div class="alarm-label" style="top:-25px; right:8px; background-color:{box_bg};">H/H</div>',
        "H": f'<div class="alarm-label" style="top:8px; right:8px; background-color:{box_bg};">H</div>',
        "L": f'<div class="alarm-label" style="bottom:{l_position}; right:8px; background-color:{box_bg};">L</div>',
        "L/L": f'<div class="alarm-label" style="bottom:8px; right:8px; background-color:{box_bg};">L/L</div>'
    }
    return labels.get(active_label, "")

# 각 POND에 맞는 알람 HTML 생성
ww_pond_alarms = get_alarm_labels_html(ww_pond_label, box_bg)
clarified_pond_alarms = get_alarm_labels_html(clarified_pond_label, box_bg)
filtered_pond_alarms = get_alarm_labels_html(filtered_pond_label, box_bg, is_filtered_pond=True)

ww_r = [1.0, 0.35, 1.0, 0.35, 1.1, 0.3, 1.1, 0.3, 1.1, 0.6, 0.2]

w_ra = st.columns(ww_r)
with w_ra[5]: st.markdown(f"<div class='{filter_a_h_pipe}'></div>", unsafe_allow_html=True)
with w_ra[6]: st.markdown(f"<div class='process-container {filter_a_glow}'><div style='color:{title_color}; font-size:1.1rem; font-weight:bold;'>Pressure Filter A</div><div style='color:{filter_a_status_color}; font-size:0.75rem; font-weight:bold;'>{filter_a_status_text}</div></div>", unsafe_allow_html=True)
with w_ra[7]: st.markdown(f"<div class='{filter_a_h_pipe}'></div>", unsafe_allow_html=True)

w_rm = st.columns(ww_r)
with w_rm[0]: st.markdown(f"""
    <div class="basin-visual" style="margin-top:-28px;">
        <div class="basin-water" style="height: {ww_pond_height}%;"></div>
        <div style="z-index:15; color:{title_color}; font-size:1.1rem; font-weight:bold; margin-bottom:5px;">W/WATER POND</div>
        <div style="z-index:15; color:{data_color}; font-weight:bold;">pH : {get_value('W_WATER_POND_pH', '7.0')}</div>
        {ww_pond_alarms}
    </div>
    """, unsafe_allow_html=True)
with w_rm[1]: st.markdown(f"""<div class='manifold-anchor' style='margin-top:-28px;'><div class='{ww_flow_class}' style='margin-top:54px;'></div></div>""", unsafe_allow_html=True)
with w_rm[2]: st.markdown(f"<div class='process-container {ww_glow_class}' style='margin-top:-28px;'><div style='color:{title_color}; font-size:1.1rem; font-weight:bold;'>Reaction Tank</div><div style='color:{data_color}; font-weight:bold;'>pH : {get_value('Reaction_Tank_pH', '7.0')}</div></div>", unsafe_allow_html=True)
with w_rm[3]: st.markdown(f"<div class='{ww_flow_class}' style='margin-top:26px;'></div>", unsafe_allow_html=True)
with w_rm[4]: st.markdown(f"""
    <div class="basin-visual {ww_glow_class}" style="margin-top:-28px;">
        <div class="basin-water" style="height: {clarified_pond_height}%;"></div>
        <div style="z-index:15; color:{title_color}; font-size:1.1rem; font-weight:bold; margin-bottom:5px;">Clarified W. POND</div>
        <div style="z-index:15; color:{data_color}; font-weight:bold;">pH : {get_value('Clarified_W_POND_pH', '7.2')}</div>
        {clarified_pond_alarms}
    </div>
    """, unsafe_allow_html=True)
with w_rm[5]: st.markdown(f"""<div class='manifold-anchor' style='margin-top:-50px;'><div style='position:absolute; top:24px; left:0px; width:100%; height:50%;'><div class='{ww_filter_a_in_pipe}' style='top:-28px; height:100%; left:0; right:auto;'></div></div><div style='position:absolute; bottom:0; left:0; width:100%; height:60%;'><div class='{ww_filter_b_in_pipe}' style='top:53px; height:100%; left:0; right:auto;'></div></div></div>""", unsafe_allow_html=True)
with w_rm[7]: st.markdown(f"""<div class='manifold-anchor' style='margin-top:-50px;'><div style='position:absolute; top:25px; left:0px; width:100%; height:50%;'><div class='{ww_filter_a_out_pipe}' style='top:-28px; height:100%;'></div></div><div style='position:absolute; bottom:0; left:0; width:100%; height:60%;'><div class='{ww_filter_b_out_pipe}' style='top:53px; height:100%;'></div></div></div>""", unsafe_allow_html=True)
with w_rm[8]: st.markdown(f"""
    <div class="basin-visual {ww_glow_class}" style="margin-top:-28px;">
        <div class="basin-water" style="height: {filtered_pond_height}%;"></div>
        <div style="z-index:15; color:{title_color}; font-size:1.1rem; font-weight:bold; margin-bottom:5px;">Filtered Pond</div>
        <div style="z-index:15; color:{data_color}; font-weight:bold;">pH : {get_value('Filtered_Pond_pH', '7.2')}</div>
        {filtered_pond_alarms}
    </div>
    """, unsafe_allow_html=True)
with w_rm[9]: st.markdown(f"""
    <div style='position:relative; height: 110px; margin-top:-28px;'>
        <div class='{ww_flow_class}' style='margin-top: 54px;'></div>
        <div style='position:absolute; width:100%; text-align:center; top: -40px; z-index:25;'>
             <div class='flow-data-box'>{ww_flow_rate}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

w_rb = st.columns(ww_r)
with w_rb[5]: st.markdown(f"<div style='margin-top:-85px;'><div class='{filter_b_h_pipe}'></div></div>", unsafe_allow_html=True)
with w_rb[6]: st.markdown(f"<div class='process-container {filter_b_glow}' style='margin-top:-85px;'><div style='color:{title_color}; font-size:1.1rem; font-weight:bold;'>Pressure Filter B</div><div style='color:{filter_b_status_color}; font-size:0.75rem; font-weight:bold;'>{filter_b_status_text}</div></div>", unsafe_allow_html=True)
with w_rb[7]: st.markdown(f"<div style='margin-top:-85px;'><div class='{filter_b_h_pipe}'></div></div>", unsafe_allow_html=True)

# ★ 4. 탈질 계통 ★
st.divider()
st.markdown("### 4. 탈질 계통")

# 변수 사전 정의 (탱크 A, B 레벨 및 현재 재고량)
tank_a_level = float(get_value('NH4OH_Tank_A_Level', 80.1))
tank_b_level = float(get_value('NH4OH_Tank_B_Level', 80.5))
# 재고 산출식: (탱크 A 레벨 + 탱크 B 레벨) * 120.55 - 5500
current_stock = (tank_a_level + tank_b_level) * 120.55 - 5500
if current_stock < 0:
    current_stock = 0

denitrification_tabs = st.tabs([" 4-1) 탈질설비계통", " 4-2) ST LOAD 기반 입고 시기 예측"])

with denitrification_tabs[0]:
    st.markdown("<div class='sub-header-final'>4-1) 탈질 설비 계통</div>", unsafe_allow_html=True)

    col4_l, col4_m, col4_r = st.columns([0.2, 1.4, 0.8])

    with col4_l:
        render_tank("NH4OH Tank A", f"{tank_a_level}", "%", tank_a_level)
        st.markdown("<div style='height: 0px;'></div>", unsafe_allow_html=True)
        render_tank("NH4OH Tank B", f"{tank_b_level}", "%", tank_b_level)

    with col4_m:
        # 데이터 기반으로 암모니아수 주입량 및 가동 상태 결정
        nh4oh_consumption_val = get_value('NH4OH_Consumption', '125')
        try:
            is_den_running = float(nh4oh_consumption_val) > 0
        except (ValueError, TypeError):
            is_den_running = False
        
        nh4oh_consumption_text = f"{nh4oh_consumption_val} kg/h"

        # 가동 상태에 따른 파이프 스타일 결정
        den_v_pipe_class = "outlet-v-up" if is_den_running else "outlet-v-solid"
        den_h_pipe_class = "line-h-flow" if is_den_running else "line-h-solid"

        st.markdown(f"""
            <div style="position: relative; height: 250px; width: 100%;">
                <div class="line-h-solid" style="position: absolute; left: -20px; top: 25px; width: 50px;"></div>
                <div class="line-h-solid" style="position: absolute; left: -20px; top: 150px; width: 50px;"></div>
                <div class="outlet-v-solid" style="position: absolute; left: 30px; top: 79px; height: 62px;"></div>
                <div class="outlet-v-solid" style="position: absolute; left: 30px; top: 143px; height: 63px;"></div>
                <div class="line-h-solid" style="position: absolute; left: 30px; top: 87px; width: 40px;"></div>
                <div class="{den_v_pipe_class}" style="position: absolute; left: 70px; top: 25px; height: 119px;"></div>
                <div class="{den_h_pipe_class}" style="position: absolute; left: 70px; top: -30px; width: 200px;"></div>
                <div style="position: absolute; left: 280px; top: 13px; z-index: 25;">
                    <div class="flow-data-box" style="font-size: 1.1rem; padding: 3px 10px;">{nh4oh_consumption_text}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with col4_r:
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        m_cols = st.columns(2)
        # 데이터 기반으로 ST LOAD, NOx 메트릭 표시 및 NOx 값에 따른 색상 분기 처리
        st_load_val = get_value('ST_LOAD', '24') # 표시용
        nox_val_str = get_value('NOx', '15') # 표시용
        nox_val_num = 15.0 # 로직 처리용 기본값

        # [수정] 데이터 파싱 로직 강화: 문자열에 포함된 숫자만 정확히 추출
        try:
            # 값에서 숫자(소수점 포함) 부분만 찾아내어 float으로 변환
            match = re.search(r'(\d+\.?\d*)', str(nox_val_str))
            if match:
                nox_val_num = float(match.group(1))
        except (ValueError, TypeError, AttributeError):
            # 파싱 실패 시 기본값 사용
            nox_val_num = 15.0

        m_cols[0].markdown(f'<div class="custom-white-metric"><div class="title">ST LOAD</div><div class="value">{st_load_val} MW</div></div>', unsafe_allow_html=True)
        # 사용자 정의 HTML로 NOx 메트릭 표시
        m_cols[1].markdown(f'<div class="custom-white-metric"><div class="title">NOx</div><div class="value">{nox_val_str} ppm</div></div>', unsafe_allow_html=True)
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        
        # 사용자 정의 HTML로 재고량 메트릭 표시
        st.markdown(f'''<div class="custom-white-metric"><div class="title">현재 재고량</div><div class="value">{current_stock:,.1f} kg</div></div>''', unsafe_allow_html=True)

with denitrification_tabs[1]:
    st.markdown("<div class='sub-header-final'>4-2) ST LOAD 기반 입고 시기 예측</div>", unsafe_allow_html=True)
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    sim_col1, sim_col2 = st.columns([0.4, 0.6], gap="large")

    with sim_col1:
        st.markdown(f"<h4 style='color: {sub_header_color};'>시뮬레이션 설정</h4>", unsafe_allow_html=True)
        
        # 현재 ST LOAD 값을 슬라이더 기본값으로 설정
        try:
            st_load_default = int(float(get_value('ST_LOAD', '24')))
        except (ValueError, TypeError):
            st_load_default = 24

        # 슬라이더: 예상 ST LOAD (최대 24MW)
        sim_load = st.slider("Steam Turbin LOAD (MW)", min_value=0, max_value=24, value=st_load_default, step=1, key="sim_load_slider")
        
        # 산정식: 24MW일 때 125kg/h 소모 -> 1MW당 (125/24) kg/h
        est_usage = sim_load * (125.0 / 24.0)
        
        st.markdown(f"<div style='margin-top:20px; padding:15px; border-radius:10px; border:1px solid {border_color};'><span style='color:{sub_header_color}; font-weight:bold;'>예상 암모니아수 사용량: </span> <span style='color:{sub_header_color}; font-size:1.2rem; font-weight:bold;'>{est_usage:.1f} kg/h</span></div>", unsafe_allow_html=True)
        
    with sim_col2:
        st.markdown(f"<h4 style='color: {sub_header_color};'>입고 일정 예측 결과</h4>", unsafe_allow_html=True)
        
        if est_usage > 0:
            # 예상 소진일 = 현재 재고 / (시간당 소모량 * 24시간)
            days_left = current_stock / (est_usage * 24)
            # 입고 필요 시점 = 전량 소진일 - 안전재고 기간(예: 3일)
            reorder_days = days_left - 3 
        else:
            days_left = 999
            reorder_days = 999
            
        res_col1, res_col2 = st.columns(2)

        # 사용자 정의 HTML로 재고량 메트릭 표시
        res_col1.markdown(f'<div class="custom-white-metric"><div class="title">현재 재고량</div><div class="value">{current_stock:,.1f} kg</div></div>', unsafe_allow_html=True)
        
        if days_left != 999:
            res_col2.markdown(f'<div class="custom-white-metric"><div class="title">예상 소진일</div><div class="value">{days_left:.1f} 일</div></div>', unsafe_allow_html=True)
            
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            if reorder_days > 0:
                st.info(f"💡 **안전 재고(3일) 확보를 위해 약 {reorder_days:.1f} 일 후 입고가 필요합니다.**")
            else:
                st.error("🚨 **긴급: 현재 재고가 안전 재고 기준에 미달합니다. 즉시 입고가 필요합니다.**")
        else:
            res_col2.markdown(f'<div class="custom-white-metric"><div class="title">예상 전량 소진일</div><div class="value">-</div></div>', unsafe_allow_html=True)
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            st.success("✅ 열병합발전시설의 미가동으로 암모니아수가 소모되지 않습니다.")


# --- 사이드바 ---
with st.sidebar:
    st.markdown(f"<div style='font-size: 1.3rem; font-weight: bold; margin-bottom: 15px; color: {sidebar_title_color} !important;'>📊 모니터링 현황</div>", unsafe_allow_html=True)
    
    # --- 순수제조계통 ---
    st.markdown(f"<p style='font-size: 1.1rem; font-weight: bold; margin-top: 10px; color: {sidebar_title_color};'>순수제조계통</p>", unsafe_allow_html=True)

    # Determine individual statuses
    ix_status_string = ""
    if train_a_running and train_b_running:
        ix_status_string = "🟢 이온교환수지: 'A' & 'B' Train 가동중"
    elif train_a_running:
        ix_status_string = "🟢 이온교환수지: 'A' Train 가동중"
    elif train_b_running:
        ix_status_string = "🟢 이온교환수지: 'B' Train 가동중"
    else:
        ix_status_string = "🔴 이온교환수지: 정지"

    ro_status_string = "🟢 R.O System: 가동중" if ro_running else "🔴 R.O System: 정지"

    # Determine overall status for color
    is_pure_system_running = train_a_running or train_b_running or ro_running
    
    # Combine strings
    combined_status = f"{ix_status_string}<br><br>{ro_status_string}"

    # Display in a single box
    if is_pure_system_running:
        st.markdown(f'<div class="sidebar-alert-success">{combined_status}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="sidebar-alert-warning">{combined_status}</div>', unsafe_allow_html=True)

    # --- DH처리계통 ---
    st.markdown(f"<p style='font-size: 1.1rem; font-weight: bold; margin-top: 10px; color: {sidebar_title_color};'>DH처리계통</p>", unsafe_allow_html=True)
    
    dh_status_strings = []
    if polisher_running:
        dh_status_strings.append("🟢 Polisher: 가동중")
    else:
        dh_status_strings.append("🔴 Polisher: 정지")
    
    if afm_running:
        dh_status_strings.append("🟢 AFM: 가동중")
    else:
        dh_status_strings.append("🔴 AFM: 정지")

    is_dh_system_running = polisher_running or afm_running
    
    combined_dh_status = "<br><br>".join(dh_status_strings)

    if is_dh_system_running:
        st.markdown(f'<div class="sidebar-alert-success">{combined_dh_status}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="sidebar-alert-warning">{combined_dh_status}</div>', unsafe_allow_html=True)

    # --- 폐수처리계통 ---
    st.markdown(f"<p style='font-size: 1.1rem; font-weight: bold; margin-top: 10px; color: {sidebar_title_color};'>폐수처리계통</p>", unsafe_allow_html=True)
    if is_ww_running:
        st.markdown('<div class="sidebar-alert-success">🟢 가동중</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="sidebar-alert-warning">🔴 정지</div>', unsafe_allow_html=True)

    # --- 탈질계통 ---
    st.markdown(f"<p style='font-size: 1.1rem; font-weight: bold; margin-top: 10px; color: {sidebar_title_color};'>탈질계통</p>", unsafe_allow_html=True)
    
    st_load_side = get_value('ST_LOAD', '24')
    nox_side = get_value('NOx', '15')
    nh4oh_side = get_value('NH4OH_Consumption', '125')

    den_icon = "🟢" if is_den_running else "🔴"
    den_details = f"{den_icon} ST Load: {st_load_side} MW<br><br>{den_icon} NOx: {nox_side} ppm<br><br>{den_icon} 암모니아수 투입량: {nh4oh_side} kg/h"

    if is_den_running:
        st.markdown(f'<div class="sidebar-alert-success">{den_details}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="sidebar-alert-warning">{den_details}</div>', unsafe_allow_html=True)

    st.markdown("<div style='flex: 1;'></div>", unsafe_allow_html=True)
