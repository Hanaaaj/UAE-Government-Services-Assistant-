"""
hero_slider.py — Auto-sliding hero banner with image + side text overlay.
Drop your images into the same folder as app.py and update SLIDES below.
Call render_hero_slider() from app.py to render it.
"""

import base64
import os
import streamlit as st


# ─────────────────────────────────────────────
# SLIDE DEFINITIONS
# Edit this list to customize each slide.
# image_file: filename of your image (must be in same folder as app.py)
# tag:        small label above the title (e.g. "🛂 Visa Services")
# title:      large headline — use \n for line breaks
# subtitle:   supporting text below the title
# btn_label:  call-to-action button text
# btn_href:   where the button links to
# accent:     highlight color for the tag pill
# ─────────────────────────────────────────────
SLIDES = [
    {
        "image_file": "slide1.jpg",           # ← replace with your image filename
        "tag": "🛂 Visa Services",
        "title": "Navigate UAE\nVisa Requirements",
        "subtitle": "From Golden Visa eligibility to tourist visa extensions — get instant, grounded answers with verified official sources.",
        "btn_label": "Ask About Visas →",
        "btn_href": "#chat",
        "accent": "#10B981",
    },
    {
        "image_file": "slide2.jpg",           # ← replace with your image filename
        "tag": "🚗 Driving License",
        "title": "Convert Your\nForeign License",
        "subtitle": "Check if your country qualifies for direct conversion and get step-by-step guidance through the RTA process.",
        "btn_label": "Check My License →",
        "btn_href": "#chat",
        "accent": "#FBBF24",
    },
    {
        "image_file": "slide3.jpg",           # ← replace with your image filename
        "tag": "🏢 Business License",
        "title": "Set Up Your\nBusiness in UAE",
        "subtitle": "Mainland, free zone, or offshore — understand the differences, costs, and steps to launch your company.",
        "btn_label": "Explore Options →",
        "btn_href": "#chat",
        "accent": "#818CF8",
    },
    {
        "image_file": "slide4.jpg",           # ← replace with your image filename
        "tag": "⭐ Golden Visa",
        "title": "Secure Your\n10-Year Residency",
        "subtitle": "Investors, entrepreneurs, talented professionals and their families — find out if you qualify for the UAE Golden Visa.",
        "btn_label": "Check Eligibility →",
        "btn_href": "#chat",
        "accent": "#F59E0B",
    },
]

# Arabic versions of the same slides
SLIDES_AR = [
    {
        "image_file": "slide1.jpg",
        "tag": "🛂 خدمات التأشيرة",
        "title": "تعرّف على\nمتطلبات التأشيرة",
        "subtitle": "من تأشيرة الذهب إلى تمديد تأشيرة السياحة — احصل على إجابات فورية مع مصادر رسمية موثّقة.",
        "btn_label": "اسأل عن التأشيرات ←",
        "btn_href": "#chat",
        "accent": "#10B981",
    },
    {
        "image_file": "slide2.jpg",
        "tag": "🚗 رخصة القيادة",
        "title": "حوّل رخصتك\nالأجنبية",
        "subtitle": "تحقق مما إذا كانت دولتك مؤهلة للتحويل المباشر واحصل على إرشادات خطوة بخطوة من هيئة الطرق والمواصلات.",
        "btn_label": "تحقق من رخصتي ←",
        "btn_href": "#chat",
        "accent": "#FBBF24",
    },
    {
        "image_file": "slide3.jpg",
        "tag": "🏢 الرخصة التجارية",
        "title": "أسّس شركتك\nفي الإمارات",
        "subtitle": "البر الرئيسي أو المنطقة الحرة أو الخارج — افهم الفروقات والتكاليف والخطوات لإطلاق شركتك.",
        "btn_label": "استكشف الخيارات ←",
        "btn_href": "#chat",
        "accent": "#818CF8",
    },
    {
        "image_file": "slide4.jpg",
        "tag": "⭐ التأشيرة الذهبية",
        "title": "احصل على\nإقامة 10 سنوات",
        "subtitle": "المستثمرون، رواد الأعمال، المهنيون الموهوبون وعائلاتهم — اكتشف ما إذا كنت مؤهلاً للتأشيرة الذهبية.",
        "btn_label": "تحقق من الأهلية ←",
        "btn_href": "#chat",
        "accent": "#F59E0B",
    },
]


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _img_to_b64(path: str) -> str | None:
    """Return base64-encoded image string, or None if file not found."""
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


def _placeholder_gradient(index: int) -> str:
    """Return a CSS gradient to use when an image file is missing."""
    gradients = [
        "linear-gradient(135deg, #063728 0%, #0F5A41 60%, #1a7a5a 100%)",
        "linear-gradient(135deg, #1e3a5f 0%, #2563EB 60%, #3b82f6 100%)",
        "linear-gradient(135deg, #3b0764 0%, #7C3AED 60%, #a855f7 100%)",
        "linear-gradient(135deg, #78350f 0%, #D97706 60%, #fbbf24 100%)",
    ]
    return gradients[index % len(gradients)]


# ─────────────────────────────────────────────
# MAIN RENDER FUNCTION
# ─────────────────────────────────────────────

def render_hero_slider(lang: str = "English", slide_interval_ms: int = 4500):
    """
    Render the auto-sliding hero banner.

    Args:
        lang:             "English" or "Arabic"
        slide_interval_ms: milliseconds between auto-slides (default 4500)
    """

    slides = SLIDES_AR if lang == "Arabic" else SLIDES
    n = len(slides)
    is_arabic = lang == "Arabic"

    # Build per-slide image + content HTML
    slides_html_parts = []
    dots_html_parts = []

    for i, slide in enumerate(slides):
        # Image
        b64 = _img_to_b64(slide["image_file"])
        if b64:
            img_css = f"url('data:image/jpeg;base64,{b64}')"
            img_style = f"background-image: {img_css}; background-size: cover; background-position: center;"
        else:
            img_style = f"background: {_placeholder_gradient(i)};"

        # Text side — left for English, right for Arabic
        text_position = "right: 0;" if is_arabic else "left: 0;"
        text_align = "right;" if is_arabic else "left;"
        title_lines = slide["title"].replace("\n", "<br>")
        accent = slide["accent"]

        slide_html = f"""
        <div class="hs-slide {'hs-slide-active' if i == 0 else ''}" id="hs-slide-{i}">

            <!-- Background image layer -->
            <div class="hs-bg" style="{img_style}"></div>

            <!-- Dark overlay for contrast -->
            <div class="hs-overlay"></div>

            <!-- Text panel -->
            <div class="hs-text-panel" style="{text_position} text-align: {text_align}">
                <div class="hs-tag" style="background: {accent}22; color: {accent}; border: 1px solid {accent}55;">
                    {slide['tag']}
                </div>
                <div class="hs-title">{title_lines}</div>
                <div class="hs-subtitle">{slide['subtitle']}</div>
                <a href="{slide['btn_href']}" class="hs-btn" style="background: {accent}; color: #fff;">
                    {slide['btn_label']}
                </a>
            </div>

        </div>
        """
        slides_html_parts.append(slide_html)
        dots_html_parts.append(
            f'<div class="hs-dot {"hs-dot-active" if i == 0 else ""}" onclick="hsGoTo({i})" id="hs-dot-{i}"></div>'
        )

    slides_html   = "\n".join(slides_html_parts)
    dots_html     = "\n".join(dots_html_parts)
    dir_attr      = 'dir="rtl"' if is_arabic else 'dir="ltr"'
    font_family   = "'Cairo', sans-serif" if is_arabic else "'Inter', sans-serif"

    full_html = f"""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Cairo:wght@400;600;700;800&display=swap" rel="stylesheet">

    <div class="hs-root" {dir_attr} style="font-family: {font_family};">

        <!-- SLIDES CONTAINER -->
        <div class="hs-track" id="hs-track">
            {slides_html}
        </div>

        <!-- LEFT ARROW -->
        <button class="hs-arrow hs-arrow-left" onclick="hsStep(-1)" aria-label="Previous">&#8592;</button>

        <!-- RIGHT ARROW -->
        <button class="hs-arrow hs-arrow-right" onclick="hsStep(1)" aria-label="Next">&#8594;</button>

        <!-- DOT INDICATORS -->
        <div class="hs-dots" id="hs-dots">
            {dots_html}
        </div>

        <!-- PROGRESS BAR -->
        <div class="hs-progress-track">
            <div class="hs-progress-bar" id="hs-progress-bar"></div>
        </div>

    </div>

    <style>
    /* ── Root container ── */
    .hs-root {{
        position: relative;
        width: 100%;
        border-radius: 24px;
        overflow: hidden;
        margin-bottom: 36px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.18);
        user-select: none;
    }}

    /* ── Slide track ── */
    .hs-track {{
        position: relative;
        width: 100%;
        height: 480px;
    }}

    /* ── Individual slide ── */
    .hs-slide {{
        position: absolute;
        inset: 0;
        opacity: 0;
        transition: opacity 0.75s cubic-bezier(0.4, 0, 0.2, 1);
        pointer-events: none;
    }}
    .hs-slide-active {{
        opacity: 1;
        pointer-events: auto;
    }}

    /* ── Background image layer ── */
    .hs-bg {{
        position: absolute;
        inset: 0;
        transition: transform 6s ease;
        transform: scale(1.04);
    }}
    .hs-slide-active .hs-bg {{
        transform: scale(1);
    }}

    /* ── Dark overlay for text legibility ── */
    .hs-overlay {{
        position: absolute;
        inset: 0;
        background: linear-gradient(
            to right,
            rgba(0, 0, 0, 0.72) 0%,
            rgba(0, 0, 0, 0.45) 45%,
            rgba(0, 0, 0, 0.08) 100%
        );
    }}
    [dir="rtl"] .hs-overlay {{
        background: linear-gradient(
            to left,
            rgba(0, 0, 0, 0.72) 0%,
            rgba(0, 0, 0, 0.45) 45%,
            rgba(0, 0, 0, 0.08) 100%
        );
    }}

    /* ── Text panel ── */
    .hs-text-panel {{
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        width: 48%;
        padding: 0 52px;
        z-index: 2;
    }}

    /* ── Tag pill ── */
    .hs-tag {{
        display: inline-block;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.8px;
        padding: 5px 14px;
        border-radius: 20px;
        margin-bottom: 18px;
        text-transform: uppercase;
    }}

    /* ── Title ── */
    .hs-title {{
        font-size: 44px;
        font-weight: 800;
        line-height: 1.12;
        color: #FFFFFF;
        margin-bottom: 18px;
        text-shadow: 0 2px 12px rgba(0,0,0,0.4);
    }}

    /* ── Subtitle ── */
    .hs-subtitle {{
        font-size: 15px;
        line-height: 1.65;
        color: rgba(255,255,255,0.85);
        margin-bottom: 32px;
        max-width: 400px;
    }}

    /* ── CTA Button ── */
    .hs-btn {{
        display: inline-block;
        padding: 13px 28px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 14px;
        text-decoration: none !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.25);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .hs-btn:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    }}

    /* ── Navigation arrows ── */
    .hs-arrow {{
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        z-index: 10;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.2);
        color: white;
        font-size: 20px;
        width: 44px;
        height: 44px;
        border-radius: 50%;
        cursor: pointer;
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
        transition: background 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    .hs-arrow:hover {{ background: rgba(255,255,255,0.28); }}
    .hs-arrow-left  {{ left:  18px; }}
    .hs-arrow-right {{ right: 18px; }}

    /* ── Dot indicators ── */
    .hs-dots {{
        position: absolute;
        bottom: 22px;
        left: 50%;
        transform: translateX(-50%);
        display: flex;
        gap: 8px;
        z-index: 10;
    }}
    .hs-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: rgba(255,255,255,0.35);
        cursor: pointer;
        transition: all 0.3s ease;
    }}
    .hs-dot-active {{
        background: #ffffff;
        width: 24px;
        border-radius: 4px;
    }}

    /* ── Progress bar ── */
    .hs-progress-track {{
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: rgba(255,255,255,0.1);
        z-index: 10;
    }}
    .hs-progress-bar {{
        height: 100%;
        background: rgba(255,255,255,0.6);
        width: 0%;
        transition: width linear;
    }}

    /* ── Responsive ── */
    @media (max-width: 768px) {{
        .hs-track       {{ height: 320px; }}
        .hs-title       {{ font-size: 26px; }}
        .hs-subtitle    {{ font-size: 13px; }}
        .hs-text-panel  {{ width: 80%; padding: 0 24px; }}
    }}
    </style>

    <script>
    (function() {{
        var total     = {n};
        var interval  = {slide_interval_ms};
        var current   = 0;
        var timer     = null;
        var progTimer = null;

        function getSlide(i)  {{ return document.getElementById('hs-slide-' + i); }}
        function getDot(i)    {{ return document.getElementById('hs-dot-' + i);   }}
        var progressBar = document.getElementById('hs-progress-bar');

        function startProgress() {{
            if (!progressBar) return;
            progressBar.style.transition = 'none';
            progressBar.style.width = '0%';
            // Force reflow
            void progressBar.offsetWidth;
            progressBar.style.transition = 'width ' + interval + 'ms linear';
            progressBar.style.width = '100%';
        }}

        function goTo(idx) {{
            // Deactivate current
            var oldSlide = getSlide(current);
            var oldDot   = getDot(current);
            if (oldSlide) oldSlide.classList.remove('hs-slide-active');
            if (oldDot)   oldDot.classList.remove('hs-dot-active');

            // Activate new
            current = (idx + total) % total;
            var newSlide = getSlide(current);
            var newDot   = getDot(current);
            if (newSlide) newSlide.classList.add('hs-slide-active');
            if (newDot)   newDot.classList.add('hs-dot-active');

            startProgress();
        }}

        function step(dir) {{
            clearInterval(timer);
            goTo(current + dir);
            timer = setInterval(function() {{ goTo(current + 1); }}, interval);
        }}

        // Expose to onclick handlers in HTML
        window.hsGoTo = function(i) {{
            clearInterval(timer);
            goTo(i);
            timer = setInterval(function() {{ goTo(current + 1); }}, interval);
        }};
        window.hsStep = step;

        // Auto-start
        startProgress();
        timer = setInterval(function() {{ goTo(current + 1); }}, interval);

        // Pause on hover
        var track = document.getElementById('hs-track');
        if (track) {{
            track.addEventListener('mouseenter', function() {{
                clearInterval(timer);
                if (progressBar) {{
                    progressBar.style.transition = 'none';
                }}
            }});
            track.addEventListener('mouseleave', function() {{
                startProgress();
                timer = setInterval(function() {{ goTo(current + 1); }}, interval);
            }});
        }}

        // Touch / swipe support
        var touchStartX = 0;
        if (track) {{
            track.addEventListener('touchstart', function(e) {{
                touchStartX = e.changedTouches[0].screenX;
            }}, {{ passive: true }});
            track.addEventListener('touchend', function(e) {{
                var diff = touchStartX - e.changedTouches[0].screenX;
                if (Math.abs(diff) > 40) step(diff > 0 ? 1 : -1);
            }}, {{ passive: true }});
        }}
    }})();
    </script>
    """

    st.components.v1.html(full_html, height=520, scrolling=False)
