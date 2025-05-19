import streamlit as st
import os
import openai

# A API Key já será lida do ambiente (Streamlit Cloud Secrets)
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="SDR Modernista", layout="centered")

st.title("🤖 SDR Modernista")
st.markdown("Converse com o nosso assistente inteligente.")

user_id = st.text_input("Identifique-se (nome ou email):", key="user_id")

if user_id:
    if "history" not in st.session_state:
        st.session_state.history = []

    user_input = st.chat_input("Digite sua mensagem")

    if user_input:
        st.session_state.history.append(("user", user_input))

        with st.spinner("Assistente está digitando..."):
            try:
                response = openai.beta.assistants.messages.create(
                    assistant_id="asst_mxd6yUB2vmSyJm34UxbtnSd6",
                    thread={"messages": [{"role": "user", "content": user_input}]}
                )
                reply = response.message['content'] if hasattr(response, 'message') else "Resposta simulada do assistente."
            except Exception as e:
                reply = f"⚠️ Erro ao conectar com o assistente: {e}"

            st.session_state.history.append(("assistant", reply))

    for role, message in st.session_state.history:
        with st.chat_message(role):
            st.markdown(message)
