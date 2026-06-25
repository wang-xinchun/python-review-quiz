from __future__ import annotations

import random

from .models import AnswerDetail, Question
from .question_bank import get_question, list_questions


class QuizSession:
    def __init__(self, questions: list[Question], chapter_scope: str) -> None:
        self.questions = questions
        self.chapter_scope = chapter_scope

    @property
    def total(self) -> int:
        return len(self.questions)

    def grade(self, answers: dict[int, str]) -> list[AnswerDetail]:
        details: list[AnswerDetail] = []
        for question in self.questions:
            if question.id is None:
                continue
            user_answer = answers.get(question.id, "")
            details.append(
                AnswerDetail(
                    question=question,
                    user_answer=user_answer,
                    is_correct=question.check_answer(user_answer),
                )
            )
        return details


def build_quiz(chapter: str, quiz_size: int) -> QuizSession:
    questions = list_questions(chapter=chapter if chapter != "全部章节" else None)
    if not questions:
        return QuizSession([], chapter)
    selected_count = min(max(1, int(quiz_size)), len(questions))
    return QuizSession(random.sample(questions, selected_count), chapter)


def build_quiz_from_ids(question_ids: list[int], chapter_scope: str = "错题回练") -> QuizSession:
    questions = [question for question_id in question_ids if (question := get_question(question_id))]
    return QuizSession(questions, chapter_scope)


def calculate_score(details: list[AnswerDetail]) -> tuple[int, int, int]:
    total = len(details)
    correct_count = sum(1 for detail in details if detail.is_correct)
    score = round(correct_count / total * 100) if total else 0
    return score, total, correct_count
