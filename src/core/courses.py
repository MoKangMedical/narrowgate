"""
窄门 (NarrowGate) — 课程引擎 (Courses Engine)

12门灵魂进化课程，每门至少5万字阅读量 + 测试题。
课程覆盖五大维度，从认知觉醒到行动穿越。

架构师：贾维斯 (Jarvis) for 小林医生
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime


COURSES_DIR = Path(__file__).parent.parent.parent / "data" / "courses"


@dataclass
class QuizQuestion:
    """测试题"""
    id: str
    question: str
    options: List[str]  # 四个选项
    correct_index: int  # 正确答案索引(0-3)
    explanation: str  # 解析
    difficulty: int  # 1-5


@dataclass
class Chapter:
    """课程章节"""
    id: str
    title: str
    order: int
    content_path: str  # markdown 文件路径
    summary: str
    reading_minutes: int  # 预估阅读时间
    quiz: List[QuizQuestion] = field(default_factory=list)


@dataclass
class Course:
    """课程"""
    id: str
    name: str
    subtitle: str
    dimension: str  # 认知/情绪/行为/关系/事业
    description: str
    icon: str
    color: str
    level_required: int  # 进化层级要求
    chapters: List[Chapter] = field(default_factory=list)
    total_reading_minutes: int = 0
    total_words: int = 0

    @property
    def chapter_count(self) -> int:
        return len(self.chapters)

    @property
    def quiz_count(self) -> int:
        return sum(len(ch.quiz) for ch in self.chapters)


# ============================================================
# 12门课程定义
# ============================================================

COURSE_DEFINITIONS = [
    Course(
        id="socratic_introspection",
        name="苏格拉底式自省",
        subtitle="学会问自己不敢问的问题",
        dimension="认知",
        description="从苏格拉底的产婆术出发，学习如何解构自己的信念系统，发现思维中的矛盾和盲区。不是读哲学史——是用苏格拉底的方法审问自己。",
        icon="🦉",
        color="#6366f1",
        level_required=1,
    ),
    Course(
        id="shadow_integration",
        name="阴影整合",
        subtitle="你最讨厌的，正是你最需要的",
        dimension="情绪",
        description="基于荣格阴影理论，学习识别、接纳和整合你压抑的自我部分。投射检测、梦境工作、情绪解码——从对抗阴影到拥抱完整。",
        icon="🌑",
        color="#7c3aed",
        level_required=1,
    ),
    Course(
        id="behavioral_reshape",
        name="行为重塑",
        subtitle="从知道到做到的最短路径",
        dimension="行为",
        description="整合原子习惯、执行意图、行为设计学，系统性修复你的执行断裂。不是再读一本习惯养成的书——是真正建立行为系统。",
        icon="⚡",
        color="#dc2626",
        level_required=1,
    ),
    Course(
        id="relationship_mirror",
        name="关系镜像",
        subtitle="每段关系都是灵魂的镜子",
        dimension="关系",
        description="通过关系模式识别、边界审计、讨好检测，看清你在关系中扮演的角色。从讨好者到真实者的进化路径。",
        icon="🪞",
        color="#059669",
        level_required=1,
    ),
    Course(
        id="systems_thinking",
        name="系统思维",
        subtitle="从棋子到棋手的视角切换",
        dimension="事业",
        description="用系统思维审视人生架构：目标系统、资源分配、杠杆点识别。不是时间管理技巧——是人生的系统工程。",
        icon="🏗️",
        color="#b8942e",
        level_required=2,
    ),
    Course(
        id="pain_alchemy",
        name="痛苦炼金术",
        subtitle="把铅变成金的灵魂工艺",
        dimension="认知",
        description="痛苦不是要消除的东西——是要转化的材料。学习意义重构、隐喻治疗、从痛苦中提取力量的古老智慧。",
        icon="🔮",
        color="#7c3aed",
        level_required=3,
    ),
    Course(
        id="evasion_anatomy",
        name="回避解剖",
        subtitle="你所有借口的完整图谱",
        dimension="行为",
        description="10种回避模式的深度解剖：否认、转移、最小化、合理化、攻击、过度理智化、假性坦诚、反问回避、表演脆弱、合理化升级。每一种都有案例、识别方法和突破策略。",
        icon="🔍",
        color="#ef4444",
        level_required=1,
    ),
    Course(
        id="stoic_resilience",
        name="斯多葛韧性",
        subtitle="在失控的世界里找到掌控",
        dimension="情绪",
        description="从爱比克泰德到马可·奥勒留，斯多葛哲学2000年的核心：控制二分法、消极想象、命运之爱。不是鸡汤——是面对苦难的操作系统。",
        icon="🏛️",
        color="#92400e",
        level_required=1,
    ),
    Course(
        id="antifragile",
        name="反脆弱修炼",
        subtitle="从失败中获益的能力",
        dimension="行为",
        description="基于Nassim Taleb的反脆弱理论：杠铃策略、凸性效应、从波动中获益。不是避免失败——是建立从失败中成长的系统。",
        icon="💪",
        color="#dc2626",
        level_required=2,
    ),
    Course(
        id="meaning_construction",
        name="意义建构",
        subtitle="在荒谬中创造意义",
        dimension="认知",
        description="Viktor Frankl的意义治疗 + 存在主义心理学：意义的三种来源、价值澄清、从苦难到意义的转化路径。当你不知道为什么活着的时候，这门课是你的指南。",
        icon="🧭",
        color="#059669",
        level_required=1,
    ),
    Course(
        id="witness_evolution",
        name="见证与进化",
        subtitle="被看见是进化的开始",
        dimension="关系",
        description="见证人体系设计、进化金字塔原理、经验值系统。如何让真实的他人见证你的成长，如何从被看见中获得力量。",
        icon="👁️",
        color="#b8942e",
        level_required=1,
    ),
    Course(
        id="narrow_gate_crossing",
        name="窄门穿越",
        subtitle="从凡人到封神的完整路径",
        dimension="全部",
        description="整合全部五维度的终极课程：从灵魂审计到行动穿越，从个人突破到帮助他人突破。这是窄门理论的完整实践指南。",
        icon="🚪",
        color="#b8942e",
        level_required=1,
    ),
]


# ============================================================
# 课程引擎
# ============================================================

class CourseEngine:
    """课程引擎"""

    def __init__(self):
        self.courses = {c.id: c for c in COURSE_DEFINITIONS}
        self._load_chapters()

    def _load_chapters(self):
        """从文件系统加载章节"""
        if not COURSES_DIR.exists():
            return
        for course_id, course in self.courses.items():
            course_dir = COURSES_DIR / course_id
            if not course_dir.exists():
                continue
            chapters_dir = course_dir / "chapters"
            quiz_file = course_dir / "quiz.json"
            meta_file = course_dir / "meta.json"

            # 加载元数据
            if meta_file.exists():
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    course.total_words = meta.get("total_words", 0)
                    course.total_reading_minutes = meta.get("total_reading_minutes", 0)

            # 加载章节
            if chapters_dir.exists():
                chapters = sorted(chapters_dir.glob("*.md"))
                for idx, ch_path in enumerate(chapters):
                    ch_id = ch_path.stem
                    content = ch_path.read_text(encoding="utf-8")
                    title = content.split("\n")[0].lstrip("# ").strip() if content else ch_id
                    words = len(content)
                    chapter = Chapter(
                        id=ch_id,
                        title=title,
                        order=idx + 1,
                        content_path=str(ch_path),
                        summary=content[:200] + "..." if len(content) > 200 else content,
                        reading_minutes=max(1, words // 500),
                    )
                    course.chapters.append(chapter)

            # 加载测试题
            if quiz_file.exists():
                with open(quiz_file, "r", encoding="utf-8") as f:
                    quiz_data = json.load(f)
                # 兼容两种格式：直接数组 或 包含 questions 字段的对象
                if isinstance(quiz_data, dict):
                    questions_list = quiz_data.get("questions", [])
                elif isinstance(quiz_data, list):
                    questions_list = quiz_data
                else:
                    questions_list = []
                for q in questions_list:
                    if not isinstance(q, dict):
                        continue
                    question = QuizQuestion(
                        id=str(q.get("id", "")),
                        question=q.get("question", ""),
                        options=q.get("options", []),
                        correct_index=q.get("correct_index", 0),
                        explanation=q.get("explanation", ""),
                        difficulty=q.get("difficulty", 1),
                    )
                    # 将题目分配到对应章节
                    ch_idx = min(q.get("chapter", 1) - 1, len(course.chapters) - 1) if course.chapters else 0
                    if 0 <= ch_idx < len(course.chapters):
                        course.chapters[ch_idx].quiz.append(question)

    def get_all_courses(self, user_level: int = 1) -> List[dict]:
        """获取用户可用的所有课程"""
        result = []
        for course in self.courses.values():
            result.append({
                "id": course.id,
                "name": course.name,
                "subtitle": course.subtitle,
                "dimension": course.dimension,
                "description": course.description,
                "icon": course.icon,
                "color": course.color,
                "level_required": course.level_required,
                "locked": user_level < course.level_required,
                "chapter_count": len(course.chapters),
                "quiz_count": course.quiz_count,
                "total_words": course.total_words,
                "total_reading_minutes": course.total_reading_minutes,
            })
        return result

    def get_course(self, course_id: str) -> Optional[Course]:
        """获取课程详情"""
        return self.courses.get(course_id)

    def get_chapter_content(self, course_id: str, chapter_id: str) -> Optional[str]:
        """获取章节内容"""
        course = self.courses.get(course_id)
        if not course:
            return None
        for ch in course.chapters:
            if ch.id == chapter_id:
                if ch.content_path and os.path.exists(ch.content_path):
                    return open(ch.content_path, "r", encoding="utf-8").read()
        return None

    def get_course_chapters(self, course_id: str) -> List[dict]:
        """获取课程的章节列表"""
        course = self.courses.get(course_id)
        if not course:
            return []
        return [
            {
                "id": ch.id,
                "title": ch.title,
                "order": ch.order,
                "reading_minutes": ch.reading_minutes,
                "quiz_count": len(ch.quiz),
                "summary": ch.summary,
            }
            for ch in course.chapters
        ]

    def get_chapter_quiz(self, course_id: str, chapter_id: str) -> List[dict]:
        """获取章节测试题"""
        course = self.courses.get(course_id)
        if not course:
            return []
        for ch in course.chapters:
            if ch.id == chapter_id:
                return [
                    {
                        "id": q.id,
                        "question": q.question,
                        "options": q.options,
                        "difficulty": q.difficulty,
                        "explanation": q.explanation,  # 作答后显示
                    }
                    for q in ch.quiz
                ]
        return []


# 全局实例
course_engine = CourseEngine()


__all__ = ["CourseEngine", "Course", "Chapter", "QuizQuestion", "COURSE_DEFINITIONS", "course_engine"]
