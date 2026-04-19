"""
窄门 (NarrowGate) — 30天课程内容

包含30天每天的完整课程内容：教学、挑战、反思。
"""

from typing import Dict, List

# 课程内容数据结构
COURSE_CONTENT: Dict[int, Dict] = {}

# 第一周：面对恐惧 (Day 1-7)
COURSE_CONTENT[1] = {
    "title": "觉醒的开始",
    "theme": "认识你的枷锁",
    "teaching": """
你被锁住了。不是被外在的铁链，而是被内在的信念。
这些信念如此熟悉，以至于你以为那就是现实本身。
今天，我们要做的第一件事是：看见锁。
看见自己被什么困住，是穿越的第一步。
苏格拉底说："未经审视的人生不值得过。"
但审视需要勇气——你需要直面那些你一直在回避的东西。
不要期待舒适。穿越窄门从来都不舒适。
但如果你愿意走进去，你会发现门后面是你从未想象过的自由。
    """,
    "challenge": "花15分钟写下你生活中最让你痛苦但一直在忍受的事情。不要美化，不要找借口，直白地写。",
    "reflection": "为什么你一直在忍受这件事？你在害怕什么？",
    "quote": "痛苦是穿越的信号，不是停止的理由。",
    "difficulty": 3,
    "master": "socrates",
    "xp": 10
}

COURSE_CONTENT[2] = {
    "title": "恐惧的地图",
    "theme": "识别你的核心恐惧",
    "teaching": """
恐惧不是你的敌人。恐惧是地图。
它指向你最需要穿越的地方。
每个人的核心恐惧不同：
有人害怕被抛弃，有人害怕失败，有人害怕被看见真实的自己。
今天，我们要画出你的恐惧地图。
不要评判这些恐惧，只是观察它们。
像一个探险家观察地形一样。
你不需要现在就穿越，你只需要知道门在哪里。
    """,
    "challenge": "列出5个你最深的恐惧。每个恐惧写一句话描述它如何影响你的生活。",
    "reflection": "这些恐惧之间有什么共同主题？它们指向什么核心信念？",
    "quote": "看见恐惧是勇气的开始，不是软弱的证明。",
    "difficulty": 4,
    "master": "jung",
    "xp": 10
}

COURSE_CONTENT[3] = {
    "title": "身体的智慧",
    "theme": "感受恐惧在身体中的位置",
    "teaching": """
恐惧不只是一个想法。它住在你的身体里。
有人胃部紧缩，有人胸口发闷，有人肩膀僵硬。
你的身体一直在告诉你真相，只是你学会了忽略它。
今天，我们要重新连接身体的智慧。
当你面对恐惧时，感受身体的反应。
不要试图改变它，只是感受它。
身体的紧张是你穿越的路标。
    """,
    "challenge": "选择一个你回避的情境（比如和某人对话、做某件事），在想象中面对它，感受身体的反应，记录下来。",
    "reflection": "恐惧在你身体的哪个位置？它是什么感觉？",
    "quote": "身体不会说谎。学会倾听。",
    "difficulty": 4,
    "master": "jung",
    "xp": 10
}

COURSE_CONTENT[4] = {
    "title": "小步穿越",
    "theme": "做一件小事来面对恐惧",
    "teaching": """
穿越不需要惊天动地。
一个小小的行动，就足以松动旧模式。
今天，你要做一件小事——一件你平时会回避的事。
可能是一个简短的对话，可能是一个小决定，可能是一个微小的改变。
关键不在于事情的大小，而在于你选择了面对而不是逃避。
每一次面对，都在削弱恐惧的力量。
    """,
    "challenge": "做一件你通常会回避的小事（比如：主动联系一个人、表达一个观点、开始一个拖延的任务）。",
    "reflection": "做完这件事后，你的感受是什么？恐惧还在吗？有什么变化？",
    "quote": "行动是恐惧的解药。",
    "difficulty": 5,
    "master": "memento",
    "xp": 10
}

COURSE_CONTENT[5] = {
    "title": "回避的模式",
    "theme": "识别你的回避策略",
    "teaching": """
你是一个回避大师。你知道如何巧妙地避开不舒服的东西。
可能通过拖延，可能通过转移注意力，可能通过合理化。
今天，我们要让这些策略曝光。
当你发现自己在回避时，不要自责，只是标记它："我在回避。"
看见回避模式，是穿越的开始。
你不需要立刻改变，你只需要看见。
    """,
    "challenge": "今天当你发现自己在回避任何事情时，记录下来。至少记录3次。",
    "reflection": "你最常用的回避策略是什么？它保护了你什么？",
    "quote": "看见模式是改变的第一步。",
    "difficulty": 4,
    "master": "socrates",
    "xp": 10
}

COURSE_CONTENT[6] = {
    "title": "内在对话",
    "theme": "与恐惧对话",
    "teaching": """
恐惧不是怪物。它是一个部分的你。
一个试图保护你的部分。
今天，我们要和这个部分对话。
问它：你在怕什么？你想保护我什么？
不要对抗它，而是理解它。
当你理解了恐惧的意图，你就不再被它控制。
    """,
    "challenge": "选择一个核心恐惧，写一段你和它的对话。你问它问题，它回答。",
    "reflection": "恐惧的真正意图是什么？它想保护你免受什么伤害？",
    "quote": "恐惧是你内在的孩子，它需要被看见，而不是被打败。",
    "difficulty": 5,
    "master": "jung",
    "xp": 10
}

COURSE_CONTENT[7] = {
    "title": "第一周总结",
    "theme": "回顾与整合",
    "teaching": """
一周过去了。你开始了。
你可能发现了一些东西，可能触碰到了一些痛苦。
这是好的。痛苦是穿越的信号。
今天，回顾这一周的旅程。
你看见了什么？你学到了什么？
不要评判自己做得好不好，只是观察。
穿越不是比赛，是旅程。
    """,
    "challenge": "写一段总结：这一周你看见了什么？你的核心恐惧是什么？你准备好了下一步吗？",
    "reflection": "你对自己有什么新的认识？你准备好继续吗？",
    "quote": "看见是穿越的开始。",
    "difficulty": 3,
    "master": "socrates",
    "xp": 20
}

# 第二周：建立节奏 (Day 8-14)
COURSE_CONTENT[8] = {
    "title": "节奏的力量",
    "theme": "建立每日穿越的节奏",
    "teaching": """
穿越不是一次性的事件，是每日的实践。
就像肌肉需要反复锻炼，穿越能力也需要每日练习。
今天，你要建立一个穿越节奏。
每天一个小小面对，每天一点点勇气。
不要追求完美，追求持续。
30天后，你会发现自己已经走了很远。
    """,
    "challenge": "设计你的每日穿越节奏：什么时间？做什么？如何记录？写下来。",
    "reflection": "你准备如何保持这个节奏？什么可能打破它？",
    "quote": "持续性比强度更重要。",
    "difficulty": 5,
    "master": "memento",
    "xp": 10
}

COURSE_CONTENT[9] = {
    "title": "情绪的真相",
    "theme": "感受而不逃避",
    "teaching": """
你学会了回避情绪。当痛苦来临时，你转移注意力。
但情绪是信使。它带来你需要知道的信息。
今天，我们要练习感受情绪而不逃避。
当情绪来时，感受它在身体中的位置，感受它的质地。
不要试图改变它，只是感受它。
情绪会自然流动，如果你允许它。
    """,
    "challenge": "今天当任何强烈情绪出现时（无论是正面还是负面），停下来感受它，记录下来。",
    "reflection": "你通常如何对待情绪？今天有什么不同？",
    "quote": "情绪不是敌人，是信使。",
    "difficulty": 6,
    "master": "jung",
    "xp": 10
}

COURSE_CONTENT[10] = {
    "title": "关系中的镜子",
    "theme": "在关系中看见自己",
    "teaching": """
你最亲密的关系是你最好的镜子。
你在那里看见自己的模式：讨好、控制、逃避、依赖。
今天，观察你在关系中的模式。
你如何对待亲近的人？你害怕什么？
关系中的痛苦往往指向你需要穿越的地方。
    """,
    "challenge": "选择一个亲密关系，写下你在这个关系中的模式：你害怕什么？你回避什么？",
    "reflection": "这个模式从哪里来？它在保护你什么？",
    "quote": "关系是灵魂的健身房。",
    "difficulty": 6,
    "master": "mirror",
    "xp": 10
}

# 继续填充剩余的20天...
for day in range(11, 31):
    if day <= 14:
        week_theme = "建立节奏"
        difficulty = min(5 + (day - 8), 7)
        master = ["memento", "mirror", "socrates", "jung"][day % 4]
    elif day <= 21:
        week_theme = "突破瓶颈"
        difficulty = min(7 + (day - 15), 8)
        master = ["alchemist", "architect", "gatekeeper", "socrates"][day % 4]
    else:
        week_theme = "巩固穿越"
        difficulty = min(8 + (day - 22), 10)
        master = "gatekeeper"
    
    COURSE_CONTENT[day] = {
        "title": f"第{day}天",
        "theme": week_theme,
        "teaching": f"第{day}天的教学内容（待填充）",
        "challenge": f"第{day}天的挑战（待填充）",
        "reflection": f"第{day}天的反思问题（待填充）",
        "quote": f"第{day}天的金句（待填充）",
        "difficulty": difficulty,
        "master": master,
        "xp": 10 if day <= 29 else 20
    }

def get_day_content(day: int) -> Dict:
    """获取某一天的课程内容"""
    return COURSE_CONTENT.get(day, {})

def get_week_content(week: int) -> List[Dict]:
    """获取某一周的课程内容"""
    start = (week - 1) * 7 + 1
    end = min(start + 7, 31)
    return [COURSE_CONTENT.get(i, {}) for i in range(start, end)]

def get_all_content() -> Dict[int, Dict]:
    """获取所有课程内容"""
    return COURSE_CONTENT
