import streamlit as st
import os
import openai

# Configurar chave da API
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="SDR Modernista", layout="centered")

st.title("🤖 SDR Modernista")
st.markdown("Converse com o nosso assistente inteligente.")

# Identificação do usuário
user_id = st.text_input("Identifique-se (nome ou email):", key="user_id")

if user_id:
    # Inicializar histórico por usuário
    if "history" not in st.session_state:
        st.session_state.history = []

    # Campo de entrada do usuário
    user_input = st.chat_input("Digite sua mensagem")

    if user_input:
        # Mostrar entrada do usuário
        st.session_state.history.append(("user", user_input))

        # Chamada ao assistente (com fallback simulada)
        with st.spinner("Assistente está digitando..."):
            try:
                response = openai.beta.assistants.messages.create(
                    assistant_id="asst_mxd6yUB2vmSyJm34UxbtnSd6",
                    thread={"messages": [{"role": "user", "content": user_input}]}
                )
                reply = response.message['content'] if hasattr(response, 'message') else "Resposta simulada do assistente."
            except Exception:
                reply = "⚠️ Erro ao conectar com o assistente. Verifique a API Key."

            st.session_state.history.append(("assistant", reply))

    # Exibir histórico de mensagens
    for role, message in st.session_state.history:
        with st.chat_message(role):
            st.markdown(message)
