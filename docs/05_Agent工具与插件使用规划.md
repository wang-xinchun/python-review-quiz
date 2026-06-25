# Agent 工具与插件使用规划

## 1. 规划目的

本项目除了完成 Python 课程期末大作业本身，还需要体现对大模型 Agent 工具链的理解和使用能力。因此需要提前规划 Codex App 中的 skills、插件和 GitHub 工作流如何服务本项目。

本文件用于回答三个问题：

1. 当前已经可用的 Codex skills 和插件有哪些。
2. 哪些工具适合本项目，应该在哪个阶段使用。
3. 哪些工具暂时不建议使用，避免项目过度复杂。

## 2. 当前已确认可用能力

### 2.1 GitHub 插件

当前已确认 GitHub 插件可用，并已经完成：

1. 读取 GitHub 用户信息。
2. 查看仓库列表。
3. 创建公共仓库 `python-review-quiz`。
4. 本地初始化 git 仓库。
5. 提交项目规划文档。
6. 推送到 GitHub。

项目仓库：

```text
https://github.com/wang-xinchun/python-review-quiz
```

用途：

1. 保存项目代码和文档。
2. 形成清晰的版本历史。
3. 记录大模型参与项目开发的过程。
4. 后续可使用 issue、commit、PR 等方式体现工程化开发流程。

推荐等级：必须使用。

### 2.2 PDF Skill

当前已安装并可用。

用途：

1. 读取课程 PPT/PDF 中的章节标题。
2. 辅助整理课程知识点。
3. 后期可用于检查或生成 PDF 报告。

使用建议：

1. 第一版不依赖 PDF 自动抽题。
2. PDF 只作为资料分析和报告素材整理工具。
3. 若 PDF 文本提取效果不好，应改为人工整理知识点。

推荐等级：建议使用。

### 2.3 Playwright / Browser 测试能力

当前已安装 `playwright` 和 `playwright-interactive` skills，插件缓存中也存在 Chrome 自动化能力。

用途：

1. 如果采用 Streamlit，可用浏览器测试应用页面。
2. 截取系统运行截图，用于课程设计报告。
3. 检查按钮、表单、自测流程和统计页面是否正常。

使用建议：

1. 开发最小可运行版本后再使用。
2. 用于验证界面，不用于增加项目复杂度。

推荐等级：建议使用。

### 2.4 Documents / PDF / Spreadsheets / Presentations 运行时插件

本地插件缓存中存在以下官方运行时插件：

1. documents：创建和编辑文档。
2. pdf：读取、创建、渲染和检查 PDF。
3. spreadsheets：创建、分析和导出表格。
4. presentations：创建和编辑演示文稿。

用途：

1. documents：后期辅助整理 Word 课程设计报告。
2. pdf：报告导出或版式检查。
3. spreadsheets：如需导出测试记录表、题库表或统计表，可辅助处理。
4. presentations：如果最终需要答辩 PPT，可辅助生成。

推荐等级：后期使用。

### 2.5 Build Web Apps 插件

本地插件缓存中存在 `build-web-apps` 插件，包含前端构建、前端测试、React、shadcn 等 skills。

用途：

1. 适合复杂前端项目。
2. 适合 React/Next.js 页面设计。
3. 适合 Web UI 调试。

对本项目的判断：

1. 如果使用 Streamlit，不需要 React/Next.js。
2. 本项目重点是 Python 课程知识，不应转为前端项目。
3. 可借用其中的“前端测试/视觉检查”思路，但不建议引入完整前端技术栈。

推荐等级：谨慎使用。

### 2.6 OpenAI Developers / OpenAI Docs 相关能力

本地插件缓存中存在 OpenAI Developers 插件，当前会话也可使用 OpenAI 文档相关 skill。

用途：

1. 如果后续要接入 OpenAI API 生成题目或复习建议，可查官方文档。
2. 如果要展示“大模型 API 调用”能力，可用于设计 API 方案。

对本项目的判断：

1. 第一版不接入实时大模型 API。
2. 大模型使用重点放在 Agent 协作开发，而不是应用运行时调用 API。
3. 如时间充足，可作为增强功能设计，不作为核心验收标准。

推荐等级：可选增强。

### 2.7 PPT Master / Presentations

当前已有 `ppt-master` skill，插件缓存中也有 presentations 能力。

用途：

1. 后期如果老师要求课堂展示，可生成答辩 PPT。
2. 可以把项目背景、模块设计、系统截图、测试结果和 AI 协作过程整理成演示稿。

推荐等级：后期可用。

## 3. 官方可安装 skill 清单中与本项目相关的能力

通过官方 curated skill 列表，发现以下未安装或可选安装的 skill 可能与项目有关：

| Skill | 当前状态 | 相关性 | 建议 |
| --- | --- | --- | --- |
| jupyter-notebook | 未安装 | 可用于数据分析、题库统计实验 | 可选 |
| screenshot | 未安装 | 可用于截图整理报告素材 | 可选 |
| security-best-practices | 未安装 | 可用于检查基础安全问题 | 低优先级 |
| gh-address-comments | 未安装 | 可用于处理 GitHub PR 评论 | 暂不需要 |
| gh-fix-ci | 未安装 | 可用于修复 CI | 暂不需要 |
| cli-creator | 未安装 | 可用于命令行工具设计 | 暂不需要 |
| openai-docs | 列表显示未安装，但当前会话已有相关文档能力 | OpenAI API 文档查询 | 可选增强 |
| cloudflare-deploy / netlify-deploy / vercel-deploy / render-deploy | 未安装 | 部署 Web 应用 | 暂不需要 |

当前建议：

1. 暂不急着安装新 skill。
2. 等 Streamlit 应用完成后，如果截图整理不方便，可考虑安装 `screenshot`。
3. 如果后续需要用 Notebook 做统计分析，可考虑安装 `jupyter-notebook`。
4. 部署类 skill 暂不使用，避免偏离课程重点。

## 4. 社区 skill / 社区插件的判断

Codex 支持从 GitHub 仓库路径安装社区 skill。社区资源的优点是覆盖面广，缺点是质量、维护情况和安全性不如官方 curated 资源稳定。

对本项目的建议：

1. 当前不安装未经验证的社区 skill。
2. 如果后续发现非常明确的需求，再单独评估。
3. 可以把“自定义项目 skill”作为更适合本项目的方向。

## 5. 建议自定义一个项目 skill

比起安装很多社区 skill，更推荐后期创建一个本项目专属 skill，例如：

```text
python-review-quiz-dev
```

它可以沉淀本项目的固定开发规则：

1. 项目目标和功能边界。
2. 目录结构。
3. 代码风格。
4. 测试要求。
5. 报告写作要求。
6. 大模型协作记录格式。

这样做的好处：

1. 能体现对 Agent 工作流的高级使用。
2. 比“多装插件”更贴合课程考察。
3. 后续每次开发时都能复用项目规则。

建议阶段：

1. 核心代码结构确定后再创建。
2. 不在项目初期创建，避免规则频繁变化。

## 6. 本项目推荐工具使用顺序

### 第一阶段：规划与版本管理

使用：

1. GitHub 插件。
2. skill-installer。
3. PDF skill。

目标：

1. 建立仓库。
2. 整理项目规划。
3. 分析课程 PPT。

当前状态：已完成大部分。

### 第二阶段：核心代码开发

使用：

1. Codex 基础编码能力。
2. GitHub 插件。
3. Python 本地运行环境。

目标：

1. 实现题库、自测、错题、统计和报告导出。
2. 每完成一阶段就提交到 GitHub。

### 第三阶段：界面测试与截图

使用：

1. Playwright。
2. Chrome 插件。
3. 可选 screenshot skill。

目标：

1. 测试 Streamlit 页面。
2. 截取系统运行图。
3. 保存报告素材。

### 第四阶段：报告整理

使用：

1. documents 插件。
2. pdf 插件。
3. spreadsheets 插件。
4. 可选 ppt-master / presentations。

目标：

1. 整理课程设计报告。
2. 整理测试表格。
3. 生成答辩材料。

### 第五阶段：增强功能

可选使用：

1. OpenAI Docs / OpenAI Developers。
2. jupyter-notebook。
3. 自定义项目 skill。

目标：

1. 设计 AI 题目生成增强方案。
2. 进行数据分析实验。
3. 沉淀项目专属 Agent 工作流。

## 7. 工具使用在报告中的写法

最终报告中可以加入“开发工具与 Agent 协作工具”小节，说明：

1. 使用 GitHub 插件创建仓库和管理版本。
2. 使用 PDF skill 分析课程资料。
3. 使用 Codex 辅助拆分需求、设计模块和生成测试用例。
4. 使用 Playwright 或浏览器插件测试 Streamlit 页面。
5. 使用文档/PDF 工具整理最终报告。
6. 所有 AI 生成内容都经过人工审查和运行验证。

## 8. 当前结论

当前最适合本项目的工具组合是：

1. 必须使用：GitHub 插件。
2. 建议使用：PDF skill、Playwright、文档/PDF 运行时工具。
3. 后期可用：spreadsheets、presentations、ppt-master、screenshot。
4. 可选增强：OpenAI Developers、OpenAI Docs、jupyter-notebook。
5. 暂不使用：部署类插件、复杂前端插件、未经验证的社区 skill。

这样既能体现 Codex App 和 Agent 工具链的使用水平，也不会让工具选择盖过 Python 课程项目本身。

## 9. 参考来源

本规划参考了以下来源：

1. OpenAI Codex 官方 Skills 文档：`https://developers.openai.com/codex/skills`
2. OpenAI Codex 官方 Plugins 文档：`https://developers.openai.com/codex/plugins`
3. OpenAI curated skills 目录：`https://github.com/openai/skills/tree/main/skills/.curated`
4. 社区 Codex 插件清单：`https://github.com/hashgraph-online/awesome-codex-plugins`

其中，官方文档和本机已安装能力优先级最高；社区资源仅作为参考，不在当前阶段直接安装。
