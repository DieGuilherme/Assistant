import streamlit as st
import os
import openai
import time
import hashlib

openai.api_key = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = "asst_mxd6yUB2vmSyJm34UxbtnSd6"

st.set_page_config(page_title="SDR Modernista", layout="centered")
st.title("🤖 SDR Modernista")
st.markdown("Converse com o nosso assistente inteligente.")

# Identificação do usuário
user_id = st.text_input("Identifique-se (nome ou email):", key="user_id")

if user_id:
    # Gera um thread_id único e persistente por usuário
    thread_key = "thread_" + hashlib.sha1(user_id.encode()).hexdigest()
    if thread_key not in st.session_state:
        thread = openai.beta.threads.create()
        st.session_state[thread_key] = thread.id

    thread_id = st.session_state[thread_key]

    # Inicializa histórico visual do chat
    if "history" not in st.session_state:
        st.session_state.history = []

    user_input = st.chat_input("Digite sua mensagem")

    if user_input:
        st.session_state.history.append(("user", user_input))

        with st.spinner("Assistente está pensando..."):
            try:
                # Adiciona mensagem do usuário à thread
                openai.beta.threads.messages.create(
                    thread_id=thread_id,
                    role="user",
                    content=user_input
                )

                # Executa o assistente
                run = openai.beta.threads.runs.create(
                    thread_id=thread_id,
                    assistant_id=ASSISTANT_ID
                )

                # Aguarda execução ser concluída
                while True:
                    run_status = openai.beta.threads.runs.retrieve(
                        thread_id=thread_id,
                        run_id=run.id
                    )
                    if run_status.status == "completed":
                        break
                    elif run_status.status == "failed":
                        raise Exception("A execução do assistente falhou.")
                    time.sleep(1)

                # Recupera todas as mensagens da thread
                messages = openai.beta.threads.messages.list(thread_id=thread_id)

                # DEBUG: Exibe no terminal o histórico da thread
                print("\n[🔍 HISTÓRICO DA THREAD]")
                for msg in reversed(messages.data):
                    print(f"{msg.role}: {msg.content[0].text.value}")

                # Pega a última resposta do assistente
                for msg in reversed(messages.data):
                    if msg.role == "assistant":
                        reply = msg.content[0].text.value
                        break
                else:
                    reply = "⚠️ Nenhuma resposta do assistente."

            except Exception as e:
                reply = f"⚠️ Erro ao conectar com o assistente: {e}"

            st.session_state.history.append(("assistant", reply))

    # Renderiza mensagens no chat
    for role, message in st.session_state.history:
        with st.chat_message(role):
            st.markdown(message)
