import json
from pathlib import Path

from pydantic import BaseModel, Field

TEST_FILE = Path(__file__).resolve().parent / "tests.jsonl"


class TestQuestion(BaseModel):
    question: str = Field(description="The question to ask the RAG system")
    keywords: list[str] = Field(description="Keywords that must appear in retrieved context")
    reference_answer: str = Field(description="The reference answer for this question")
    category: str = Field(description="Question category")


def load_tests():
    tests = []
    with TEST_FILE.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                tests.append(TestQuestion(**json.loads(line)))
    return tests
