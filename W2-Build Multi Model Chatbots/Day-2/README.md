# Gradio UI

`app.py` is the Day 2 page. It opens one local window with three tabs:

- **Shout** uppercases the text you type.
- **Chat** streams a markdown answer from Azure OpenAI.
- **Brochure** reads a company site with the Week 1 scraper, then streams a brochure from Azure OpenAI.

Chat and Brochure can use the Azure deployments `gpt-4o` (`GPT_MODEL`), `gpt-4o-mini`, and `gpt-4.1`.

## Run

Activate the conda env you use for this course, then from the repo root:

```bash
pip install gradio requests beautifulsoup4 python-dotenv openai
python "W2-Build Multi Model Chatbots/Day-2/app.py"
```

Gradio prints a local URL, usually http://127.0.0.1:7860. Open that in a browser. Stop the app with Ctrl+C.

You can also open `1-gradio.ipynb` and run the last cell. That calls the same `launch()`.

## Settings

These keys live in the repo root `.env`:

```
GPT_KEY
GPT_ENDPOINT
GPT_API_VERSION
GPT_MODEL
```

Optional sign-in. If both are set, the page asks for them before it opens:

```
GRADIO_USER
GRADIO_PASSWORD
```
