from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .config import DB_PATH
from .models import AnswerDetail, StudyRecord
from .question_bank import get_connection
from .quiz_engine import calculate_score


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def save_quiz_result(
    chapter_scope: str,
    details: list[AnswerDetail],
    db_path: Path = DB_PATH,
) -> StudyRecord:
    score, total, correct_count = calculate_score(details)
    quiz_time = now_text()
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO quiz_records (quiz_time, chapter_scope, score, total, correct_count)
            VALUES (?, ?, ?, ?, ?)
            """,
            (quiz_time, chapter_scope, score, total, correct_count),
        )
        quiz_id = int(cursor.lastrowid)
        for detail in details:
            connection.execute(
                """
                INSERT INTO answer_records
                    (quiz_id, question_id, user_answer, correct_answer, is_correct, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    quiz_id,
                    detail.question.id,
                    detail.user_answer,
                    detail.question.answer,
                    1 if detail.is_correct else 0,
                    quiz_time,
                ),
            )
    return StudyRecord(
        id=quiz_id,
        quiz_time=quiz_time,
        chapter_scope=chapter_scope,
        score=score,
        total=total,
        correct_count=correct_count,
    )


def list_quiz_records(limit: int = 20, db_path: Path = DB_PATH) -> list[dict]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT id, quiz_time, chapter_scope, score, total, correct_count
            FROM quiz_records
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def list_wrong_answers(
    chapter: str | None = None,
    limit: int = 100,
    db_path: Path = DB_PATH,
) -> list[dict]:
    sql = """
        SELECT
            answer_records.id,
            answer_records.quiz_id,
            answer_records.question_id,
            answer_records.user_answer,
            answer_records.correct_answer,
            answer_records.created_at,
            questions.chapter,
            questions.question_type,
            questions.difficulty,
            questions.stem,
            questions.options,
            questions.explanation
        FROM answer_records
        JOIN questions ON questions.id = answer_records.question_id
        WHERE answer_records.is_correct = 0
    """
    params: list[str | int] = []
    if chapter and chapter != "全部章节":
        sql += " AND questions.chapter = ?"
        params.append(chapter)
    sql += " ORDER BY answer_records.id DESC LIMIT ?"
    params.append(limit)
    with get_connection(db_path) as connection:
        rows = connection.execute(sql, params).fetchall()
    return [dict(row) for row in rows]


def unique_wrong_question_ids(chapter: str | None = None, db_path: Path = DB_PATH) -> list[int]:
    wrong_answers = list_wrong_answers(chapter=chapter, limit=500, db_path=db_path)
    seen: set[int] = set()
    ids: list[int] = []
    for answer in wrong_answers:
        question_id = int(answer["question_id"])
        if question_id not in seen:
            seen.add(question_id)
            ids.append(question_id)
    return ids
