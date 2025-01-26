from application.service import YouTubeContentService

import streamlit as st
from html import escape
from app import AppContainer


# 컨테이너 초기화
st.session_state.setdefault("app_container", AppContainer())
container = st.session_state["app_container"]

# 서비스 가져오기
youtube_service: YouTubeContentService = container.youtube_service()


st.session_state.setdefault('view_mode', 'large')
def set_view_mode(mode):
    st.session_state["view_mode"] = mode

st.set_page_config(layout="wide")

st.logo(
    "asset/logo_big.png",
    size='large'
)

# 왼쪽 사이드바: YouTube 콘텐츠 리스트
contents = youtube_service.list_all_content()
st.sidebar.header(f"📚 **내 YouTube 지식 ({len(contents)}개)**")

# 카테고리별로 콘텐츠 그룹화
from itertools import groupby
contents.sort(key=lambda x: x.category)  # 카테고리별 정렬
grouped_contents = groupby(contents, key=lambda x: x.category)

st.markdown(
    """
    <style>
    .small-button {
        font-size: 12px;  /* 텍스트 크기 조정 */
        padding: 5px 10px; /* 버튼 크기 조정 */
        margin: 2px;  /* 버튼 간격 */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 카테고리별로 콘텐츠를 나누어 표시
for category, group in grouped_contents:
    count = sum(1 for x in contents if x.category == category)
    with st.sidebar.expander(f'{category}({count}개)' if category else "기타"):
        for content in group:
            # 클릭 가능한 콘텐츠 제목 링크
            if st.button(content.title, key=f"content_{content.url.url}"):
                st.session_state["selected_content"] = content

with st.sidebar:
    view_mode = st.radio(
        "요약 화면 비율을 선택하세요:",
        options=["large", "small"],
        index=["large", "small"].index(st.session_state["view_mode"]),
    )

    st.session_state["view_mode"] = view_mode  # 선택된 모드를 상태에 반영

if "selected_content" in st.session_state:
    selected_content = st.session_state["selected_content"]

col1, col2 = st.columns([2 if st.session_state['view_mode'] == 'small' else 3, 2])

if 'selected_content' in st.session_state:
    # 중단: 스크립트 (열고 닫기 가능)
    # CSS 스타일 정의
    st.markdown(
        """
        <style>
        .styled-box {
            max-height: 300px;
            overflow-y: auto;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #f9f9f9;
            font-family: Arial, sans-serif;
        }
        .styled-box .timestamp {
            padding: .2em .4em;
            border-radius: 5px;
            background-color: rgba(135,131,120,.15);
            font-size: .9em;
            color: #ff4081;
        }
        .styled-box .text {
            font-size: 16px;
            color: #333;
            margin-bottom: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # 대본 내용을 HTML로 변환
    formatted_script = "\n".join(
        f'<div>'
        f'<span class="timestamp">{chunk.timestamp[0]}</span>'
        f'<span class="text">{escape(chunk.text)}</span>'
        f'</div>'
        for chunk in selected_content.script.chunks  # if chunk.text != ''
    )

with col1:
    if "selected_content" in st.session_state:

        st.header(selected_content.title)

        tab1, tab2, tab3, tab4 = st.tabs(["유튜브 정보", "타임라인 요약", "핵심 정보", "채팅"])


        with tab1:
            selected_content = st.session_state["selected_content"]
            st.markdown("##### 🌐 **URL 정보**")
            st.markdown(f"[{selected_content.url.url}]({selected_content.url.url})", unsafe_allow_html=True)

            st.markdown("##### 📝 **설명**")
            st.write(selected_content.description)
            st.divider()

            st.markdown("##### 🔖 **태그**")
            st.markdown(", ".join([f"`{tag}`" for tag in selected_content.tags]))

    else:
        st.header("콘텐츠를 선택하세요")
        st.write("왼쪽에서 콘텐츠를 선택하면 여기에 상세 정보가 표시됩니다.")

with col2:
    if "selected_content" in st.session_state:

        selected_content = st.session_state["selected_content"]

        st.session_state.setdefault("current_video_time", 0)


        # 상단: 유튜브 영상 (열고 닫기 가능)
        with st.expander("🎬 영상", expanded=True):
            st.video(selected_content.url.url)


        # HTML로 스타일링된 대본 표시
        with st.expander("📜 스크립트", expanded=False):
            st.html(f"<div class='styled-box'> {formatted_script} </div>")

