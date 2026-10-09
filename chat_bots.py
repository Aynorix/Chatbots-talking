"""Run a fixed-round conversation between two OpenAI SDK chat models."""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass

from openai import OpenAI


BOT_PROMPTS = {
    "Bot A": (
        "You are Bot A in a two-bot conversation. Be curious, constructive, and clear. "
        "Build on the other bot's most recent point and add a useful new idea. Keep "
        "your reply to about 100 words."
    ),
    "Bot B": (
        "You are Bot B in a two-bot conversation. Be thoughtful and analytical. "
        "Respond directly to the other bot, question assumptions when useful, and "
        "move the discussion forward. Keep your reply to about 100 words."
    ),
}


def load_local_env() -> None:
    """Load simple KEY=VALUE settings from a local .env file without overwriting the shell."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    try:
        with open(env_path, encoding="utf-8") as env_file:
            for line in env_file:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip("\"'")
                if key:
                    os.environ.setdefault(key, value)
    except FileNotFoundError:
        pass


class ConfigurationError(Exception):
    """Raised when a bot is missing a required provider setting."""


@dataclass
class Bot:
    name: str
    model: str
    client: OpenAI
    system_prompt: str

    def reply(self, seed: str, transcript: list[tuple[str, str]]) -> str:
        conversation = [f"Seed message: {seed}"]
        conversation.extend(f"{speaker}: {message}" for speaker, message in transcript)
        prompt = (
            "Continue the conversation below. Reply as yourself, without repeating "
            "your name or describing these instructions.\n\n"
            + "\n\n".join(conversation)
        )
        result = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        message = result.choices[0].message.content
        if not message or not message.strip():
            raise RuntimeError(f"{self.name} returned an empty response.")
        return message.strip()


def setting(bot: str, key: str, shared_key: str | None = None) -> str:
    """Read a bot-specific setting, falling back to a shared setting."""
    bot_key = f"BOT_{bot}_{key}"
    return os.getenv(bot_key, "").strip() or (
        os.getenv(shared_key, "").strip() if shared_key else ""
    )


def create_bot(name: str) -> Bot:
    short_name = name[-1]
    model = setting(short_name, "MODEL") or os.getenv("OPENAI_MODEL", "").strip()
    api_key = setting(short_name, "API_KEY", "OPENAI_API_KEY")
    base_url = setting(short_name, "BASE_URL", "OPENAI_BASE_URL")
    missing = []
    if not model:
        missing.append(f"BOT_{short_name}_MODEL")
    if not api_key:
        missing.append(f"BOT_{short_name}_API_KEY")
    if missing:
        raise ConfigurationError(
            f"{name} is missing {', '.join(missing)}. See the README for setup."
        )

    client = OpenAI(api_key=api_key, base_url=base_url or None)
    return Bot(name=name, model=model, client=client, system_prompt=BOT_PROMPTS[name])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Have two language-model bots discuss a topic for a fixed number of rounds."
    )
    parser.add_argument("--seed", help="starting message for the conversation")
    parser.add_argument(
        "--rounds", type=int, help="number of rounds; each round contains one reply from each bot"
    )
    return parser.parse_args()


def prompt_for_inputs(args: argparse.Namespace) -> tuple[str, int]:
    seed = args.seed or input("Enter the seed message for the bots: ").strip()
    if not seed:
        raise ValueError("The seed message cannot be empty.")

    rounds = args.rounds
    if rounds is None:
        while True:
            raw_rounds = input("How many conversation rounds? [3]: ").strip()
            if not raw_rounds:
                rounds = 3
                break
            try:
                rounds = int(raw_rounds)
            except ValueError:
                print("Enter a whole number, such as 3.")
                continue
            if rounds > 0:
                break
            print("Enter a number greater than zero.")
    if rounds < 1:
        raise ValueError("The number of rounds must be at least 1.")
    return seed, rounds


def run(seed: str, rounds: int, bot_a: Bot, bot_b: Bot) -> int:
    transcript: list[tuple[str, str]] = []
    print("\nTwo-bot conversation")
    print(f"Seed: {seed}")
    print(f"Rounds: {rounds} ({rounds * 2} bot replies)\n")

    for round_number in range(1, rounds + 1):
        print(f"--- Round {round_number}/{rounds} ---")
        for bot in (bot_a, bot_b):
            try:
                response = bot.reply(seed, transcript)
            except Exception as exc:
                print(f"\nError while requesting a reply from {bot.name}: {exc}", file=sys.stderr)
                return 1
            transcript.append((bot.name, response))
            print(f"{bot.name} ({bot.model}):\n{response}\n")
    return 0


def main() -> int:
    load_local_env()
    args = parse_args()
    try:
        seed, rounds = prompt_for_inputs(args)
        bot_a = create_bot("Bot A")
        bot_b = create_bot("Bot B")
    except (ConfigurationError, ValueError, EOFError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    return run(seed, rounds, bot_a, bot_b)


if __name__ == "__main__":
    raise SystemExit(main())
