from __future__ import annotations

from pathlib import Path

from .config import DB_PATH
from .question_bank import get_connection


def get_overview(db_path: Path = DB_PATH) -> dict:
    with get_connection(db_path) as connection:
        question_count = connection.execute("SELECT COUNT(*) AS total FROM questions").fetchone()["total"]
        chapter_count = connection.execute("SELECT COUNT(DISTINCT chapter) AS total FROM questions").fetchone()["total"]
        quiz_count = connection.execute("SELECT COUNT(*) AS total FROM quiz_records").fetchone()["total"]
        answer_row = connection.execute(
            """
            SELECT
                COUNT(*) AS total_answers,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) AS correct_answers,
                SUM(CASE WHEN is_correct = 0 THEN 1 ELSE 0 END) AS wrong_answers
            FROM answer_records
            """
        ).fetchone()
    total_answers = int(answer_row["total_answers"] or 0)
    correct_answers = int(answer_row["correct_answers"] or 0)
    avg_accuracy = correct_answers / total_answers if total_answers else 0.0
    return {
        "question_count": int(question_count),
        "chapter_count": int(chapter_count),
        "quiz_count": int(quiz_count),
        "wrong_count": int(answer_row["wrong_answers"] or 0),
        "avg_accuracy": avg_accuracy,
    }


def question_counts_by_chapter(db_path: Path = DB_PATH) -> list[dict]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT chapter, COUNT(*) AS question_count
            FROM questions
            GROUP BY chapter
            ORDER BY chapter ASC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def chapter_accuracy(db_path: Path = DB_PATH) -> list[dict]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT
                questions.chapter,
                COUNT(answer_records.id) AS total,
                SUM(CASE WHEN answer_records.is_correct = 1 THEN 1 ELSE 0 END) AS correct
            FROM answer_records
            JOIN questions ON questions.id = answer_records.question_id
            GROUP BY questions.chapter
            ORDER BY questions.chapter ASC
            """
        ).fetchall()
    result = []
    for row in rows:
        total = int(row["total"] or 0)
        correct = int(row["correct"] or 0)
        result.append(
            {
                "chapter": row["chapter"],
                "total": total,
                "correct": correct,
                "accuracy": correct / total if total else 0.0,
            }
        )
    return result


def wrong_counts_by_chapter(db_path: Path = DB_PATH) -> list[dict]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT questions.chapter, COUNT(answer_records.id) AS wrong_count
            FROM answer_records
            JOIN questions ON questions.id = answer_records.question_id
            WHERE answer_records.is_correct = 0
            GROUP BY questions.chapter
            ORDER BY wrong_count DESC, questions.chapter ASC
            """
        ).fetchall()
    return [dict(row) for row in rows]
