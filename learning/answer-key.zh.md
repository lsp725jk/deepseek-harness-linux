# 参考答案与评分要点

先做完题再看。这里给的是“可接受的答案骨架”，不是唯一措辞；评分看概念是否准确、边界是否清楚。

## 模块 1：术语

### 闭卷自测

1. Turn 是一轮用户可见请求；Step 是其中一次模型请求及其工具阶段。一个 turn 可含多个 step。
2. 任何模型可见输入都必须能从 Session 日志重建，否则恢复/回放/审计会丢上下文。反例：只在内存里追加一段 prompt，没有对应事件。
3. Bundle 提供可复用配置行；Profile 是有序选择 bundle 并叠加自己 patch 的装配；Patch 是按 id 覆盖的 YAML 层。
4. Sandbox：`dsh-sandbox` 定义、`dsh-sandbox-local` 提供、`tool-bash-sandbox` 消费。
5. Electron main 只做窗口/壳；Desktop Host 是运行 Cordis 与 Session 的 Node 子进程。
6. Tool 是模型可调用的动作；Skill 是可加载的知识/流程，通常通过 skill 工具读取，可能再调用工具。
7. 不能。Projection 从日志派生，日志才是事实源；删掉日志再重建 projection 会丢事实。
8. Effect 把注册和清理绑定到插件/fiber 生命周期；手工 removeListener 容易漏掉异常路径、重复注册和卸载顺序。

### 纠错练习

1. 一个 turn 可以包含多个 step（工具结果后再次请求）。
2. Plugin 是加载单位；Tool 是它可能注册的模型能力，二者不等价。
3. 反了：Bundle 是 npm 包中的配置行，Profile 是用户目录下的运行装配。
4. 反了：Session 日志是事实源，Projection 是派生读模型。
5. 错。Desktop 与 Web 共用 base、Agent Loop、Session、Tools；Desktop 只是不同载体。

## 模块 2：架构

### 练习题要点

1. 命令 → args → profile-boot → app-boot/Loader → profile+bundles+patches → web bundle 激活 → webServer 监听。
2. Electron main → 创建 BrowserWindow → spawn Desktop Host → 加载 desktop profile → Web Host 监听 → IPC boot/ready → 页面连接 API/WS → 首次渲染。
3. 示例：工具=输入 schema、输出 canonical value、测试注册+执行+dispose；provider=输入请求、输出流、测试 mock/真实 API；client UI=输入投影、输出组件、测试 slot 注册/卸载。
4. 因为 Loader 按 `inject` 和 service 可用性激活；行顺序只影响同 id 覆盖结果，不是执行顺序。
5. 由工具执行/工具注册表产生并写入 Session；UI 只能渲染结果，不能自己伪造事实。

## 模块 3：代码

### 自测

1. 动态 import 让未用到的命令不加载重依赖；会影响启动路径，但按 mode 分摊。
2. `inject` 决定依赖和服务可用性；行顺序不决定激活顺序。
3. `defineTool` 定义 schema/execute/output；`ctx.tools.register` 注册到服务；`ctx.effect` 管生命周期/回滚（工具注册通常也由 registry 的注册机制处理）。
4. 事件 payload 必须是可持久化 JSON；Error 含栈/非枚举字段，无法可靠重放。
5. Desktop Host 负责 Host 能力和桌面专属能力；main 只做壳，避免把插件树塞进 Electron 主进程。
6. 普通工具失败是可恢复的模型输入；让它看到错误并决定下一步，比直接终止 turn 更有用。

### 练习 A 参考结构

- `packages/experimental/tool-repo-stats/src/index.ts`：导出 `name`、`inject`、`Config`、`apply`；`apply` 里 `ctx.tools.register(defineTool({...}))`。
- `parameters`：`root?`；`output`：扩展名计数与 total/truncated。
- 遍历时限制深度/文件数，跳过 node_modules/.git/.desktop-build；错误用稳定 code。
- bundle patch：`- insert: - id: tool-repo-stats name: '@your-scope/dsh-tool-repo-stats'`。
- 测试：注册可见、执行计数、dispose 后消失；真实 Loader composition 测试优于手搭 ctx。

### 练习 B 参考顺序

`turn/start → step/start → tool/call → tool/result → step/end → step/start → assistant/message → step/end → turn/end`；取消时 turn/step 仍要成对收尾，工具调用要么落 result，要么落取消结果。

## 结课 20 题评分要点

- 每题 1 分，关键词命中即可；不要求逐字。
- 第 7/8 题节点缺失超过 2 个记 0.5；能说清 Host 与 Client 边界即可。
- 第 10 题必须指出“整段 config 替换”，否则 0.5。
- 第 18 题至少提到：事件类型声明合并、payload 可 JSON、是否进 `deriveMessages`、投影/测试。
- 第 20 题必须包含“新增包 + inject + defineTool + bundle 行 + 测试”，缺 bundle 或测试各扣 0.5。

## 迁移任务评分

- C1：看是否只读、schema 与 execute 一致、错误码、是否改 core、测试覆盖 dispose。
- C2：看流式/工具调用适配、认证/重试位置、请求头记录、测试策略、是否误改 session/loop。
- C3：看生命周期/信号/退出、持久化路径、复用 base/headless、验收清单。
- C4：高分答案会按“日志是否写入/是否可 derive/投影是否读同一事件/客户端是否只读缓存”排查，而不是先猜 UI bug。

通过线：20 题 ≥16，且 C 至少一题 ≥7/10。未通过时，按错题回到对应模块，不要求重读整门课。
