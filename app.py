import streamlit as st
import os
import openai
import time

openai.api_key = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = "asst_mxd6yUB2vmSyJm34UxbtnSd6"

st.set_page_config(page_title="SDR Modernista", layout="centered")
st.title("🤖 SDR Modernista")
st.markdown("Converse com o nosso assistente inteligente.")

user_id = st.text_input("Identifique-se (nome ou email):", key="user_id")

if user_id:
    if "history" not in st.session_state:
        st.session_state.history = []
    if "thread_id" not in st.session_state:
        # Cria uma thread única por usuário/sessão
        thread = openai.beta.threads.create()
        st.session_state.thread_id = thread.id

    user_input = st.chat_input("Digite sua mensagem")

    if user_input:
        st.session_state.history.append(("user", user_input))

        with st.spinner("Assistente está pensando..."):
            try:
                # Adiciona mensagem do usuário à thread
                openai.beta.threads.messages.create(
                    thread_id=st.session_state.thread_id,
                    role="user",
                    content=user_input
                )

                # Executa o assistente
                run = openai.beta.threads.runs.create(
                    thread_id=st.session_state.thread_id,
                    assistant_id=ASSISTANT_ID
                )

                # Aguarda finalização
                while True:
                    run_status = openai.beta.threads.runs.retrieve(
                        thread_id=st.session_state.thread_id,
                        run_id=run.id
                    )
                    if run_status.status == "completed":
                        break
                    elif run_status.status == "failed":
                        raise Exception("A execução falhou.")
                    time.sleep(1)

                # Busca últimas mensagens
                messages = openai.beta.threads.messages.list(
                    thread_id=st.session_state.thread_id
                )

                # Recupera a última resposta do assistente
                for msg in reversed(messages.data):
                    if msg.role == "assistant":
                        reply = msg.content[0].text.value
                        break
                else:
                    reply = "⚠️ Nenhuma resposta recebida."

            except Exception as e:
                reply = f"⚠️ Erro ao conectar com o assistente: {e}"

            st.session_state.history.append(("assistant", reply))

    for role, message in st.session_state.history:
        with st.chat_message(role):
            st.markdown(message)
