# AI听记读取

适用于会议听记、会议纪要、摘要、逐字稿、发言内容及会议行动项。复用官方DWS的只读聚合命令，不把听记当聊天消息，也不要求用户先复制正文。

## 工具与范围

通过scripts/dws_runtime.py的resolve_cli()定位已校验的DWS；不存在时按SKILL.md安装。以下dws指该可执行文件，不假定系统PATH已有安装。本流程在v1.0.63实测；升级后先查本机help，在线文档参数可能与本机版本不同。

- 有听记链接时自动从`/app/transcribes/<taskUuid>`或查询参数`taskUuid`提取ID；不要把完整URL传给--id，也不猜ID。
- 无链接时按用户给定主题、时间和范围查列表。未指定范围先查我创建的最近5条；没有匹配再查共享给我的范围，确有需要才扩展全部可访问，不直接下载全部会议正文。
- 多条候选有歧义时展示标题、时间供选择；用户要求测试时可以选最近一条可访问样本并说明选择。状态未完成、无权限或空列表不能当作正文读取成功。

## 查找

```bash
dws minutes +list-mine --limit 5 --format json
dws minutes +list-shared --help
dws minutes +search --help
```

按主题、日期或全部可访问范围查找时，根据`+search --help`组装参数。列表检查data.minutes、data.complete及meta.pagination；达到预览/页数限制只代表当前范围不完整，不能说历史已读全。不因当前账号只有一条自建记录就说公司只有一场会议。

## 读取所需产物

```bash
# 会议讲了什么：摘要及基础定位
dws minutes +detail --id <taskUuid> --artifacts basic,summary --format json
# 关键词和已提取行动项
dws minutes +detail --id <taskUuid> --artifacts basic,keywords,todos --format json
# 核对原话、决定、完整会议记录时才读取转写
dws minutes +detail --id <taskUuid> --artifacts basic,summary,keywords,transcript,todos --page-limit 100 --format json
```

`+detail`默认自动追完逐字稿分页，保留逐项失败。输出大时用Python subprocess捕获stdout/stderr到项目`.work-assistant/runs/dingtalk/<唯一运行目录>/`，不要把完整响应直接打印到对话。原始响应目录在POSIX设0700、文件0600；不把真实会议数据、签名链接或登录态放入skill、公开产物或提交包。摘要可能带有含签名的图片URL，对外展示时剔除凭据，不把“读到图片链接”当成看过图片。

无需重新实现官方分页器。需要纯转写时用`minutes +transcript --id <taskUuid>`；单页排查使用`minutes get transcription --id <taskUuid> --cursor <nextToken>`，当前版本参数是--cursor。原子接口首页最多50段，检查result.nextToken/hasNext继续读取；出现重复token、空页却有下一页、页数上限或中途错误时记录缺口，不把已有片段当全文。

## 检查响应与真实内容

单ID的`+detail`实测响应直接在顶层返回basic/summary/keywords/todos/transcript，并非所有命令都套data；列表则有ok/data/meta。按实际结构读取，不把格式未知当成空结果。

1. 命令退出码、顶层complete/failureCount与各产物success、dingOpenErrcode都需检查。success和错误码在不同产物里可能为布尔/数字或字符串。失败时保留已获得数据和错误，不反复重试权限错误，也不自动申请权限。
2. basic.result含标题、起止时间、duration（毫秒）、URL；按用户时区呈现日期。
3. summary.result.fullSummary为AI摘要；keywords.result.keywords为关键词；检查实际内容是否为空及是否仍在生成。
4. todos.result.items及itemCount为规范化行动项；actions与dingtalkTodoList可能是同一批事项的重复表示，不叠加计数。自动提取待办不等于已派发的钉钉任务，负责人/截止时间未返回时不补造。
5. transcript检查complete、pages、paragraphCount、duplicateCount及paragraphList实际长度。逐段保留paragraphId、startTime/endTime（相对毫秒）、paragraph、nickName/speakerDisplay等字段。检查ID冲突、空正文、时间范围；读取开头、中段和末段确认内容可用。接口分页读全仅证明取全了服务端可用转写，不证明录音每一秒都有文字或识别完全准确。
6. 发言人标记可能匿名、合并或错误，不能用标签数量或AI摘要“参与人”推断完整参会名单。摘要中的决定、责任人和期限用于需求变更前应回看相关原话；无法确认时标记“AI摘要提取，待核对”。

## 整理与权限边界

使用SKILL.md的信息卡规则，将事实、决定、建议、待确认、冲突和行动项分开。依据附听记标题/日期、taskUuid、链接、产物类型；引用原话另附段落ID和相对时间。结合聊天或文档时逐项保留来源，会议日期不能误写为读取日期。

本路由只读取。不因读到了行动项就创建待办，不因推断姓名就修改发言人，不自动更新纪要、开启录音、生成导图、申请/分享权限或发送消息。用户另有明确操作要求时再检查对应命令和已有授权；读取权限不代表写入权限。

官方参考：[DWS听记指南](https://github.com/DingTalk-Real-AI/dingtalk-workspace-cli/blob/main/skills/multi/dingtalk-minutes/references/minutes.md)。执行参数以本机help和实际响应为准。
