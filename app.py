from __future__ import annotations

import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from src.config import EXPORT_DIR, ensure_directories
from src.models import DIFFICULTIES, QUESTION_TYPES, Question
from src.question_bank import (
    add_question,
    count_questions,
    get_chapters,
    get_question,
    init_db,
    list_questions,
    seed_from_json,
)
from src.quiz_engine import build_quiz, build_quiz_from_ids
from src.record_manager import list_quiz_records, list_wrong_answers, save_quiz_result, unique_wrong_question_ids
from src.report_exporter import export_report, generate_report_text
from src.statistics_service import chapter_accuracy, get_overview, question_counts_by_chapter, wrong_counts_by_chapter


TYPE_LABELS = {
    "single": "单选题",
    "judge": "判断题",
    "blank": "填空题",
}

LABEL_TO_TYPE = {label: key for key, label in TYPE_LABELS.items()}


def bootstrap() -> None:
    ensure_directories()
    init_db()
    if "seed_count" not in st.session_state:
        st.session_state.seed_count = seed_from_json()


def page_style() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 2rem;
            max-width: 1180px;
        }
        .metric-card {
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 14px 16px;
            background: #ffffff;
        }
        .muted {
            color: #64748b;
            font-size: 0.92rem;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def question_dict(question: Question) -> dict:
    return {
        "编号": question.id,
        "章节": question.chapter,
        "题型": TYPE_LABELS.get(question.question_type, question.question_type),
        "难度": question.difficulty,
        "题干": question.stem,
        "答案": question.answer,
        "解析": question.explanation,
    }


def render_horizontal_bar(df: pd.DataFrame, value_col: str, label_col: str, color: str = "#0f6cbf") -> None:
    chart = (
        alt.Chart(df)
        .mark_bar(color=color, cornerRadiusEnd=3)
        .encode(
            x=alt.X(f"{value_col}:Q", title=None),
            y=alt.Y(f"{label_col}:N", title=None, sort=None, axis=alt.Axis(labelLimit=260)),
            tooltip=[label_col, value_col],
        )
        .properties(height=max(220, len(df) * 34))
    )
    st.altair_chart(chart, use_container_width=True)


def option_value(label: str) -> str:
    text = label.strip()
    if "." in text:
        return text.split(".", 1)[0].strip()
    if "．" in text:
        return text.split("．", 1)[0].strip()
    return text


def render_home() -> None:
    st.title("Python课程智能复习与自测系统")
    overview = get_overview()
    cols = st.columns(5)
    cols[0].metric("题目数", overview["question_count"])
    cols[1].metric("章节数", overview["chapter_count"])
    cols[2].metric("练习次数", overview["quiz_count"])
    cols[3].metric("平均正确率", f"{overview['avg_accuracy'] * 100:.1f}%")
    cols[4].metric("累计错题", overview["wrong_count"])

    st.subheader("章节题量")
    counts = question_counts_by_chapter()
    if counts:
        df = pd.DataFrame(counts).rename(columns={"chapter": "章节", "question_count": "题目数"})
        render_horizontal_bar(df, "题目数", "章节")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("题库为空。")

    st.subheader("最近练习")
    records = list_quiz_records(limit=8)
    if records:
        st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)
    else:
        st.info("暂无练习记录。")


def render_question_bank() -> None:
    st.title("题库管理")
    chapters = ["全部章节"] + get_chapters()
    type_options = ["全部题型"] + list(TYPE_LABELS.values())

    with st.container():
        col1, col2, col3 = st.columns([1.2, 1.0, 1.8])
        chapter = col1.selectbox("章节筛选", chapters)
        type_label = col2.selectbox("题型筛选", type_options)
        keyword = col3.text_input("关键词搜索", placeholder="题干、解析或章节")

    question_type = LABEL_TO_TYPE.get(type_label) if type_label != "全部题型" else None
    questions = list_questions(
        chapter=None if chapter == "全部章节" else chapter,
        question_type=question_type,
        keyword=keyword,
    )

    st.caption(f"当前显示 {len(questions)} 道题")
    if questions:
        st.dataframe(pd.DataFrame([question_dict(question) for question in questions]), use_container_width=True, hide_index=True)
    else:
        st.info("没有符合条件的题目。")

    st.divider()
    st.subheader("新增题目")
    with st.form("add_question_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([1.2, 1.0, 1.0])
        new_chapter = col1.text_input("章节", value="第1章 Python导论")
        new_type_label = col2.selectbox("题型", list(TYPE_LABELS.values()))
        difficulty = col3.selectbox("难度", list(DIFFICULTIES))
        stem = st.text_area("题干", height=90)
        selected_type = LABEL_TO_TYPE[new_type_label]
        if selected_type == "single":
            options_text = st.text_area("选项", value="A. \nB. \nC. \nD. ", height=120)
            answer = st.text_input("答案", value="A")
        elif selected_type == "judge":
            options_text = "对\n错"
            answer = st.selectbox("答案", ["对", "错"])
        else:
            options_text = ""
            answer = st.text_input("答案")
        explanation = st.text_area("解析", height=90)
        submitted = st.form_submit_button("保存题目")

    if submitted:
        options = [line.strip() for line in options_text.splitlines() if line.strip()]
        try:
            question = Question(
                chapter=new_chapter,
                question_type=selected_type,
                difficulty=difficulty,
                stem=stem,
                options=options,
                answer=answer,
                explanation=explanation,
            )
            if not question.stem or not question.answer:
                st.error("题干和答案不能为空。")
            elif question.question_type == "single" and len(question.options) < 2:
                st.error("单选题至少需要两个选项。")
            else:
                question_id = add_question(question)
                st.success(f"题目已保存，编号：{question_id}")
        except ValueError as exc:
            st.error(str(exc))


def render_quiz_question(question: Question) -> str:
    st.markdown(f"**{question.id}. {question.stem}**")
    key = f"answer_{question.id}"
    if question.question_type == "single":
        selected = st.radio("选择答案", question.options, key=key, label_visibility="collapsed")
        return option_value(selected)
    if question.question_type == "judge":
        return st.radio("选择答案", ["对", "错"], key=key, horizontal=True, label_visibility="collapsed")
    return st.text_input("填写答案", key=key, label_visibility="collapsed")


def render_quiz() -> None:
    st.title("自测练习")
    chapters = ["全部章节"] + get_chapters()
    question_total = count_questions()
    if question_total == 0:
        st.warning("题库为空，请先添加题目。")
        return

    col1, col2 = st.columns([1.3, 1.0])
    chapter = col1.selectbox("选择章节", chapters)
    quiz_size = col2.slider("题量", min_value=1, max_value=min(10, question_total), value=min(5, question_total))

    if st.button("开始自测", type="primary"):
        session = build_quiz(chapter, quiz_size)
        if session.total == 0:
            st.warning("当前章节没有题目。")
        else:
            st.session_state.quiz_question_ids = [question.id for question in session.questions if question.id is not None]
            st.session_state.quiz_chapter_scope = chapter
            st.session_state.quiz_result = None
            st.rerun()

    question_ids = st.session_state.get("quiz_question_ids", [])
    if not question_ids:
        return

    questions = [question for question_id in question_ids if (question := get_question(question_id))]
    session = build_quiz_from_ids(question_ids, st.session_state.get("quiz_chapter_scope", chapter))

    with st.form("quiz_form"):
        answers: dict[int, str] = {}
        for question in questions:
            st.container(border=True)
            answers[int(question.id)] = render_quiz_question(question)
            st.write("")
        submitted = st.form_submit_button("提交答案")

    if submitted:
        details = session.grade(answers)
        record = save_quiz_result(session.chapter_scope, details)
        st.session_state.quiz_result = {
            "record_id": record.id,
            "score": record.score,
            "total": record.total,
            "correct_count": record.correct_count,
            "details": details,
        }

    result = st.session_state.get("quiz_result")
    if result:
        st.success(f"本次得分：{result['score']} 分，答对 {result['correct_count']} / {result['total']} 题。")
        for detail in result["details"]:
            status = "正确" if detail.is_correct else "错误"
            with st.expander(f"{status}｜{detail.question.stem}"):
                st.write(f"你的答案：{detail.user_answer or '未填写'}")
                st.write(f"正确答案：{detail.question.answer}")
                st.write(f"解析：{detail.question.explanation}")


def render_wrong_book() -> None:
    st.title("错题本")
    chapters = ["全部章节"] + get_chapters()
    chapter = st.selectbox("章节筛选", chapters, key="wrong_chapter")
    wrong_answers = list_wrong_answers(chapter=None if chapter == "全部章节" else chapter)

    col1, col2 = st.columns([1, 1])
    col1.metric("错题记录", len(wrong_answers))
    wrong_ids = unique_wrong_question_ids(chapter=None if chapter == "全部章节" else chapter)
    col2.metric("去重题目", len(wrong_ids))

    if wrong_ids and st.button("从错题开始回练"):
        st.session_state.quiz_question_ids = wrong_ids[:10]
        st.session_state.quiz_chapter_scope = "错题回练"
        st.session_state.quiz_result = None
        st.success("错题已加入自测页面。请切换到“自测练习”提交答案。")

    if wrong_answers:
        for item in wrong_answers:
            with st.expander(f"{item['chapter']}｜{item['stem']}"):
                st.write(f"你的答案：{item['user_answer'] or '未填写'}")
                st.write(f"正确答案：{item['correct_answer']}")
                st.write(f"解析：{item['explanation']}")
                if item["options"]:
                    st.code("\n".join(json.loads(item["options"])), language="text")
    else:
        st.info("暂无错题记录。")


def render_statistics_and_report() -> None:
    st.title("学习统计与报告")
    overview = get_overview()
    cols = st.columns(4)
    cols[0].metric("练习次数", overview["quiz_count"])
    cols[1].metric("平均正确率", f"{overview['avg_accuracy'] * 100:.1f}%")
    cols[2].metric("累计错题", overview["wrong_count"])
    cols[3].metric("题库题目", overview["question_count"])

    st.subheader("章节正确率")
    accuracy = chapter_accuracy()
    if accuracy:
        df = pd.DataFrame(accuracy)
        df["正确率"] = (df["accuracy"] * 100).round(1)
        chart_df = df.rename(columns={"chapter": "章节"})
        render_horizontal_bar(chart_df, "正确率", "章节")
        st.dataframe(
            chart_df.rename(columns={"total": "答题数", "correct": "正确数", "accuracy": "正确率原值"})[
                ["章节", "答题数", "正确数", "正确率"]
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("暂无练习记录。")

    st.subheader("错题分布")
    wrong_stats = wrong_counts_by_chapter()
    if wrong_stats:
        wrong_df = pd.DataFrame(wrong_stats).rename(columns={"chapter": "章节", "wrong_count": "错题数"})
        render_horizontal_bar(wrong_df, "错题数", "章节", color="#dc2626")
    else:
        st.info("暂无错题分布。")

    st.subheader("学习报告")
    report_text = generate_report_text()
    st.download_button("下载报告文本", data=report_text, file_name="study_report.md", mime="text/markdown")
    if st.button("导出到本地 exports 目录"):
        output_path = export_report()
        st.success(f"已导出：{output_path}")


def render_agent_records() -> None:
    st.title("Agent协作记录")
    record_path = Path("docs/06_Agent协作记录.md")
    if record_path.exists():
        st.markdown(record_path.read_text(encoding="utf-8"))
    else:
        st.info("暂无协作记录。")


def main() -> None:
    st.set_page_config(page_title="Python复习自测系统", page_icon="PY", layout="wide")
    bootstrap()
    page_style()

    pages = {
        "首页概览": render_home,
        "题库管理": render_question_bank,
        "自测练习": render_quiz,
        "错题本": render_wrong_book,
        "学习统计与报告": render_statistics_and_report,
        "Agent协作记录": render_agent_records,
    }
    with st.sidebar:
        st.header("python-review-quiz")
        selected_page = st.radio("导航", list(pages.keys()))
        st.caption("Python课程期末大作业")

    pages[selected_page]()


if __name__ == "__main__":
    main()
