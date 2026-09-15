import ast
import os
import re
import subprocess
import sys
from pathlib import Path

import streamlit as st
from google import genai


# =========================================================
# 🔑 Gemini API Key
# =========================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY  It has not been set.")
    st.stop()

# =========================================================
# 🤖 مدل‌های جایگزین Gemini
# =========================================================
FALLBACK_MODELS = [
    "gemini-flash-latest",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-flash-lite-latest",
    "gemini-pro-latest",
]


# =========================================================
# 📁 مسیرهای پروژه
# =========================================================
BASE_DIR = Path(__file__).resolve().parent

GENERATED_DIR = BASE_DIR / "generated"
MEDIA_DIR = BASE_DIR / "media"

GENERATED_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# ⚙️ تنظیمات Streamlit
# =========================================================
st.set_page_config(
    page_title="Lumina Studio",
    page_icon="✨",
    layout="wide",
)


# =========================================================
# 🎨 عنوان برنامه
# =========================================================
st.title(
    "✨ Lumina Studio"
)

st.caption(
    "موتور خودکار تولید، بررسی و رندر انیمیشن‌های آموزشی با "
    "Gemini + Lumina + Manim"
)


# =========================================================
# 🎛️ تنظیمات سایدبار
# =========================================================
with st.sidebar:

    st.header("⚙️ تنظیمات رندر")

    quality = st.selectbox(
        "کیفیت ویدیو:",
        [
            "-pql (سریع / 480p)",
            "-pqm (متوسط / 720p)",
            "-pqh (باکیفیت / 1080p)",
        ],
        index=0,
    )

    st.markdown("---")

    st.subheader("🤖 مدل‌های هوش مصنوعی")

    st.caption(
        "در صورت دریافت خطای موقت 503 یا UNAVAILABLE، "
        "برنامه به‌صورت خودکار مدل بعدی را امتحان می‌کند."
    )

    st.markdown("---")

    st.info(
        "Lumina Studio ابتدا کد Python را تولید و بررسی می‌کند "
        "و سپس آن را با Manim رندر می‌کند."
    )


# =========================================================
# 📝 ورودی سناریو
# =========================================================
user_prompt = st.text_area(
    "📝 سناریوی آموزشی یا انگیزشی خود را وارد کنید:",
    height=160,
    value=(
        "یک انیمیشن مفهومی درباره قضیه فیثاغورس بساز. "
        "ابتدا یک نقل قول کوردی از پیرەمێرد داخل QuoteCard "
        "نمایش بده، سپس فرمول a^2 + b^2 = c^2 را با "
        "FormulaHighlightCard هایلایت کن و در آخر یک "
        "مثلث قائم‌الزاویه رسم نما."
    ),
)


# =========================================================
# 🧠 System Prompt
# =========================================================
SYSTEM_PROMPT = r"""
You are an expert Python and Manim animator specializing in
educational and motivational animations using the Lumina engine.

Your task is to generate clean, complete, executable Python
animation code based on the user's scenario.

The installed environment uses:

- Manim Community v0.21.0
- Lumina animation engine

IMPORTANT:
The following Lumina constructor signatures are confirmed
and MUST NOT be changed or guessed.

QuoteCard:
QuoteCard(text_content, author='', font_name='Rudaw', **kwargs)

FormulaHighlightCard:
FormulaHighlightCard(latex_str, label_text='', font_name='Rudaw', **kwargs)

=========================================================
MANDATORY IMPORTS
=========================================================

The generated file MUST begin with these exact imports:

from manim import *
from lumina import LuminaScene, QuoteCard, FormulaHighlightCard
from lumina.themes import KURDISH_FONT

=========================================================
MANDATORY SCENE
=========================================================

The scene MUST be:

class GeneratedVideo(LuminaScene):
    def construct(self):

=========================================================
QUOTECARD RULES
=========================================================

QuoteCard MUST use:

text_content=

author=

font_name=

Correct example:

quote_card = QuoteCard(
    text_content=quote_text,
    author=author_text,
    font_name="Rudaw",
)

NEVER use:

quote=

NEVER use:

font=

NEVER invent another parameter name.

=========================================================
FORMULAHIGHLIGHTCARD RULES
=========================================================

FormulaHighlightCard MUST use:

latex_str=

label_text=

font_name=

Correct example:

formula_card = FormulaHighlightCard(
    latex_str=r"a^2 + b^2 = c^2",
    label_text="قضیه فیثاغورس",
    font_name="Rudaw",
)

NEVER use:

formula=

NEVER use:

latex=

NEVER use:

text=

NEVER use:

font=

=========================================================
KURDISH / SORANI TEXT
=========================================================

For Kurdish or Sorani text, use:

font_name="Rudaw"

Do not use:

font=

The exact Lumina API requires font_name.

The import:

from lumina.themes import KURDISH_FONT

must still be present because it is part of the required
Lumina environment.

=========================================================
GENERAL MANIM RULES
=========================================================

- Use standard Manim Community v0.21.0 APIs.
- Do not invent Manim methods.
- Do not invent Lumina classes.
- Do not invent Lumina constructor parameters.
- Keep the animation stable.
- Avoid unnecessary complexity.
- Use reasonable run_time values.
- Use FadeIn, FadeOut, Write, Create, Transform,
  ReplacementTransform, etc. when appropriate.
- Keep objects inside the camera frame.
- Use self.wait() where appropriate.
- Make the animation educational and visually clear.
- Use MathTex for mathematical formulas when appropriate.
- Use Triangle, Line, Polygon, Square, VGroup and other
  standard Manim objects when appropriate.

=========================================================
CODE QUALITY
=========================================================

The generated code MUST be:

- complete
- self-contained
- syntactically valid Python
- executable by Manim Community v0.21.0
- compatible with the installed Lumina API

Do not use placeholders such as:

TODO

pass

YOUR_CODE_HERE

Do not leave unfinished functions.

=========================================================
OUTPUT FORMAT
=========================================================

Return ONLY the Python code inside exactly one markdown
Python code block.

Do not write explanations before or after the code.
"""


# =========================================================
# 🧹 پاک‌سازی پاسخ Gemini
# =========================================================
def clean_generated_code(raw_text: str) -> str:
    """
    کد Python را از پاسخ Gemini استخراج و پاک‌سازی می‌کند.
    """

    if not raw_text:
        return ""

    text = raw_text.strip()

    # -----------------------------------------------------
    # استخراج از ```python ... ```
    # -----------------------------------------------------
    match = re.search(
        r"```(?:python|py)?\s*(.*?)```",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if match:
        text = match.group(1).strip()

    # -----------------------------------------------------
    # حذف code fence باقی‌مانده
    # -----------------------------------------------------
    text = re.sub(
        r"^\s*```python\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"^\s*```\s*",
        "",
        text,
    )

    text = re.sub(
        r"\s*```\s*$",
        "",
        text,
    )

    return text.strip()


# =========================================================
# 🔍 بررسی Syntax کد
# =========================================================
def check_python_syntax(code: str):
    """
    بررسی می‌کند که کد تولیدشده از نظر Syntax معتبر باشد.
    """

    try:
        ast.parse(code)
        return True, None

    except SyntaxError as err:
        message = (
            f"خط Syntax در خط {err.lineno}:\n"
            f"{err.msg}"
        )

        if err.text:
            message += (
                f"\n\nکد مشکل‌دار:\n{err.text.strip()}"
            )

        return False, message

    except Exception as err:
        return False, str(err)


# =========================================================
# 🛡️ اعتبارسنجی ساختار Lumina
# =========================================================
def validate_lumina_code(code: str):
    """
    بررسی ساختار اصلی کد تولیدشده.
    """

    errors = []

    # -----------------------------------------------------
    # importهای ضروری
    # -----------------------------------------------------
    required_imports = [
        "from manim import *",
        (
            "from lumina import "
            "LuminaScene, QuoteCard, FormulaHighlightCard"
        ),
        "from lumina.themes import KURDISH_FONT",
    ]

    for required_import in required_imports:

        if required_import not in code:
            errors.append(
                f"import ضروری پیدا نشد:\n{required_import}"
            )

    # -----------------------------------------------------
    # کلاس اصلی
    # -----------------------------------------------------
    if "class GeneratedVideo(LuminaScene):" not in code:
        errors.append(
            "کلاس GeneratedVideo(LuminaScene) پیدا نشد."
        )

    # -----------------------------------------------------
    # construct
    # -----------------------------------------------------
    if "def construct(self):" not in code:
        errors.append(
            "تابع construct(self) پیدا نشد."
        )

    # -----------------------------------------------------
    # QuoteCard
    # -----------------------------------------------------
    if "QuoteCard(" in code:

        if "quote=" in code:
            errors.append(
                "QuoteCard از quote= استفاده کرده است. "
                "باید text_content= استفاده شود."
            )

        if "font=" in code:
            errors.append(
                "QuoteCard از font= استفاده کرده است. "
                "باید font_name= استفاده شود."
            )

        if "text_content=" not in code:
            errors.append(
                "QuoteCard باید text_content= داشته باشد."
            )

    # -----------------------------------------------------
    # FormulaHighlightCard
    # -----------------------------------------------------
    if "FormulaHighlightCard(" in code:

        if "formula=" in code:
            errors.append(
                "FormulaHighlightCard از formula= استفاده کرده است. "
                "باید latex_str= استفاده شود."
            )

        if "latex=" in code:
            errors.append(
                "FormulaHighlightCard از latex= استفاده کرده است. "
                "باید latex_str= استفاده شود."
            )

        if "font=" in code:
            errors.append(
                "FormulaHighlightCard از font= استفاده کرده است. "
                "باید font_name= استفاده شود."
            )

        if "latex_str=" not in code:
            errors.append(
                "FormulaHighlightCard باید latex_str= داشته باشد."
            )

    return errors


# =========================================================
# 🤖 تولید کد توسط Gemini
# =========================================================
def generate_code_with_gemini(prompt: str):

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY خالی است."
        )

    if GEMINI_API_KEY == "AIzaSy...":
        raise RuntimeError(
            "GEMINI_API_KEY هنوز با کلید واقعی جایگزین نشده است."
        )

    try:
        client = genai.Client(
            api_key=GEMINI_API_KEY.strip()
        )

    except Exception as err:
        raise RuntimeError(
            f"خطا در ایجاد Gemini Client:\n{err}"
        ) from err

    response = None
    used_model = None
    last_error = None

    # -----------------------------------------------------
    # تلاش با مدل‌های مختلف
    # -----------------------------------------------------
    for model_name in FALLBACK_MODELS:

        try:

            response = client.models.generate_content(
                model=model_name,
                contents=(
                    SYSTEM_PROMPT
                    + "\n\n"
                    + "USER SCENARIO:\n"
                    + prompt
                ),
            )

            used_model = model_name
            break

        except Exception as err:

            last_error = err
            error_text = str(err)

            temporary_error = (
                "503" in error_text
                or "UNAVAILABLE" in error_text
                or "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
            )

            if temporary_error:

                st.warning(
                    f"مدل {model_name} موقتاً در دسترس نیست. "
                    "در حال امتحان مدل بعدی..."
                )

                continue

            raise RuntimeError(
                f"خطا در ارتباط با Gemini:\n{error_text}"
            ) from err

    # -----------------------------------------------------
    # هیچ مدلی پاسخ نداده
    # -----------------------------------------------------
    if response is None:

        raise RuntimeError(
            "هیچ‌یک از مدل‌های Gemini پاسخ ندادند.\n\n"
            f"آخرین خطا:\n{last_error}"
        )

    # -----------------------------------------------------
    # دریافت متن
    # -----------------------------------------------------
    raw_text = getattr(
        response,
        "text",
        None,
    )

    if not raw_text:

        raise RuntimeError(
            "Gemini پاسخی برای تولید کد برنگرداند."
        )

    code = clean_generated_code(
        raw_text
    )

    return code, used_model


# =========================================================
# 💾 ذخیره کد تولیدشده
# =========================================================
def save_generated_code(code: str) -> Path:

    output_file = (
        GENERATED_DIR / "auto_scene.py"
    )

    try:

        output_file.write_text(
            code,
            encoding="utf-8",
        )

    except Exception as err:

        raise RuntimeError(
            f"خطا در ذخیره فایل:\n{err}"
        ) from err

    return output_file


# =========================================================
# 🎬 اجرای Manim
# =========================================================
def render_video(
    python_file: Path,
    quality_flag: str,
):
    """
    اجرای Manim با همان Python interpreter که Streamlit
    با آن اجرا شده است.
    """

    command = [
        sys.executable,
        "-m",
        "manim",
        quality_flag,
        str(python_file),
        "GeneratedVideo",
    ]

    try:

        result = subprocess.run(
            command,
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    except Exception as err:

        raise RuntimeError(
            f"خطا در اجرای Manim:\n{err}"
        ) from err

    return result


# =========================================================
# 🔎 پیدا کردن فایل MP4
# =========================================================
def find_rendered_video():
    """
    فایل GeneratedVideo.mp4 را در پوشه media پیدا می‌کند.
    """

    if not MEDIA_DIR.exists():
        return None

    candidates = list(
        MEDIA_DIR.rglob(
            "GeneratedVideo.mp4"
        )
    )

    if not candidates:
        return None

    # جدیدترین فایل را انتخاب می‌کنیم
    candidates.sort(
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    return candidates[0]


# =========================================================
# 🚀 دکمه ساخت ویدیو
# =========================================================
if st.button(
    "🚀 ساخت خودکار ویدیو",
    use_container_width=True,
):

    # =====================================================
    # مرحله ۱: بررسی API Key
    # =====================================================
    if (
        not GEMINI_API_KEY
        or GEMINI_API_KEY == "AIzaSy..."
    ):

        st.error(
            "❌ ابتدا GEMINI_API_KEY را در ابتدای فایل "
            "با کلید واقعی Gemini جایگزین کنید."
        )

        st.stop()

    # =====================================================
    # بررسی سناریو
    # =====================================================
    if not user_prompt.strip():

        st.warning(
            "لطفاً ابتدا یک سناریو وارد کنید."
        )

        st.stop()

    # =====================================================
    # مرحله ۲: تولید کد
    # =====================================================
    with st.spinner(
        "۱/۲: در حال تولید کد Python توسط Gemini..."
    ):

        try:

            code, used_model = (
                generate_code_with_gemini(
                    user_prompt
                )
            )

        except Exception as err:

            st.error(
                "❌ خطا در تولید کد:"
            )

            st.code(
                str(err),
                language="text",
            )

            st.stop()

    # =====================================================
    # نمایش مدل استفاده‌شده
    # =====================================================
    st.sidebar.success(
        f"مدل فعال: {used_model}"
    )

    # =====================================================
    # مرحله ۳: بررسی Syntax
    # =====================================================
    syntax_ok, syntax_error = (
        check_python_syntax(code)
    )

    if not syntax_ok:

        st.error(
            "❌ کد تولیدشده دارای خطای Syntax است."
        )

        st.code(
            syntax_error,
            language="text",
        )

        with st.expander(
            "مشاهده کد تولیدشده"
        ):
            st.code(
                code,
                language="python",
            )

        st.stop()

    # =====================================================
    # مرحله ۴: بررسی API Lumina
    # =====================================================
    validation_errors = (
        validate_lumina_code(code)
    )

    if validation_errors:

        st.error(
            "❌ کد تولیدشده با API نصب‌شده Lumina "
            "سازگار نیست."
        )

        for error in validation_errors:

            st.warning(
                error
            )

        with st.expander(
            "مشاهده کد تولیدشده"
        ):
            st.code(
                code,
                language="python",
            )

        st.stop()

    # =====================================================
    # مرحله ۵: ذخیره فایل
    # =====================================================
    try:

        gen_file = save_generated_code(
            code
        )

    except Exception as err:

        st.error(
            str(err)
        )

        st.stop()

    # =====================================================
    # نمایش موفقیت تولید کد
    # =====================================================
    st.success(
        "✅ کد Python با موفقیت تولید و بررسی شد."
    )

    # =====================================================
    # نمایش کد
    # =====================================================
    with st.expander(
        "🐍 مشاهده کد تولیدشده",
        expanded=False,
    ):

        st.code(
            code,
            language="python",
        )

    # =====================================================
    # اطلاعات فایل
    # =====================================================
    st.caption(
        f"فایل تولیدشده: {gen_file}"
    )

    # =====================================================
    # مرحله ۶: رندر
    # =====================================================
    with st.spinner(
        "۲/۲: در حال کامپایل و رندر ویدیو با Manim..."
    ):

        q_flag = quality.split()[0]

        result = render_video(
            gen_file,
            q_flag,
        )

    # =====================================================
    # بررسی نتیجه رندر
    # =====================================================
    if result.returncode != 0:

        st.error(
            "❌ خطایی هنگام رندر انیمیشن رخ داد."
        )

        # -------------------------------------------------
        # stderr
        # -------------------------------------------------
        if result.stderr:

            st.subheader(
                "🔴 خطای Manim"
            )

            st.code(
                result.stderr,
                language="text",
            )

        # -------------------------------------------------
        # stdout
        # -------------------------------------------------
        if result.stdout:

            with st.expander(
                "📋 خروجی کامل Manim"
            ):

                st.code(
                    result.stdout,
                    language="text",
                )

        st.stop()

    # =====================================================
    # رندر موفق
    # =====================================================
    st.success(
        "🎉 ویدیو با موفقیت رندر شد!"
    )

    # =====================================================
    # پیدا کردن فایل ویدیو
    # =====================================================
    target_video = (
        find_rendered_video()
    )

    if (
        target_video
        and target_video.exists()
    ):

        st.success(
            f"🎬 فایل ویدیو آماده است:\n"
            f"{target_video}"
        )

        # -------------------------------------------------
        # پخش ویدیو
        # -------------------------------------------------
        st.video(
            str(target_video)
        )

        # -------------------------------------------------
        # دانلود
        # -------------------------------------------------
        try:

            video_data = (
                target_video.read_bytes()
            )

            st.download_button(
                label="⬇️ دانلود ویدیو MP4",
                data=video_data,
                file_name="lumina_video.mp4",
                mime="video/mp4",
                use_container_width=True,
            )

        except Exception as err:

            st.warning(
                f"ویدیو ساخته شد، اما آماده‌سازی دانلود "
                f"با خطا مواجه شد:\n{err}"
            )

    else:

        st.warning(
            "⚠️ Manim بدون خطا اجرا شد، اما فایل "
            "GeneratedVideo.mp4 پیدا نشد."
        )

        # -------------------------------------------------
        # نمایش خروجی Manim برای بررسی مسیر
        # -------------------------------------------------
        if result.stdout:

            with st.expander(
                "📋 خروجی Manim"
            ):

                st.code(
                    result.stdout,
                    language="text",
                )
