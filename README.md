# PM 跨平台工作助手

以产品经理工作为核心：从需求沟通与会议评审中提取依据，核对变更，编写或更新PRD、原型、流程和验收清单，并跟进项目进展。按需接入钉钉和企业微信，也支持相关跨职能协作。

名称与目录：`pm-work-assistant`；调用：`$pm-work-assistant`。

GitHub 仓库：[pm-work-assistant](https://github.com/ziqilxb-dev/pm-work-assistant)。

## 使用示例

- “整理这次需求评审的决定、分歧和待确认事项，保留原话依据。”
- “结合钉钉评审听记和企微文档，列出方案变化及未确认内容。”
- “回顾这个项目本周的进展和阻塞，附来源。”
- “根据确认的需求做PRD、原型和验收清单。”

## 接入方式

安装完整skill目录，见 [安装入口](INSTALL_FOR_AI.md)。根据使用的平台选择安装与授权，不要求同时接两边。

- 钉钉：[读取流程](references/dingtalk.md)，DWS安装器、聊天采集、AI听记读取与文档工作流。
- 企业微信：[接入流程](references/wecom.md)，官方wecom-cli及用户扫码绑定，会议和文档读取；其他模块按在线schema使用。
- [PM协作与信息整理](references/workflows.md)负责进展、跟进和总结；[产品流程](references/pm-workflow.md)负责需求、评审与变更衔接、PRD、原型、流程、验收及产品数据分析。

企业微信机器人会话列表不代表能读取普通聊天历史。两平台功能、授权及实际验证状态分别记录，不承诺能力对等。无需常驻监听；读取不自动发送消息或修改业务数据。

## 验证与隐私

[验证记录](tests/VALIDATION.md)区分安装、授权、真实读取和写回；[系统兼容性](references/compatibility.md)区分DWS与企微CLI。原始业务数据仅保存在使用项目私有目录，不随skill分发。

## 作品展示与下载

- [作品展示页源码](docs/index.html)（本地浏览器打开，四个虚构交互案例）
- [完整 Skill 安装包](downloads/pm-work-assistant-20261010.zip)

仓库、Skill 名称与安装目录统一为 `pm-work-assistant`。
