# PM衔接与写回

## 移交

聊天由collect.py整理证据；听记保留DWS原始响应及分页证据（见 [听记读取](minutes.md)）。当前agent根据原文生成语义信息卡。需要持久化移交时用pm-handoff.json：
```json
{
  "source_packet":"evidence.json",
  "client_supplements":null,
  "coverage":{"scope":"会话和时间窗","remaining_gaps":[],"pagination_complete":false},
  "items":[{
    "id":"stable-topic-id","topic":"业务问题",
    "kind":"reported_fact|confirmed_decision|proposal|question|conflict|action",
    "statement":"内容与适用范围",
    "evidence":[{"message_id":"真实ID","time":"消息时间","source":"CLI或客户端"}],
    "limitations":[],
    "document_impact":{"target":null,"section":null,"proposed_change":null},
    "ready_for_prd":false
  }]
}
```

ready_for_prd需明确决定、适用条件及充分上下文，截图或单独“是”不足以置true。所有正文读到也可能无决策。建议、假设、转述不能自动升格为需求。

仅总结时在聊天交付；需要本地产物时用HTML展示结论/依据/缺口/文档影响，用户指定格式优先。包内 [PM工作流](pm-workflow.md) 负责需求、PRD、原型、流程和验收，不复制它的模板。不要在公开产物嵌入本机原始聊天或凭据。

听记依据在evidence中使用 `source_type: "minutes"`、`task_uuid`、`artifact`、`paragraph_id`、`start_ms`、`end_ms` 和 `url`，不伪造message_id。仅有AI摘要时标记artifact=summary；未核对的摘要和自动提取待办不能直接升级为已确认决定或实际派发任务。多来源移交可增加source_packets数组，逐项保留覆盖范围。

## 钉钉文档读取

根据用户链接提取真实节点ID，或按主题搜索定位。先检查本机 `dws doc read --help` 与 `dws doc block list --help`，读取正文；结构、图片或表格有缺口时按需补读。仅阅读不触发写回。

## 钉钉文档局部写回

1. 用户链接或已确认映射确定目标；不默认写入旧测试文档。读取正文与块列表，检查现行规则。
2. 准备目标块、原文、新文及消息依据，保存写前快照。写前再读比较；变化后重算，不能覆盖过时内容。
3. 用户已要求写回且依据充分时执行doc block update，只改明确块。仅运行读取skill不授予文档写权限，不反复确认已有授权。
4. 回读验证目标文本和其他块。CLI回读不是视觉验证；复杂图片表格核对实际结构，有损Markdown不是完整备份。
5. 此流程未验证原子条件写，写前检查仍有并发窗口。发现冲突停止后续写入，不能自动回滚覆盖他人改动。记录文档、块、写前后、来源和结果。
6. 按本轮范围用现有PM流程同步相关产物；不因聊天提到一个项目就修改该项目。
