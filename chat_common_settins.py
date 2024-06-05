from webui_pages.dialogue.dialogue import chat_box, parse_command, get_messages_history
import streamlit as st
from webui_pages.utils import *
from streamlit_chatbox import *
from streamlit_modal import Modal
from datetime import datetime
from configs import (TEMPERATURE, HISTORY_LEN, PROMPT_TEMPLATES, LLM_MODELS,
                     DEFAULT_KNOWLEDGE_BASE, DEFAULT_SEARCH_ENGINE, SUPPORT_AGENT_MODEL)
from server.knowledge_base.utils import LOADER_DICT
import uuid

def dialogue_page_comm(api: ApiRequest, is_lite: bool = False,selected_kb='security'):
    st.session_state.setdefault("conversation_ids", {})
    st.session_state["conversation_ids"].setdefault(chat_box.cur_chat_name, uuid.uuid4().hex)
    st.session_state.setdefault("file_chat_id", None)
    if not chat_box.chat_inited:
        st.toast(
            f"欢迎使用,您可以开始提问了."
        )
        chat_box.init_session()

    cols = st.columns(1)
    export_btn = cols[0]
    # if cols[1].button(
    #         "清空对话",
    #         use_container_width=True,
    # ):
    #     chat_box.reset_history()
    #     st.rerun()

    now = datetime.now()
    export_btn.download_button(
        "导出记录",
        "".join(chat_box.export2md()),
        file_name=f"{now:%Y-%m-%d %H.%M}_对话记录.md",
        mime="text/markdown",
        use_container_width=True,
    )
    st.sidebar.empty()


    # 弹出自定义命令帮助信息
    modal = Modal("自定义命令", key="cmd_help", max_width="1000")
    if modal.is_open():
        with modal.container():
            cmds = [x for x in parse_command.__doc__.split("\n") if x.strip().startswith("/")]
            st.write("\n\n".join(cmds))

    conversation_name='default'
    chat_box.use_chat_name(conversation_name)
    running_models = list(api.list_running_models())
    available_models = []
    config_models = api.list_config_models()
    if not is_lite:
        for k, v in config_models.get("local", {}).items():
            if (v.get("model_path_exists")
                    and k not in running_models):
                available_models.append(k)
    for k, v in config_models.get("online", {}).items():
        if not v.get("provider") and k not in running_models and k in LLM_MODELS:
            available_models.append(k)
    llm_model='chatglm3-6b'
    if (st.session_state.get("prev_llm_model") != llm_model
            and not is_lite
            and not llm_model in config_models.get("online", {})
            and not llm_model in config_models.get("langchain", {})
            and llm_model not in running_models):
        with st.spinner(f"正在加载模型： {llm_model}，请勿进行操作或刷新页面"):
            prev_model = st.session_state.get("prev_llm_model")
            r = api.change_llm_model(prev_model, llm_model)
            if msg := check_error_msg(r):
                st.error(msg)
            elif msg := check_success_msg(r):
                st.success(msg)
                st.session_state["prev_llm_model"] = llm_model
    prompt_template_name='default'
    temperature=0.7
    history_len = 3

    # selected_kb='security'
    kb_top_k = 3
    score_threshold = 1.0


    chat_box.output_messages()

    chat_input_placeholder = "请输入对话内容，换行请使用Shift+Enter "

    def on_feedback(
            feedback,
            message_id: str = "",
            history_index: int = -1,
    ):
        reason = feedback["text"]
        score_int = chat_box.set_feedback(feedback=feedback, history_index=history_index)
        api.chat_feedback(message_id=message_id,
                          score=score_int,
                          reason=reason)
        st.session_state["need_rerun"] = True

    feedback_kwargs = {
        "feedback_type": "thumbs",
        "optional_text_label": "欢迎反馈您打分的理由",
    }

    if prompt := st.chat_input(chat_input_placeholder, key="prompt"):
        if parse_command(text=prompt, modal=modal):  # 用户输入自定义命令
            st.rerun()
        else:
            history = get_messages_history(history_len)

            chat_box.user_say(prompt)

            chat_box.ai_say([
                f"正在查询知识库 `{selected_kb}` ...",
                Markdown("...", in_expander=True, title="知识库匹配结果", state="complete"),
            ])
            text = ""
            for d in api.knowledge_base_chat(prompt,
                                             knowledge_base_name=selected_kb,
                                             top_k=kb_top_k,
                                             score_threshold=score_threshold,
                                             history=history,
                                             model=llm_model,
                                             prompt_name=prompt_template_name,
                                             temperature=temperature):
                if error_msg := check_error_msg(d):  # check whether error occured
                    st.error(error_msg)
                elif chunk := d.get("answer"):
                    text += chunk
                    chat_box.update_msg(text, element_index=0)
            chat_box.update_msg(text, element_index=0, streaming=False)
            chat_box.update_msg("\n\n".join(d.get("docs", [])), element_index=1, streaming=False)


    if st.session_state.get("need_rerun"):
        st.session_state["need_rerun"] = False
        st.rerun()




