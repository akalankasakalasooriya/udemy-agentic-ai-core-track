import os
import sys
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv
from openai import AzureOpenAI

cwd = Path.cwd().resolve()
repo_root = next((p for p in [cwd, *cwd.parents] if (p / ".git").exists()), cwd)
load_dotenv(repo_root / ".env", override=True)

azure = AzureOpenAI(
    api_key=os.getenv("GPT_KEY"),
    api_version=os.getenv("GPT_API_VERSION"),
    azure_endpoint=os.getenv("GPT_ENDPOINT"),
)
azure_model = os.getenv("GPT_MODEL", "gpt-4o")
deployments = []
for name in (azure_model, "gpt-4o-mini", "gpt-4.1"):
    if name not in deployments:
        deployments.append(name)

brochure_root = repo_root / "W1-LLM Engineer" / "Day-4" / "1-company-brochre"
sys.path.insert(0, str(brochure_root))

from src.brochure import brochure_system_prompt, fetch_all_relevant_contents

system_message = (
    "You are a helpful assistant that responds in markdown without code blocks."
)


def shout(text):
    print(f"shout called with {text}")
    return (text or "").upper()


def stream_reply(prompt, deployment):
    prompt = (prompt or "").strip()
    if not prompt:
        yield "Type a message first."
        return

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt},
    ]
    stream = azure.chat.completions.create(
        model=deployment,
        messages=messages,
        stream=True,
        timeout=120.0,
    )
    result = ""
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            result += chunk.choices[0].delta.content
            yield result


def stream_brochure(company_name, url, deployment):
    company_name = (company_name or "").strip()
    url = (url or "").strip()
    if not company_name or not url:
        yield "Enter a company name and a landing page URL."
        return

    yield "Reading the site and picking relevant pages..."
    try:
        contents = fetch_all_relevant_contents(url)
    except Exception as exc:
        yield f"Could not read {url}: {exc}"
        return

    user_prompt = (
        f"You are looking at a company called: {company_name}\n"
        "Here are the contents of its landing page and other relevant pages; "
        "use this information to build a short brochure in markdown without code blocks.\n\n"
        f"{contents}"
    )
    messages = [
        {"role": "system", "content": brochure_system_prompt},
        {"role": "user", "content": user_prompt[:5000]},
    ]
    stream = azure.chat.completions.create(
        model=deployment,
        messages=messages,
        stream=True,
        timeout=120.0,
    )
    result = ""
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            result += chunk.choices[0].delta.content
            yield result


def build_demo():
    with gr.Blocks(title="Gradio") as demo:
        gr.Markdown("# Gradio")
        with gr.Tabs():
            with gr.Tab("Shout"):
                shout_in = gr.Textbox(label="Your message", lines=2)
                shout_out = gr.Textbox(label="Response", lines=2)
                shout_button = gr.Button("Shout")
                gr.Examples(["hello", "howdy"], inputs=shout_in)
                shout_button.click(shout, shout_in, shout_out)
                shout_in.submit(shout, shout_in, shout_out)

            with gr.Tab("Chat"):
                chat_in = gr.Textbox(label="Your message", lines=6)
                chat_model = gr.Dropdown(deployments, value=azure_model, label="Model")
                chat_out = gr.Markdown(label="Response")
                chat_button = gr.Button("Send")
                gr.Examples(
                    [
                        ["Explain the Transformer architecture to a layperson", azure_model],
                        [
                            "Explain the Transformer architecture to an aspiring AI engineer",
                            "gpt-4o-mini",
                        ],
                    ],
                    inputs=[chat_in, chat_model],
                )
                chat_button.click(stream_reply, [chat_in, chat_model], chat_out)
                chat_in.submit(stream_reply, [chat_in, chat_model], chat_out)

            with gr.Tab("Brochure"):
                company = gr.Textbox(label="Company name")
                url = gr.Textbox(label="Landing page URL including http:// or https://")
                brochure_model = gr.Dropdown(deployments, value=azure_model, label="Model")
                brochure = gr.Markdown(label="Brochure")
                brochure_button = gr.Button("Create brochure")
                gr.Examples(
                    [
                        ["Hugging Face", "https://huggingface.co", azure_model],
                        ["Edward Donner", "https://edwarddonner.com", "gpt-4.1"],
                    ],
                    inputs=[company, url, brochure_model],
                )
                brochure_button.click(
                    stream_brochure, [company, url, brochure_model], brochure
                )
                url.submit(stream_brochure, [company, url, brochure_model], brochure)
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
