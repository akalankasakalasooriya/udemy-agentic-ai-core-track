# Choosing an LLM and Benchmarks: Important Notes

`1-connect-four.ipynb` runs five Connect Four boards against the Azure deployments `gpt-4o`, `gpt-4o-mini`, and `gpt-4.1`, then ranks them by score.

## Choosing a model

- Parameter count is not the only choice. Chinchilla scaling says that for a fixed training budget, a smaller model trained on more data can beat a larger model trained on less.
- As a rough rule, compute-optimal training uses about 20 training tokens per parameter.
- Check size, training data, cost, latency, and context window together.

## Benchmarks in the lecture

- **GPQA**: graduate-level science questions.
- **MMLU-Pro**: a harder version of MMLU with more answer options and more reasoning.
- **HLE (Humanity's Last Exam)**: very hard questions written to stay ahead of current models.

## Why benchmarks fail

- **Training data contamination**: a benchmark's questions or answers leak into training data, so the score measures memory.
- **Overfitting**: teams tune models toward a known test, and the score stops predicting real work.
- **Not consistently applied**: prompts, few-shot examples, and grading differ between reports, so scores are not comparable.
- **Too narrow in scope**: a test covers one skill, not the whole job.
- **Hard to measure nuanced reasoning**: multiple-choice or exact-match grading misses partly correct or well-argued answers.
- **Saturation**: top models score near the ceiling, so the test no longer separates them.

## Rules for our Connect Four benchmark

- The five positions have one correct column each. The answer key was checked by a script, so every position has exactly one correct column.
- The `choose the win` position has a block and a win available. The win is the correct reply.
- Scores come from 5 positions only. Treat the ranking as a rough signal, not a final verdict.
- Do not tune the prompt on these exact boards and then report the result as a benchmark score. That is the overfitting problem above.

## Settings

These keys live in the repo root `.env`:

```
GPT_KEY
GPT_ENDPOINT
GPT_API_VERSION
GPT_MODEL
```
