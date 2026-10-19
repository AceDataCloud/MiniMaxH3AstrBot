# MiniMax H3 video for AstrBot

Generate one MiniMax H3 video in an AstrBot conversation through your own Ace Data Cloud account. `minimax_h3_generate_video` submits one text or first-frame video job; `minimax_h3_get_task` queries the same task until its final video is ready.

This independent **MiniMax H3 integration is provided by Ace Data Cloud**; it is not an official plugin from the MiniMax H3 publisher or the AstrBot team. Use your own Ace API key.

[简体中文指南](readme/README_zh_Hans.md) · [MiniMax H3 Videos API](https://platform.acedata.cloud/documents/minimax-videos?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=minimaxh3astrbot_readme_documents_minimax_videos) · [Tasks API](https://platform.acedata.cloud/documents/minimax-tasks?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=minimaxh3astrbot_readme_documents_minimax_tasks) · [Current prices](https://platform.acedata.cloud/services/minimax?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=minimaxh3astrbot_readme_services_minimax)

## 1. Find and install

Current upstream navigation is **Plugins → Plugins → Plugin Market / Installed**; older English versions may label the section Extensions. Search **MiniMax H3** and verify **MiniMax H3 by Ace Data Cloud**, author **acedatacloud**, and the matching service icon.

**Publication status on 2026-10-19: not publicly listed in the official market.** The market search/install instructions above apply after publication. For the current preview, use the repository path below rather than waiting for a card that is not there.

Repository installation: **Plugins → Plugins → Installed → Install Plugin (+) → Install from URL**, with `https://github.com/AceDataCloud/MiniMaxH3AstrBot`. Source is already available. Confirm it is enabled and loaded. A repository/file installation is a separate path from official market installation.

## Configure your key

New account? Register and sign in first. If the Applications page has no General application yet, choose **Initialize General Application**, then continue with the key steps below.

In [Ace Data Cloud Applications](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=minimaxh3astrbot_readme_api_key), copy a generation API key from your General application or create a key that permits both `/minimax/videos` and `/minimax/tasks`. Check current per-second pricing, duration, resolution, and balance before submitting. Paste the key into the plugin's **Ace Data Cloud generation API key with MiniMax H3 access** setting. Do not add `Bearer ` or use a `platform-...` management token. AstrBot masks the field in WebUI but stores the original value in its data directory, which should be protected.

Select a chat model that supports tool calling. Allow both MiniMax H3 tools in the conversation's profile and persona.

### Token screenshots: copy or create a dedicated key

[Register or sign in to Ace](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=minimaxh3astrbot_readme_signup), then open **Applications → General application** and initialize it if absent. Use **1** to copy the selected key, or **2 Manage Keys → Create** for a dedicated key. If Allowed APIs is enabled, include `/minimax/tasks` and `/minimax/videos`; check current entitlement, balance and prices before use.

![Copy an Ace key or open Manage Keys (redacted)](_assets/tutorial/get-api-key-en.png)

Use a name such as `AstrBot MiniMax H3` and set expiry/limits as needed. The screenshot’s `Dify tutorial` is an older example, not a required label.

![Create an optional dedicated API key (shared Ace page, not AstrBot)](_assets/tutorial/create-api-key-en.png)

Images were reused and checked on **2026-10-19**; original capture dates are unknown. Credentials, App ID and balance are redacted. This is the shared Ace Applications UI, not proof of AstrBot installation or a live service call. [Image sources and limits](_assets/tutorial/sources.json).

### Where to paste it in AstrBot

Open **Plugins → Plugins → Installed**, select the gear (**Plugin Configuration**) on **MiniMax H3 by Ace Data Cloud**, paste the key into **Ace Data Cloud generation API key with MiniMax H3 access** (stored field `api_key`), and save. Paste the key only, with no `Bearer ` prefix; never put it in model-provider settings or a chat prompt. UI masking does not encrypt the data-directory config. These are exact text steps; no fabricated settings image is used.

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
