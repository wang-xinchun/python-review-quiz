from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .config import DB_PATH, EXPORT_DIR, ensure_directories
from .record_manager import list_quiz_records, list_wrong_answers
from .statistics_service import chapter_accuracy, get_overview, wrong_counts_by_chapter


def percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def generate_report_text(db_path: Path = DB_PATH) -> str:
    overview = get_overview(db_path)
    chapters = chapter_accuracy(db_path)
    wrong_stats = wrong_counts_by_chapter(db_path)
    recent_records = list_quiz_records(limit=5, db_path=db_path)
    wrong_answers = list_wrong_answers(limit=5, db_path=db_path)
    weak_chapters = sorted(chapters, key=lambda item: item["accuracy"])[:3]

    lines = [
        "# Python课程智能复习与自测系统学习报告",
        "",
        f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 一、总体情况",
        "",
        f"- 题库题目数：{overview['question_count']}",
        f"- 覆盖章节数：{overview['chapter_count']}",
        f"- 练习次数：{overview['quiz_count']}",
        f"- 平均正确率：{percent(overview['avg_accuracy'])}",
        f"- 累计错题数：{overview['wrong_count']}",
        "",
        "## 二、章节正确率",
        "",
    ]
    if chapters:
        lines.append("| 章节 | 答题数 | 正确数 | 正确率 |")
        lines.append("| --- | --- | --- | --- |")
        for item in chapters:
            lines.append(f"| {item['chapter']} | {item['total']} | {item['correct']} | {percent(item['accuracy'])} |")
    else:
        lines.append("暂无练习记录。")

    lines.extend(["", "## 三、薄弱章节建议", ""])
    if weak_chapters:
        for item in weak_chapters:
            lines.append(f"- {item['chapter']}：当前正确率 {percent(item['accuracy'])}，建议优先复习相关知识点。")
    else:
        lines.append("- 暂无练习数据，建议先完成一次自测。")

    lines.extend(["", "## 四、错题分布", ""])
    if wrong_stats:
        for item in wrong_stats:
            lines.append(f"- {item['chapter']}：{item['wrong_count']} 道错题")
    else:
        lines.append("- 暂无错题记录。")

    lines.extend(["", "## 五、最近练习", ""])
    if recent_records:
        lines.append("| 时间 | 章节 | 得分 | 正确题数 | 总题数 |")
        lines.append("| --- | --- | --- | --- | --- |")
        for record in recent_records:
            lines.append(
                f"| {record['quiz_time']} | {record['chapter_scope']} | {record['score']} | "
                f"{record['correct_count']} | {record['total']} |"
            )
    else:
        lines.append("暂无练习记录。")

    lines.extend(["", "## 六、近期错题示例", ""])
    if wrong_answers:
        for index, item in enumerate(wrong_answers, start=1):
            lines.append(f"{index}. {item['stem']}")
            lines.append(f"   - 你的答案：{item['user_answer']}")
            lines.append(f"   - 正确答案：{item['correct_answer']}")
    else:
        lines.append("暂无错题。")

    return "\n".join(lines) + "\n"


def export_report(db_path: Path = DB_PATH, export_dir: Path = EXPORT_DIR) -> Path:
    ensure_directories()
    export_dir.mkdir(exist_ok=True)
    report_text = generate_report_text(db_path)
    file_name = f"study_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    output_path = export_dir / file_name
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(report_text)
    return output_path
