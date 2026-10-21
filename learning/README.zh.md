# DeepSeek Harness 学习与迁移课

这是一套面向开发者的三模块课程：先建立术语，再建立架构地图，最后读代码并做小改动；学完后用迁移测试检验是否真的理解，而不是记住结论。

## 适合谁

- 会 TypeScript / Node.js，能用 Git 和终端。
- 用过至少一个 AI coding agent，但没有读过 DSH 源码。
- 目标不是背 API，而是能判断“新需求应该落在哪个插件、哪个 seam、哪个事件”。

## 三个模块

| 模块 | 你会得到什么 | 验收方式 |
|---|---|---|
| 1. 术语 | 用准确词汇描述 DSH 的运行、装配、扩展和持久化 | 术语闭卷测验 |
| 2. 架构 | 能从 CLI/Desktop 入口画到插件树、Host、Session 和工具执行 | 架构口述 + 三张图 |
| 3. 代码 | 能沿真实文件追踪一次 turn，并新增一个只读工具 | 代码阅读题 + 小改动 |

## 建议节奏

- 第 1 天：模块 1 + 模块 2 前半，约 90 分钟。
- 第 2 天：模块 2 后半 + 模块 3，约 120 分钟。
- 第 3 天：做迁移测试；把答案或代码发给我，我按 rubric 评分并指出下一步。

## 学习法：三遍法

1. **地图遍**：只看目录、README 和架构图，不追细节；目标是知道东西在哪。
2. **追踪遍**：选一条真实路径（例如一次 turn 或一次 CLI 启动），每读一个文件只回答“它负责什么、它依赖谁、谁调用它”。
3. **改动遍**：做最小改动（优先新增插件，不改核心），用测试和 `dump-config` 验证。

## 文件

- [01-terminology.zh.md](01-terminology.zh.md)：术语与易混点。
- [02-architecture.zh.md](02-architecture.zh.md)：架构、启动、turn 数据流和扩展点。
- [03-code-implementation.zh.md](03-code-implementation.zh.md)：源码阅读路线和小练习。
- [04-transfer-assessment.zh.md](04-transfer-assessment.zh.md)：迁移测试题目与评分标准。
- [answer-key.zh.md](answer-key.zh.md)：参考答案；建议做完再打开。

## 重要原则

- 不要一开始改 `packages/core/agent-loop` 或 `packages/core/session`；先通过 bundle、tool、provider、client UI 这些扩展点做事。
- 任何模型可见输入都必须能从 Session 日志重建；看到“只在内存里加了一段 prompt”的实现，先怀疑它。
- 注册都要能回滚：新服务、工具、监听器、UI 槽位都应通过 `ctx.effect` 或注册返回的 disposer 管理。
- 先读 `README.md` 和架构文档，再读源码；DSH 的命名很精确，术语错位会导致后面全错。

## 开始之前

先做 [04-transfer-assessment.zh.md](04-transfer-assessment.zh.md) 的“诊断 8 题”，把答案留在手边；学完三个模块后再做一次，对比两次答案。诊断不计分，只用来定位你的起点。
