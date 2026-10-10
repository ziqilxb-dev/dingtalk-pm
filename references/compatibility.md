# 操作系统兼容性与实际验证

此文件下方平台矩阵主要描述DWS。企业微信使用独立CLI：官方覆盖macOS x64/arm64、Linux x64/arm64、Windows x64；本机macOS arm64安装及启动已验证，授权与真实数据结果见 [验证记录](../tests/VALIDATION.md)。企微安装无需DWS，详见 [企微接入](wecom.md)。不能将DWS的Windows ARM64支持外推给企微。

## 分层条件

- AI宿主：可加载skill、执行Python脚本和访问本机文件；完整客户端补读还需电脑操作工具。
- Python：3.9+，Windows可使用py -3或python；macOS/Linux常用python3。
- DWS：setup.py自动识别系统及架构，下载固定官方v1.0.63发行包，校验包内官方SHA256；安装到用户缓存目录，无管理员权限需求，不共享登录态。
- PM本地服务：Python源码跨平台；浏览器导出需Playwright 1.60.0和Chromium。Linux可能另需系统库，未自动提权安装。
- 钉钉客户端：不随包分发。能否通过辅助功能/窗口工具补读取决于真实系统与宿主，不能从CLI支持外推出UI支持。

## 平台矩阵

| 平台 | 安装资产 | 当前验证 |
|---|---|---|
| Windows x64 | dws-windows-amd64.zip | 官方资产及校验、解包逻辑；真机登录/消息读取待测 |
| Windows ARM64 | dws-windows-arm64.zip | 官方资产及校验、解包逻辑；真机登录/消息读取待测 |
| macOS Intel | dws-darwin-amd64.tar.gz | 官方资产及校验、解包逻辑；真机运行待测 |
| macOS Apple Silicon | dws-darwin-arm64.tar.gz | 本机安装、版本启动、真实消息读取；PM浏览器测试通过 |
| Linux x64 | dws-linux-amd64.tar.gz | 官方资产及校验、解包逻辑；真机登录/消息读取待测 |
| Linux ARM64 | dws-linux-arm64.tar.gz | 官方资产及校验、解包逻辑；真机登录/消息读取待测 |

客户端补读仅在当前macOS+Codex环境实际验证过；其他系统必须现场验收。32位及其他架构不猜选资产，明确报不支持。

## 参赛交付验收

拿一台Windows x64机器执行setup.cmd、`python scripts/doctor.py --provider dingtalk`，用户本人登录；读取测试私聊/群，检查缺口；创建临时PM项目，启动本地服务，验证保存和截图。若使用客户端补读，再验证目标AI工具的窗口读取能力。完成这些后才能将Windows标记为端到端已验证。

来源：https://github.com/DingTalk-Real-AI/dingtalk-workspace-cli/releases/tag/v1.0.63
