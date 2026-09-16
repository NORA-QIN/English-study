import json, os, subprocess, tempfile
from pathlib import Path
import requests
from gtts import gTTS

RECIPIENT = os.environ["FEISHU_RECIPIENT_OPEN_ID"]
BASE = "https://open.feishu.cn/open-apis"
HISTORY = Path("vocab_history.json")
WORDS = [
 {"word":"estimate","ipa":"/ˈestɪmeɪt/ (v.), /ˈestɪmət/ (n.)","pos":"verb 动词；noun 名词","meaning":"估计；估算；估价","definition":"to roughly calculate a value, amount, time, or cost; a rough calculation","examples":["We estimate that the work will take three days.","Could you give me a cost estimate?"],"special":"动词和名词结尾读音不同；rough estimate 表示粗略估算。","slang":"guesstimate 是 guess 与 estimate 合成的非正式说法。","syn":"estimate 基于有限信息估算；guess 更随意；assess 强调分析判断。","origin":"来自拉丁语 aestimare，意为评价或估价。"},
 {"word":"concise","ipa":"/kənˈsaɪs/","pos":"adjective 形容词","meaning":"简明的；言简意赅的","definition":"giving the necessary information clearly in very few words","examples":["Please keep the summary concise.","Her explanation was concise but complete."],"special":"concise writing / concise summary；不等于 precise（精确的）。","slang":"无常见俚语。","syn":"concise 简短且信息完整；brief 只强调短；succinct 更正式、有力。","origin":"来自拉丁语 concidere，原意为切短。"},
 {"word":"reluctant","ipa":"/rɪˈlʌktənt/","pos":"adjective 形容词","meaning":"不情愿的；勉强的","definition":"unwilling and hesitant to do something","examples":["She was reluctant to change the design.","He gave a reluctant agreement."],"special":"be reluctant to do something 是固定搭配。","slang":"无常见俚语。","syn":"reluctant 不情愿；hesitant 犹豫；unwilling 明确不愿意。","origin":"来自拉丁语 reluctari，意为反抗、抵抗。"},
 {"word":"counterpart","ipa":"/ˈkaʊntəpɑːt/","pos":"noun 名词","meaning":"对应的人或事物；职位相当者","definition":"a person or thing with the same role or function in another place or organization","examples":["I discussed the issue with my counterpart in London.","The mobile app is simpler than its desktop counterpart."],"special":"常见于跨团队、跨公司或不同版本之间的对应关系。","slang":"无常见俚语。","syn":"counterpart 强调对应角色；peer 强调同等级；equivalent 强调价值或功能相等。","origin":"原指契约的副本，后来指相互对应的一方。"},
 {"word":"trade-off","ipa":"/ˈtreɪd ɒf/","pos":"noun 名词","meaning":"权衡；取舍","definition":"a balance in which gaining one benefit requires giving up another","examples":["There is a trade-off between speed and quality.","Every design decision involves trade-offs."],"special":"常用结构是 a trade-off between A and B。","slang":"give-and-take 可表示双方互相让步，但不完全等同。","syn":"trade-off 强调得失交换；compromise 强调双方妥协；balance 强调维持平衡。","origin":"来自商业交易中以一种利益换取另一种利益。"},
 {"word":"nuance","ipa":"/ˈnjuːɑːns/","pos":"noun 名词；verb 动词（少见）","meaning":"细微差别；微妙之处","definition":"a small but important difference in meaning, feeling, or expression","examples":["The translation misses an important nuance.","She understands the nuances of user behavior."],"special":"常用复数 nuances；nuanced 作形容词表示细致入微的。","slang":"无常见俚语。","syn":"nuance 是意义或感受上的微差；subtlety 是不易察觉的精细之处；shade 可指程度差异。","origin":"来自法语 nue，原指云层呈现的细微色调。"},
 {"word":"undermine","ipa":"/ˌʌndəˈmaɪn/","pos":"verb 动词","meaning":"逐渐削弱；暗中损害","definition":"to gradually weaken someone's position, confidence, or effectiveness","examples":["Poor communication can undermine trust.","The delays undermined confidence in the project."],"special":"强调缓慢或不明显地造成削弱，不是“埋藏”。","slang":"无常见俚语。","syn":"undermine 暗中削弱；weaken 泛指变弱；sabotage 强调故意破坏。","origin":"原指从城墙下挖地道，使建筑失去支撑。"},
 {"word":"mitigate","ipa":"/ˈmɪtɪɡeɪt/","pos":"verb 动词","meaning":"减轻；缓和（风险或损害）","definition":"to make something harmful, unpleasant, or serious less severe","examples":["We need a plan to mitigate the risks.","The update mitigates the impact of the bug."],"special":"mitigate risk / damage / impact；通常不是彻底消除。","slang":"无常见俚语。","syn":"mitigate 减轻严重程度；reduce 降低数量或程度；prevent 阻止发生。","origin":"来自拉丁语 mitigare，意为使柔和。"},
 {"word":"contingency","ipa":"/kənˈtɪndʒənsi/","pos":"noun 名词","meaning":"意外情况；应急事项","definition":"a possible future event that must be prepared for, especially an emergency","examples":["We need a contingency plan in case the launch fails.","The budget includes money for contingencies."],"special":"contingency plan 是应急预案；常与 in case 连用。","slang":"Plan B 是更口语化的近似表达。","syn":"contingency 潜在意外情况；emergency 已发生的紧急情况；fallback 是备用方案。","origin":"来自拉丁语 contingere，意为偶然发生。"},
 {"word":"counterintuitive","ipa":"/ˌkaʊntərɪnˈtjuːɪtɪv/","pos":"adjective 形容词","meaning":"违反直觉的","definition":"opposite to what seems naturally correct or expected","examples":["It sounds counterintuitive, but fewer choices can improve decisions.","The result was completely counterintuitive."],"special":"常用来介绍一个看似矛盾、实际合理的结论。","slang":"无常见俚语。","syn":"counterintuitive 违反直觉；surprising 出人意料；paradoxical 表面自相矛盾。","origin":"由 counter（相反）与 intuitive（直觉的）组成。"},
 {"word":"tentative","ipa":"/ˈtentətɪv/","pos":"adjective 形容词","meaning":"暂定的；试探性的；不确定的","definition":"not yet final or certain; done without confidence","examples":["The tentative launch date is October 1.","She gave a tentative answer."],"special":"tentative schedule / agreement / conclusion 都表示尚未最终确认。","slang":"无常见俚语。","syn":"tentative 暂定或试探；provisional 正式语境中的临时；uncertain 单纯不确定。","origin":"来自拉丁语 tentare，意为尝试。"},
 {"word":"align","ipa":"/əˈlaɪn/","pos":"verb 动词","meaning":"对齐；使目标或意见一致","definition":"to arrange things in a straight line or bring plans and opinions into agreement","examples":["Please align the icons with the text.","We need to align on the project goals."],"special":"align with 表示与……一致；align on 表示就某事达成一致。","slang":"无常见俚语，但 align on 在职场英语中非常常见。","syn":"align 强调方向一致；agree 强调意见相同；coordinate 强调协同行动。","origin":"来自法语 ligne（线），最初表示排成一条线。"},
 {"word":"compelling","ipa":"/kəmˈpelɪŋ/","pos":"adjective 形容词","meaning":"令人信服的；极有吸引力的","definition":"very convincing or so interesting that it holds attention","examples":["She presented a compelling argument.","The product needs a compelling story."],"special":"compelling evidence / reason / narrative 是高频搭配。","slang":"无常见俚语。","syn":"compelling 强到让人难以忽视；convincing 令人相信；engaging 吸引注意。","origin":"来自 compel，原意为强迫，引申为强烈吸引。"},
 {"word":"leverage","ipa":"/ˈliːvərɪdʒ/","pos":"noun 名词；verb 动词","meaning":"杠杆作用；利用资源取得优势","definition":"the power to influence a situation; to use something to achieve a better result","examples":["The team has strong leverage in the negotiation.","We can leverage user feedback to improve the product."],"special":"商业英语中常作动词，但避免为显得专业而过度使用。","slang":"无严格俚语；职场中常被当作 buzzword。","syn":"leverage 利用现有优势；use 最普通；capitalize on 强调抓住机会获益。","origin":"来自 lever（杠杆），借用以小力产生大效果的概念。"},
]

def choose_word():
    current_words = {item["word"] for item in WORDS}
    history = json.loads(HISTORY.read_text()) if HISTORY.exists() else []
    used = [word for word in history if word in current_words]
    available = [item for item in WORDS if item["word"] not in set(used)]
    if not available:
        used = []
        available = WORDS
    return available[0], used

def main():
    w, used = choose_word()
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
    used.append(word)
    HISTORY.write_text(json.dumps(used, ensure_ascii=False, indent=2) + "\n")
    print("Sent vocabulary text and audio to Feishu.")

if __name__ == "__main__":
    main()
