from manim import *
from .themes import apply_dark_theme, apply_motivational_theme


class LuminaScene(Scene):
    """کلاس پایه برای همه صحنه‌های Lumina"""

    def setup(self):
        apply_dark_theme(self)


class MotivationalScene(LuminaScene):
    """قالب مخصوص ویدیوهای انگیزشی"""

    def setup(self):
        apply_motivational_theme(self)
