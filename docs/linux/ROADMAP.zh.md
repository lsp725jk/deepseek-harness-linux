# Linux 发布链后续路线

## 已实现

- GitHub Actions 工作流 `.github/workflows/linux-desktop.yml` 在 Ubuntu 22.04 x64 上构建未签名 AppImage 和 deb。
- push 到 `main`、pull request、手动触发都会跑构建并上传 Actions artifact；推送 `v*` tag 时同时创建或更新 GitHub Release。
- 构建后运行 `sha256sum` 生成 `SHA256SUMS`，随产物一起上传。
- 工作流不读取签名密钥、更新密钥或云端 COS 凭据，只构建未签名产物。

## 代码签名

未实现。需要可信的 Linux 代码签名证书或 HSM，并在 CI 中配置受保护的密钥注入；当前产物名带 `-unsigned`，避免被误认为正式签名包。

## 自动更新

未实现。electron-updater 需要稳定的更新 feed、签名元数据和发布策略；v1 在 Linux 隐藏检查更新入口，避免无 feed 的无效更新。

## arm64

未实现。需要同时补齐 `linux-arm64` 构建目标、Electron arm64 载荷、Node/Python arm64 主运行时、wheels 和 CI arm64 runner；现有 x64 工作流不会声称支持 arm64。

## 下一步

- 先让 x64 工作流在真实 GitHub runner 上跑通，再把固定 action 版本升级策略交给仓库维护者。
- 签名与自动更新应在确定发布渠道、证书和密钥保管方式后再启用。
- arm64 单独建工作流，不要在 x64 产物里混入未验证的 arm64 构建。
