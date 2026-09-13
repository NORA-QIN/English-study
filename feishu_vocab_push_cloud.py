import json, os, subprocess, tempfile
from pathlib import Path
import requests
from gtts import gTTS

WORD = "streamline"
RECIPIENT = os.environ["FEISHU_RECIPIENT_OPEN_ID"]
BASE = "https://open.feishu.cn/open-apis"

def main():
    token = requests.post(f"{BASE}/auth/v3/tenant_access_token/internal", json={
        "app_id": os.environ["FEISHU_APP_ID"],
        "app_secret": os.environ["FEISHU_APP_SECRET"],
    }).json()["tenant_access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    with tempfile.TemporaryDirectory() as d:
        mp3, opus = Path(d)/"word.mp3", Path(d)/"word.opus"
        gTTS(WORD, lang="en").save(str(mp3))
        subprocess.run(["ffmpeg", "-y", "-i", str(mp3), "-c:a", "libopus", "-b:a", "48k", str(opus)], check=True)
        text = (f"📚 每日英语词汇\n\n**{WORD}**（动词）\n读音：/ˈstriːmlaɪn/\n"
                "含义：简化流程；提高效率；使更顺畅\n\n"
                "We need to streamline the approval process.\n我们需要简化审批流程。\n\n"
                "使用提醒：强调去除不必要环节，从而提高效率。\n\n"
                "来历：原指空气动力学中阻力更小的流线型外形，后来引申为让流程更顺畅高效。")
        send = lambda msg_type, content: requests.post(f"{BASE}/im/v1/messages?receive_id_type=open_id", headers=headers, json={"receive_id": RECIPIENT, "msg_type": msg_type, "content": json.dumps(content, ensure_ascii=False)}).raise_for_status()
        send("text", {"text": text})
        with open(opus, "rb") as audio:
            upload = requests.post(f"{BASE}/im/v1/files", headers=headers, data={"file_type":"opus", "file_name":"streamline.opus"}, files={"file": audio})
        upload.raise_for_status()
        send("audio", {"file_key": upload.json()["data"]["file_key"]})
    print("Sent vocabulary text and audio to Feishu.")

if __name__ == "__main__":
    main()
