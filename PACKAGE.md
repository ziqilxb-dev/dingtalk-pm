# 钉钉与产品工作流 · 跨平台参赛包

单一skill：按需读取指定私聊/群聊 → 补读关键缺失 → 整理结论 → 需求、PRD、原型、流程及验收 → 按授权更新文档。

## 首次使用

1. 安装Python 3.9+，将整个dingtalk-pm文件夹导入支持skill、执行本地命令和文件操作的AI工具。Codex可放到其skills目录；其他宿主使用各自导入方式。
2. Windows双击setup.cmd；macOS/Linux执行 `sh setup.sh`。安装器识别Windows/macOS/Linux及x64/ARM64，只下载对应官方DWS并校验SHA256，不改系统PATH。
3. 用 `python scripts/setup.py --login` 登录自己的钉钉（macOS/Linux通常用python3）。不需要开发者提供账户或令牌。
4. 对AI说：“查看我和某人最近关于某主题的讨论，整理结论及需求影响。”也可直接要求编写PRD或原型。

需要本地保存、预览及截图：`python scripts/setup.py --project <项目目录> --with-export`，随后按references/runtime.md按需启动服务。Linux的Chromium若缺系统库，依Playwright官方错误提示安装，安装器不自动提权。

## 包内内容

scripts/：跨平台安装、自检、CLI解析和采集、PM项目初始化。
assets/：PM完整工作流、模板、前端组件，以及本地预览、保存、备份、截图服务源码。
references/：消息补读、证据移交、文档写回与部署说明。
bin/：官方发行包校验清单和许可证，不包含单一平台的大型二进制。
tests/：安装器、采集和PM服务验证。

## 能力与验证范围

CLI核心有六种系统/架构的安装适配；此交付不等于六平台都经过真机测试。已实际测试macOS Apple Silicon；其他平台发布资产及安装逻辑验证见references/compatibility.md。

客户端补读还取决于AI宿主是否提供电脑操作能力、系统权限和钉钉客户端。无此能力仍能使用CLI和PM流程，缺失消息需用户提供原文或截图。纯网页聊天环境不能直接运行这些本地脚本。包不内置独立模型服务，AI推理由宿主提供。

网络需能访问GitHub发行包、Python依赖源和钉钉服务。离线分发须提前准备对应平台依赖。默认按需运行，不安装定时任务、常驻监控或快捷键。包中不含用户聊天、凭据或项目运行配置。
