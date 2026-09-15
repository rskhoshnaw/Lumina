from manim import *
from lumina.themes import KURDISH_FONT


class QuoteCard(VGroup):
    """کارت مدرن برای نمایش نقل‌قول یا متن‌های مفهومی"""

    def __init__(self, text_content, author="", font_name=KURDISH_FONT, **kwargs):
        super().__init__(**kwargs)

        body = Text(
            f"«{text_content}»",
            font=font_name,
            font_size=30,
            line_spacing=1.2,
            color="#FFFFFF",
        )

        elements = [body]
        if author:
            author_text = Text(
                f"— {author}", font=font_name, font_size=22, color="#FFE66D"
            ).next_to(body, DOWN, buff=0.35, aligned_edge=RIGHT)
            elements.append(author_text)

        inner_group = VGroup(*elements)

        box = RoundedRectangle(
            corner_radius=0.2,
            height=inner_group.height + 0.8,
            width=inner_group.width + 1.2,
            color="#4ECDC4",
            stroke_width=2,
            fill_color="#181824",
            fill_opacity=0.75,
        )

        inner_group.move_to(box.get_center())
        self.add(box, inner_group)


class FormulaHighlightCard(VGroup):
    """باکس متحرک هایلایت فرمول با برچسب توضیحی"""

    def __init__(self, latex_str, label_text="", font_name=KURDISH_FONT, **kwargs):
        super().__init__(**kwargs)

        formula = MathTex(latex_str, font_size=44, color="#FFF5E6")
        elements = [formula]

        if label_text:
            label = Text(label_text, font=font_name, font_size=24, color="#4ECDC4")
            label.next_to(formula, UP, buff=0.35)
            elements.insert(0, label)

        group = VGroup(*elements)

        bg = SurroundingRectangle(
            group,
            buff=0.3,
            corner_radius=0.15,
            color="#FF6B6B",
            stroke_width=1.5,
            fill_color="#121216",
            fill_opacity=0.85,
        )
        self.add(bg, group)
