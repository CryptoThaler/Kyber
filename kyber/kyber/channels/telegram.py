"""KYBER Telegram Channel — Bridges Telegram messages to Kyber tasks and
forwards algedonic signals (pain/pleasure) to Telegram chats.

Usage:
    from kyber import Kyber
    from kyber.channels.telegram import TelegramChannel, TelegramConfig

    kyber = Kyber()
    # ... spawn agents ...

    config = TelegramConfig(bot_token="123:ABC", allowed_chat_ids={-100123})
    channel = TelegramChannel(kyber, config)
    channel.run()  # blocking — starts polling
"""
from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Set

from kyber.core.vsm import AlgedonicSignal

logger = logging.getLogger("kyber.channels.telegram")


@dataclass
class TelegramConfig:
    """Configuration for the Kyber Telegram channel."""

    # Required — obtain from @BotFather on Telegram
    bot_token: str = field(default_factory=lambda: os.environ.get("KYBER_TELEGRAM_BOT_TOKEN", ""))

    # Security: only process messages from these chat IDs.
    # Empty set = accept all (NOT recommended for production).
    allowed_chat_ids: Set[int] = field(default_factory=lambda: _parse_chat_ids(
        os.environ.get("KYBER_TELEGRAM_ALLOWED_CHATS", "")))

    # Chat ID where algedonic (pain/pleasure) signals are forwarded.
    # If empty, signals are not forwarded.
    alerts_chat_id: Optional[int] = field(default_factory=lambda: _parse_optional_int(
        os.environ.get("KYBER_TELEGRAM_ALERTS_CHAT", "")))

    # Default task type for free-text messages (no /command prefix)
    default_task_type: str = field(default_factory=lambda:
        os.environ.get("KYBER_TELEGRAM_DEFAULT_TASK", "prompt"))

    # Forward pain signals at or above this severity to Telegram
    alert_min_severity: int = field(default_factory=lambda: int(
        os.environ.get("KYBER_TELEGRAM_ALERT_MIN_SEVERITY", "5")))

    # Maximum message length before truncation
    max_response_length: int = 4096

    # Polling interval in seconds (only used in polling mode)
    poll_interval: float = 1.0

    def validate(self):
        """Raise ValueError if configuration is invalid."""
        if not self.bot_token:
            raise ValueError(
                "bot_token is required. Set KYBER_TELEGRAM_BOT_TOKEN env var "
                "or pass bot_token= to TelegramConfig."
            )
        if self.alert_min_severity < 1 or self.alert_min_severity > 10:
            raise ValueError("alert_min_severity must be between 1 and 10")


def _parse_chat_ids(raw: str) -> Set[int]:
    """Parse comma-separated chat IDs from env var."""
    if not raw.strip():
        return set()
    return {int(cid.strip()) for cid in raw.split(",") if cid.strip()}


def _parse_optional_int(raw: str) -> Optional[int]:
    """Parse an optional integer from env var."""
    return int(raw) if raw.strip() else None


class TelegramChannel:
    """Bridges a Telegram bot to a Kyber instance.

    Inbound: Telegram messages become Kyber tasks routed through S2.
    Outbound: Algedonic signals are forwarded to a Telegram alerts chat.

    Commands:
        /task <type> <message>  — submit a typed task
        /status                 — show Kyber system status
        /agents                 — list registered agents
        /help                   — show available commands
        (free text)             — submit as default_task_type
    """

    def __init__(self, kyber: Any, config: Optional[TelegramConfig] = None):
        self.kyber = kyber
        self.config = config or TelegramConfig()
        self.config.validate()
        self._app = None
        self._custom_handlers: Dict[str, Callable] = {}

    def register_command(self, command: str, handler: Callable):
        """Register a custom /command handler.

        Handler signature: async def handler(kyber, chat_id, args_text) -> str
        """
        self._custom_handlers[command] = handler

    async def _setup(self):
        """Initialize the python-telegram-bot application."""
        from telegram import Update
        from telegram.ext import (
            ApplicationBuilder,
            CommandHandler,
            MessageHandler,
            filters,
        )

        self._app = (
            ApplicationBuilder()
            .token(self.config.bot_token)
            .build()
        )

        # Built-in commands
        self._app.add_handler(CommandHandler("start", self._cmd_start))
        self._app.add_handler(CommandHandler("help", self._cmd_help))
        self._app.add_handler(CommandHandler("status", self._cmd_status))
        self._app.add_handler(CommandHandler("agents", self._cmd_agents))
        self._app.add_handler(CommandHandler("task", self._cmd_task))

        # Custom commands
        for cmd, handler in self._custom_handlers.items():
            self._app.add_handler(CommandHandler(cmd, self._make_custom_handler(handler)))

        # Free-text messages → default task type
        self._app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message)
        )

        # Wire algedonic bus → Telegram alerts
        if self.config.alerts_chat_id:
            self.kyber.bus.subscribe(self._forward_signal)

        logger.info("Telegram channel initialized (bot token: ...%s)", self.config.bot_token[-4:])

    def _is_allowed(self, chat_id: int) -> bool:
        """Check if a chat is in the allow-list (empty = allow all)."""
        if not self.config.allowed_chat_ids:
            return True
        return chat_id in self.config.allowed_chat_ids

    # ── Commands ──────────────────────────────────────────────

    async def _cmd_start(self, update, context):
        if not self._is_allowed(update.effective_chat.id):
            return
        await update.message.reply_text(
            "Kyber Agent OS connected.\n"
            "Send a message to submit a task, or use /help for commands."
        )

    async def _cmd_help(self, update, context):
        if not self._is_allowed(update.effective_chat.id):
            return
        lines = [
            "Kyber Telegram Commands:",
            "",
            "/task <type> <message> — submit a typed task",
            "/status — system status",
            "/agents — list agents",
            "/help — this message",
            "",
            "Send any text to submit as a task.",
        ]
        if self._custom_handlers:
            lines.append("\nCustom commands:")
            for cmd in sorted(self._custom_handlers):
                lines.append(f"  /{cmd}")
        await update.message.reply_text("\n".join(lines))

    async def _cmd_status(self, update, context):
        if not self._is_allowed(update.effective_chat.id):
            return
        import json
        status = self.kyber.status()
        text = json.dumps(status, indent=2, default=str)
        await update.message.reply_text(f"```\n{text[:self.config.max_response_length]}\n```",
                                        parse_mode="Markdown")

    async def _cmd_agents(self, update, context):
        if not self._is_allowed(update.effective_chat.id):
            return
        agents = self.kyber.coordinator._agents
        if not agents:
            await update.message.reply_text("No agents registered.")
            return
        lines = []
        for agent in agents.values():
            status = "alive" if agent.state.is_alive else "dead"
            health = "healthy" if agent.state.is_healthy else "distressed"
            lines.append(
                f"• {agent.identity.name} [{agent.identity.vsm_level.name}] "
                f"— {status}/{health}, tasks: {agent.state.task_count}"
            )
        await update.message.reply_text("\n".join(lines))

    async def _cmd_task(self, update, context):
        if not self._is_allowed(update.effective_chat.id):
            return
        args = update.message.text.split(maxsplit=2)
        if len(args) < 3:
            await update.message.reply_text("Usage: /task <type> <message>")
            return
        task_type = args[1]
        message = args[2]
        result = await self.kyber.run(
            task_type=task_type,
            payload={"details": message, "source": "telegram",
                     "chat_id": update.effective_chat.id}
        )
        await self._send_result(update, result)

    async def _handle_message(self, update, context):
        """Handle free-text messages as tasks."""
        if not self._is_allowed(update.effective_chat.id):
            return
        text = update.message.text
        if not text.strip():
            return
        result = await self.kyber.run(
            task_type=self.config.default_task_type,
            payload={"details": text, "source": "telegram",
                     "chat_id": update.effective_chat.id}
        )
        await self._send_result(update, result)

    async def _send_result(self, update, result):
        """Format and send a TaskResult back to Telegram."""
        if result is None:
            await update.message.reply_text("No agent available to handle this task.")
            return
        if result.success:
            output = str(result.output) if result.output else "(no output)"
            if len(output) > self.config.max_response_length:
                output = output[:self.config.max_response_length - 20] + "\n... (truncated)"
            await update.message.reply_text(output)
        else:
            await update.message.reply_text(f"Task failed: {result.error}")

    # ── Algedonic signal forwarding ──────────────────────────

    async def _forward_signal(self, signal: AlgedonicSignal):
        """Forward algedonic signals to the alerts chat."""
        if signal.severity < self.config.alert_min_severity:
            return
        if not self._app or not self.config.alerts_chat_id:
            return
        emoji = signal.emoji
        text = (
            f"{emoji} Kyber {signal.signal_type.upper()} (sev {signal.severity}/10)\n"
            f"Source: {signal.source_id} [{signal.source_level.name}]\n"
            f"{signal.message}"
        )
        try:
            await self._app.bot.send_message(
                chat_id=self.config.alerts_chat_id,
                text=text
            )
        except Exception as e:
            logger.error("Failed to forward signal to Telegram: %s", e)

    # ── Custom handler wrapper ───────────────────────────────

    def _make_custom_handler(self, handler: Callable):
        async def wrapper(update, context):
            if not self._is_allowed(update.effective_chat.id):
                return
            args_text = update.message.text.split(maxsplit=1)
            args_text = args_text[1] if len(args_text) > 1 else ""
            try:
                response = await handler(self.kyber, update.effective_chat.id, args_text)
                if response:
                    await update.message.reply_text(str(response)[:self.config.max_response_length])
            except Exception as e:
                await update.message.reply_text(f"Error: {e}")
        return wrapper

    # ── Run ───────────────────────────────────────────────────

    def run(self):
        """Start the bot in polling mode (blocking)."""
        async def _run():
            await self._setup()
            await self._app.initialize()
            await self._app.start()
            await self._app.updater.start_polling(poll_interval=self.config.poll_interval)
            logger.info("Kyber Telegram bot is running (polling)...")
            # Keep running until interrupted
            stop_event = asyncio.Event()
            try:
                await stop_event.wait()
            except (KeyboardInterrupt, asyncio.CancelledError):
                pass
            finally:
                await self._app.updater.stop()
                await self._app.stop()
                await self._app.shutdown()

        asyncio.run(_run())

    async def start_async(self):
        """Start the bot in polling mode (non-blocking, for use within an existing event loop)."""
        await self._setup()
        await self._app.initialize()
        await self._app.start()
        await self._app.updater.start_polling(poll_interval=self.config.poll_interval)
        logger.info("Kyber Telegram bot started (async polling)...")

    async def stop_async(self):
        """Stop the bot gracefully."""
        if self._app:
            await self._app.updater.stop()
            await self._app.stop()
            await self._app.shutdown()
            logger.info("Kyber Telegram bot stopped.")
