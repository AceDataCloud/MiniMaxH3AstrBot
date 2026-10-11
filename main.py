"""MiniMax H3 video tools for AstrBot through Ace Data Cloud."""

from __future__ import annotations

import json

from astrbot.api import AstrBotConfig
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star

from .client import MiniMaxH3Client, MiniMaxH3Error


class MiniMaxH3Plugin(Star):
    """Expose one video submission and one existing-task lookup tool."""

    def __init__(self, context: Context, config: AstrBotConfig) -> None:
        super().__init__(context)
        self.config = config

    @filter.llm_tool(name="minimax_h3_generate_video")
    async def minimax_h3_generate_video(
        self,
        event: AstrMessageEvent,
        prompt: str,
        duration: int = 4,
        resolution: str = "768P",
        ratio: str = "",
        image_url: str = "",
    ) -> str:
        """Submit one billable MiniMax H3 text or first-frame video job.

        Args:
            prompt(string): Description of the desired video.
            duration(number): 4–15 output seconds.
            resolution(string): 768P or 2K.
            ratio(string): Output ratio; empty picks 16:9 or image-adaptive.
            image_url(string): Optional authorized HTTPS first-frame image.

        Returns:
            JSON submission status and task ID, never a finished-video claim.
        """
        try:
            result = await MiniMaxH3Client(self.config.get("api_key", "")).submit(
                prompt, duration, resolution, ratio, image_url
            )
        except MiniMaxH3Error as exc:
            result = {"status": "error", "message": str(exc)}
        return json.dumps(result, ensure_ascii=False)

    @filter.llm_tool(name="minimax_h3_get_task")
    async def minimax_h3_get_task(self, event: AstrMessageEvent, task_id: str) -> str:
        """Query an existing MiniMax H3 task without generating another video.

        Args:
            task_id(string): Exact task ID from minimax_h3_generate_video.

        Returns:
            JSON task status and final video URL only after terminal success.
        """
        try:
            result = await MiniMaxH3Client(self.config.get("api_key", "")).query(
                task_id
            )
        except MiniMaxH3Error as exc:
            result = {"status": "error", "message": str(exc), "task_id": task_id}
        return json.dumps(result, ensure_ascii=False)
