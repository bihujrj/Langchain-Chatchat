# from flask import Flask
# app = Flask(__name__)
#
# # 装饰器的作用是将路由映射到视图函数index
# @app.route("/")
# def hello():
#     print('xxxx')
#     return "hello"
#
# app.run(host='0.0.0.0',port=5000)
# # app.run()

import streamlit as st

from chat_common_settins import dialogue_page_comm
from eepower_settings import dialogue_page_eepower
from webui_pages.utils import *
from streamlit_option_menu import option_menu
from webui_pages.dialogue.dialogue import dialogue_page, chat_box
from webui_pages.knowledge_base.knowledge_base import knowledge_base_page
import os
import sys
from configs import VERSION
from server.utils import api_address


api = ApiRequest(base_url=api_address())

if __name__ == "__main__":
    is_lite = "lite" in sys.argv

    st.set_page_config(
        "飞跃留学问答",
        os.path.join("../img", "ltxy_icon.png"),
        initial_sidebar_state="collapsed",
        # menu_items={
        #     'Get Help': 'https://github.com/chatchat-space/Langchain-Chatchat',
        #     'Report a bug': "https://github.com/chatchat-space/Langchain-Chatchat/issues",
        #     'About': f"""欢迎使用 Langchain-Chatchat WebUI {VERSION}！"""
        # },
        layout="wide",
    )
    #st.set_page_config(layout="wide")
    #st.sidebar.empty()
    dialogue_page_comm(api=api, is_lite=is_lite,selected_kb='abroad')

    # pages = {
    #     "对话": {
    #         "icon": "chat",
    #         "func": dialogue_page_eepower,
    #     },
    #     # "知识库管理": {
    #     #     "icon": "hdd-stack",
    #     #     "func": knowledge_base_page,
    #     # },
    # }

    # with st.sidebar:
    #     # st.image(
    #     #     os.path.join(
    #     #         "img",
    #     #         "logo-long-chatchat-trans-v2.png"
    #     #     ),
    #     #     use_column_width=True
    #     # )
    #     # st.caption(
    #     #     f"""<p align="right">当前版本：{VERSION}</p>""",
    #     #     unsafe_allow_html=True,
    #     # )
    #     options = list(pages)
    #     icons = [x["icon"] for x in pages.values()]
    #
    #     default_index = 0
    #     selected_page = option_menu(
    #         "",
    #         options=options,
    #         icons=icons,
    #         # menu_icon="chat-quote",
    #         default_index=default_index,
    #     )
    #
    # if selected_page in pages:
    #     pages[selected_page]["func"](api=api, is_lite=is_lite)
