"""
窄门 (NarrowGate) — 深夜独白引导问题库

灵魂深处的提问，引导用户在深夜与自己对话。
"""

import random
from typing import List

# 灵魂引导问题库（按主题分类）
PROMPT_CATEGORIES = {
    "存在与意义": [
        "此刻，你觉得活着最重要的是什么？",
        "如果生命只剩一年，你会做什么？",
        "你有没有想过，你存在的意义是什么？",
        "今天发生了什么让你觉得值得？",
        "你觉得什么样的人生才算没有白活？",
        "你害怕死亡吗？为什么？",
        "如果可以重新选择，你还会选择现在的生活吗？",
        "你觉得自己在逃避什么？",
    ],
    
    "恐惧与渴望": [
        "你内心深处最害怕什么？",
        "你最渴望得到什么？为什么还没有去追求？",
        "有什么事情你一直想做但不敢做？",
        "你害怕失败还是害怕成功？",
        "如果没有任何限制，你最想成为什么样的人？",
        "你害怕孤独吗？",
        "你最不想失去什么？",
        "你有什么梦想已经放弃了吗？为什么？",
    ],
    
    "关系与孤独": [
        "你有没有觉得身边都是人，却依然感到孤独？",
        "谁是你最想倾诉却说不出口的人？",
        "你有没有伤害过在乎的人？后来怎么样了？",
        "你觉得真正被理解是什么感觉？",
        "你最感激的人是谁？为什么没有告诉过他们？",
        "有没有一段关系让你至今难以释怀？",
        "你觉得爱情是什么？",
        "你害怕被抛弃吗？",
    ],
    
    "过去与未来": [
        "如果能对十年前的自己说一句话，你会说什么？",
        "你最后悔的一件事是什么？",
        "有没有一个瞬间，你觉得人生被改变了？",
        "你觉得自己变了吗？哪里变了？",
        "十年后你希望自己是什么样子？",
        "你害怕变老吗？",
        "过去的痛苦对你有什么意义？",
        "你愿意原谅过去的自己吗？",
    ],
    
    "真实与伪装": [
        "你在别人面前和独处时，是同一个人吗？",
        "你有没有戴着面具生活？面具下面是什么？",
        "你最不想让别人知道你什么？",
        "你觉得真实的自己是什么样的？",
        "你有没有假装开心过？",
        "你害怕别人看到真实的你吗？",
        "你觉得自己值得被爱吗？",
        "如果没有任何人评判你，你会怎么做？",
    ],
    
    "情绪与感受": [
        "此刻你的心里是什么感觉？",
        "你有多久没有好好哭过了？",
        "你最近一次感到真正的快乐是什么时候？",
        "你有没有觉得活着很累？",
        "你如何面对自己的负面情绪？",
        "你有没有觉得全世界都不理解你？",
        "你害怕自己的情绪吗？",
        "你觉得平静是什么感觉？",
    ],
    
    "枷锁与自由": [
        "你觉得什么束缚着你？",
        "你有没有觉得自己被困住了？",
        "什么是你不敢放弃的？",
        "你觉得自由是什么？",
        "你害怕打破规则吗？",
        "你有没有觉得活着不属于自己？",
        "你愿意为了自由付出什么代价？",
        "你觉得自己是自由的吗？",
    ],
}


def get_random_prompt() -> str:
    """获取一个随机的灵魂引导问题"""
    category = random.choice(list(PROMPT_CATEGORIES.keys()))
    prompt = random.choice(PROMPT_CATEGORIES[category])
    return prompt


def get_prompt_by_category(category: str) -> str:
    """按类别获取引导问题"""
    if category in PROMPT_CATEGORIES:
        return random.choice(PROMPT_CATEGORIES[category])
    return get_random_prompt()


def get_all_categories() -> List[str]:
    """获取所有问题类别"""
    return list(PROMPT_CATEGORIES.keys())


def get_prompts_by_category(category: str) -> List[str]:
    """获取某个类别的所有问题"""
    return PROMPT_CATEGORIES.get(category, [])


def get_daily_prompt(user_id: str, day: int = None) -> str:
    """
    基于用户ID和日期生成确定性的每日引导问题
    同一天同一用户看到相同的问题
    """
    import hashlib
    from datetime import datetime
    
    if day is None:
        day = datetime.now().toordinal()
    
    # 使用用户ID和日期生成种子
    seed_str = f"{user_id}_{day}"
    seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
    
    # 选择类别和问题
    categories = list(PROMPT_CATEGORIES.keys())
    category = categories[seed % len(categories)]
    prompts = PROMPT_CATEGORIES[category]
    prompt = prompts[seed % len(prompts)]
    
    return prompt


# 深夜独白的开场白
WELCOME_MESSAGES = [
    "夜深了，这是只属于你的时刻。",
    "放下所有的伪装，和自己说说话吧。",
    "在寂静中，听听内心的声音。",
    "此刻无需坚强，只需真实。",
    "黑暗中，你最能看清自己。",
    "这是你与灵魂的约定。",
    "夜色温柔，允许自己脆弱。",
    "在这里，没有评判，只有倾听。",
]


def get_welcome_message() -> str:
    """获取随机开场白"""
    return random.choice(WELCOME_MESSAGES)


# 情绪标签
MOOD_OPTIONS = [
    {"emoji": "🌑", "label": "忧郁", "key": "melancholy"},
    {"emoji": "🌊", "label": "平静", "key": "calm"},
    {"emoji": "🔥", "label": "愤怒", "key": "angry"},
    {"emoji": "💧", "label": "释然", "key": "relieved"},
    {"emoji": "🌪️", "label": "迷茫", "key": "confused"},
    {"emoji": "✨", "label": "希望", "key": "hopeful"},
]


def get_mood_options() -> list:
    """获取情绪选项"""
    return MOOD_OPTIONS
