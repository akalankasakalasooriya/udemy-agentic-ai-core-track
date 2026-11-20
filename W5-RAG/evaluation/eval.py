import math
import os
import sys
from pathlib import Path

from openai import AzureOpenAI
from pydantic import BaseModel, Field

WEEK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WEEK))

from answer import answer_question, fetch_context
from evaluation.test import load_tests
from store import CHAT_MODEL

client = AzureOpenAI(
    api_key=os.getenv("GPT_KEY"),
    api_version=os.getenv("GPT_API_VERSION"),
    azure_endpoint=os.getenv("GPT_ENDPOINT"),
)


class RetrievalEval(BaseModel):
    mrr: float
    ndcg: float
    keywords_found: int
    total_keywords: int
    keyword_coverage: float


class AnswerEval(BaseModel):
    feedback: str = Field(description="Short comparison of the generated answer with the reference.")
    accuracy: float = Field(
        description="1 if any fact is wrong, 3 if acceptable, 5 only if it matches the reference."
    )
    completeness: float = Field(
        description="1 if key facts are missing, 5 only if every fact from the reference is included."
    )
    relevance: float = Field(
        description="1 if off topic, 5 only if it answers the question and adds nothing else."
    )


def calculate_mrr(keyword, docs):
    keyword = keyword.lower()
    for rank, doc in enumerate(docs, start=1):
        if keyword in doc.page_content.lower():
            return 1.0 / rank
    return 0.0


def calculate_dcg(relevances, k):
    total = 0.0
    for index, score in enumerate(relevances[:k]):
        total += score / math.log2(index + 2)
    return total


def calculate_ndcg(keyword, docs, k=10):
    keyword = keyword.lower()
    relevances = [1 if keyword in doc.page_content.lower() else 0 for doc in docs[:k]]
    ideal = calculate_dcg(sorted(relevances, reverse=True), k)
    if not ideal:
        return 0.0
    return calculate_dcg(relevances, k) / ideal


def evaluate_retrieval(test, k=10):
    docs = fetch_context(test.question)
    mrr_scores = [calculate_mrr(keyword, docs) for keyword in test.keywords]
    ndcg_scores = [calculate_ndcg(keyword, docs, k) for keyword in test.keywords]
    found = sum(1 for score in mrr_scores if score > 0)
    total = len(test.keywords)
    coverage = (found / total * 100) if total else 0.0
    return RetrievalEval(
        mrr=sum(mrr_scores) / len(mrr_scores) if mrr_scores else 0.0,
        ndcg=sum(ndcg_scores) / len(ndcg_scores) if ndcg_scores else 0.0,
        keywords_found=found,
        total_keywords=total,
        keyword_coverage=coverage,
    )


def evaluate_answer(test):
    generated, docs = answer_question(test.question)
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert evaluator assessing the quality of answers. "
                "Compare the generated answer with the reference answer. "
                "Only give 5/5 scores for perfect answers."
            ),
        },
        {
            "role": "user",
            "content": f"""Question:
{test.question}

Generated Answer:
{generated}

Reference Answer:
{test.reference_answer}

Score the generated answer from 1 (very poor) to 5 (ideal):
1. Accuracy: how factually correct it is compared with the reference. If any fact is wrong, accuracy is 1.
2. Completeness: how much of the reference answer is covered. Score 5 only if every fact is included.
3. Relevance: how directly it answers the question. Score 5 only if it adds nothing extra.
""",
        },
    ]
    response = client.beta.chat.completions.parse(
        model=CHAT_MODEL,
        messages=messages,
        response_format=AnswerEval,
        temperature=0,
        timeout=120.0,
    )
    return response.choices[0].message.parsed, generated, docs
