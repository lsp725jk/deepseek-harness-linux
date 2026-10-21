# 模块 3：代码实现

目标：沿真实文件追踪一次启动和一次 turn；能新增一个只读工具，并用 `dump-config`、单元测试和事件日志证明它接对了。

## 1. 先准备可观察环境

~~~sh
pnpm install
pnpm dsh --profile web --dump-config > /tmp/web-tree.yml
pnpm dsh --profile web --dump-config-schema > /tmp/web-schema.json
~~~

`dump-config` 展示最终组合后的插件树；先学会看它，再去读源码，否则很容易把 base 的默认值和 web 的覆盖值混在一起。

## 2. 推荐阅读顺序

不要从 `packages` 里随机打开文件。按“入口 → 装配 → 驱动 → 持久化 → 载体 → 扩展”的顺序读：

1. `apps/cli/src/bin.ts`：命令如何分发。
2. `apps/cli/src/profile-boot.ts`：profile 如何启动。
3. `packages/boot/app-boot/src/profile.ts`：bundle/profile/patch 如何合并。
4. `packages/bundle/base/cordis.patch.yml`：共享底座的实际行。
5. `packages/bundle/web-app/cordis.patch.yml`：Web 载体如何覆盖 base。
6. `packages/core/agent-loop/src/agent.ts`：turn/step 驱动。
7. `packages/core/session/src/types.ts`：事件类型和日志约束。
8. `packages/core/tools/README.md`：工具注册契约。
9. `packages/fs/tool-fs/src/index.ts`：一个真实工具包的插件形态。
10. `packages/host/webserver` 与 `packages/client`：Host/Client 边界。
11. `apps/desktop/src/main.ts`、`apps/desktop-host/src/index.ts`：桌面载体。

## 3. 代码走读 1：CLI 只是分发器

`apps/cli/src/bin.ts` 的 `runCli` 按 mode 分发：

~~~ts
switch (invocation.mode) {
  case 'profile': {
    const { runProfile } = await import('./profile-boot.ts')
    await runProfile({ ... })
    break
  }
  case 'plugin':
    process.exit(await runPlugin(...))
    break
  case 'dump-config':
    runDumpConfig(...)
    break
}
~~~

要点：

- 参数解析和 profile 启动分开；`runCli` 不持有 Agent/Session。
- 动态 import 让不相关的命令不必加载整个 Web/Desktop 依赖。
- `dump-config` 和真正运行共用 profile 解析，因此它是可信的装配观察点。
- 默认分支用 `satisfies never` 做穷尽检查；新增 mode 时编译器会提醒。

## 4. 代码走读 2：Bundle 是一组可覆盖的行

`packages/bundle/base/cordis.patch.yml` 用 insert 声明共享服务：

~~~yaml
- insert:
    - id: llm
      name: '@deepseek-ai/dsh-llm'

    - id: session
      name: '@deepseek-ai/dsh-session'

    - id: tools
      name: '@deepseek-ai/dsh-tools'
~~~

Web 载体在 `packages/bundle/web-app/cordis.patch.yml` 里用同一个 id 覆盖配置：

~~~yaml
- id: tools
  config:
    mode: !!js process.env.DSH_TOOLS_MODE
~~~

要点：

- `!!js` 是 Loader 的表达式，不是普通 YAML；它会在合适时机求值。
- 行顺序不是加载顺序；插件靠 `inject` 等待服务。
- 覆盖是整段 `config` 替换；要保留 base 的字段必须重写全部字段。
- 新工具通常只需要在某个 bundle 里 `insert` 一行，不需要改 loop。

## 5. 代码走读 3：工具包长什么样

`packages/fs/tool-fs/src/index.ts` 的插件形态：

~~~ts
export const name = 'tool-fs'
export const inject = ['tools', 'fs', 'systemPrompt', 'workingDirectory']
export interface Config { read?: boolean; write?: boolean; /* ... */ }
export const Config = z.object({ /* defaults */ })
export function apply(ctx: Context, config: Config): void {
  // 校验 config，然后 applyReadTool/applyWriteTool/...
}
~~~

工具注册本身用 `defineTool`（见 `packages/core/tools/README.md`）：

~~~ts
ctx.tools.register(defineTool({
  name: 'read_file',
  description: 'Read a file from disk.',
  parameters: {
    path: { type: 'string', required: true },
    offset: { type: 'number' },
  },
  output: {
    schema: { type: 'string' },
    render: (_args, value) => [{ type: 'text', text: value }],
  },
  async execute(args, exec) {
    return readFile(args.path, { encoding: 'utf8', signal: exec.signal })
  },
}))
~~~

要点：

- 工具包只声明“模型能做什么”，具体文件后端是 `ctx.fs`；这就是 Definition/Provider/Consumer 的分层。
- `parameters` 同时是模型 schema 和运行时校验来源；不要手写第二份。
- `execute` 只返回声明的 canonical value；UI 展示由 `output.render`/presentation 负责。
- 工具失败应返回结构化错误结果，不要用异常结束整个 turn，除非无法继续。

## 6. 代码走读 4：Agent Loop 的 turn/step

`packages/core/agent-loop/src/agent.ts` 里核心是 `kick()` → `turn()` → `step()`：

- `kick()`：在空闲时唤醒驱动，处理 inbox 中的输入。
- `turn()`：建立 `turn/start`/`turn/end`，循环执行 step，直到完成/取消/失败。
- `step()`：组装 prompt/tool schema，调用 LLM，处理 assistant 流和工具调用。
- `prepareRequest()` / `buildRequest()`：把 Session 日志中可重建的上下文变成实际请求。
- `toolsChanged()`：工具集变化会影响 prompt，需要重新组装。

一个 step 结束不等于 turn 结束：工具结果可能需要再请求模型；因此 loop 会根据“是否还有工具要执行/是否有新输入”决定是否进入下一个 step。

读这段时只问三个问题：

1. 这个函数在哪个事件边界内运行？
2. 它追加了哪些 Session 事件？
3. 它什么时候让出控制权给下一个 step/turn？

## 7. 代码走读 5：Session 事件是声明合并的

`packages/core/session/src/types.ts` 定义基础事件；其他包通过 declaration merging 增加事件类型。例如 tools 包在 `packages/core/tools/src/types.ts` 里扩展 `SessionEventMap`：

~~~ts
declare module '@deepseek-ai/dsh-session/types' {
  interface SessionEventMap {
    'tool/ptc-dispatch-start': PtcDispatchStartEventData
    'tool/ptc-dispatch': PtcDispatchEventData
  }
}
~~~

要点：

- 事件 payload 是持久化数据，必须能用 JSON 表达；不要塞函数、类实例、循环引用。
- 日志专用事件（log-only）不会进入 `deriveMessages()`，因此不会重新变成模型上下文。
- 想让模型看到的新输入，必须同时设计它的事件和 `deriveMessages` 的读取路径；否则重放会丢。
- 事件监听器用 `ctx.on` 注册，返回 disposer；插件卸载后不能继续写日志。

## 8. 代码走读 6：Desktop 与 Desktop Host

`apps/desktop/src/main.ts` 是 Electron 壳：

- 创建窗口、菜单、托盘、协议处理。
- 用 `ELECTRON_RUN_AS_NODE=1` 启动 `apps/desktop-host`。
- 接收 Host 的 `boot/ready` IPC，把端口/token 交给页面。
- Linux 上关闭自动更新入口，保持 `updatesSupported = process.platform !== 'linux'`。

`apps/desktop-host/src/index.ts` 是真正的 Host：

- 以 Node 模式运行，加载 `desktop` profile。
- 负责 Office 引擎、退出检查、平台会话、更新任务等桌面专属能力。
- 它仍然复用 `base` + `web-app`，不是另一套 Agent。

## 9. 练习 A：新增只读工具 `repo_stats`

目标：统计当前 workspace 中各扩展名的文件数，返回 JSON；不写文件、不执行命令。

要求：

1. 新建一个插件包（学习分支可放 `packages/experimental/tool-repo-stats`，不要直接改 core）。
2. 导出 `name`、`inject = ['tools', 'workingDirectory']`、`Config`、`apply`。
3. 用 `defineTool` 注册 `repo_stats`：参数 `root?` 为字符串；输出 `{ extensions: Record<string, number>, total: number }`。
4. 用 Node `fs/promises` 遍历目录；跳过 `node_modules`、`.git`、`.desktop-build`；限制最大文件数并在结果中报告 `truncated`。
5. 在 `learning` 的本地测试分支的 base/学习 bundle patch 中 insert 一行，加载插件。
6. 写一个测试：注册后 `ctx.tools` 能看到 `repo_stats`，执行后返回正确计数；再 dispose 插件，确认工具消失。

验收命令（按你的测试文件路径调整）：

~~~sh
pnpm exec vitest run packages/experimental/tool-repo-stats/tests/repo-stats.spec.ts
pnpm run typecheck
pnpm dsh --profile web --dump-config | grep repo-stats
~~~

## 10. 练习 B：追踪一次 turn 的事件

在一个测试里创建 Agent（参考 `packages/core/agent/tests` 的 testkit 用法），让 mock LLM 先返回一个工具调用，再返回最终回答；断言事件顺序满足：

~~~text
turn/start -> step/start -> tool/call -> tool/result -> step/end -> step/start -> assistant/message -> step/end -> turn/end
~~~

然后回答：

1. 哪些事件是模型可见的，哪些是 log-only？
2. 如果把 `tool/result` 从 `deriveMessages` 中删掉，会发生什么？
3. 取消发生在第一个 step 后时，哪些事件必须仍然成对？

## 11. 练习 C：观察装配覆盖

1. 用 `--dump-config` 导出 web 和 desktop 两个 profile 的树。
2. 找到 `tools`、`session`、`system-prompt` 三行，比较两个 profile 的 `config`。
3. 解释哪些差异来自 base，哪些来自 web-app，哪些来自 desktop 专属 patch。
4. 用 `--patch` 临时覆盖一个字段，再导出，确认只有目标行变化。

## 12. 代码阅读自测

1. `runCli` 为什么用动态 import 分支？这会影响启动时间吗？
2. `inject` 和 YAML 行顺序，哪个决定插件何时激活？
3. `ctx.tools.register`、`ctx.effect`、`defineTool` 三者的职责分别是什么？
4. Session 事件为什么不能直接存 `Error` 对象？
5. Desktop Host 和 Web Host 的代码边界在哪里？为什么 Desktop main 不直接跑 Agent？
6. 一个工具调用失败时，为什么通常不应直接结束 turn？

参考答案见 [answer-key.zh.md](answer-key.zh.md) 的模块 3 部分。
