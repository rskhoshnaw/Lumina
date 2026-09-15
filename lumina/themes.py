from manim import *

DARK_BG = "#0C0C0C"
LIGHT_BG = "#F8F5F0"
ACCENT = "#FF6B6B"
PRIMARY = "#4ECDC4"
SECONDARY = "#FFE66D"
TEXT_COLOR = "#F7F7F7"

# فونت‌های پیش‌فرض
ENGLISH_FONT = "Arial"
KURDISH_FONT = "Rudaw"  # اگر کار نکرد به "Tahoma" یا "Noto Naskh Arabic" تغییر بده


def apply_dark_theme(scene):
    config.background_color = DARK_BG
    Text.set_default(color=TEXT_COLOR, font=ENGLISH_FONT)
    MathTex.set_default(color=TEXT_COLOR)


def apply_light_theme(scene):
    config.background_color = LIGHT_BG
    Text.set_default(color="#1A1A1A", font=ENGLISH_FONT)
    MathTex.set_default(color="#1A1A1A")


def apply_motivational_theme(scene):
    config.background_color = "#111111"
    Text.set_default(color="#FFF5E6", font=ENGLISH_FONT)
    MathTex.set_default(color="#FFE6C7")
