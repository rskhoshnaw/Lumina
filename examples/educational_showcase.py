from manim import *
from lumina import LuminaScene, QuoteCard, FormulaHighlightCard
from lumina.themes import KURDISH_FONT


class FullShowcase(LuminaScene):
    def construct(self):
        # بخش ۱: کارت انگیزشی
        quote = QuoteCard(
            text_content="بیرکاری، زمانی سروشتە بۆ تێگەیشتن لە جیهان",
            author="پیرەمێرد",
            font_name=KURDISH_FONT,
        ).to_edge(UP)

        self.play(FadeIn(quote, shift=DOWN), run_time=1.2)
        self.wait(1)

        # بخش ۲: فرمول هایلایت شده با جعبه سینمایی
        formula_card = FormulaHighlightCard(
            latex_str=r"\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}",
            label_text="ئینتیگرالی گاوسی (Gaussian Integral)",
            font_name=KURDISH_FONT,
        ).next_to(quote, DOWN, buff=0.7)

        self.play(Create(formula_card[0]), run_time=1)
        self.play(Write(formula_card[1]), run_time=1.5)
        self.wait(1.5)

        # بخش ۳: ترنزیشن نرم به محور مختصات و رسم تابع
        self.play(
            FadeOut(quote, shift=UP),
            formula_card.animate.scale(0.65).to_corner(UL),
            run_time=1.2,
        )

        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[0, 1.5, 0.5],
            x_length=8,
            y_length=3.5,
            axis_config={"color": GREY_B},
        ).to_edge(DOWN, buff=0.8)

        # تابع چگالی گاوسی
        import numpy as np

        gaussian_graph = axes.plot(lambda x: np.exp(-(x**2)), color="#FFE66D")
        area = axes.get_area(
            gaussian_graph, x_range=[-3, 3], color="#4ECDC4", opacity=0.35
        )

        self.play(Create(axes), run_time=1)
        self.play(Create(gaussian_graph), FadeIn(area), run_time=1.8)
        self.wait(2)
