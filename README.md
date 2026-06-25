# python-review-quiz

Python课程智能复习与自测系统。

本项目是《Python程序设计》课程期末大作业，目标是构建一个轻量级复习与自测应用，支持题库管理、自测练习、自动判分、错题记录、学习统计和报告导出。

## 项目目标

1. 围绕 Python 课程知识点组织复习内容。
2. 使用 Python 基础语法、数据结构、函数、模块、类和文件操作完成核心功能。
3. 通过大模型 Agent 辅助完成规划、开发、测试和报告整理。
4. 保留清晰的开发文档，方便形成最终课程设计报告。

## 当前阶段

当前已经完成第一版核心功能开发：

1. 题库管理。
2. 自测练习。
3. 自动判分。
4. 错题记录。
5. 学习统计。
6. 学习报告导出。
7. Agent 协作记录展示。

已完成文档：

1. 项目立项与总体规划。
2. 大模型 Agent 协作方案。
3. 最终报告结构草案。
4. 开发任务清单。
5. 项目范围审查与知识点覆盖。
6. Agent 工具与插件使用规划。
7. Agent 协作记录。
8. 数据库与模块设计。
9. 测试记录和问题修复记录。

## 运行方式

安装依赖：

```bash
python -m pip install -r requirements.txt
```

启动应用：

```bash
python -m streamlit run app.py
```

默认访问地址：

```text
http://localhost:8501
```

运行测试：

```bash
python -m unittest discover -s tests -v
```

## 目录结构

```text
app.py                 Streamlit 应用入口
src/                   核心业务模块
data/seed_questions.json 初始题库
tests/                 自动化测试
docs/                  项目规划、协作记录和测试文档
```

## 说明

课程 PPT 和示例报告文件仅作为本地参考资料，不提交到公共 GitHub 仓库。
