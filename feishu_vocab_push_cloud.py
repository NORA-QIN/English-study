import json, os, subprocess, tempfile
from pathlib import Path
import requests
from gtts import gTTS

RECIPIENT = os.environ["FEISHU_RECIPIENT_OPEN_ID"]
BASE = "https://open.feishu.cn/open-apis"
HISTORY = Path("vocab_history.json")
WORDS = [
    ("streamline", "/ˈstriːmlaɪn/", "简化流程；提高效率", "工作中强调去除不必要环节。"),
    ("clarify", "/ˈklærəfaɪ/", "澄清；讲清楚", "clarify a point / clarify expectations。"),
    ("feasible", "/ˈfiːzəbəl/", "可行的", "常用于评估方案是否能实际完成。"),
    ("subtle", "/ˈsʌtəl/", "细微的；不明显的", "注意 b 不发音；常用于描述差异。"),
    ("overlook", "/ˌəʊvəˈlʊk/", "忽略；遗漏", "overlook a detail 是常见搭配。"),
]

def choose_word():
    used = set(json.loads(HISTORY.read_text()) if HISTORY.exists() else [])
    available = [item for item in WORDS if item[0] not in used]
    if not available:
        used.clear()
        available = WORDS
    return available[0]

def main():
    word, ipa, meaning, note = choose_word()
    token = requests.post(f"{BASE}/auth/v3/tenant_access_token/internal", json={
        "app_id": os.environ["FEISHU_APP_ID"],
        "app_secret": os.environ["FEISHU_APP_SECRET"],
    }).json()["tenant_access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    with tempfile.TemporaryDirectory() as d:
        mp3, opus = Path(d)/"word.mp3", Path(d)/"word.opus"
        gTTS(word, lang="en").save(str(mp3))
        subprocess.run(["ffmpeg", "-y", "-i", str(mp3), "-c:a", "libopus", "-b:a", "48k", str(opus)], check=True)
        text = (f"📚 每日英语词汇\n\n**{word}**\n读音：{ipa}\n含义：{meaning}\n\n"
                f"例句：We need to {word} the approval process.\n我们需要{meaning.split('；')[0]}审批流程。\n\n"
                f"使用提醒：{note}\n\n小测验：Can you use **{word}** in a sentence?")
        send = lambda msg_type, content: requests.post(f"{BASE}/im/v1/messages?receive_id_type=open_id", headers=headers, json={"receive_id": RECIPIENT, "msg_type": msg_type, "content": json.dumps(content, ensure_ascii=False)}).raise_for_status()
        send("text", {"text": text})
        with open(opus, "rb") as audio:
            upload = requests.post(f"{BASE}/im/v1/files", headers=headers, data={"file_type":"opus", "file_name":f"{word}.opus"}, files={"file": audio})
        upload.raise_for_status()
        send("audio", {"file_key": upload.json()["data"]["file_key"]})
    used = json.loads(HISTORY.read_text()) if HISTORY.exists() else []
    used.append(word)
    HISTORY.write_text(json.dumps(used, ensure_ascii=False, indent=2) + "\n")
    print("Sent vocabulary text and audio to Feishu.")

if __name__ == "__main__":
    main()
