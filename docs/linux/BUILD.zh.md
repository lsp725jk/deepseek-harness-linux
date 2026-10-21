# Linux x64 构建与运行

## 目标

- 目标平台：Linux x86_64，Ubuntu 22.04+/Debian 12 为验收基线；AppImage 面向其他 x64 发行版。
- 产物：未签名 AppImage、deb，以及复用同一运行时的 `dsh` CLI。
- 构建版本：`0.2.1-rc.2`（tag `dsh-v0.2.1-rc.2`）。
- 本次验收构建在 Ubuntu 20.04（glibc 2.31）的 VMware 虚拟机中完成，因此同时兼容 Ubuntu 20.04+/22.04+；AppImage 已用 `--appimage-extract-and-run` 在 Xvfb 下验证窗口，deb 已安装验证。
- 目标不是重新实现 DSH，而是把上游的 Windows/macOS Desktop 发布链补齐到 Linux。

## 方式一：Docker（推荐给 CI / 有 Docker 的机器）

```sh
bash apps/desktop/linux/build-in-container.sh
```

该脚本会：

1. 用 `apps/desktop/linux/Dockerfile` 构建 Ubuntu 22.04 构建镜像；
2. 挂载源码与 pnpm store；
3. 执行 `pnpm install --frozen-lockfile`；
4. 执行 `pnpm --dir apps/desktop run package:linux:x64:unsigned`。

产物目录：

```text
apps/desktop/.desktop-build/targets/linux-x64/unsigned-artifacts/
```

实际文件名（electron-builder 的 `${os}` 使用 `linux`，架构别名使用 `x86_64`/`amd64`）：

```text
deepseek-harness-0.2.1-rc.2-linux-x86_64-unsigned.AppImage
deepseek-harness-0.2.1-rc.2-linux-amd64-unsigned.deb
```

只构建解包目录并跑 smoke：

```sh
bash apps/desktop/linux/build-in-container.sh --dir
```

## 方式二：直接在 Ubuntu 22.04 VM / 主机

```sh
sudo apt-get update
sudo apt-get install -y build-essential python3 git curl xz-utils unzip file \
  xvfb xauth bubblewrap fakeroot dpkg-dev \
  libgtk-3-0 libnss3 libasound2 libgbm1 libxss1 libxtst6 \
  libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 libcups2 libdrm2 \
  libatk1.0-0 libatk-bridge2.0-0 fonts-noto-cjk

# Node 24.21.0 + pnpm 11.28.5（版本必须与仓库 packageManager 一致）
curl -fsSLO https://nodejs.org/dist/v24.21.0/node-v24.21.0-linux-x64.tar.xz
sudo tar -xJf node-v24.21.0-linux-x64.tar.xz -C /usr/local --strip-components=1
sudo npm install -g pnpm@11.28.5

# 在源码根目录
pnpm install --frozen-lockfile
cd apps/desktop
pnpm run package:linux:x64:unsigned      # 生成 AppImage + deb
# 或
pnpm run package:linux:x64:dir -- --unsigned   # 只生成 linux-unpacked 并跑 smoke
```

首次构建会下载 Electron、Linux Node、Python standalone 与 Python wheels，并安装桌面生产依赖；之后走缓存。

Linux 的 LibreOffice 使用 WASM 引擎；`prepare-dsh.ts` 会跳过 kit 的 Linux 原生探测，避免把缺失的 `linux-x64-glibc` 开发包误判为“已安装但不完整”。

## 产物与安装

```text
.desktop-build/targets/linux-x64/unsigned-artifacts/
  deepseek-harness-0.2.1-rc.2-linux-x64-unsigned.AppImage
  deepseek-harness-0.2.1-rc.2-linux-x64-unsigned.deb
```

AppImage：

```sh
chmod +x deepseek-harness-*.AppImage
./deepseek-harness-*.AppImage
# 无 FUSE 的环境：
./deepseek-harness-*.AppImage --appimage-extract-and-run
```

deb：

```sh
sudo apt-get install ./deepseek-harness-*.deb
# 安装后：
/opt/DeepSeek\ Harness/deepseek-harness
bash apps/desktop/linux/install-cli.sh   # 把 dsh 链到 ~/.local/bin
# 或直接：
"/opt/DeepSeek Harness/resources/runtime/cli/bin/dsh" --version
```

## 关键实现点

- `scripts/desktop-build-paths.mjs` / `package-target.ts`：新增 `linux-x64` target；
- `prepare-runtime.ts` / `prepare-cli.ts` / `prepare-dsh.ts`：Linux Electron 路径与 POSIX CLI；
- `electron-builder-config.mjs`：AppImage + deb、Linux 图标、desktop entry、无更新 feed；
- `src/main.ts`：Linux 隐藏更新入口；
- `smoke-packaged-runtime.ts`：识别 `linux-unpacked` 并执行 Host/Office smoke。

## 验证命令

```sh
# 解包 smoke（无需模型 API）
pnpm run package:linux:x64:dir -- --unsigned

# CLI / Web
dsh --version
dsh --dump-config | grep -E 'tool-bash|tool-pwsh|sandbox'
dsh web --port 3080
```

架构与代码边界见 `docs/analysis/deepseek-harness-architecture.zh.md`；限制见 `docs/linux/LIMITATIONS.zh.md`。
## GitHub Actions 自动构建

工作流：[.github/workflows/linux-desktop.yml](../../.github/workflows/linux-desktop.yml)。

- 触发：push 到 `main`、推送 `v*` tag、手动 `workflow_dispatch`。
- Runner：`ubuntu-22.04` x64；安装 Electron 运行库并清理磁盘后，执行 `pnpm install --frozen-lockfile` 和 `package:linux:x64:unsigned`。
- 产物：AppImage、deb、`SHA256SUMS`；先作为 Actions artifact 保留 14 天。
- tag 构建：用 `softprops/action-gh-release` 创建/更新 pre-release，并上传同样的三个文件。
- 工作流不读取签名密钥、更新密钥或 COS 凭据，只构建未签名产物；arm64、签名和自动更新见 [ROADMAP.zh.md](ROADMAP.zh.md)。
