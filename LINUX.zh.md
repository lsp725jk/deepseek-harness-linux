# DeepSeek Harness Linux x64

[![Linux desktop package](https://github.com/lsp725jk/deepseek-harness-linux/actions/workflows/linux-desktop.yml/badge.svg)](https://github.com/lsp725jk/deepseek-harness-linux/actions/workflows/linux-desktop.yml)

本仓库是 [deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) 的 Linux x64 适配分支；基于 tag `dsh-v0.2.1-rc.2`（commit `687f282e`）。上游为 MIT 协议。

## 直接使用（Ubuntu / Debian）

从 [GitHub Release](https://github.com/lsp725jk/deepseek-harness-linux/releases/tag/v0.2.1-rc.2-linux) 下载 AppImage 或 deb：

```sh
# AppImage
chmod +x deepseek-harness-0.2.1-rc.2-linux-x86_64-unsigned.AppImage
./deepseek-harness-0.2.1-rc.2-linux-x86_64-unsigned.AppImage

# 无 FUSE 的服务器 / 容器
./deepseek-harness-0.2.1-rc.2-linux-x86_64-unsigned.AppImage --appimage-extract-and-run

# deb
sudo apt install ./deepseek-harness-0.2.1-rc.2-linux-amd64-unsigned.deb
"/opt/DeepSeek Harness/deepseek-harness"
```

首次启动会进入 Welcome，配置模型 API Key（或平台账号）、工作目录和语言；随后即可在桌面窗口里使用会话、文件、终端和 Office 预览。

## 在 Windows 上的 Ubuntu VM 中使用

1. 在 VMware 中启动 Ubuntu 22.04（或 20.04）虚拟机。
2. 把 `dist/linux-x64` 里的 AppImage/deb 复制进虚拟机（共享文件夹、拖拽或 `scp` 均可）。
3. 在虚拟机终端执行上面的 AppImage 或 deb 命令。

如果共享目录未挂载，可在虚拟机中执行：

```sh
sudo mkdir -p /mnt/hgfs
sudo mount -t vmhgfs .host:/ /mnt/hgfs
ls /mnt/hgfs
```

## CLI

安装 deb 后：

```sh
"/opt/DeepSeek Harness/resources/runtime/cli/bin/dsh" --version
"/opt/DeepSeek Harness/resources/runtime/cli/bin/dsh" web --port 3080
```

浏览器打开 `http://127.0.0.1:3080` 即可使用 Web 界面；无桌面环境时也能用 CLI + Web。

## 从源码构建

```sh
pnpm install --frozen-lockfile
pnpm --dir apps/desktop run package:linux:x64:unsigned
```

产物在 `apps/desktop/.desktop-build/targets/linux-x64/unsigned-artifacts/`。

需要 Node 24.21.0、pnpm 11.28.5，以及 GTK/NSS/GBM/X11/ALSA 等 Electron 运行库；完整步骤见 [docs/linux/BUILD.zh.md](docs/linux/BUILD.zh.md)。

## GitHub Actions

仓库内的 [.github/workflows/linux-desktop.yml](.github/workflows/linux-desktop.yml) 会在 push 到 `main`、推送 `v*` tag 或手动触发时，在 Ubuntu 22.04 x64 上构建未签名 AppImage/deb，并上传 Actions artifact；tag 构建会同时发布 GitHub Release。

## 学习与迁移

三模块学习课（术语、架构、代码实现）与迁移测评在 [learning/README.zh.md](learning/README.zh.md)；答案在 [learning/answer-key.zh.md](learning/answer-key.zh.md)。

## 当前限制

- 产物未签名；没有自动更新 feed；Linux 隐藏“检查更新”入口。
- Linux 桌面账户按 Web 身份发送平台头；服务端拒绝时使用 API Key。
- Office 使用 WASM 引擎，首次转换较慢。
- 暂未验收 arm64；未做代码签名、公证或正式 CI 上传。
- AppImage/deb 大于 GitHub 单文件 100 MB 限制，发布时作为 Release Assets 上传，不进入 git 历史。

更完整的架构分析见 [docs/analysis/deepseek-harness-architecture.zh.md](docs/analysis/deepseek-harness-architecture.zh.md)。