# 模块 1：专业术语

目标：看到 DSH 的文档、日志或代码时，能准确说出每个词指的是哪一层，不把“插件、服务、工具、bundle”混成一类。

## 1. 运行时与执行

| 术语 | 一句话定义 | 在 DSH 里看哪里 |
|---|---|---|
| Agent harness | 驱动模型、工具、会话和上下文的基础设施；本身不是模型 | 整个仓库 |
| Agent | 一次可创建、可恢复、可取消的智能体实例 | `packages/core/agent` |
| Turn | 一轮用户可见的请求；从 `turn/start` 到 `turn/end` | `packages/core/agent-loop` |
| Step | 一次模型请求及其后的工具阶段；一个 turn 可以有多 step | `agent-loop/src/agent.ts` 的 `step()` |
| Session | 一次对话的持久化事实源，通常是 append-only 事件日志 | `packages/core/session` |
| SessionEvent | 写入 Session 的类型化记录，例如 `turn/start`、`tool/result` | `session/src/types.ts` 的声明合并 |
| model-visible ⟺ logged | 任何进入模型请求的内容，都必须能从 Session 日志重建 | `docs/architecture.md` |
| Replay | 从日志重建消息、工具历史、UI 状态 | `deriveMessages`、Session projection |
| Inbox | Agent 的待处理输入队列；followup/steer/inject 进入不同位置 | `packages/core/agent-loop/src/inbox.ts` |

**易错**：Turn 不是 Step。一个 turn 里模型可以先请求工具，拿到结果后再请求一次；第二次请求是新的 step，不是新的 turn。

## 2. 组合：Cordis、插件、服务

| 术语 | 一句话定义 | 在 DSH 里看哪里 |
|---|---|---|
| Cordis | DSH 使用的插件/服务/事件运行时 | `vendor/cordis` |
| Context（`ctx`） | 插件看到的运行时上下文；服务、事件、effect 都挂在它上面 | `@deepseek-ai/cordis` |
| Plugin | 一段可加载/卸载的代码，通常导出 `name`、`inject`、`Config`、`apply` | 各 package 的 `src/index.ts` |
| Service | 挂在 `ctx` 上的能力对象，例如 `ctx.tools`、`ctx.sessions`、`ctx.llm` | `packages/*/*/src/index.ts` |
| Service Definition | 定义能力接口和语义的包，不提供具体实现 | 例如 `packages/sandbox/sandbox` |
| Provider | 实现某个 Service Definition 的包 | 例如 `packages/sandbox/sandbox-local` |
| Consumer | 使用某个服务的包 | 例如 `packages/shell/tool-bash` |
| Capability seam | Definition / Provider / Consumer 三角色组成的能力接缝 | `docs/architecture.md` |
| Effect | 由 `ctx.effect()` 管理的注册，卸载时自动回滚 | 任何注册服务、工具、监听器的插件 |
| Disposer | 注册返回的清理函数；卸载插件或销毁 fiber 时调用 | `ctx.effect`、`ctx.on`、`register` |

**易错**：Plugin 不是 Service，也不是 Tool。插件是加载单位；服务是它向 `ctx` 提供的能力；工具是它注册给模型的能力之一。

## 3. 装配：Profile、Bundle、Patch

| 术语 | 一句话定义 | 在 DSH 里看哪里 |
|---|---|---|
| Profile | 一个命名运行配置，位于 `$DSH_HOME/profiles/<name>`，由 package.json 与 patch 文件描述 | `packages/boot/app-boot/src/profile.ts` |
| Bundle | 以 npm 包分发的一组 Cordis 配置行，通过 `dsh.bundle` 指向 patch | `packages/bundle/*/cordis.patch.yml` |
| Patch | YAML 覆盖层；按 `id` 定位行，后写覆盖前写 | `packages/bundle/base/cordis.patch.yml` |
| Loader | 读取 Cordis 配置、解析服务依赖并激活插件的运行时 | `@deepseek-ai/cordis-plugin-loader` |
| Composition | 把多个 patch 层合成为最终插件树 | `composeEntries`、`prepareProfileEntries` |
| Overlay | 叠加的配置层；命令行 `--patch` 是最后一层 | `apps/cli/src/profile-boot.ts` |

**装配顺序**：bundle patch → profile 的 `cordis.patch.yml` → `$DSH_HOME/cordis.patch.yml` → 命令行 `--patch`；后面的层覆盖前面的同 `id` 行。

**易错**：Profile 不是“用户设置”，Bundle 也不是“插件包”的同义词。Profile 是装配结果，Bundle 是可复用的一组配置行。

## 4. 模型与能力

| 术语 | 一句话定义 | 在 DSH 里看哪里 |
|---|---|---|
| Tool | 模型可调用的能力：有 name、description、参数 schema、execute 和 presentation | `packages/core/tools`、`packages/fs/tool-fs` |
| Tool registry | 保存工具定义、可见性、权限和执行的注册表 | `ctx.tools` |
| Tool call / result | 模型请求执行工具，以及执行业务返回的结构化结果 | Session 的 `tool/call`、`tool/result` |
| Skill | 可加载的指令/脚本知识包，通常通过 skill 工具读取 | `packages/skill`、`packages/skill/skill-office` |
| MCP | 外部工具/资源服务器协议；DSH 通过 MCP client 接入 | `packages/mcp/mcp-client` |
| Subagent | 由主 Agent 派生、拥有自己 Session 的子智能体 | `packages/subagent` |
| Workflow | 由多个节点/工具步骤组成的编排能力 | `packages/workflow` |
| PTC | Programmatic Tool Calling；模型写程序调用工具，而不是逐条 function call | `packages/ptc-runtime` |
| Compaction | 压缩上下文，控制 token 预算 | `packages/compaction` |
| Sandbox | 对进程/文件访问做限制的策略与实现 | `packages/sandbox` |

**易错**：Skill 通常不是 Tool。Tool 是模型可直接调用的动作；Skill 是一段被读取/加载的知识或流程，可能再调用工具。

## 5. 载体与界面

| 术语 | 一句话定义 | 在 DSH 里看哪里 |
|---|---|---|
| Host | 运行 Cordis 插件树和 Session 的 Node 进程 | `packages/bundle/web-app`、`apps/desktop-host` |
| Client | 浏览器/Electron 渲染层，通过 HTTP/WS 投影 Host 状态 | `packages/client` |
| Web Host | 提供 HTTP/WS、API gateway、静态前端的 Host 能力 | `packages/host/webserver`、`packages/api/gateway` |
| Desktop Host | 桌面版实际运行 Host 的子进程，不是 Electron main | `apps/desktop-host` |
| Electron shell | 只负责窗口、菜单、协议、目录选择等壳能力 | `apps/desktop/src/main.ts` |
| Primary runtime | 打包进桌面的 Node/Python/pnpm 解释器与依赖 | `apps/desktop/scripts/prepare-runtime.ts` |
| Headless | 不启动 UI 的一次性 CLI 运行 profile | `packages/bundle/headless` |
| ACP | 通过 stdio 接入的自动化协议载体 | `packages/bundle/acp-app` |
| SDK | TypeScript/Python 远程调用 Host 的客户端 | `packages/sdk`、`python/sdk-runtime` |

**易错**：Desktop 不是另一套 harness。它只是 Electron 壳 + 私有 Desktop Host + 同一个 Web Host；核心插件树与 Web 版共用。

## 6. 持久化与验证

| 术语 | 一句话定义 | 在 DSH 里看哪里 |
|---|---|---|
| Session format version | Session 日志的兼容代际；只在新 reader 无法安全解释旧记录时递增 | `packages/core/session/src/types.ts` |
| Persistence | 把 Session 事件写入磁盘/数据库的实现 | `packages/session/session-persistence-jsonl` |
| Projection | 从事件日志派生列表、标题、统计等读模型 | `packages/session/session-projection` |
| Snapshot | 录制后回放的期望输出，用于 keyless 测试 | `packages/test-support/session-snapshot` |
| Fixture | 测试输入或固定数据 | 各 package 的 `tests/fixtures` |
| Smoke | 打包后跑真实进程的最小验收，不是单元测试 | `apps/desktop/scripts/smoke-runtime.ts` |

**易错**：Projection 不是事实源；它从 Session 日志派生。日志才是可以重放的事实。

## 7. 闭卷自测

1. 用一句话区分 Turn 和 Step。
2. 为什么“模型可见 ⟺ logged”是硬约束？举一个违反它的例子。
3. Profile、Bundle、Patch 三者的关系是什么？
4. Service Definition、Provider、Consumer 各举一个 DSH 例子。
5. 为什么 Desktop Host 不是 Electron main？
6. Tool 和 Skill 的区别是什么？
7. 一个 Projection 能否成为 Session 的事实源？为什么？
8. `ctx.effect` 和手工 `removeListener` 的差别是什么？

## 8. 术语纠错练习

下面每句都有一处错误，请改正：

1. “一个 turn 只包含一次模型请求。”
2. “Plugin 就是 Tool，注册工具就是加载插件。”
3. “Bundle 是用户目录下的运行配置，Profile 是 npm 包。”
4. “Session projection 是事实源，日志只是缓存。”
5. “Desktop 版有一套独立的 Agent Loop，和 Web 版不共享。”

答案在 [answer-key.zh.md](answer-key.zh.md) 的模块 1 部分。先写自己的答案，再对照。
