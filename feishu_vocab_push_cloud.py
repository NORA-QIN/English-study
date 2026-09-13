import json, os, subprocess, tempfile
from pathlib import Path
import requests
from gtts import gTTS

RECIPIENT = os.environ["FEISHU_RECIPIENT_OPEN_ID"]
BASE = "https://open.feishu.cn/open-apis"
HISTORY = Path("vocab_history.json")
WORDS = [
 {"word":"clarify","ipa":"/ˈklærəfaɪ/","pos":"verb 动词","meaning":"澄清；讲清楚；使明确","definition":"to make something easier to understand by explaining it more clearly","examples":["Could you clarify what you mean?","We need to clarify the project requirements before we start."],"special":"clarify a point / clarify expectations；比 explain 更强调消除歧义。","slang":"无常见俚语。","syn":"clarify 强调变清楚；explain 强调解释过程；specify 强调列出细节。","origin":"来自拉丁语 clarus（明亮、清楚）。"},
 {"word":"feasible","ipa":"/ˈfiːzəbəl/","pos":"adjective 形容词","meaning":"可行的；能实现的","definition":"possible and practical to do successfully","examples":["Is this plan feasible within our budget?","We are looking for a feasible solution."],"special":"technically feasible 表示技术上可行；commercially feasible 表示商业上可行。","slang":"无常见俚语。","syn":"feasible 偏实际可行；possible 只表示可能；practical 强调实用。","origin":"来自法语 faisable，意为能够完成的。"},
 {"word":"subtle","ipa":"/ˈsʌtəl/","pos":"adjective 形容词","meaning":"细微的；不明显的；微妙的","definition":"not easy to notice or understand, but important","examples":["There is a subtle difference between the two designs.","She used subtle humor to make her point."],"special":"注意 b 不发音；subtle difference 是高频搭配。","slang":"无常见俚语。","syn":"subtle 细微且不易察觉；slight 程度小；delicate 需要谨慎处理。","origin":"来自拉丁语 subtilis，原意为精细、薄。"},
 {"word":"overlook","ipa":"/ˌəʊvəˈlʊk/","pos":"verb 动词；noun 名词","meaning":"忽略、遗漏；俯瞰景色","definition":"to fail to notice something; or to have a view from above","examples":["I overlooked one important detail.","The hotel room overlooks the harbor."],"special":"作动词时常表示偶然遗漏；overlook 也可作名词，指观景处。","slang":"overlook something 可委婉表示漏看了某事。","syn":"overlook 偶然遗漏；ignore 有意不理会；miss 未注意到或错过。","origin":"由 over + look 构成，字面是从上面看。"},
 {"word":"streamline","ipa":"/ˈstriːmlaɪn/","pos":"verb 动词；adjective 形容词","meaning":"简化流程；提高效率；流线型的","definition":"to make a process simpler and more efficient","examples":["We need to streamline the approval process.","This tool streamlines our daily workflow."],"special":"比 simplify 更强调减少阻力、提高效率。","slang":"无常见俚语。","syn":"streamline 强调效率；simplify 强调降低复杂度；optimize 强调达到最佳状态。","origin":"原指空气动力学中的流线型外形，后来引申为让流程更顺畅。"},
]

def choose_word():
    used = set(json.loads(HISTORY.read_text()) if HISTORY.exists() else [])
    available = [item for item in WORDS if item["word"] not in used]
    if not available:
        used.clear()
        available = WORDS
    return available[0]

def main():
    w = choose_word()
    word, ipa, meaning = w["word"], w["ipa"], w["meaning"]
    token = requests.post(f"{BASE}/auth/v3/tenant_access_token/internal", json={
        "app_id": os.environ["FEISHU_APP_ID"],
        "app_secret": os.environ["FEISHU_APP_SECRET"],
    }).json()["tenant_access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    with tempfile.TemporaryDirectory() as d:
        mp3, opus = Path(d)/"word.mp3", Path(d)/"word.opus"
        gTTS(word, lang="en").save(str(mp3))
        subprocess.run(["ffmpeg", "-y", "-i", str(mp3), "-c:a", "libopus", "-b:a", "48k", str(opus)], check=True)
        text = (f"📚 每日英语词汇\n\n**{word}**　{ipa}\n词性：{w['pos']}\n\n"
                f"中文释义：{meaning}\nEnglish definition：{w['definition']}\n\n"
                f"使用范例：\n- " + "\n- ".join(w["examples"]) + "\n\n"
                f"特殊用法：{w['special']}\n俚语：{w['slang']}\n\n"
                f"同义词辨析：{w['syn']}\n\n词源故事：{w['origin']}\n\n"
                f"复习：请用 **{word}** 造一个和工作或日常生活有关的句子。")
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
