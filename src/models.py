from __future__ import annotations

from dataclasses import dataclass


QUESTION_TYPES = ("single", "judge", "blank")
DIFFICULTIES = ("基础", "中等", "提高")


def normalize_text(value: str) -> str:
    return str(value).strip()


def normalize_judge_answer(value: str) -> str:
    text = normalize_text(value).casefold()
    true_values = {"对", "正确", "true", "t", "yes", "y", "1"}
    false_values = {"错", "错误", "false", "f", "no", "n", "0"}
    if text in true_values:
        return "对"
    if text in false_values:
        return "错"
    return normalize_text(value)


@dataclass
class Question:
    chapter: str
    question_type: str
    difficulty: str
    stem: str
    options: list[str]
    answer: str
    explanation: str
    id: int | None = None

    def __post_init__(self) -> None:
        if self.question_type not in QUESTION_TYPES:
            raise ValueError(f"Unsupported question type: {self.question_type}")
        self.chapter = normalize_text(self.chapter)
        self.difficulty = normalize_text(self.difficulty) or "基础"
        self.stem = normalize_text(self.stem)
        self.answer = normalize_text(self.answer)
        self.explanation = normalize_text(self.explanation)
        self.options = [normalize_text(option) for option in self.options if normalize_text(option)]

    def normalized_answer(self, value: str) -> str:
        if self.question_type == "single":
            return normalize_text(value).upper()
        if self.question_type == "judge":
            return normalize_judge_answer(value)
        return normalize_text(value).casefold()

    def check_answer(self, user_answer: str) -> bool:
        return self.normalized_answer(user_answer) == self.normalized_answer(self.answer)

    def __str__(self) -> str:
        prefix = f"[{self.chapter}｜{self.difficulty}]"
        return f"{prefix} {self.stem}"


@dataclass
class AnswerDetail:
    question: Question
    user_answer: str
    is_correct: bool


@dataclass
class StudyRecord:
    id: int
    quiz_time: str
    chapter_scope: str
    score: int
    total: int
    correct_count: int

    @property
    def accuracy(self) -> float:
        if self.total == 0:
            return 0.0
        return self.correct_count / self.total
