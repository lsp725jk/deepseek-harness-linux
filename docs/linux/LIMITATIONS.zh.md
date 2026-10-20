# Linux v1 已知限制

当前交付是 **unsigned、x64、本地分发** 的 Linux 桌面版；以下限制是有意裁剪，不是隐藏缺陷。

## 分发与更新

- 不做代码签名、公证、上传或 CI 发布；产物名带 `-unsigned`，不能与正式发布包混用。
- Linux 不接 electron-updater feed；菜单中的“检查更新”已隐藏，避免无 feed 报错。
- arm64 已有代码路径与锁文件，但 v1 未构建/未验收。

## 账户与平台

- `dsh-base` 的 `desktopPlatform` 仍只给 darwin/win32；Linux 桌面按 Web 身份发送账户平台头。
- 若服务端拒绝该身份，请使用 API Key 模式；后续可单独补 Linux 平台头，不伪造 `desktop-linux`。
- 不自动迁移 Windows 侧的 `$DSH_HOME`、会话、插件或凭据；需要时在新机重新登录/安装插件。

## 桌面壳

- 没有 Windows 托盘/后台隐藏确认；Linux 关闭最后一个窗口即退出。
- “管理 dsh 命令…”菜单在 Linux 隐藏；请用 `apps/desktop/linux/install-cli.sh` 或 deb 内的 CLI。
- AppImage 在无 FUSE 的环境需 `--appimage-extract-and-run`；deb 不依赖 FUSE。

## 能力

- Office→PDF 强制走 `libreoffice-kit-wasm`（无 Linux 原生 kit）；`prepare-dsh` 已跳过 kit 的 Linux 原生探测，避免把缺失的开发包误判为不完整；首次转换较慢，属于预期。
- 沙箱优先 bwrap，其次 Landlock；两者都不可用时命令会报 `SANDBOX_UNAVAILABLE`，不会静默无沙箱执行。
- 语音输入等实验插件依赖的原生包若未随 Linux 生产依赖安装，启用时会失败；核心 agent 不受影响。

## 构建环境

- 构建主机必须是 Linux x64（原生或 Docker/WSL2/VM）；不支持在 Windows 上直接交叉生成 Linux 桌面包。
- 本次 deb 使用 `dpkg-deb` 从 `linux-unpacked` 生成（electron-builder 26 的 fpm 下载在受限网络下会卡住）；`Depends` 已补齐 GTK/NSS/GBM/X11 等 Electron 运行库。
- 验收基线 Ubuntu 22.04（glibc 2.35）+ Debian 12；更老的 glibc 发行版未验收。