from app import LumenaAIApp

import streamlit as st


# 앱 초기화
if "app" not in st.session_state:
    st.session_state["app"] = LumenaAIApp()

app = st.session_state["app"]

st.set_page_config(layout="wide")

st.logo(
    "asset/logo_big.png",
    size='large'
)


# 왼쪽 사이드바: YouTube 콘텐츠 리스트
st.sidebar.header("📚 **내 YouTube 지식**")


with st.sidebar:
    if "show_add_knowledge" not in st.session_state:
        st.session_state["show_add_knowledge"] = False

    # "새로운 지식 추가하기" 버튼
    if st.button("➕ 새로운 지식", use_container_width=True, type='primary'):
        st.session_state["show_add_knowledge"] = not st.session_state["show_add_knowledge"]


    # 유튜브 링크 입력 창 (버튼 클릭 시 표시)
    if st.session_state["show_add_knowledge"]:
        st.text_input("유튜브 링크를 입력하세요:", key="new_youtube_link")
        if st.button("추가"):
            new_link = st.session_state.get("new_youtube_link", "")
            if new_link:
                # 유튜브 링크 추가 로직 호출
                app.add_youtube_content(new_link)
                st.success("새로운 지식이 추가되었습니다!")
                st.session_state["show_add_knowledge"] = False  # 창 닫기
            else:
                st.error("유효한 유튜브 링크를 입력하세요.")


    search_query = st.text_input(" 🔍 검색어를 입력하세요:")
    if search_query:
        app.set_search_query(search_query)
    else:
        app.set_search_query('')



all_youtube_contents = app.get_search_youtube_contents()




# 카테고리별로 콘텐츠 그룹화
from itertools import groupby
all_youtube_contents = app.get_search_youtube_contents()
all_youtube_contents.sort(key=lambda x: x.category)  # 카테고리별 정렬
grouped_contents = groupby(all_youtube_contents, key=lambda x: x.category)


if app.search_query != '':
    st.sidebar.markdown(
        f"""
        <div style="font-family: 'Arial, sans-serif'; font-size: 16px; color: #FF4081; text-align: center; line-height: 1.6;">
            <b>🔍 검색 결과:</b>  
            <span style="font-size: 20px; color: #333;">{len(all_youtube_contents)}개</span>
            <br>✨ 찾으시는 지식이 여기에 있어요! ✨
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.sidebar.markdown(
        f"""
        <div style="font-family: 'Arial, sans-serif'; font-size: 16px; color: #007BFF; text-align: center; line-height: 1.6;">
            <b>📚 총 {len(all_youtube_contents)}개의 지식이 쌓여있어요!</b>  
            <br>🌟 <i>새로운 인사이트를 발견해보세요!</i> 🌟
        </div>
        """,
        unsafe_allow_html=True,
    )
st.sidebar.write('')

# 카테고리별로 콘텐츠를 나누어 표시
for category, group in grouped_contents:
    count = sum(1 for x in all_youtube_contents if x.category == category)
    with st.sidebar.expander(f'{category}({count}개)' if category else "기타"):
        for content in group:
            # 클릭 가능한 콘텐츠 제목 링크
            if st.button(content.title):
                app.select_youtube_content(content)


with st.sidebar:
    if len(all_youtube_contents) == 0:
        st.warning("🔍 검색된 결과가 없습니다.")

    view_mode = st.radio(
        "요약 화면 비율을 선택하세요:",
        options=["large", "small"],
        index=["large", "small"].index(app.view_mode),
    )
    app.set_view_mode(view_mode)


col1, col2 = st.columns([2 if app.view_mode == 'small' else 3, 2])

selected_content = app.selected_youtube_content

if selected_content is not None:
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

with col1:
    if selected_content is not None:

        st.header(selected_content.title)

        tab1, tab2, tab3, tab4 = st.tabs(["유튜브 정보", "타임라인 요약", "핵심 정보", "채팅"])

        with tab1:
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
    if selected_content is not None:
        
        # 상단: 유튜브 영상 (열고 닫기 가능)
        with st.expander("🎬 영상", expanded=True):
            st.video(selected_content.url.url)

        # HTML로 스타일링된 대본 표시
        if selected_content.script_auto is not None:
            with st.expander("📜 스크립트(Youtube)", expanded=False):
                st.html(f"<div class='styled-box'> {selected_content.formatted_script_auto} </div>")

        # HTML로 스타일링된 대본 표시
        if selected_content.script is not None:
            with st.expander("📜 스크립트(Whisper V3)", expanded=False):
                st.html(f"<div class='styled-box'> {selected_content.formatted_script} </div>")