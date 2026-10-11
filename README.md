# MiniMax H3 video for AstrBot

Generate one MiniMax H3 video in an AstrBot conversation through your own Ace Data Cloud account. `minimax_h3_generate_video` submits one text or first-frame video job; `minimax_h3_get_task` queries the same task until its final video is ready.

[简体中文指南](readme/README_zh_Hans.md) · [MiniMax H3 Videos API](https://platform.acedata.cloud/documents/minimax-videos) · [Tasks API](https://platform.acedata.cloud/documents/minimax-tasks) · [Current prices](https://platform.acedata.cloud/services/minimax)

## Find and install

In AstrBot WebUI, open **Extensions → Plugins → AstrBot Plugin Market** and search **MiniMax H3**. Confirm the card says **MiniMax H3 by Ace Data Cloud**, the author is **acedatacloud**, and the logo matches the [current MiniMax service icon](https://cdn.acedata.cloud/2440b75bb8.png). Install it, then check **Installed** for load errors.

The official AstrBot Cloud listing is pending. After the source release is merged, **Installed → Install (+) → Install from URL** with `https://github.com/AceDataCloud/MiniMaxH3AstrBot` can preview it. A URL installation does not prove market publication.

## Configure your key

In [Ace Data Cloud Applications](https://platform.acedata.cloud/console/applications), copy a generation API key from your General application or create a key that permits both `/minimax/videos` and `/minimax/tasks`. Check current per-second pricing, duration, resolution, and balance before submitting. Paste the key into the plugin's **Ace Data Cloud generation API key with MiniMax H3 access** setting. Do not add `Bearer ` or use a `platform-...` management token. AstrBot masks the field in WebUI but stores the original value in its data directory, which should be protected.

Select a chat model that supports tool calling. Allow both MiniMax H3 tools in the conversation's profile and persona.

## Generate once, then query

Ask the bot:

> Use `minimax_h3_generate_video` exactly once to make a yellow paper kite rising over a calm green meadow. Use 4 seconds, 768P, 16:9. Show me the task ID.

The tool sends one asynchronous `POST /minimax/videos` request and returns `status: submitted` with a task ID. Keep the ID and ask:

> Use `minimax_h3_get_task` with the exact task ID `<task_id>`. Tell me its status and final video URL. Do not generate another video.

If pending, query the same ID later. Only `status: succeeded`, `success: true`, and a final HTTPS video URL indicate completion. The plugin never retries a paid submission automatically.

The model is always `MiniMax-H3`. The first version supports text-to-video and one authorized HTTPS first-frame `image_url`. Duration is 4–15 seconds; resolution is `768P` or `2K`. Leave `ratio` blank for 16:9 text video or an image-adaptive ratio. For text video, an explicit ratio must be one of the documented fixed ratios. The completed task returns output seconds; check the usage page for actual Credits. Multi-image, reference video, audio, and other multimodal controls are outside this first version.

## Verify and troubleshoot

Match the returned task ID or trace ID in Ace Data Cloud usage when available. `task.usage.output_seconds` is a quantity, not a charged amount; confirm the live usage row before stating a cost. Task lookup reads an existing job and does not submit another generation.

| Symptom | Check |
| --- | --- |
| Plugin fails to load | AstrBot version, **Failed to Load Plugins**, and **Data & Logs → Logs**. |
| Tools are missing | Plugin enabled, both tools allowed in the active profile and persona, chat model supports tool calling. |
| HTTP 401/403 | Key type, both allowed API paths, and account access. |
| Network error after submission | Inspect request history before generating again; a timeout may already have created a paid task. |
| Pending task | Query the same task ID later. |
| Failed task | Use the task ID to inspect request history. |

The key goes only to `https://api.acedata.cloud`; redirects are rejected. The plugin exposes the final video URL and public output usage to the model, without raw internal data. It uses Python's standard library and needs no runtime package installation.

## Validation and brand asset

On official AstrBot `v4.28.2`, an isolated editable installation registered both tools. ChatUI submitted one `MiniMax-H3` 4-second 768P text video and queried the same task ID once, with no second generation. The task reported `succeeded` and four output seconds; the final MP4 responded HTTP 200 and decoded as H.264 video with AAC audio, 1344×768, 4.458 seconds. The exact submission trace matched one successful `/minimax/videos` usage row with 2.40283288 Credits original and 2.162549592 Credits deducted. See the [sanitized evidence](tests/e2e-results.json). First-frame image and other settings were validated structurally but not generated. This is a local editable installation; official Cloud review, market installation, and a first call from a market installation remain open.

`logo.png` is the unmodified 128×128 [current MiniMax service icon](https://cdn.acedata.cloud/2440b75bb8.png), SHA-256 `154514d088b3a8d98d1279f6ede93fd5b593a21038f4530ea1bb551a8045ed02`.
