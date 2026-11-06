import io
import os
import subprocess
import sys
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from openai import AzureOpenAI

cwd = Path.cwd().resolve()
repo_root = next((p for p in [cwd, *cwd.parents] if (p / ".git").exists()), cwd)
load_dotenv(repo_root / ".env", override=True)

day_dir = repo_root / "W4-Model Evaluation" / "Day-4"
day3 = repo_root / "W4-Model Evaluation" / "Day-3"
sys.path.insert(0, str(day3))

from system_info import default_commands, retrieve_system_info

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

hf_models = [
    "Qwen/Qwen2.5-Coder-7B-Instruct",
    "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct",
]
models = deployments + hf_models

system_info = retrieve_system_info()
compile_command, run_command = default_commands(day_dir)

system_prompt = """
Your task is to convert Python code into high performance C++ code.
Respond only with C++ code. Do not provide any explanation other than occasional comments.
The C++ response needs to produce an identical output in the fastest possible time.
"""

pi = """
import time

def calculate(iterations, param1, param2):
    result = 1.0
    for i in range(1, iterations+1):
        j = i * param1 - param2
        result -= (1/j)
        j = i * param1 + param2
        result += (1/j)
    return result

start_time = time.time()
result = calculate(200_000_000, 4, 1) * 4
end_time = time.time()

print(f"Result: {result:.12f}")
print(f"Execution Time: {(end_time - start_time):.6f} seconds")
"""


def cpp_only(text):
    text = (text or "").strip()
    if "```" not in text:
        return text + "\n"
    block = text.split("```", 2)[1]
    if block.startswith("cpp") or block.startswith("c++"):
        block = block.split("\n", 1)[-1]
    return block.strip() + "\n"


def messages_for(python):
    user = f"""
Port this Python code to C++ with the fastest possible implementation that produces identical output in the least time.
The system information is:
{system_info}
Your response will be written to a file called main.cpp and then compiled and executed; the compilation command is:
{compile_command}
Respond only with C++ code.
Python code to port:

```python
{python}
```
"""
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user},
    ]


def chat(model, messages):
    if model in hf_models:
        hf = InferenceClient(token=os.getenv("HF_TOKEN"))
        response = hf.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=4000,
        )
    else:
        response = azure.chat.completions.create(
            model=model,
            messages=messages,
            timeout=120.0,
        )
    return response.choices[0].message.content


def port(model, python):
    try:
        reply = chat(model, messages_for(python))
    except Exception as exc:
        return f"// {model} failed: {exc}\n"
    return cpp_only(reply)


def run_python(code):
    buffer = io.StringIO()
    old = sys.stdout
    sys.stdout = buffer
    try:
        exec(code, {"__builtins__": __builtins__})
        output = buffer.getvalue()
    except Exception as exc:
        output = f"{type(exc).__name__}: {exc}"
    finally:
        sys.stdout = old
    return output


def compile_and_run(cpp):
    if not compile_command:
        return (
            "No C++ compiler on PATH. "
            "https://www.programiz.com/cpp-programming/online-compiler/"
        )
    (day_dir / "main.cpp").write_text(cpp_only(cpp), encoding="utf-8")
    try:
        subprocess.run(
            compile_command,
            check=True,
            text=True,
            capture_output=True,
            timeout=120,
        )
        result = subprocess.run(
            run_command,
            check=True,
            text=True,
            capture_output=True,
            timeout=60,
        )
    except subprocess.CalledProcessError as exc:
        return exc.stderr or str(exc)
    except subprocess.TimeoutExpired:
        return "The C++ program ran longer than 60 seconds."
    return result.stdout


def build_demo():
    with gr.Blocks(title="Python to C++") as demo:
        gr.Markdown("# Python to C++")
        with gr.Row():
            python = gr.Textbox(label="Python", lines=24, value=pi)
            cpp = gr.Textbox(label="C++", lines=24)
        model = gr.Dropdown(models, value=models[0], label="Model")
        with gr.Row():
            convert = gr.Button("Convert")
            run_py = gr.Button("Run Python")
            run_cpp = gr.Button("Compile and run")
        python_out = gr.Textbox(label="Python stdout", lines=4)
        cpp_out = gr.Textbox(label="C++ stdout", lines=4)
        convert.click(port, [model, python], cpp)
        run_py.click(run_python, python, python_out)
        run_cpp.click(compile_and_run, cpp, cpp_out)
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
