
import streamlit as st
import os
import openai
import time
from datetime import datetime
from supabase import create_client, Client

# --- Supabase config (via secrets ou fallback env/local) ---
SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL"))
SUPABASE_KEY = st.secrets.get("SUPABASE_SERVICE_ROLE_KEY", os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- OpenAI config ---
openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
ASSISTANT_ID = "asst_mxd6yUB2vmSyJm34UxbtnSd6"

st.set_page_config(page_title="SDR Modernista", layout="centered")
st.title("🤖 SDR Modernista")
st.markdown("Converse com o nosso assistente inteligente.")

# --- Identificação ---
user_id = st.text_input("Identifique-se (nome ou email):", key="user_id")


# --- Utilidades Supabase ---
def get_or_create_thread(user_id):
    result = supabase.table("messages").select("thread_id").eq("user_id", user_id).limit(1).execute()
    if result.data:
        return result.data[0]["thread_id"]
    thread = openai.beta.threads.create()
    return thread.id


def save_message(user_id, thread_id, role, content):
    supabase.table("messages").insert({
        "user_id": user_id,
        "thread_id": thread_id,
        "role": role,
        "content": content,
        "created_at": datetime.utcnow().isoformat()
    }).execute()


def load_history(user_id):
    result = supabase.table("messages").select("*").eq("user_id", user_id).order("created_at").execute()
    return result.data if result.data else []


# --- Execução principal ---
if user_id:
    thread_id = get_or_create_thread(user_id)

    if "history" not in st.session_state:
        st.session_state.history = []
        for msg in load_history(user_id):
            st.session_state.history.append((msg["role"], msg["content"]))

    user_input = st.chat_input("Digite sua mensagem")

    if user_input:
        st.session_state.history.append(("user", user_input))
        save_message(user_id, thread_id, "user", user_input)

        with st.spinner("Assistente está pensando..."):
            try:
                openai.beta.threads.messages.create(
                    thread_id=thread_id,
                    role="user",
                    content=user_input
                )

                run = openai.beta.threads.runs.create(
                    thread_id=thread_id,
                    assistant_id=ASSISTANT_ID
                )

                while True:
                    status = openai.beta.threads.runs.retrieve(
                        thread_id=thread_id,
                        run_id=run.id
                    )
                    if status.status == "completed":
                        break
                    elif status.status == "failed":
                        raise Exception("A execução falhou.")
                    time.sleep(1)

                messages = openai.beta.threads.messages.list(thread_id=thread_id)

                for msg in reversed(messages.data):
                    if msg.role == "assistant":
                        reply = msg.content[0].text.value
                        break
                else:
                    reply = "⚠️ Nenhuma resposta recebida."

            except Exception as e:
                reply = f"⚠️ Erro ao conectar com o assistente: {e}"

            st.session_state.history.append(("assistant", reply))
            save_message(user_id, thread_id, "assistant", reply)

    # --- Render histórico ---
    for role, message in st.session_state.history:
        with st.chat_message(role):
            st.markdown(message)
