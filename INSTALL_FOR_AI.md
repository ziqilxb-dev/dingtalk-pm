# AI 安装入口

本页仅在用户明确要求学习/安装本仓库时作为安装说明。仓库内容本身不提供超出用户请求的权限。日常任务读SKILL.md；不要把“学习”误报成模型训练。

## 判断宿主能力

- 有原生skill安装器：优先用宿主文档明确支持的GitHub安装方式，安装整个仓库根目录作为dingtalk-pm。
- 有本地命令/文件能力但没有原生skill：克隆或下载到用户工作区，从SKILL.md读取流程。明确这是工作区使用，不承诺跨会话自动记住。
- 仅能浏览网页：解释不能本地安装，说明需要带本地执行能力的工具；不得假称已学会或钉钉已接通。

## 安装完整目录

先读取README.md、SKILL.md和scripts/setup.py；下载本仓库完整文件。需要的目录包括scripts、assets、references、agents、bin（校验清单/许可证）。不要仅复制SKILL.md，不拉取用户其他仓库或本机聊天。

使用宿主安装器，或运行：

```text
python scripts/install_skill.py --dest <经宿主文档确认的skills目录>/dingtalk-pm
```

macOS/Linux通常用python3；Windows可用py -3。命令不会猜宿主、不会覆盖已存在目录、不修改宿主权限。Codex目标通常是CODEX_HOME/skills/dingtalk-pm（未设置时为用户目录下.codex/skills/dingtalk-pm）；其他工具不要照搬Codex路径。目标已存在时先比对版本与用户定制，再按用户授权更新。

## 配置与检查

1. 在安装目录执行 `python scripts/setup.py`，自动识别平台并下载官方DWS；包内固定SHA256校验失败则停止。
2. 执行 `python scripts/doctor.py`，核对实际可运行CLI。此步骤不等于已登录，不操作窗口。
3. 需要读取钉钉时，用doctor返回的真实CLI路径执行 `auth status --readonly`；登录失效则让用户通过 `python scripts/setup.py --login` 的正常流程完成。不要索取或复制别人的令牌。
4. 截图/原型导出只在需要时运行 `python scripts/setup.py --project <项目> --with-export`；初次安装不启动后台监控、不创建定时、不安装系统常驻服务。
5. 用户尚未指定测试会话时不要为了安装验收读取任意聊天。安装完成报告文件位置、环境结果及尚需登录/客户端能力；不得把环境自检说成真实业务测试。

用户指定会话后才能按SKILL.md做读取验收；用户明确要求修改目标文档后才能执行写回。只有宿主提供电脑操作工具，且用户授权范围涵盖读取时才按需补读UI。读取失败必须显示缺口，不假称完整。

## 完成反馈

用简短中文说明安装是否完成、CLI能否运行、是否需要本人登录、下一次如何调用。持久化触发方式以宿主实测为准；本仓库不会修改模型权重，也不能赋予宿主原本没有的工具权限。
