from __future__ import annotations

import json
from html import escape
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from src.config import ensure_directories
from src.models import DIFFICULTIES, Question
from src.question_bank import (
    add_question,
    count_questions,
    get_chapters,
    get_question,
    init_db,
    list_questions,
    seed_from_json,
)
from src.quiz_engine import build_quiz, build_quiz_from_ids, find_unanswered_questions
from src.record_manager import list_quiz_records, list_wrong_answers, save_quiz_result, unique_wrong_question_ids
from src.report_exporter import export_report, generate_report_text
from src.statistics_service import chapter_accuracy, get_overview, question_counts_by_chapter, wrong_counts_by_chapter


TYPE_LABELS = {
    "single": "单选题",
    "judge": "判断题",
    "blank": "填空题",
}

LABEL_TO_TYPE = {label: key for key, label in TYPE_LABELS.items()}

TYPE_TONES = {
    "single": "blue",
    "judge": "teal",
    "blank": "orange",
}


def bootstrap() -> None:
    ensure_directories()
    init_db()
    if "seed_count" not in st.session_state:
        st.session_state.seed_count = seed_from_json()


def page_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            --app-bg: #f6f8fb;
            --surface: #ffffff;
            --surface-soft: #f8fafc;
            --text-main: #172033;
            --text-muted: #64748b;
            --line: #dbe3ef;
            --blue: #2563eb;
            --teal: #0f766e;
            --orange: #c2410c;
            --red: #dc2626;
            --shadow: 0 10px 28px rgba(15, 23, 42, 0.07);
        }
        .stApp {
            background: var(--app-bg);
            color: var(--text-main);
        }
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 4rem;
            max-width: 1220px;
        }
        section[data-testid="stSidebar"] {
            background: #eef3f8;
            border-right: 1px solid var(--line);
        }
        section[data-testid="stSidebar"] h2 {
            letter-spacing: 0;
            color: var(--text-main);
        }
        section[data-testid="stSidebar"] label[data-baseweb="radio"] {
            border-radius: 8px;
            padding: 4px 8px;
            margin: 2px 0;
        }
        section[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) {
            background: #ffffff;
            border: 1px solid var(--line);
            box-shadow: 0 6px 16px rgba(15, 23, 42, 0.06);
        }
        .sidebar-brand {
            display: flex;
            align-items: center;
            gap: 12px;
            margin: 8px 0 22px;
        }
        .brand-mark {
            display: grid;
            place-items: center;
            width: 38px;
            height: 38px;
            border-radius: 8px;
            color: #ffffff;
            font-weight: 800;
            background: #172033;
            box-shadow: var(--shadow);
        }
        .brand-title {
            margin: 0;
            font-weight: 800;
            color: var(--text-main);
        }
        .brand-subtitle {
            margin: 2px 0 0;
            color: var(--text-muted);
            font-size: 0.82rem;
        }
        .page-header {
            display: flex;
            justify-content: space-between;
            gap: 18px;
            align-items: flex-end;
            padding: 4px 0 18px;
            border-bottom: 1px solid var(--line);
            margin-bottom: 18px;
        }
        .page-header h1 {
            margin: 0;
            color: var(--text-main);
            font-size: 2rem;
            line-height: 1.18;
            letter-spacing: 0;
        }
        .page-header p {
            margin: 8px 0 0;
            color: var(--text-muted);
            max-width: 680px;
        }
        .header-meta {
            color: var(--teal);
            border: 1px solid #99f6e4;
            background: #f0fdfa;
            border-radius: 8px;
            padding: 8px 10px;
            font-size: 0.86rem;
            white-space: nowrap;
        }
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(148px, 1fr));
            gap: 12px;
            margin: 2px 0 22px;
        }
        .stat-card {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 15px 16px;
            box-shadow: var(--shadow);
            min-height: 112px;
        }
        .stat-card span {
            color: var(--text-muted);
            font-size: 0.88rem;
        }
        .stat-card strong {
            display: block;
            margin-top: 8px;
            color: var(--text-main);
            font-size: 1.8rem;
            line-height: 1.1;
        }
        .stat-card small {
            display: block;
            margin-top: 8px;
            color: var(--text-muted);
        }
        .stat-card.blue { border-top: 3px solid var(--blue); }
        .stat-card.teal { border-top: 3px solid var(--teal); }
        .stat-card.orange { border-top: 3px solid var(--orange); }
        .stat-card.red { border-top: 3px solid var(--red); }
        .stat-card.gray { border-top: 3px solid #64748b; }
        .section-title {
            margin: 26px 0 12px;
        }
        .section-title h2 {
            margin: 0;
            color: var(--text-main);
            font-size: 1.28rem;
            line-height: 1.3;
            letter-spacing: 0;
        }
        .section-title p {
            margin: 5px 0 0;
            color: var(--text-muted);
            font-size: 0.94rem;
        }
        .toolbar-note {
            color: var(--text-muted);
            font-size: 0.9rem;
            margin: 0 0 10px;
        }
        .question-head {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 10px;
            flex-wrap: wrap;
        }
        .question-number {
            color: var(--text-muted);
            font-size: 0.86rem;
            font-weight: 700;
        }
        .chip {
            display: inline-flex;
            align-items: center;
            min-height: 24px;
            border-radius: 7px;
            padding: 2px 8px;
            font-size: 0.78rem;
            font-weight: 700;
            border: 1px solid var(--line);
            background: var(--surface-soft);
            color: var(--text-muted);
        }
        .chip.blue {
            color: var(--blue);
            border-color: #bfdbfe;
            background: #eff6ff;
        }
        .chip.teal {
            color: var(--teal);
            border-color: #99f6e4;
            background: #f0fdfa;
        }
        .chip.orange {
            color: var(--orange);
            border-color: #fed7aa;
            background: #fff7ed;
        }
        .question-stem {
            color: var(--text-main);
            font-weight: 760;
            font-size: 1.02rem;
            line-height: 1.65;
            margin-bottom: 8px;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-color: var(--line);
            border-radius: 8px;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.045);
            background: var(--surface);
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid var(--line);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: var(--shadow);
        }
        .muted {
            color: var(--text-muted);
            font-size: 0.92rem;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.7rem;
        }
        div[data-testid="stButton"] > button,
        div[data-testid="stDownloadButton"] > button {
            border-radius: 8px;
            min-height: 42px;
            font-weight: 760;
            letter-spacing: 0;
        }
        div[data-testid="stButton"] > button[kind="primary"] {
            background: var(--blue);
            border-color: var(--blue);
        }
        div[data-testid="stAlert"] {
            border-radius: 8px;
            border: 1px solid var(--line);
        }
        div[data-testid="stExpander"] {
            border-radius: 8px;
            border-color: var(--line);
            background: var(--surface);
        }
        textarea, input, div[data-baseweb="select"] > div {
            border-radius: 8px !important;
        }
        @media (max-width: 780px) {
            .page-header {
                display: block;
            }
            .header-meta {
                display: inline-block;
                margin-top: 12px;
            }
            .page-header h1 {
                font-size: 1.58rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def safe_text(value: object) -> str:
    return escape(str(value), quote=True)


def render_page_header(title: str, description: str, meta: str | None = None) -> None:
    meta_html = f'<div class="header-meta">{safe_text(meta)}</div>' if meta else ""
    st.markdown(
        f"""
        <div class="page-header">
            <div>
                <h1>{safe_text(title)}</h1>
                <p>{safe_text(description)}</p>
            </div>
            {meta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_cards(metrics: list[dict[str, str]]) -> None:
    cards = []
    for metric in metrics:
        tone = safe_text(metric.get("tone", "gray"))
        cards.append(
            f'<div class="stat-card {tone}">'
            f'<span>{safe_text(metric["label"])}</span>'
            f'<strong>{safe_text(metric["value"])}</strong>'
            f'<small>{safe_text(metric["note"])}</small>'
            f"</div>"
        )
    st.markdown(f'<div class="metric-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_section_title(title: str, description: str = "") -> None:
    description_html = f"<p>{safe_text(description)}</p>" if description else ""
    st.markdown(
        f"""
        <div class="section-title">
            <h2>{safe_text(title)}</h2>
            {description_html}
        </div>
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
    render_page_header("Python课程智能复习与自测系统", "题库状态、练习表现和错题情况集中查看", "课程期末大作业")
    overview = get_overview()
    render_metric_cards(
        [
            {"label": "题目数", "value": str(overview["question_count"]), "note": "初始题库规模", "tone": "blue"},
            {"label": "章节数", "value": str(overview["chapter_count"]), "note": "课程知识覆盖", "tone": "teal"},
            {"label": "练习次数", "value": str(overview["quiz_count"]), "note": "累计自测记录", "tone": "orange"},
            {"label": "平均正确率", "value": f"{overview['avg_accuracy'] * 100:.1f}%", "note": "全部答题表现", "tone": "gray"},
            {"label": "累计错题", "value": str(overview["wrong_count"]), "note": "需要复盘内容", "tone": "red"},
        ]
    )

    render_section_title("章节题量", "检查 7 个课程章节的题目覆盖是否均衡")
    counts = question_counts_by_chapter()
    if counts:
        df = pd.DataFrame(counts).rename(columns={"chapter": "章节", "question_count": "题目数"})
        render_horizontal_bar(df, "题目数", "章节")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("题库为空。")

    render_section_title("最近练习", "展示最近的自测结果")
    records = list_quiz_records(limit=8)
    if records:
        records_df = pd.DataFrame(records).rename(
            columns={
                "quiz_time": "时间",
                "chapter_scope": "章节范围",
                "score": "得分",
                "total": "总题数",
                "correct_count": "正确数",
            }
        )
        st.dataframe(records_df[["时间", "章节范围", "得分", "正确数", "总题数"]], use_container_width=True, hide_index=True)
    else:
        st.info("暂无练习记录。")


def render_question_bank() -> None:
    render_page_header("题库管理", "按章节、题型和关键词维护复习题目", "42 道初始题")
    chapters = ["全部章节"] + get_chapters()
    type_options = ["全部题型"] + list(TYPE_LABELS.values())

    with st.container(border=True):
        st.markdown('<p class="toolbar-note">筛选题目</p>', unsafe_allow_html=True)
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

    render_section_title("新增题目", "录入后会直接写入本地 SQLite 题库")
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


def render_quiz_question(question: Question, index: int, total: int) -> str:
    tone = TYPE_TONES.get(question.question_type, "gray")
    st.markdown(
        f"""
        <div class="question-head">
            <span class="question-number">第 {index} / {total} 题</span>
            <span class="chip {tone}">{safe_text(TYPE_LABELS.get(question.question_type, question.question_type))}</span>
            <span class="chip">{safe_text(question.difficulty)}</span>
        </div>
        <div class="question-stem">{safe_text(question.stem)}</div>
        """,
        unsafe_allow_html=True,
    )
    key = f"answer_{question.id}"
    if question.question_type == "single":
        selected = st.radio("选择答案", question.options, key=key, index=None, label_visibility="collapsed")
        return option_value(selected) if selected else ""
    if question.question_type == "judge":
        selected = st.radio("选择答案", ["对", "错"], key=key, index=None, horizontal=True, label_visibility="collapsed")
        return selected or ""
    return st.text_input("填写答案", key=key, label_visibility="collapsed")


def render_quiz() -> None:
    render_page_header("自测练习", "选择章节和题量后生成一轮练习", "提交前检查未作答")
    chapters = ["全部章节"] + get_chapters()
    question_total = count_questions()
    if question_total == 0:
        st.warning("题库为空，请先添加题目。")
        return

    with st.container(border=True):
        st.markdown('<p class="toolbar-note">出题设置</p>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1.4, 1.0, 0.8])
        chapter = col1.selectbox("选择章节", chapters)
        quiz_size = col2.slider("题量", min_value=1, max_value=min(10, question_total), value=min(5, question_total))
        col3.write("")
        col3.write("")
        start_quiz = col3.button("开始自测", type="primary", use_container_width=True)

    if start_quiz:
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

    render_section_title("本轮题目", f"共 {len(questions)} 道题")
    with st.form("quiz_form"):
        answers: dict[int, str] = {}
        for index, question in enumerate(questions, start=1):
            with st.container(border=True):
                answers[int(question.id)] = render_quiz_question(question, index, len(questions))
            st.write("")
        submitted = st.form_submit_button("提交答案")

    if submitted:
        unanswered = find_unanswered_questions(questions, answers)
        if unanswered:
            st.warning(f"还有 {len(unanswered)} 道题未作答，请完成后再提交。")
            st.session_state.quiz_result = None
        else:
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
    render_page_header("错题本", "集中复盘错题和薄弱章节", "支持错题回练")
    chapters = ["全部章节"] + get_chapters()
    chapter = st.selectbox("章节筛选", chapters, key="wrong_chapter")
    wrong_answers = list_wrong_answers(chapter=None if chapter == "全部章节" else chapter)

    wrong_ids = unique_wrong_question_ids(chapter=None if chapter == "全部章节" else chapter)
    render_metric_cards(
        [
            {"label": "错题记录", "value": str(len(wrong_answers)), "note": "包含重复做错记录", "tone": "red"},
            {"label": "去重题目", "value": str(len(wrong_ids)), "note": "可用于回练", "tone": "orange"},
        ]
    )

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
    render_page_header("学习统计与报告", "汇总答题表现并生成 Markdown 学习报告", "可导出")
    overview = get_overview()
    render_metric_cards(
        [
            {"label": "练习次数", "value": str(overview["quiz_count"]), "note": "累计练习", "tone": "orange"},
            {"label": "平均正确率", "value": f"{overview['avg_accuracy'] * 100:.1f}%", "note": "整体表现", "tone": "teal"},
            {"label": "累计错题", "value": str(overview["wrong_count"]), "note": "复盘重点", "tone": "red"},
            {"label": "题库题目", "value": str(overview["question_count"]), "note": "题库规模", "tone": "blue"},
        ]
    )

    stats_tab, report_tab = st.tabs(["统计图表", "报告预览"])
    with stats_tab:
        render_section_title("章节正确率")
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

        render_section_title("错题分布")
        wrong_stats = wrong_counts_by_chapter()
        if wrong_stats:
            wrong_df = pd.DataFrame(wrong_stats).rename(columns={"chapter": "章节", "wrong_count": "错题数"})
            render_horizontal_bar(wrong_df, "错题数", "章节", color="#dc2626")
        else:
            st.info("暂无错题分布。")

    with report_tab:
        report_text = generate_report_text()
        st.download_button("下载报告文本", data=report_text, file_name="study_report.md", mime="text/markdown")
        if st.button("导出到本地 exports 目录"):
            output_path = export_report()
            st.success(f"已导出：{output_path}")
        st.text_area("报告预览", report_text, height=360)


def render_agent_records() -> None:
    render_page_header("Agent协作记录", "保留关键提示词、采纳内容和验证结果", "报告素材")
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
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="brand-mark">PY</div>
                <div>
                    <p class="brand-title">python-review-quiz</p>
                    <p class="brand-subtitle">Python课程复习系统</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        selected_page = st.radio("导航", list(pages.keys()))
        st.caption("Python课程期末大作业")

    pages[selected_page]()


if __name__ == "__main__":
    main()
