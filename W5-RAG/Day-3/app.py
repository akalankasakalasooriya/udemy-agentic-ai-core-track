import os
import sys
from pathlib import Path

import gradio as gr

WEEK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WEEK))

from answer import answer_question
from store import LARGE, client, knowledge_base


def format_context(docs):
    blocks = []
    for doc in docs:
        source = doc.metadata.get("source", "")
        path = Path(source)
        try:
            label = str(path.relative_to(knowledge_base))
        except ValueError:
            label = path.name
        blocks.append(f"**{label}**\n\n{doc.page_content}")
    return "\n\n---\n\n".join(blocks) if blocks else "No matching context."


def add_user(message, history):
    message = (message or "").strip()
    history = history or []
    if not message:
        return "", history
    return "", history + [{"role": "user", "content": message}]


def reply(history):
    history = history or []
    if not history or history[-1].get("role") != "user":
        return history, "Ask a question about Insurellm."
    question = history[-1]["content"]
    text, docs = answer_question(question, history[:-1])
    if not isinstance(text, str):
        text = str(text)
    return history + [{"role": "assistant", "content": text}], format_context(docs)


def build_demo():
    with gr.Blocks(title="Insurellm") as demo:
        gr.Markdown("# Insurellm")
        try:
            count = client().get_collection(LARGE).count()
        except Exception:
            count = 0
        if not count:
            gr.Markdown(
                "The Azure embedding store is empty. "
                "Run the last build cell in `1-pipeline.ipynb` first."
            )
        with gr.Row():
            with gr.Column():
                chatbot = gr.Chatbot(label="Conversation", height=520, buttons=["copy"])
                message = gr.Textbox(label="Your question", lines=2)
                send = gr.Button("Send")
                gr.Examples(
                    ["Who is Lancaster?", "What is carllm?"],
                    inputs=message,
                )
            with gr.Column():
                context = gr.Markdown(value="Retrieved context shows up here.")
        send.click(add_user, [message, chatbot], [message, chatbot]).then(
            reply, chatbot, [chatbot, context]
        )
        message.submit(add_user, [message, chatbot], [message, chatbot]).then(
            reply, chatbot, [chatbot, context]
        )
    return demo


demo = build_demo()


def launch():
    user = os.getenv("GRADIO_USER")
    password = os.getenv("GRADIO_PASSWORD")
    auth = (user, password) if user and password else None
    demo.queue()
    demo.launch(auth=auth)


if __name__ == "__main__":
    launch()
