import os
import sys
from collections import defaultdict
from pathlib import Path

import gradio as gr
import pandas as pd

WEEK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WEEK))

from evaluation.eval import evaluate_answer, evaluate_retrieval
from evaluation.test import load_tests

MRR_GREEN = 0.9
MRR_AMBER = 0.75
NDCG_GREEN = 0.9
NDCG_AMBER = 0.75
COVERAGE_GREEN = 90.0
COVERAGE_AMBER = 75.0
ANSWER_GREEN = 4.5
ANSWER_AMBER = 4.0


def paint(value, green, amber):
    if value >= green:
        return "green"
    if value >= amber:
        return "orange"
    return "red"


def metric_line(label, value, green, amber, text):
    color = paint(value, green, amber)
    return (
        f"<div style='margin:8px 0;padding:10px;border-left:5px solid {color}'>"
        f"<div>{label}</div><div style='font-size:22px;color:{color}'>{text}</div></div>"
    )


def category_frame(groups, column):
    rows = []
    for name, values in groups.items():
        rows.append({
            "category": name,
            column: sum(values) / len(values),
            "count": len(values),
        })
    return pd.DataFrame(rows)


def run_retrieval(progress=gr.Progress()):
    tests = load_tests()
    total_mrr = 0.0
    total_ndcg = 0.0
    total_coverage = 0.0
    groups = defaultdict(list)
    for index, test in enumerate(tests, start=1):
        result = evaluate_retrieval(test)
        total_mrr += result.mrr
        total_ndcg += result.ndcg
        total_coverage += result.keyword_coverage
        groups[test.category].append(result.mrr)
        progress(index / len(tests), desc=f"Retrieval {index} / {len(tests)}")
    count = len(tests)
    html = (
        metric_line("MRR", total_mrr / count, MRR_GREEN, MRR_AMBER, f"{total_mrr / count:.4f}")
        + metric_line("nDCG", total_ndcg / count, NDCG_GREEN, NDCG_AMBER, f"{total_ndcg / count:.4f}")
        + metric_line(
            "Keyword coverage",
            total_coverage / count,
            COVERAGE_GREEN,
            COVERAGE_AMBER,
            f"{total_coverage / count:.1f}%",
        )
    )
    return html, category_frame(groups, "mrr")


def run_answers(progress=gr.Progress()):
    tests = load_tests()
    totals = {"accuracy": 0.0, "completeness": 0.0, "relevance": 0.0}
    groups = defaultdict(list)
    for index, test in enumerate(tests, start=1):
        result, _, _ = evaluate_answer(test)
        totals["accuracy"] += result.accuracy
        totals["completeness"] += result.completeness
        totals["relevance"] += result.relevance
        groups[test.category].append(result.accuracy)
        progress(index / len(tests), desc=f"Answers {index} / {len(tests)}")
    count = len(tests)
    html = "".join(
        metric_line(name, totals[name] / count, ANSWER_GREEN, ANSWER_AMBER, f"{totals[name] / count:.2f}/5")
        for name in ("accuracy", "completeness", "relevance")
    )
    return html, category_frame(groups, "accuracy")


def build_demo():
    with gr.Blocks(title="RAG evaluation") as demo:
        gr.Markdown("# RAG evaluation")
        gr.Markdown(
            "Green starts at 0.9 for MRR and nDCG, and 4.5 for an answer score. "
            "Amber starts at 0.75 and 4.0."
        )
        gr.Markdown("## Retrieval")
        retrieval_button = gr.Button("Run retrieval")
        retrieval_html = gr.HTML()
        retrieval_table = gr.Dataframe(label="Average MRR by category")
        retrieval_button.click(run_retrieval, outputs=[retrieval_html, retrieval_table])

        gr.Markdown("## Answers")
        answer_button = gr.Button("Run answers")
        answer_html = gr.HTML()
        answer_table = gr.Dataframe(label="Average accuracy by category")
        answer_button.click(run_answers, outputs=[answer_html, answer_table])
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
