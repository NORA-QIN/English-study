#!/usr/bin/env python3
"""Send one vocabulary card and its pronunciation to Feishu."""

import argparse
import json
import subprocess
import sys
import urllib.request
from pathlib import Path


WORD = {
    "word": "streamline",
    "pos": "动词",
    "ipa": "/ˈstriːmlaɪn/",
    "meaning": "简化流程；提高效率；使更顺畅",
    "examples": [
        ("We need to streamline the approval process.", "我们需要简化审批流程。"),
        ("This tool streamlines our daily workflow.", "这个工具让我们的日常工作流程更高效。"),
    ],
    "note": "常用于工作、产品和管理场景，强调去除不必要环节，从而提高效率。",
    "story": "streamline 原本是空气动力学用语，指让物体拥有更流畅、阻力更小的外形，后来引申为让流程更顺畅高效。",
}

RECIPIENT = "ou_1e1e2666fc3399795415396f908c30d0"


def run(*args: str) -> None:
    subprocess.run(list(args), check=True)


def find_audio(word: str, destination: Path) -> None:
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    try:
        with urllib.request.urlopen(url, timeout=8) as response:
            entries = json.load(response)
        for entry in entries:
            for item in entry.get("phonetics", []):
                audio = item.get("audio")
                if audio:
                    urllib.request.urlretrieve(audio, destination)
                    return
    except Exception as exc:
        print(f"在线发音源暂不可用（{exc}），测试改用 macOS 系统 TTS。", file=sys.stderr)
    # Fallback keeps the prototype testable offline; production can require online audio.
    aiff = destination.with_suffix(".aiff")
    run("say", "-o", str(aiff), word)
    subprocess.run(["ffmpeg", "-y", "-i", str(aiff), str(destination)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def card_text(data: dict) -> str:
    examples = "\n".join(f"- {en}\n  {zh}" for en, zh in data["examples"])
    return (
        f"📚 每日英语词汇\n\n"
        f"**{data['word']}**（{data['pos']}）\n"
        f"读音：{data['ipa']}\n"
        f"含义：{data['meaning']}\n\n"
        f"例句：\n{examples}\n\n"
        f"使用提醒：{data['note']}\n\n"
        f"来历：{data['story']}\n\n"
        f"小测验：We are ________ the customer registration process."
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--user-id", default=RECIPIENT)
    parser.add_argument("--word", default=WORD["word"])
    parser.add_argument("--send", action="store_true", help="actually send to Feishu")
    args = parser.parse_args()

    data = dict(WORD)
    data["word"] = args.word
    runtime = Path("runtime")
    runtime.mkdir(exist_ok=True)
    mp3 = runtime / f"{args.word}.mp3"
    opus = runtime / f"{args.word}.opus"
    find_audio(args.word, mp3)
    subprocess.run(["ffmpeg", "-y", "-i", str(mp3), "-c:a", "libopus", "-b:a", "48k", str(opus)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    text = card_text(data)
    print(text)
    print(f"音频已准备：{opus}")
    if args.send:
        run("lark-cli", "im", "+messages-send", "--as", "bot", "--user-id", args.user_id, "--markdown", text, "--idempotency-key", f"vocab-text-{args.word}")
        run("lark-cli", "im", "+messages-send", "--as", "bot", "--user-id", args.user_id, "--audio", str(opus), "--idempotency-key", f"vocab-audio-{args.word}")
        print("已发送文字和语音到飞书。")
    else:
        print("当前为 dry-run；加 --send 才会发送。")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"错误：{exc}", file=sys.stderr)
        raise SystemExit(1)
