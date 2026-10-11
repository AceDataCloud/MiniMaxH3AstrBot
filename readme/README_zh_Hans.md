# AstrBot MiniMax H3 视频插件

通过您自己的 Ace Data Cloud 账号，在 AstrBot 对话中生成一条 MiniMax H3 视频。`minimax_h3_generate_video` 提交一次文生或首帧图生视频任务，`minimax_h3_get_task` 用同一个任务 ID 查询最终结果。

[English guide](../README.md) · [MiniMax H3 视频接口](https://platform.acedata.cloud/documents/minimax-videos) · [任务接口](https://platform.acedata.cloud/documents/minimax-tasks) · [当前价格](https://platform.acedata.cloud/services/minimax)

## 查找与安装

在 AstrBot WebUI 中打开 **扩展 → 插件 → AstrBot 插件市场**，搜索 **MiniMax H3**。核对卡片名称 **MiniMax H3 by Ace Data Cloud**、作者 **acedatacloud** 和[当前 MiniMax 服务图标](https://cdn.acedata.cloud/2440b75bb8.png)，安装后在**已安装**页检查加载状态。

官方 AstrBot Cloud 上架仍待完成。源码合并后，可通过**已安装 → 安装 (+) → 从 URL 安装**并填写 `https://github.com/AceDataCloud/MiniMaxH3AstrBot` 预览。通过 URL 安装不代表已在官方市场上架。

## 配置密钥

在 [Ace Data Cloud 应用管理](https://platform.acedata.cloud/console/applications)复制生成 API Key，或创建同时允许 `/minimax/videos` 与 `/minimax/tasks` 的 Key。提交前核对当前每秒价格、时长、分辨率和余额。将 Key 填入插件的 **Ace Data Cloud generation API key with MiniMax H3 access** 配置项，不要添加 `Bearer `，也不要使用 `platform-...` 管理令牌。AstrBot WebUI 会遮蔽显示此字段，但原值保存在数据目录中，请保护该目录。

选择支持工具调用的对话模型，并在当前对话的 profile 与 persona 中允许两个 MiniMax H3 工具。

## 生成一次，然后查询

可以对机器人说：

> 用 `minimax_h3_generate_video` 生成一条黄色纸风筝从绿色草地升起的视频。4 秒、768P、16:9。只提交一次并告诉我任务 ID。

工具会异步提交一次 `POST /minimax/videos` 请求，返回 `status: submitted` 和任务 ID。这时还不能认为视频已完成。保存 ID，随后说：

> 用 `minimax_h3_get_task` 查询准确的任务 ID `<task_id>`，告诉我状态与最终视频链接，不要重新生成。

如果仍是 pending，稍后继续查询同一个 ID。只有 `status: succeeded`、`success: true` 和最终 HTTPS 视频链接同时出现才算完成。插件不会自动重试付费提交。

模型固定为 `MiniMax-H3`。首版支持文生视频和一张您有权处理的 HTTPS `image_url` 首帧图。时长 4–15 秒，分辨率为 `768P` 或 `2K`。留空 `ratio` 时，文生视频选 16:9，首帧图生视频随图片自适应；文生视频也可明确选择文档支持的固定比例。任务结果返回输出秒数，实际 Credits 请看用量记录。多图、参考视频、音频和其他多模态控制尚未覆盖。

## 核验与排查

在 Ace Data Cloud 用量记录中优先按返回的任务 ID 或 trace ID 核对。`task.usage.output_seconds` 是计费用量，不是已扣积分；实际费用以实时用量记录为准。任务查询只读取已有任务，不会再次生成。

| 现象 | 检查 |
| --- | --- |
| 插件加载失败 | AstrBot 版本、**加载失败的插件**和**数据与日志 → 日志**。 |
| 看不到工具 | 插件启用、当前 profile 与 persona 允许两个工具、对话模型支持工具调用。 |
| HTTP 401/403 | Key 类型、两个 API 路径的权限和账号访问权限。 |
| 提交后网络报错 | 再次生成前先看请求历史；超时也可能已创建付费任务。 |
| 任务仍在进行 | 稍后查询同一个任务 ID。 |
| 任务失败 | 用任务 ID 查请求历史。 |

Key 只会发送到 `https://api.acedata.cloud`，重定向会被拒绝。插件只把最终视频链接和公开的输出用量交给对话模型，不返回内部原始数据。运行时仅用 Python 标准库。

## 验收与品牌图标

在官方 AstrBot `v4.28.2` 的隔离实例中，editable 安装成功注册两个工具。ChatUI 用 `MiniMax-H3`、4 秒、768P 提交了一次文生视频任务，并查询同一个 ID 一次，没有重复生成。任务返回 `succeeded`、输出 4 秒；最终 MP4 返回 HTTP 200，H.264 视频和 AAC 音频，1344×768、4.458 秒。准确的提交 trace ID 对应一条成功的 `/minimax/videos` 用量记录，原价 2.40283288 Credits、实扣 2.162549592 Credits。见[脱敏实测证据](../tests/e2e-results.json)。首帧图及其他设置仅做结构校验，未实际生成。这只是本地 editable 安装；Cloud 审核、市场安装以及市场包的首次调用仍待完成。

`logo.png` 是[当前 MiniMax 服务图标](https://cdn.acedata.cloud/2440b75bb8.png)的原文件，128×128，SHA-256 为 `154514d088b3a8d98d1279f6ede93fd5b593a21038f4530ea1bb551a8045ed02`。
