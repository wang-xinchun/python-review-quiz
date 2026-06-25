from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, Iterator

from .config import DB_PATH, SEED_PATH, ensure_directories
from .models import Question


@contextmanager
def get_connection(db_path: Path = DB_PATH) -> Iterator[sqlite3.Connection]:
    ensure_directories()
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db(db_path: Path = DB_PATH) -> None:
    with get_connection(db_path) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chapter TEXT NOT NULL,
                question_type TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                stem TEXT NOT NULL,
                options TEXT NOT NULL DEFAULT '[]',
                answer TEXT NOT NULL,
                explanation TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS quiz_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_time TEXT NOT NULL,
                chapter_scope TEXT NOT NULL,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                correct_count INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS answer_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                user_answer TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                is_correct INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (quiz_id) REFERENCES quiz_records(id),
                FOREIGN KEY (question_id) REFERENCES questions(id)
            );
            """
        )


def row_to_question(row: sqlite3.Row) -> Question:
    return Question(
        id=row["id"],
        chapter=row["chapter"],
        question_type=row["question_type"],
        difficulty=row["difficulty"],
        stem=row["stem"],
        options=json.loads(row["options"]),
        answer=row["answer"],
        explanation=row["explanation"],
    )


def add_question(question: Question, db_path: Path = DB_PATH) -> int:
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO questions
                (chapter, question_type, difficulty, stem, options, answer, explanation)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                question.chapter,
                question.question_type,
                question.difficulty,
                question.stem,
                json.dumps(question.options, ensure_ascii=False),
                question.answer,
                question.explanation,
            ),
        )
        return int(cursor.lastrowid)


def add_questions(questions: Iterable[Question], db_path: Path = DB_PATH) -> int:
    count = 0
    for question in questions:
        add_question(question, db_path)
        count += 1
    return count


def list_questions(
    chapter: str | None = None,
    question_type: str | None = None,
    keyword: str | None = None,
    db_path: Path = DB_PATH,
) -> list[Question]:
    sql = "SELECT * FROM questions WHERE 1 = 1"
    params: list[str] = []
    if chapter and chapter != "全部章节":
        sql += " AND chapter = ?"
        params.append(chapter)
    if question_type and question_type != "全部题型":
        sql += " AND question_type = ?"
        params.append(question_type)
    if keyword:
        sql += " AND (stem LIKE ? OR explanation LIKE ? OR chapter LIKE ?)"
        like_keyword = f"%{keyword.strip()}%"
        params.extend([like_keyword, like_keyword, like_keyword])
    sql += " ORDER BY id ASC"
    with get_connection(db_path) as connection:
        rows = connection.execute(sql, params).fetchall()
    return [row_to_question(row) for row in rows]


def get_question(question_id: int, db_path: Path = DB_PATH) -> Question | None:
    with get_connection(db_path) as connection:
        row = connection.execute("SELECT * FROM questions WHERE id = ?", (question_id,)).fetchone()
    return row_to_question(row) if row else None


def delete_question(question_id: int, db_path: Path = DB_PATH) -> None:
    with get_connection(db_path) as connection:
        connection.execute("DELETE FROM questions WHERE id = ?", (question_id,))


def get_chapters(db_path: Path = DB_PATH) -> list[str]:
    with get_connection(db_path) as connection:
        rows = connection.execute("SELECT DISTINCT chapter FROM questions ORDER BY chapter ASC").fetchall()
    return [row["chapter"] for row in rows]


def count_questions(db_path: Path = DB_PATH) -> int:
    with get_connection(db_path) as connection:
        row = connection.execute("SELECT COUNT(*) AS total FROM questions").fetchone()
    return int(row["total"])


def load_seed_questions(seed_path: Path = SEED_PATH) -> list[Question]:
    with open(seed_path, "r", encoding="utf-8") as file:
        raw_questions = json.load(file)
    return [Question(**item) for item in raw_questions]


def seed_from_json(seed_path: Path = SEED_PATH, db_path: Path = DB_PATH) -> int:
    if count_questions(db_path) > 0:
        return 0
    questions = load_seed_questions(seed_path)
    return add_questions(questions, db_path)
