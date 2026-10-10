# 企业微信接入

使用WecomTeam官方wecom-cli。本流程接入环境检测、用户授权、在线能力发现，以及会议/文档读取；日程、待办、邮件、微盘、表格按实时schema和相应官方参考按需调用。文档列有能力不代表当前账号已授权或实测成功。

## 安装与检查

1. 用`python scripts/wecom.py --check`检查已安装版本（至少1.2.1）和授权。可用`--cli <绝对路径>`或WECOM_CLI指定已有官方二进制。该脚本也发现用户缓存目录下通过npm或pnpm安装的官方原生程序，不保存任何令牌。
2. 缺失时需要Node.js >=18及npm，运行`npm install --prefix <用户缓存目录>/work-assistant/wecom @wecom/cli@1.3.4`。用户缓存目录在本流程为`~/.cache`（Windows用用户目录下.cache）；也可复用系统安装，或用pnpm add --dir指向同一目录。仅安装所选平台，不强制先安装DWS。
3. 官方发行范围为macOS x64/arm64、Linux x64/arm64和Windows x64；Windows ARM64本流程未验证，不沿用DWS的六平台支持承诺。
4. unauthorized时，经用户要求接入后运行以下官方用户授权流程，不读取凭据文件、不索取Secret：

```bash
python scripts/wecom.py -- auth init --noninteractive --no-browser --output-qrcode <项目私有目录>/auth-qr.png
```

展示二维码供用户用企业微信扫码并完成机器人绑定。保持窗口后台；二维码约5分钟有效，过期后说明状态，仅用户准备好时重新发起。扫码或绑定未完成是外部阻塞，不能用模拟内容宣称真实接通。随后再次--check，必须返回authorized才执行业务命令。

## 能力发现与调用

下文的wecom-cli可统一替换为`python scripts/wecom.py --`。先执行`wecom-cli --help`，再查相应方法`--help`或`--schema`；服务目录和schema由服务端下发，查看业务帮助也需要授权与网络。命令参数优先采用当前schema，而非把DWS参数照搬。

通用JSON参数通过subprocess参数数组传入，不把用户文本拼入shell。用`--output <私有路径>`或subprocess捕获响应落盘；大正文可能另存file_path，必须实际读取文件才算拿到正文。`--page-count`输出NDJSON，逐行解析且核对末页has_more，达到页数上限不能视为完整。

## 会议读取

```bash
wecom-cli meeting list --help
wecom-cli meeting get --help
wecom-cli meeting original get --help
```

- 从主题或日期定位真实会议。list支持begin_time和end_time（YYYY-MM-DD HH:mm:ss，需一起提供），cursor及limit；检索小范围默认最近30天，说明时区和范围，不自动全组织扫描。无记录不等于接口不可用，也不能证明有正文可读。
- list读取created_meetings与attended_meetings，保留meeting_id/sub_meeting_id，按对象ID去重。has_more=true用next_cursor翻页；token循环或错误时保留缺口。
- get使用`{"meeting_ids":[{"meeting_id":"真实ID"}]}`，每批最多10个对象；周期会议携带相应sub_meeting_id，不把9位会议号当API ID。
- 纪要和行动项位于meetings[].notes[].note_content/todo_content，结合has_note_permission判断。若正文为空，说明未生成/不可访问等实际状态，不能把会议元信息当纪要。
- 需要逐字原话、核对决定或自定义分析时，original get传meeting_id，必要时sub_meeting_id；不指定media_index即全部媒体段，用户明确第N段才传N-1。返回original_data含时间及说话人；has_more=true以next_cursor续拉并按序拼接。摘要不能代替转写。
- 无权限不绕过、不自动申请。空正文、部分分页、匿名或疑似错误发言人单独标记。

## 文档读取

先按链接类型或搜索结果确定对象，不猜docid。doc.weixin.qq.com/doc/对应普通doc，smartpage类型用smartpage方法，sheet/smartsheet分别走各自模块；不能把不同类型硬塞给doc contents get。

按名称找文档时先查看doc search --help，使用真实标题关键词且小批量定位。普通doc用`doc contents get`，参数docid及content_type（如markdown）；检查name/content/version/file_path。智能文档等根据当前schema调用对应读取方法。长正文落盘时核对文件存在并读入；图片或复杂表格未查看则标记缺口。

## 其他任务和写入

日程、待办、邮件、微盘、表格等按用户目标查对应help/schema及官方操作参考，再执行最小范围。先验证真实读取；写入另按用户授权，保存写前状态、使用实际支持的局部修改或追加并回读。不能以“加一段”代替用户要求的原段修改，更不能擅自全量覆盖。消息模块的机器人会话列表不是普通私聊/群聊历史，不据此承诺聊天读取。

通用整理见workflows.md，产品产物见pm-workflow.md。不自动启用机器人推送、发送消息、录制会议、创建任务或修改成员权限。

## 真实验收

环境可运行→authorized→业务列表返回→指定真实对象正文非空→分页/字段核对分别记录。空列表只算查询成功，尚未取得真实正文；任何auth失败或未完成时保持“待授权，业务数据未验证”。验证记录写tests/VALIDATION.md（仅无敏感信息摘要），原始数据只在项目.work-assistant/runs。验收读取一条最近可访问会议；没有合适会议时用一份用户指定或能明确定位的相关文档，不为测试制造业务记录。

官方来源：[CLI参考](https://github.com/WecomTeam/wecom-cli/blob/main/docs/cli-reference.md)、[会议列表](https://github.com/WecomTeam/wecom-cli/blob/main/skills/wecomcli-meeting/references/meeting-list.md)、[会议转写](https://github.com/WecomTeam/wecom-cli/blob/main/skills/wecomcli-meeting/references/meeting-original-get.md)、[文档](https://github.com/WecomTeam/wecom-cli/blob/main/skills/wecomcli-doc/SKILL.md)。
