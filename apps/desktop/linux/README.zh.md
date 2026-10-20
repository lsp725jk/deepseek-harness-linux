# Linux 构建目录

- `Dockerfile`：Ubuntu 22.04 + Node 24.21.0 + pnpm 11.28.5 构建镜像。
- `build-in-container.sh`：一键构建 AppImage/deb（`--dir` 只做解包 smoke）。
- `install-cli.sh`：从 deb/解包目录安装 `dsh` CLI 到 `~/.local/bin`。

完整说明见 [docs/linux/BUILD.zh.md](../../../docs/linux/BUILD.zh.md)。
