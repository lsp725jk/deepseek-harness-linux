# 模块 2：项目架构

目标：能在白板上画出“从命令/窗口到模型请求和工具执行”的完整路径，并判断一个新需求应该落在哪个扩展点。

## 1. 五个心智模型

先记住这五句话，后面所有细节都挂在它们下面：

1. **一切皆插件**：没有需要打补丁的“特权内核”；服务、工具、UI、持久化都可替换。
2. **组合是分层的**：base bundle → 载体 bundle → profile patch → 用户 patch → 命令行 overlay，后写覆盖同 id 行。
3. **Host 跑树，Client 做投影**：Node Host 运行 Cordis 插件树和 Session；浏览器/Electron 只消费 HTTP/WS 与事件投影。
4. **日志是事实源**：Session 事件日志 append-only；模型消息、工具历史、UI 状态都能从日志重建。
5. **平台载体很薄**：Web、Desktop、CLI、SDK、ACP 都是同一套 base + 不同载体 bundle；Linux 移植主要是补发布链，不是重写核心。

## 2. 总览图

~~~mermaid
flowchart TB
  subgraph Apps[载体]
    CLI[dsh CLI]
    DESK[Electron Desktop]
    WEB[浏览器 Web]
    SDK[SDK / ACP]
  end

  subgraph Boot[装配层]
    ARGS[args / profile selection]
    BOOT[app-boot / Loader]
    PROFILE[profile + bundles + patches]
  end

  subgraph Tree[Cordis 插件树]
    BASE[dsh-base 服务]
    AGENT[agent-loop]
    SESSION[Session + persistence]
    TOOLS[tools registry]
    LLM[LLM adapters]
    HOST[web host / API gateway]
    CLIENT[client plugins]
  end

  subgraph Runtime[运行环境]
    SHELL[bash / pwsh]
    FS[fs / sandbox]
    PY[python / office / MCP]
  end

  CLI --> ARGS --> BOOT
  DESK -->|spawn Desktop Host| BOOT
  WEB -->|HTTP/WS| HOST
  SDK -->|JSON-RPC| HOST
  BOOT --> PROFILE --> BASE
  BASE --> AGENT
  BASE --> SESSION
  BASE --> TOOLS
  BASE --> LLM
  BASE --> HOST
  HOST --> CLIENT
  AGENT --> TOOLS
  AGENT --> LLM
  TOOLS --> SHELL
  TOOLS --> FS
  TOOLS --> PY
~~~

注意：图中的箭头是“主要依赖/调用”，不是全部；真实的激活顺序由 Loader 按服务可用性和 `inject` 决定，行顺序不是加载语义。

## 3. 目录地图

| 目录 | 职责 | 先看什么 |
|---|---|---|
| `apps/cli` | 命令行入口、参数解析、profile 启动 | `src/bin.ts`、`src/profile-boot.ts` |
| `apps/desktop` | Electron 壳、打包、运行时准备 | `src/main.ts`、`scripts/prepare-*` |
| `apps/desktop-host` | 桌面版真实 Host 进程、Office/更新/退出协调 | `src/index.ts`、`src/cli.ts` |
| `apps/web` | 浏览器前端外壳 | 与 client 插件配合 |
| `packages/boot` | app-boot、profile、plugin manager、HMR | `app-boot/src/profile.ts` |
| `packages/bundle` | base/web/headless/SDK/ACP 的配置行 | `base/cordis.patch.yml`、`web-app/cordis.patch.yml` |
| `packages/core` | Agent、Agent Loop、Session、Tools、System Prompt | `agent-loop/src/agent.ts`、`session/src/types.ts` |
| `packages/host` | Web server、静态资源、目录选择、插件清单 | `host/webserver` |
| `packages/client` | 浏览器插件、UI 槽位、状态投影 | `client/ui-*` |
| `packages/llm` | 模型适配器、重试、token 计量 | `llm/llm-deepseek` |
| `packages/session` | Session 持久化、投影、标题、SQLite 查询 | `session-persistence-jsonl` |
| `packages/shell` | bash/pwsh 工具与沙箱适配 | `tool-bash`、`bash-sandbox` |
| `packages/fs` | 文件服务、观察策略、read/write/edit 工具 | `tool-fs` |
| `packages/sandbox` | 沙箱定义与本地实现 | `sandbox`、`sandbox-local` |
| `packages/test-support` | 回放、mock、snapshot、loader smoke | `agent-loop-testkit` |
| `docs` | 架构、subsystems、cookbook、user 文档 | `architecture.md`、`cordis-primer.md` |

## 4. 启动路径 A：CLI

~~~text
用户输入 dsh --profile web
  -> apps/cli/src/bin.ts: runCli()
  -> parseDshArgs() 选择 mode=profile
  -> apps/cli/src/profile-boot.ts: runProfile()
  -> packages/boot/app-boot: loadLayeredEnv / loadProfile / Loader
  -> 读取 profile 的 package.json + bundles
  -> 合并 bundle patches + profile patch + user patch + --patch
  -> Loader 激活插件，等待服务可用
  -> web bundle 绑定 webServer，开始监听
~~~

关键点：

- `runCli` 只做分发；真正的 profile 启动在 `profile-boot.ts`。
- `dump-config` 也走同一套 profile 解析，只是不激活整棵树；它是你验证“装配结果”的第一工具。
- Loader 是服务可用性驱动的：配置文件里的行顺序不是启动顺序，插件通过 `inject` 声明依赖。

## 5. 启动路径 B：Desktop

~~~text
Electron main (apps/desktop/src/main.ts)
  -> 创建 BrowserWindow，加载 dsh-app://app/
  -> spawn Desktop Host (ELECTRON_RUN_AS_NODE=1)
  -> apps/desktop-host/src/index.ts
  -> 复用 profile runner 加载 desktop profile
  -> base + web-app + desktop 专属 patch
  -> Web Host 监听 127.0.0.1 随机端口
  -> Host 通过 Node IPC 发 boot/ready（端口、token、cookie）
  -> 页面用这些信息连接 /api 与 WebSocket
~~~

关键点：

- Electron main 不跑插件树；它是窗口/菜单/协议/目录选择的外壳。
- Desktop Host 是 Node 进程，不是浏览器；它和 Web Host 是“同一个 Host 的桌面载体”。
- 页面加载的是打包后的 Web 前端，但它仍然通过 HTTP/WS 和 Host 通信，不存在“桌面专属 Agent Loop”。

## 6. Profile 如何装配

一个 profile 至少包含：

- `package.json`：`dsh.profile.bundles` 指定有序 bundle 列表。
- `cordis.patch.yml`：该 profile 的覆盖层。

一个 bundle 包包含：

- `package.json` 的 `dsh.bundle` 指向 patch 文件。
- patch 文件里是一组 Cordis 行（insert/update/remove）。

装配顺序：

1. 按 `dsh.profile.bundles` 顺序应用每个 bundle 的 patch。
2. 应用 profile 自己的 `cordis.patch.yml`。
3. 应用 `$DSH_HOME/cordis.patch.yml`。
4. 应用命令行 `--patch`。

同 `id` 的行，后面的层覆盖前面的层。覆盖是整段 `config` 替换，不是深合并；所以每个覆盖层必须写出它负责的完整配置。

例子：base 里有一行 `id: tools`，web-app 里可能再次出现 `id: tools` 来改 `mode`；最终只有一行生效，值来自最后一个包含该行的层。

## 7. 一次 Turn 的数据流

~~~text
turn/start
  claim inbox: 取 queued message / next-step input
  assemble: system prompt sections + tool schemas
  agent/pre-step
  step/start
  agent/request -> prepareCall
  append user/message; log request/header
  llm/stream -> assistant stream chunks
  assistant/message | assistant/attempt
  tool/call*
    tools/pre-execute
    tools/execute
    tools/post-execute
  tool/result*
  step/end
  有工具结果或新输入 -> 下一个 step
turn/end
~~~

需要记住的三条不变式：

1. `turn/start` 与 `turn/end` 成对；`step/start` 与 `step/end` 成对；取消/失败也要走收尾事件。
2. 模型请求头记录实际 provider/model、reasoning effort、max tokens；重放不能靠“当前默认值”猜。
3. 工具失败通常是一个 `tool/result`（isError），不是把整个 turn 直接炸掉；只有无法继续的请求/持久化错误才结束 turn。

## 8. Host 与 Client 的边界

Host 负责：

- 插件树、Agent、Session、工具执行、模型调用。
- HTTP API、WebSocket 事件、静态前端资源。
- 认证 cookie、loopback/trusted host 校验。
- 把 Session 事件投影成 Client 可消费的 envelope。

Client 负责：

- 渲染会话、工具卡片、侧栏、设置、终端等。
- 通过 API/WS 发命令，订阅投影；不直接读 Host 文件或跑 Agent。
- 用 UI 插件（`packages/client/ui-*`）向槽位注册组件。

判断一个需求该放哪边：

- 改变“模型能做什么/何时做” → Host 侧插件或工具。
- 改变“用户看到什么/怎么点” → Client 侧 UI 插件。
- 只有两边都要改时，才同时新增 Host 事件/投影与 Client 呈现。

## 9. 扩展点速查

| 想做的事 | 首选扩展点 | 不要先改 |
|---|---|---|
| 新增模型调用工具 | 新 tool 包 + `ctx.tools.register` + bundle patch | agent-loop |
| 接入新模型供应商 | `packages/llm/*` 的适配器实现 | session/agent-loop |
| 改变文件读写策略 | `fs` / `fs-observation-policy` / sandbox seam | tool-fs 里写业务分支 |
| 新增侧栏面板 | `packages/client/ui-*` + slot | Host API 里塞 UI 状态 |
| 改变系统提示结构 | `packages/core/system-prompt` 的 section 注册 | 在 loop 里拼字符串 |
| 新增运行载体 | 新 app + 复用 base/web bundle | 复制一套 core |
| 压缩上下文 | `packages/compaction/*` 插件 | 改 Session 日志格式 |

## 10. 架构练习

1. 画出 `dsh --profile web` 从命令到 Web Host 监听的 6 个关键节点。
2. 画出 Desktop 从 Electron main 到 BrowserWindow 首次渲染的 7 个关键节点。
3. 选三个扩展点（工具、provider、client UI），各写一句“输入/输出/测试”。
4. 解释为什么“行顺序不是加载顺序”，并举一个 `inject` 的例子。
5. 一条 `tool/result` 应该由谁产生？它为什么不是“UI 自己拼出来的”？

参考答案见 [answer-key.zh.md](answer-key.zh.md) 的模块 2 部分。
