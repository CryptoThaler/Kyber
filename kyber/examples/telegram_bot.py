#!/usr/bin/env python3
"""Kyber Telegram Bot — Example

Connects a Kyber agent fleet to Telegram so users can submit tasks
and receive algedonic alerts via chat.

Setup:
    1. Copy .env.example to .env and set KYBER_TELEGRAM_BOT_TOKEN
    2. pip install kyber-agent[telegram]
    3. python examples/telegram_bot.py

Telegram commands:
    /start              — greeting
    /help               — list commands
    /task <type> <msg>  — submit a typed task
    /status             — Kyber system status
    /agents             — list registered agents
    (any text)          — submit as "prompt" task
"""
import os
import sys

# Load .env if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from kyber import Kyber
from kyber.channels.telegram import TelegramChannel, TelegramConfig


def main():
    token = os.environ.get("KYBER_TELEGRAM_BOT_TOKEN", "")
    if not token:
        print("Error: Set KYBER_TELEGRAM_BOT_TOKEN in .env or environment.")
        sys.exit(1)

    # Build Kyber fleet
    kyber = Kyber()
    kyber.spawn("assistant", capabilities={"prompt", "think", "summarize"})
    kyber.spawn("coder", capabilities={"code_review", "code_gen", "debug"})

    # Configure Telegram channel
    config = TelegramConfig()  # reads from env vars
    channel = TelegramChannel(kyber, config)

    # Optional: register a custom command
    async def ping_handler(kyber_instance, chat_id, args):
        status = kyber_instance.status()
        return f"Pong! Uptime: {status['uptime_s']}s, Agents: {len(kyber_instance.coordinator._agents)}"

    channel.register_command("ping", ping_handler)

    print(f"Starting Kyber Telegram bot...")
    print(f"  Agents: {len(kyber.coordinator._agents)}")
    print(f"  Bot token: ...{token[-4:]}")
    print(f"  Press Ctrl+C to stop")
    channel.run()


if __name__ == "__main__":
    main()
