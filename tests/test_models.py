import unittest

from src.models import Question


class QuestionAnswerTest(unittest.TestCase):
    def test_single_choice_answer_is_case_insensitive(self):
        question = Question(
            chapter="第1章",
            question_type="single",
            difficulty="基础",
            stem="测试题",
            options=["A. 正确", "B. 错误"],
            answer="A",
            explanation="解析",
        )

        self.assertTrue(question.check_answer("a"))
        self.assertFalse(question.check_answer("B"))

    def test_judge_answer_accepts_common_values(self):
        question = Question(
            chapter="第1章",
            question_type="judge",
            difficulty="基础",
            stem="测试题",
            options=["对", "错"],
            answer="对",
            explanation="解析",
        )

        self.assertTrue(question.check_answer("正确"))
        self.assertTrue(question.check_answer("true"))
        self.assertFalse(question.check_answer("错"))

    def test_blank_answer_ignores_case_and_spaces(self):
        question = Question(
            chapter="第1章",
            question_type="blank",
            difficulty="基础",
            stem="测试题",
            options=[],
            answer="input",
            explanation="解析",
        )

        self.assertTrue(question.check_answer(" Input "))
        self.assertFalse(question.check_answer("print"))


if __name__ == "__main__":
    unittest.main()
