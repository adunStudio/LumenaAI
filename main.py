from app import LumenaAIApp

import streamlit as st

from domain.value_object.youtube_video_link import YouTubeVideoLink
from domain.entity.execute_result import  ExecuteResult, ExecuteResultType
from itertools import groupby

# 앱 초기화
if "app" not in st.session_state:
    st.session_state["app"] = LumenaAIApp()

app: LumenaAIApp = st.session_state["app"]

st.set_page_config(page_title="LumenaAI 유튜브 분석/요약 플랫폼", layout='wide')

print('render')


st.logo(
    "asset/logo_big.png",
    size='large'
)

print("페이지: " + app.page)


########################################################################################################################
# 사이드바: 추가/검색
########################################################################################################################
def sidebar_top_render():
    with st.sidebar:
        st.header("📚 **내 YouTube 지식**")

        # "새로운 지식 추가하기" 버튼
        if st.button("➕ 새로운 지식", use_container_width=True, type='primary'):
            print('before')
            app.set_page('add')
            print('after')
            print("페이지: " + app.page)

        search_query = st.text_input(" 🔍 검색어를 입력하세요:")
        if search_query:
            app.set_search_query(search_query)
        else:
            app.set_search_query('')

########################################################################################################################
# 사이드바: 카테고리 목록
########################################################################################################################
def sidebar_channel_render():
    all_youtube_contents.sort(key=lambda x: x.channel)  # 채널별 정렬
    grouped_contents = groupby(all_youtube_contents, key=lambda x: x.channel)

    with st.sidebar:
        if app.search_query != '':
            st.markdown(
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
            st.markdown(
                f"""
                <div style="font-family: 'Arial, sans-serif'; font-size: 16px; color: #007BFF; text-align: center; line-height: 1.6;">
                    <b>📚 총 {len(all_youtube_contents)}개의 지식이 쌓여있어요!</b>  
                    <br>🌟 <i>새로운 인사이트를 발견해보세요!</i> 🌟
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.write('')

        # 채널별로 콘텐츠를 나누어 표시
        for channel, group in grouped_contents:
            count = sum(1 for x in all_youtube_contents if x.channel == channel)
            with st.expander(f'{channel}({count}개)' if channel else "기타"):
                for content in group:
                    if st.button(content.title):
                        app.set_page('main')
                        app.select_youtube_content(content)


        if len(all_youtube_contents) == 0:
            st.warning("🔍 검색된 결과가 없습니다.")

########################################################################################################################
# 사이드바: 설정
########################################################################################################################
def sidebar_setting_render():
    with st.sidebar:
        view_mode = st.radio(
            "요약 화면 비율을 선택하세요:",
            options=["large", "small"],
            index=["large", "small"].index(app.view_mode),
        )
        app.set_view_mode(view_mode)


########################################################################################################################
# 메인 페이지:
########################################################################################################################
def main_page_render():
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
                with st.expander("📜 스크립트(Youtube Auto)", expanded=True):
                    st.html(f"<div class='styled-box'> {selected_content.formatted_script_auto} </div>")

            # HTML로 스타일링된 대본 표시
            if selected_content.script is not None:
                with st.expander("📜 스크립트(Whisper V3)", expanded=True):
                    st.html(f"<div class='styled-box'> {selected_content.formatted_script} </div>")

########################################################################################################################
# 추가 페이지:
########################################################################################################################
def add_page_render():
    c1, c2, c3 = st.columns([1, 3, 1])

    with c2:
        # 로고 및 제목
        st.subheader(":red[유튜브]에서 요약된 지식을 얻으세요!")

        # 검색 입력 박스 및 버튼
        youtube_link = st.text_input("Youtube 영상 링크를 입력하세요.", placeholder="https://www.youtube.com/watch?v=유튜브 영상 링크를 입력하세요.")

        is_valid_link = YouTubeVideoLink.is_valid_youtube_link(youtube_link)

        if st.button("새로운 지식 추가하기", use_container_width=True, type='primary', disabled=is_valid_link):
            if not is_valid_link:
                st.error("유효한 유튜브 링크를 입력하세요.")
            else:
                st.success("유튜브 링크가 입력됐습니다.")
                st.warning("페이지를 이동하면 작업이 취소됩니다.")
                result = True

                with st.spinner("영상을 검색 중입니다..."):
                    result: ExecuteResult = app.first_parse_and_store(youtube_link)
                    if result.result is True:
                        st.success("영상 수집을 완료했습니다.")
                    else:
                        st.error(result.message.value)

                if result.result is True:
                    with st.spinner("스크립트를 검색 중입니다..."):
                        result: ExecuteResult = app.second_auto_script_parse(youtube_link)
                        if result.result is True:
                            st.success("스크립트 수집을 완료했습니다.")
                        else:
                            st.error(result.message.value)

                if result.result is True:
                    st.balloons()
                    with st.spinner("곧 페이지 이동이 시작됩니다. 잠시만 기다려주세요!"):
                        import time
                        time.sleep(1)
                        app.cache_clear()
                        app.select_youtube_content_by_url(youtube_link)
                        app.set_page('main')
                        st.rerun()
                elif result.message == ExecuteResultType.DUPLICATE_CONTENT:
                    app.select_youtube_content_by_url(youtube_link)
                    app.set_page('main')
                    st.rerun()

########################################################################################################################


sidebar_top_render()

with st.spinner('지식 모으는중..'):
    all_youtube_contents = app.get_search_youtube_contents()

sidebar_channel_render()
sidebar_setting_render()

if app.page == 'main':
    main_page_render()
elif app.page == 'add':
    add_page_render()




