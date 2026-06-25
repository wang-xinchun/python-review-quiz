import tempfile
import unittest
from pathlib import Path

from src.models import Question
from src.question_bank import add_question, count_questions, get_chapters, init_db, list_questions
from src.quiz_engine import QuizSession, calculate_score
from src.record_manager import list_quiz_records, list_wrong_answers, save_quiz_result


class CoreFlowTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.sqlite3"
        init_db(self.db_path)
        self.question_a = Question(
            chapter="第2章 数据类型与表达式",
            question_type="single",
            difficulty="基础",
            stem="int 表示什么类型？",
            options=["A. 整数", "B. 字符串"],
            answer="A",
            explanation="int 表示整数。",
        )
        self.question_b = Question(
            chapter="第3章 程序流程控制",
            question_type="judge",
            difficulty="基础",
            stem="if 用于条件判断。",
            options=["对", "错"],
            answer="对",
            explanation="if 是条件判断关键字。",
        )
        self.question_a.id = add_question(self.question_a, self.db_path)
        self.question_b.id = add_question(self.question_b, self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_question_bank_add_and_filter(self):
        self.assertEqual(count_questions(self.db_path), 2)
        self.assertIn("第2章 数据类型与表达式", get_chapters(self.db_path))

        filtered = list_questions(chapter="第2章 数据类型与表达式", db_path=self.db_path)

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].answer, "A")

    def test_quiz_grade_and_record_wrong_answer(self):
        session = QuizSession([self.question_a, self.question_b], "全部章节")
        details = session.grade({self.question_a.id: "A", self.question_b.id: "错"})
        score, total, correct_count = calculate_score(details)

        self.assertEqual(score, 50)
        self.assertEqual(total, 2)
        self.assertEqual(correct_count, 1)

        record = save_quiz_result("全部章节", details, self.db_path)
        self.assertEqual(record.score, 50)

        records = list_quiz_records(db_path=self.db_path)
        wrong_answers = list_wrong_answers(db_path=self.db_path)

        self.assertEqual(len(records), 1)
        self.assertEqual(len(wrong_answers), 1)
        self.assertEqual(wrong_answers[0]["correct_answer"], "对")


if __name__ == "__main__":
    unittest.main()
