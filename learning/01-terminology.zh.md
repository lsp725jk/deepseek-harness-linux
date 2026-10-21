# 模块 1：专业术语

目标：看到 DSH 的文档、日志或代码时，能准确说出每个词指的是哪一层，不把“插件、服务、工具、bundle”混成一类。

> 先看速查表建立边界；后半部分有 43 个术语的逐条详解（官方/仓库定义、用途、原理、作用范围、常见混淆、验证）。HTML 版会把它渲染成可搜索卡片。

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

<!-- TERMINOLOGY_DETAILS_START -->

## 术语详解

> 上面的表用于速查；这里逐条展开。官方定义优先引用仓库 glossary，其余标注为“仓库定义（按源码/文档归纳）”。

### 术语 1：Agent Harness / DSH（智能体运行框架）（agent harness）

**一句话**：把模型、工具、会话、上下文和插件树装配起来的运行时；DSH 本身不是模型。

**官方 / 仓库定义**：仓库 README/architecture：DeepSeek Harness 是开源 agent harness，基于 everything-is-a-plugin 的 Cordis；Web/Desktop/CLI/SDK/ACP 共用同一套 base 与 core。

**用途**：让模型具备可组合的工具、持久会话、上下文管理、权限/沙箱和多载体交付能力。

**原理**：Cordis 插件树提供服务；Agent Loop 驱动模型/工具；Session 日志作为事实源；profile/bundle 负责装配。

**作用范围**：Harness 包含运行时与编排层，不等于模型、UI 或单个 Agent；具体供应商/工具通过扩展点接入。

**在 DSH 里**：仓库根 README；docs/architecture.md；apps/cli；packages/core；packages/bundle。

**常见混淆**：把 DSH 当成一个模型或聊天壳；它是运行时/装配框架。

**最小验证**：读 docs/architecture.md 并运行 dsh --profile web --dump-config。

**分类**：总览

### 术语 2：Turn（轮）（turn）

**一句话**：一次被接纳输入的完整排空过程，从 turn/start 到 turn/end。

**官方 / 仓库定义**：DSH glossary（docs/glossary.md#loop-hierarchy）：one drain of admitted input in a session, ending after the model and its tools stop or a terminal policy intervenes.

**用途**：把一次用户可见请求与中间的多次模型/工具往返包成一个可取消、可审计、可恢复的生命周期。

**原理**：Agent Loop 在空闲时从 inbox 取输入，开启 turn；内部按 step 循环；完成、取消或失败都写 turn/end。

**作用范围**：一个 turn 含 0..N 个 step；不同 turn 之间有 turn/end 边界；它不是单次模型请求。

**在 DSH 里**：packages/core/agent-loop/src/agent.ts 的 turn()；Session 事件 turn/start、turn/end。

**常见混淆**：把 turn 当成一次 LLM 请求；实际一次请求只是 step。

**最小验证**：在 Session 日志里数 turn/start 与 step/start；一个 turn 可以有多条 step/start。

**分类**：执行

### 术语 3：Step（步）（step）

**一句话**：一次模型请求及其引发的工具执行；turn 的下一层调度单位。

**官方 / 仓库定义**：DSH glossary（docs/glossary.md#loop-hierarchy）：one model request plus the tool executions caused by its response; a turn contains zero or more steps.

**用途**：把“请求模型 + 执行它要求的工具”作为可重试、可中断、可观测的最小单元。

**原理**：组装 prompt/tool schema → 请求 → 流式 assistant → 工具调用 → 工具结果 → step/end；有工具结果或新输入时进入下一个 step。

**作用范围**：一个 step 只对应一次模型请求；工具阶段属于该 step；step 不等于工具调用。

**在 DSH 里**：agent-loop/src/agent.ts 的 step()；step/start、step/end、tool/call、tool/result 事件。

**常见混淆**：把 step 当成“一次工具调用”；一个 step 可以没有工具，也可以有多个工具调用。

**最小验证**：观察 turn/start → step/start → tool/call → tool/result → step/end 的顺序。

**分类**：执行

### 术语 4：Session（会话）（session）

**一句话**：一次对话的 append-only 事件日志，是恢复、回放和投影的事实源。

**官方 / 仓库定义**：仓库定义（按 packages/core/session 与 docs/architecture.md 归纳）：由 Session 服务管理的持久化事件历史，带 SessionId、序号和格式版本。

**用途**：让模型消息、工具历史、生命周期和 UI 投影都能从同一份日志重建。

**原理**：Session.append 写入类型化事件；deriveMessages 从事件生成模型消息；persistence 写 JSONL，query/projection 建读模型。

**作用范围**：Session 是会话事实，不是项目/工作目录；一个 Agent 绑定一个 Session，子 Agent 有独立 Session。

**在 DSH 里**：packages/core/session；packages/session/session-persistence-jsonl；packages/session/session-projection。

**常见混淆**：把 Session 当成 workspace 或前端 store；Session 是日志，workspace 是文件系统/项目范围。

**最小验证**：查看会话 .jsonl；用 snapshotEvents() 断言事件序列。

**分类**：持久化

### 术语 5：SessionEvent 与 model-visible ⟺ logged（session event / logged invariant）

**一句话**：任何进入模型请求的内容都必须能从 Session 日志重建；日志专用事件不进入模型上下文。

**官方 / 仓库定义**：仓库不变式（docs/architecture.md）：模型可见的输入必须可从 Session 日志重建；log-only 事件由 deriveMessages 忽略。

**用途**：保证恢复、回放、压缩、审计、fork 不会悄悄改变模型看到的内容。

**原理**：事件是持久化事实；模型消息由读取路径派生；payload 必须是可 JSON 持久化的值；log-only 事件只服务 UI/审计。

**作用范围**：适用于 prompt/context 注入、工具结果、请求头等模型可见内容；纯 UI 临时状态不必写日志。

**在 DSH 里**：packages/core/session/src/types.ts；known-event-types.ts；agent-loop 的 derive/prepare 路径。

**常见混淆**：只在内存里拼一段 prompt、不写事件；刷新或恢复后模型看到的内容会变。

**最小验证**：恢复同一 Session 后重新 deriveMessages，比较请求头和消息是否一致。

**分类**：持久化

### 术语 6：Profile（配置档）（profile）

**一句话**：位于 $DSH_HOME/profiles/<name>/ 的命名运行配置，选择 bundle 并叠加自己的 patch。

**官方 / 仓库定义**：仓库定义（按 apps/cli 与 packages/boot 归纳）：profile 目录包含 package.json（dsh.profile.bundles 有序列表）与 cordis.patch.yml（用户覆盖层）。

**用途**：让同一套代码以 web、desktop、headless、SDK 等不同组合运行，而不复制核心。

**原理**：CLI --profile 选择目录；app-boot 读取 bundle 列表，按顺序合并 patch；最后应用 profile patch 和命令行 overlay。

**作用范围**：Profile 是装配结果，不是用户设置页面；一个进程加载一个 profile；它不等于 npm package。

**在 DSH 里**：apps/cli/src/profile-boot.ts；packages/boot/app-boot/src/profile.ts；~/.dsh/profiles/<name>/。

**常见混淆**：把 Profile 当成“用户偏好设置”或“插件包”；它是运行配置组合。

**最小验证**：dsh --profile web --dump-config，查看最终组合树。

**分类**：装配

### 术语 7：Bundle（配置束）（bundle）

**一句话**：以 npm 包分发的一组 Cordis 配置行，通过 package.json 的 dsh.bundle 指向 patch 文件。

**官方 / 仓库定义**：仓库定义（packages/bundle/README.md）：bundle 提供可复用的配置行，profile 按需选择并按顺序应用。

**用途**：把共享底座（base）、载体（web-app/headless）和配置从核心代码中解耦，便于组合与发布。

**原理**：bundle 的 cordis.patch.yml 用 insert/update/remove 行描述树；应用后行进入 Loader 配置。

**作用范围**：Bundle 是配置分发单位，不是运行中的插件实例；一个 profile 可加载多个 bundle。

**在 DSH 里**：packages/bundle/base、web-app、headless、sdk-app、acp-app 的 cordis.patch.yml。

**常见混淆**：把 Bundle 等同于 npm 包本身；npm 包只是载体，bundle 是其中的配置入口。

**最小验证**：查看 package.json 的 dsh.bundle 字段和 patch 内容。

**分类**：装配

### 术语 8：Patch / Overlay（覆盖层）（patch / overlay）

**一句话**：按 id 定位 Cordis 行的 YAML 覆盖层；后写覆盖前写，config 整段替换。

**官方 / 仓库定义**：仓库定义（packages/bundle/*/cordis.patch.yml 与 docs/architecture.md）：patch 通过 id 覆盖目标行；不是深合并。

**用途**：在不改上游代码的情况下替换/调整配置，支持 profile 定制和命令行实验。

**原理**：多个 patch 按 bundle → profile → user → CLI 顺序合成；同 id 最后写入者生效；行内 config 被完整替换。

**作用范围**：只影响目标 id 行；未写的字段不会从旧层继承；覆盖不等于新增插件代码。

**在 DSH 里**：bundle patch、profile 的 cordis.patch.yml、$DSH_HOME/cordis.patch.yml、--patch 参数。

**常见混淆**：以为 config 会深合并；实际整段替换，所以覆盖层要写全字段。

**最小验证**：用 --dump-config 比较覆盖前后的同一行。

**分类**：装配

### 术语 9：Loader（加载器）（loader）

**一句话**：Cordis 的配置加载器：解析行、按服务可用性与 inject 激活插件、管理 fiber 生命周期。

**官方 / 仓库定义**：仓库定义（vendor/cordis + app-boot）：Loader 驱动 Cordis 插件树直到稳定；激活顺序由依赖/服务可用性决定。

**用途**：把静态 patch 变成运行中的服务图，并支持 HMR/卸载。

**原理**：Loader 读取配置行，创建插件 fiber；插件声明 inject，等待服务出现；注册通过 effect 回滚。

**作用范围**：Loader 不按 YAML 行顺序加载；配置覆盖在加载前已经完成；它不等于插件代码本身。

**在 DSH 里**：vendor/cordis；@deepseek-ai/cordis-plugin-loader；packages/boot/app-boot/src/index.ts。

**常见混淆**：认为行顺序就是启动顺序；实际是由服务可用性驱动。

**最小验证**：看 Loader 日志/启动顺序；在 dump-config 中观察 inject 依赖。

**分类**：装配

### 术语 10：Plugin（插件）（plugin）

**一句话**：可加载/卸载的 Cordis 模块，通常导出 name、inject、Config、apply；服务包可默认导出服务类。

**官方 / 仓库定义**：仓库约定（packages/AGENTS.md）：函数插件命名导出 name/inject/Config/apply，服务包默认导出服务类；混合形式会让 Loader 丢弃命名空间。

**用途**：把能力拆成可组合、可替换、可回滚的单元。

**原理**：Loader 调用 apply(ctx, config)；插件在 ctx 上注册服务、工具、监听器；fiber 卸载时 effect 回滚。

**作用范围**：一个插件可注册多个能力；插件不等于 Service，也不等于 Tool。

**在 DSH 里**：packages/*/*/src/index.ts；apps/desktop-host；packages/client/ui-*。

**常见混淆**：把 Plugin 等同于 Tool；工具只是插件可能注册的一个模型能力。

**最小验证**：加载/卸载插件，观察服务或工具是否随之出现/消失。

**分类**：组合

### 术语 11：Service（服务）（service）

**一句话**：挂在 ctx 上的共享能力对象，例如 ctx.tools、ctx.sessions、ctx.llm。

**官方 / 仓库定义**：仓库定义（Cordis + docs/architecture.md）：服务是插件之间通过 ctx 使用的能力接口，由 Service Definition/Provider/Consumer 构成能力接缝。

**用途**：让插件通过能力接口解耦，而不是互相 import 具体实现。

**原理**：Provider 注册服务；Consumer 通过 inject 声明依赖并使用 ctx.<service>；服务生命周期随 fiber/effect 管理。

**作用范围**：服务是共享能力；Tool 是服务的一种消费者/注册项；Service 不等于 Plugin。

**在 DSH 里**：ctx.tools、ctx.llm、ctx.sessions、ctx.shell、ctx.fs、ctx.sandbox。

**常见混淆**：把 Service 当成某个具体工具或插件；服务是能力接口/对象。

**最小验证**：在插件的 inject 中声明服务；dump-config 查看依赖。

**分类**：组合

### 术语 12：Capability Seam（能力接缝）（capability seam）

**一句话**：一个可替换能力的三角色整体：Service Definition、Provider、Consumer。

**官方 / 仓库定义**：DSH glossary（docs/glossary.md#capability-seam）：seam 是带三角色的可替换能力；它永远不是单个角色，保留给完整能力使用。

**用途**：在不改 Consumer 的前提下替换 Provider，并把策略/平台差异隔离在能力边界。

**原理**：Definition 定义服务与语义；Provider 实现平台/后端；Consumer 注入服务；Loader 按可用性装配。

**作用范围**：适用于可替换能力（shell、sandbox、fs、llm 等）；不是任何 interface 或任意依赖都叫 seam。

**在 DSH 里**：packages/shell（Definition）、bash-local/bash-sandbox（Providers）、tool-bash（Consumer）。

**常见混淆**：把 seam 说成单个 Service/interface；seam 是完整能力，单个角色应叫 Definition/Provider/Consumer。

**最小验证**：画出一个能力的 Definition/Provider/Consumer 三角色，并替换 Provider 跑测试。

**分类**：组合

### 术语 13：Effect / Disposer（副作用与清理）（effect / disposer）

**一句话**：由 ctx.effect() 管理的注册副作用；返回 disposer，插件卸载时自动回滚。

**官方 / 仓库定义**：仓库定义（Cordis 插件约定）：注册服务、工具、监听器、UI 槽位等应通过 effect 或注册返回的 disposer 管理。

**用途**：避免重复注册、泄漏和热更新残留，保证卸载可逆。

**原理**：effect 绑定到当前 fiber/plugin 生命周期；dispose 时按注册清理；ctx.on/register 通常返回 disposer。

**作用范围**：所有需要回滚的注册；不是业务事务，也不保证跨进程/持久化回滚。

**在 DSH 里**：vendor/cordis 的 ctx.effect；各插件的 ctx.on/register。

**常见混淆**：认为手动 removeListener 就足够；异常路径、重复注册和 HMR 容易漏清理。

**最小验证**：dispose 插件后确认工具/服务/监听器消失；HMR 安全测试。

**分类**：组合

### 术语 14：Tool（工具）（tool）

**一句话**：模型可调用的动作：name、description、参数 schema、execute、output/presentation。

**官方 / 仓库定义**：仓库定义（packages/core/tools/README.md）：defineTool 声明类型化参数、输出契约、执行体和可选 UI 呈现；工具注册到 ctx.tools。

**用途**：把文件、终端、网络、数据库等实际动作以受控 schema 暴露给模型。

**原理**：模型产生 tool call → registry 校验/权限/执行 → 结果写 tool/result → 模型看到结果；native 或 PTC 两种呈现。

**作用范围**：Tool 是模型接口；具体能力由 Provider/Service 实现；Tool 不是 Plugin/Service。

**在 DSH 里**：packages/core/tools；packages/fs/tool-fs；packages/shell/tool-bash；packages/web/tool-web。

**常见混淆**：把 Tool 当成后端函数或插件；工具只是模型可见的动作接口。

**最小验证**：注册后 dump-config 看到 schema；调用产生 tool/call 与 tool/result。

**分类**：能力

### 术语 15：Tool Registry（工具注册表）（tool registry）

**一句话**：ctx.tools：保存工具定义、可见性、权限与执行，并把 schema 喂给 prompt 组装。

**官方 / 仓库定义**：仓库定义（packages/core/tools）：注册即让工具对 Agent 可见；registry 负责 schema、校验、策略、执行和结果封装。

**用途**：集中管理工具生命周期、可见性、权限、并发和呈现，避免 loop 里散落工具逻辑。

**原理**：register 注册；restrict 按 scope 过滤；pre/post 管线；native/PTC 执行；结果进入 Session。

**作用范围**：每个 Agent scope 可有不同可见性/限制；registry 不是 UI 列表，也不是业务实现。

**在 DSH 里**：packages/core/tools/src/index.ts；agent-loop/src/tool-calls.ts。

**常见混淆**：把 registry 当成静态工具清单；它同时管执行/策略/呈现。

**最小验证**：注册、restrict、dispose，检查 prompt schema 与执行结果。

**分类**：能力

### 术语 16：Skill（技能）（skill）

**一句话**：可加载的指令/脚本知识包，通常通过 skill 工具读取；不是模型可直接执行的动作。

**官方 / 仓库定义**：仓库定义（packages/skill）：skill 提供领域流程/知识，由 tool-skill 读取；Office 等 skill 还会提供 CLI 路径。

**用途**：把可复用流程和领域知识注入上下文，而不是把每种流程写进 agent-loop。

**原理**：发现/读取 skill 内容 → 作为工具结果/上下文进入模型 → 模型按流程调用现有 tools/shell。

**作用范围**：Skill 内容通常模型可见；实际执行仍通过 tools/shell；skill 不是权限边界。

**在 DSH 里**：packages/skill/skill-filesystem；skill-office；tool-skill。

**常见混淆**：把 Skill 当成 Tool/function；skill 是知识/流程，tool 是动作。

**最小验证**：调用 skill 工具，查看返回内容/Office CLI 路径。

**分类**：能力

### 术语 17：Host（宿主进程）（host）

**一句话**：运行 Cordis 插件树、Agent、Session、工具和 Web API 的 Node 进程。

**官方 / 仓库定义**：仓库定义（docs/architecture.md）：Web Host 与 Desktop Host 是不同载体，但都运行同一套 Host/插件树。

**用途**：承载有状态运行时；让 Client 只做投影和交互。

**原理**：app-boot/Loader 装配树；webServer 提供 HTTP/WS；Agent/Session/Tools 在进程内运行。

**作用范围**：Host 不是 Electron main，也不是浏览器；一个 Host 进程通常服务一个 profile。

**在 DSH 里**：packages/bundle/web-app；packages/host/webserver；apps/desktop-host。

**常见混淆**：把 Host 当成 Web 服务器或 UI；Host 是运行时。

**最小验证**：dsh web 启动后看进程、端口和日志；Client 只是连接方。

**分类**：载体

### 术语 18：Client（客户端）（client）

**一句话**：浏览器/Electron 渲染层，通过 HTTP/WS 消费 Host 投影；UI 插件位于 packages/client/ui-*。

**官方 / 仓库定义**：仓库定义（packages/client）：Client 通过 API/WS 发命令、订阅投影、渲染 UI；不直接运行 Agent。

**用途**：把交互与运行时分离，使 Web、Desktop 复用同一套 Host。

**原理**：Client 插件注册槽位/状态；Host 广播投影；用户操作转成 API 命令。

**作用范围**：Client 不读 Host 文件系统、不直接跑模型；它不是 Agent 的一部分。

**在 DSH 里**：packages/client；apps/web；apps/desktop 的 preload/renderer。

**常见混淆**：把 Client 当成 Host 的一部分；禁用 Client 后 Host 仍可 headless/SDK 运行。

**最小验证**：停掉浏览器仍可通过 CLI/SDK 驱动同一 Host。

**分类**：载体

### 术语 19：Desktop Host（桌面宿主）（desktop host）

**一句话**：桌面版实际运行 Host 的 Node 子进程；Electron main 通过 IPC 启动/管理它。

**官方 / 仓库定义**：仓库定义（apps/desktop-host）：Electron 以 ELECTRON_RUN_AS_NODE 启动 Desktop Host，加载 desktop profile，复用 Web Host 与插件树。

**用途**：把有状态 Host 与 Electron 壳隔离，避免把插件树塞进主进程，同时复用 Web 运行时。

**原理**：Electron main 创建窗口/协议 → spawn Desktop Host → Host 监听 Web/API → IPC boot/ready 把 token/端口交给页面。

**作用范围**：Desktop Host 不是 Electron main，也不是独立 Agent 实现；它负责 Office/更新/退出等桌面能力。

**在 DSH 里**：apps/desktop-host/src/index.ts；apps/desktop/src/main.ts；desktop profile patch。

**常见混淆**：把 Electron main 当 Host；main 只是壳，Host 是 Node 子进程。

**最小验证**：看进程树：Electron main + Desktop Host；日志出现 dsh web 地址。

**分类**：载体

### 术语 20：Primary Runtime（主运行时）（primary runtime）

**一句话**：打包进 Desktop 的独立 Node/Python/pnpm/依赖运行时，位于 resources/runtime/primary-runtime。

**官方 / 仓库定义**：仓库定义（scripts/primary-runtime）：lock.json 固定 Node/Python/pnpm 版本与哈希，prepare-runtime 下载、校验并组装。

**用途**：让用户机器无需预装 Node/Python/pnpm，并保证构建可复现。

**原理**：lock 记录版本/URL/hash；prepare-runtime 下载/校验；CLI/runtime 从打包目录解析解释器。

**作用范围**：只包含受控运行时；不等于系统工具链；Office/Python 依赖也随 runtime 打包。

**在 DSH 里**：scripts/primary-runtime/lock.json；apps/desktop/scripts/prepare-runtime.ts；resources/runtime/versions.json。

**常见混淆**：依赖用户系统的 node/python；桌面版用自己的 primary runtime。

**最小验证**：查看 resources/runtime/versions.json；dsh --version 正常。

**分类**：载体

### 术语 21：Sandbox（沙箱）（sandbox）

**一句话**：对进程/文件访问施加限制的策略与实现；Linux 用 bwrap → Landlock，按可用性 fail-closed。

**官方 / 仓库定义**：仓库定义（packages/sandbox）：dsh-sandbox 是 Service Definition，sandbox-local 提供本地实现，bash/fs 工具是 Consumer。

**用途**：降低工具执行对用户系统的风险；在能力边界上统一策略。

**原理**：工具请求经过 sandbox 服务/策略；本地 provider 用命名空间/seccomp/Landlock 等约束；拒绝时返回结构化标记。

**作用范围**：不是完整 VM 安全边界；平台能力不同；工具/provider 仍需做输入校验。

**在 DSH 里**：packages/sandbox/sandbox；sandbox-local；sandbox-policy；fs-sandbox；bash-sandbox。

**常见混淆**：把 sandbox 当成 VM/容器；DSH 的本地沙箱是进程/文件策略。

**最小验证**：触发拒绝，观察 [sandbox: ...] 标记；dump-config 查看 sandbox seam。

**分类**：安全

### 术语 22：Projection（投影）（projection）

**一句话**：从 Session 事件派生的读模型（列表、标题、统计、UI 状态），不是事实源。

**官方 / 仓库定义**：仓库定义（packages/session/session-projection）：projection 从事件日志派生，可重建；日志才是事实。

**用途**：让查询/渲染高效，避免每次重放全部日志。

**原理**：监听事件增量更新；从日志重建；缓存/数据库可丢弃。

**作用范围**：可重建、可缓存；不能反向作为 Session 事实源；AI 可见内容仍以日志为准。

**在 DSH 里**：packages/session/session-projection；client store 中的派生状态。

**常见混淆**：把投影数据库当主库；删掉投影后必须能从日志恢复。

**最小验证**：删除/重建 projection，Session 日志与模型上下文不受影响。

**分类**：持久化

### 术语 23：Compaction（上下文压缩）（compaction）

**一句话**：压缩上下文以控制 token 预算的插件集合，例如基础压缩、图片卸载、工具结果裁剪。

**官方 / 仓库定义**：仓库定义（packages/compaction）：通过插件在模型请求前压缩/裁剪上下文，同时遵守 model-visible ⟺ logged。

**用途**：让长会话/大工具结果不超出 context window，同时保留可恢复性。

**原理**：按策略选择/摘要/裁剪消息；压缩结果进入模型请求；原始日志仍保留。

**作用范围**：改变模型可见上下文，但不删除 Session 日志；压缩策略可组合。

**在 DSH 里**：packages/compaction/compaction-basic；compaction-image-offload；compaction-tool-result-pruner。

**常见混淆**：把 compaction 当成删除日志；日志保留，压缩的是请求上下文。

**最小验证**：长会话后检查请求消息变短、日志仍完整。

**分类**：持久化

### 术语 24：PTC（程序化工具调用）（programmatic tool calling）

**一句话**：模型写一段程序来调用工具，而不是逐条 function call；DSH 用 run_code + 生成 SDK 呈现。

**官方 / 仓库定义**：仓库定义（packages/core/tools/README.md）：mode=ptc 时模型只看到 run_code 和生成 SDK；子调用仍走 tool registry。

**用途**：支持复杂多工具编排、并行子调用和更少的模型往返。

**原理**：模型生成 run_code 程序；运行时提供工具 SDK；子调用 dispatch 回 registry；maxParallelSubCalls 限制并发。

**作用范围**：PTC 是工具呈现模式，不是另一个 Agent；工具仍受权限/沙箱/结果记录约束。

**在 DSH 里**：packages/core/tools/src/ptc.ts；ptc-runtime；agent-loop/src/tool-calls.ts。

**常见混淆**：把 PTC 当成任意代码执行；它仍然是受控的工具调用。

**最小验证**：配置 mode=ptc，跑 run_code，观察 tool/ptc-dispatch。

**分类**：能力

### 术语 25：MCP（模型上下文协议）（Model Context Protocol）

**一句话**：连接外部工具/资源服务器的协议；DSH 通过 mcp-client 把外部能力适配进 ctx.tools。

**官方 / 仓库定义**：仓库定义（packages/mcp）：MCP client 发现并调用外部 server 的 tools/resources；通过适配层进入 DSH 工具树。

**用途**：复用 MCP 生态工具，而不必为每个工具写一个内置插件。

**原理**：配置 server/transport；client 发现 tools/resources；适配为工具定义；调用结果转成 DSH 结果。

**作用范围**：外部进程/服务器；需要信任、权限、超时和错误处理；不是内置插件。

**在 DSH 里**：packages/mcp/mcp-client；mcp-resources；profile 中的 MCP 配置。

**常见混淆**：把 MCP 当成一个工具；MCP 是协议/服务器接入层。

**最小验证**：配置一个 MCP server，列出工具并调用，查看 tool/result。

**分类**：能力

### 术语 26：Subagent（子智能体）（subagent）

**一句话**：由主 Agent 派生、拥有独立 Session 的子 Agent；通过 subagent 工具调用并返回结果。

**官方 / 仓库定义**：仓库定义（packages/subagent）：子 Agent 有独立 Session/生命周期，lineage 记录父子关系；scope 不自动继承。

**用途**：隔离上下文、并行调研、把专项任务交给独立 Agent。

**原理**：父 Agent 发起 subagent 工具调用；运行时创建子 Session/Agent；子 Agent 完成后结果回到父工具结果。

**作用范围**：子 Agent 不是同一 turn 的 step；工具/权限/模型可不同；日志独立。

**在 DSH 里**：packages/subagent/subagent；tool-subagent；subagent-fork-in-process。

**常见混淆**：把 subagent 当成一次工具调用；它是独立 Agent/Session。

**最小验证**：父工具调用 → 子 Session 出现 → 父收到结果。

**分类**：执行

### 术语 27：Agent（智能体）（agent）

**一句话**：一个可创建、恢复、取消的 live agent；有独立 Session 和控制面。

**官方 / 仓库定义**：仓库定义（packages/core/agent）：ctx.agents.create()/resume() 返回 AgentHandle；通过 followup/steer/inject/cancel/whenIdle 驱动。

**用途**：给插件、UI 和编排器一个稳定的控制面，而不是直接操作 loop 内部状态。

**原理**：create/resume 构建 Agent 与 Session；消息进入 inbox；driver（agent-loop）推进；dispose 停止循环并回滚 scope。

**作用范围**：Agent 绑定 Session，但 Session 不是 Agent；子 Agent 有独立 Session；Agent 的 scope 可注册专属工具/提示/监听器。

**在 DSH 里**：packages/core/agent；packages/core/agent-loop；ctx.agents。

**常见混淆**：把 Agent 当成模型调用或 Session；Agent 是控制面+运行时对象。

**最小验证**：创建 Agent → followup → whenIdle；查看 agent/created、turn/start、agent/disposed。

**分类**：执行

### 术语 28：Inbox（输入队列）（inbox）

**一句话**：Agent 待处理输入的队列，区分 followup、steer、inject 的语义。

**官方 / 仓库定义**：仓库定义（agent-loop/src/inbox.ts）：followup 排队下一轮，steer 提交下一步输入，inject 注入模型可见上下文但不唤醒。

**用途**：让人/插件在 turn 运行中安全地补充、纠偏或注入上下文。

**原理**：输入带 target 与唤醒标志；loop 在 step 边界 claim；inject 进入下一次 admitted step。

**作用范围**：只影响目标 Agent/Session；不是持久化消息本身；取消时可清空/保留。

**在 DSH 里**：agent-loop/src/inbox.ts；AgentHandle.followup/steer/inject。

**常见混淆**：把 inject 当成 followup；inject 不唤醒 driver。

**最小验证**：运行中 steer/inject，观察 step 边界与 agent/inbox 事件。

**分类**：执行

### 术语 29：Workspace（工作区）（workspace）

**一句话**：用户项目目录/当前工作目录，以及文件工具访问的作用范围。

**官方 / 仓库定义**：仓库定义（packages/workspace、working-directory）：workspace 表示项目/目录上下文；Session 的 cwd 会随工具改变，但 sandbox 权限根不变。

**用途**：让模型和工具知道在哪里读写，同时与 Session 生命周期解耦。

**原理**：workingDirectory 服务维护 cwd；fs/bash 工具相对路径解析；sandbox 使用权限根。

**作用范围**：Workspace 不是 Session 日志，也不是 UI 工作区；切换 cwd 不等于扩大 sandbox。

**在 DSH 里**：packages/workspace；packages/session/working-directory；fs/sandbox。

**常见混淆**：把 workspace 当成 Session 或 Git 仓库；它是目录/项目上下文。

**最小验证**：切换 cwd 后读文件，观察相对路径与 sandbox root。

**分类**：运行时

### 术语 30：Model Provider / Adapter（模型适配器）（model provider / adapter）

**一句话**：把 DSH 的统一 LLM 请求映射到具体供应商 API 的适配器，负责流式、工具调用和错误语义。

**官方 / 仓库定义**：仓库定义（packages/llm）：llm 定义消息/流/工具调用接缝；llm-deepseek 等 provider 实现具体 API。

**用途**：让 Agent/Session 不依赖某个供应商，支持多模型路由。

**原理**：prepareCall/请求头选择 provider+model；adapter 发请求、转流事件；错误/重试由 llm-retry 等插件处理。

**作用范围**：Provider 不拥有 Session；请求头记录实际 provider/model/reasoning；能力差异由 adapter 声明。

**在 DSH 里**：packages/llm/llm；llm-deepseek；llm-deepseek-api-key；llm-retry。

**常见混淆**：把 provider 当成 Agent/模型本身；它只是 API 适配层。

**最小验证**：切换 provider 配置，检查 request/header 与流事件。

**分类**：模型

### 术语 31：Web Host（Web 宿主）（web host）

**一句话**：在 Host 进程内提供 HTTP/WS、API gateway 和静态前端的 Web 载体。

**官方 / 仓库定义**：仓库定义（bundle/web-app + host/webserver）：Web Host 绑定 webServer，暴露 /api 与 WebSocket，服务浏览器前端。

**用途**：让浏览器/桌面页面连接同一套 Host 状态。

**原理**：webServer 提供 HTTP/WS；API gateway 暴露 controller；前端静态资源由 host 提供；cookie/loopback 校验。

**作用范围**：Web Host 是 Host 的一部分，不是 Client；端口/认证只影响接入。

**在 DSH 里**：packages/bundle/web-app；packages/host/webserver；packages/api/gateway。

**常见混淆**：把 Web Host 当成浏览器页面；页面是 Client。

**最小验证**：dsh web 启动，浏览器/curl 访问 /api。

**分类**：载体

### 术语 32：Headless（无头模式）（headless）

**一句话**：不启动 UI 的一次性 CLI 运行 profile，复用 base 能力执行任务。

**官方 / 仓库定义**：仓库定义（packages/bundle/headless）：headless profile 用于 CLI 一次性运行，不加载浏览器/桌面壳。

**用途**：在服务器/脚本里跑 Agent，不需要 Electron 或浏览器。

**原理**：选择 headless bundle；base 服务 + agent-loop 运行；命令结束/退出。

**作用范围**：Headless 不是另一个 Agent；只是不同 profile/载体。

**在 DSH 里**：packages/bundle/headless；apps/cli 的 --profile headless。

**常见混淆**：把 headless 当成无模型模式；它仍然调用模型/工具。

**最小验证**：dsh --profile headless "task"（需要 API Key）。

**分类**：载体

### 术语 33：ACP（Agent Client Protocol）（ACP）

**一句话**：通过 stdio 接入的自动化协议载体，让外部客户端驱动 DSH。

**官方 / 仓库定义**：仓库定义（packages/bundle/acp-app）：ACP 是自动化接入载体，使用 base 能力，不启动 Web/Desktop UI。

**用途**：给编辑器和自动化工具一个标准输入输出接口。

**原理**：ACP 进程通过 stdio 收发协议消息；映射到 Agent/Session 操作。

**作用范围**：ACP 是载体/协议，不是 Tool；权限/能力仍由 profile 决定。

**在 DSH 里**：packages/bundle/acp-app；packages/acp。

**常见混淆**：把 ACP 当成 MCP；两者协议/用途不同。

**最小验证**：用 ACP 客户端启动并发送一轮请求。

**分类**：载体

### 术语 34：SDK（远程客户端）（SDK）

**一句话**：TypeScript/Python 远程调用 Host 的客户端与协议栈，投影 Agent Loop。

**官方 / 仓库定义**：仓库定义（packages/sdk、python/sdk-runtime）：SDK 通过 JSON-RPC 连接 Host，提供会话/Agent 操作。

**用途**：让外部程序嵌入 DSH，而不是自己实现一轮 loop。

**原理**：SDK server 暴露 JSON-RPC；client 生成调用；事件流投影会话。

**作用范围**：SDK 是客户端，不是 Agent 本身；需要 Host 运行。

**在 DSH 里**：packages/sdk/protocol、client、server；python/sdk-runtime。

**常见混淆**：把 SDK 当成 Host/模型；它是远程控制面。

**最小验证**：启动 SDK server，客户端创建会话并收到事件。

**分类**：载体

### 术语 35：Goal（目标）（goal）

**一句话**：附加在已有 Session 上的持久化完成目标，带 phase、revision 和 round 上限。

**官方 / 仓库定义**：DSH glossary（docs/glossary.md#goal）：goal 是一个 durable completion objective；phase 为 active/paused/blocked/complete，有 goal-round cap。

**用途**：让 Agent 在多个 turn/round 中持续推进一个明确目标，并可暂停/阻塞/恢复。

**原理**：Goal 状态写入 Session；goal round 物化为一个 goal 来源 turn；激活是 process-local，恢复需 human-authorized resume。

**作用范围**：Goal 是状态，不是 scheduler/独立会话；同一 Session 的普通人类 turn 不消耗 goal round。

**在 DSH 里**：packages/goal；command-goal；tool-goal；goal-round-driver。

**常见混淆**：把 goal 当成 todo 或定时任务；goal 有 phase/round cap/重启语义。

**最小验证**：创建 goal，运行 round，查看 phase/round 事件。

**分类**：编排

### 术语 36：Todo / Schedule（待办与定时）（todo / schedule）

**一句话**：Todo 是模型可见的清单工具；Schedule 是定时触发的后续任务；两者都不是 Goal。

**官方 / 仓库定义**：仓库定义（packages/todo、packages/schedule）：todo_write 管理清单；schedule 管理定时提醒/后续输入。

**用途**：Todo 跟踪任务步骤；Schedule 在指定时间唤醒/提交任务。

**原理**：Todo 返回清单状态；Schedule 注册计时器/后续输入，触发后进入 Session。

**作用范围**：Todo 不保证执行；Schedule 不是持久目标；Goal 才有 phase/round cap。

**在 DSH 里**：packages/todo/tool-todo；packages/schedule/schedule；tool-schedule。

**常见混淆**：用 todo 代替 goal，或把 schedule 当成 cron 管理器；语义/持久化不同。

**最小验证**：创建 todo/schedule，观察工具结果和触发事件。

**分类**：编排

### 术语 37：Workflow（工作流）（workflow）

**一句话**：由多个步骤/工具节点组成的编排能力，用于可重复的复杂流程。

**官方 / 仓库定义**：仓库定义（packages/workflow）：workflow 提供多节点编排与运行记录；tool-workflow 暴露给模型。

**用途**：把多步流程从单次 prompt 中抽出来，便于复用和审计。

**原理**：定义节点/依赖/输入输出；运行器按图执行；结果回到 Session。

**作用范围**：Workflow 不是 Agent/PTC；它编排步骤，步骤内部仍调用 tools/agents。

**在 DSH 里**：packages/workflow/workflow；workflow-ptc；tool-workflow。

**常见混淆**：把 workflow 当成普通工具调用；它是多节点编排层。

**最小验证**：运行一个 workflow，查看节点状态与结果。

**分类**：编排

### 术语 38：Session Format Version（会话格式版本）（session format version）

**一句话**：Session 日志的兼容代际；只在新 reader 无法安全解释旧记录时递增。

**官方 / 仓库定义**：仓库定义（packages/core/session/src/types.ts）：单一单调整数；header 记录版本；reader 保留历史语义。

**用途**：让持久化日志跨版本可读/可迁移，避免静默误读。

**原理**：事件带 discriminator；版本升级链；旧 reader 拒绝不安全的新字段；快照/迁移测试。

**作用范围**：结构变化本身不足以升版本；只有现有 discriminator 无法防止不安全解释时才 bump。

**在 DSH 里**：packages/core/session/src/types.ts；packages/session/session-format*。

**常见混淆**：把所有 schema 变化都当成升版本；错误的版本策略会破坏兼容。

**最小验证**：读旧日志/迁移 fixture，确认 reader 行为与版本规则。

**分类**：持久化

### 术语 39：Persistence（持久化）（persistence）

**一句话**：把 Session 事件写入 JSONL/SQLite 等存储的实现；与投影读模型分开。

**官方 / 仓库定义**：仓库定义（packages/session/session-persistence-jsonl 等）：persistence 负责事件落盘/读取；query/projection 负责检索/读模型。

**用途**：让会话可恢复、可审计、可跨进程继续。

**原理**：append 事件；按 seq 读取；校验日志完整性；SQLite 用于查询索引。

**作用范围**：Persistence 不等于 projection；日志是事实源，SQLite 索引可重建。

**在 DSH 里**：packages/session/session-persistence*；session-query-sqlite。

**常见混淆**：把 SQLite 查询库当事实源；JSONL 日志才是。

**最小验证**：重启后恢复 Session；删除查询索引再重建。

**分类**：持久化

### 术语 40：Snapshot / Fixture / Smoke（测试三词）（snapshot / fixture / smoke）

**一句话**：Snapshot 是回放期望输出；Fixture 是固定输入；Smoke 是打包后真实进程的最小验收。

**官方 / 仓库定义**：仓库定义（packages/test-support、apps/desktop/scripts）：snapshot 用于 keyless 回放；fixture 提供稳定输入；smoke 验证打包运行时。

**用途**：分别保证行为不漂移、输入可复现、发布包真的能跑。

**原理**：录制模型/工具输出 → 回放比较；fixture 固定数据；smoke 启动真实 Electron/CLI 并调用 API/Office。

**作用范围**：三者不能互相替代；单元测试通过不代表 smoke 通过。

**在 DSH 里**：packages/test-support/session-snapshot；tests/fixtures；apps/desktop/scripts/smoke-*.ts。

**常见混淆**：用单元测试代替 snapshot/smoke；覆盖的失败模式不同。

**最小验证**：跑对应测试命令，观察回放/真实进程结果。

**分类**：验证

### 术语 41：Human Command（人类命令）（human command）

**一句话**：以 / 开头的指令，由人类适配器通过 ctx.commands 执行，不进入模型消息。

**官方 / 仓库定义**：DSH glossary（docs/glossary.md#human-command）：human command 由 human-facing adapter 解释执行；区别于 model tool 与 shell。

**用途**：提供确定性的 UI/控制操作，不消耗模型上下文。

**原理**：命令插件注册；UI 解析/分发；命令处理器直接操作领域状态或返回 UI 结果。

**作用范围**：命令输出通常是 UI 状态；只有处理器另行写入持久域才产生事实。

**在 DSH 里**：packages/interaction/commands；command-* 插件；UI 命令面板。

**常见混淆**：把 slash command 当成模型 tool；它不进入模型消息。

**最小验证**：执行 /goal 等命令，观察不产生模型请求。

**分类**：交互

### 术语 42：Round / Exchange（轮次/交换）（round / exchange）

**一句话**：Round 是外层策略迭代（如 goal round）；Exchange 是连续人类输入 turn 的聊天折叠单位。

**官方 / 仓库定义**：DSH glossary（docs/glossary.md#loop-hierarchy）：round 是包含 turn 的外层策略迭代；exchange 是连续 turns 的聊天分组。

**用途**：区分调度策略的生命周期与 UI 对话分组，避免把所有 turn 都叫 round。

**原理**：Round 计数器属于策略；exchange 由首个含人类输入的 turn 决定，直到下一个。

**作用范围**：不要用 round 表示每个 turn/step；exchange 只用于投影/折叠。

**在 DSH 里**：Goal/ Ralph 策略；client 会话列表/折叠。

**常见混淆**：把 turn、round、exchange 混用；层级和归属不同。

**最小验证**：看 goal round 与普通 turn 的计数/归属。

**分类**：执行

### 术语 43：Agent Scope（智能体作用域）（agent scope）

**一句话**：按 Agent 隔离注册的作用域；注册要么全局，要么属于一个 scope key，且不向子 Agent 继承。

**官方 / 仓库定义**：DSH glossary（docs/glossary.md#agent-scope）：scope 是 per-agent registration 的单位；两级、扁平；scoped 注册不会继承给子 Agent。

**用途**：让不同 Agent 拥有不同工具/提示/监听器，而不污染全局。

**原理**：scope key 通常是 live agent 对象；agent.ctx 注册 scope-visible+scope-lifetime；dispatch 带 scope carrier。

**作用范围**：subagent 不自动继承 scope；lineage 只是数据，不改变可见性。

**在 DSH 里**：packages/core/scope；agent.ctx；agent-preset。

**常见混淆**：以为子 Agent 自动继承父 Agent 的工具；实际需要显式装配。

**最小验证**：给父 Agent 注册 scoped tool，创建子 Agent，确认子 Agent 不可见。

**分类**：组合

<!-- TERMINOLOGY_DETAILS_END -->

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