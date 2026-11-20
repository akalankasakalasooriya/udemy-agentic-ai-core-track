# Agentic AI core track

Course notebooks. Use the `udemy` conda env.

## Weeks

- `W1-LLM Engineer` — Azure chat, a web summarizer, tokens, a company brochure
- `W2-Build Multi Model Chatbots` — Azure deployments behind Gradio
- `W3-Open Source Models` — Hugging Face tokenizers and small local models
- `W4-Model Evaluation` — a Connect Four check, a small leaderboard, Python to C++
- `W5-RAG` — Insurellm notes, a local Chroma store, retrieval and answer scores

## Week 5

Open the notebooks in order. The last cell of each notebook opens the Gradio page.

| Day | Notebook | What it does |
|---|---|---|
| 1 | `W5-RAG/Day-1/1-dictionary.ipynb` | Match question words to employee and product notes, then chat |
| 2 | `W5-RAG/Day-2/1-vectors.ipynb` | Chunk, embed with `all-MiniLM-L6-v2`, plot the vectors |
| 3 | `W5-RAG/Day-3/1-pipeline.ipynb` | Retrieve from that store and answer. Builds the Azure embedding store used by `Day-3/app.py` |
| 4 | `W5-RAG/Day-4/1-eval.ipynb` | Score retrieval, then one answer. `Day-4/app.py` runs the full scoreboard |

Chat uses the Azure deployment `gpt-4o-mini`. Cloud embeddings use `text-embedding-3-large`. Day 2 keeps the small Hugging Face model. Chroma files live in `W5-RAG/vector_db` and stay out of git.

```bash
conda activate udemy
```

Keys in the repo root `.env`:

```
GPT_KEY
GPT_ENDPOINT
GPT_API_VERSION
```

### Versions

- openai 3.57.0
- langchain-openai 1.8.5
- chromadb 1.5.9
- langchain-chroma 1.1.0
- langchain-huggingface 1.2.3
- langchain-text-splitters 1.1.3
- sentence-transformers 6.3.0
- scikit-learn 1.9.1
- plotly 7.1.0
- gradio 6.29.0
