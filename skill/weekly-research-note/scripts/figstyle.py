"""주간 리서치 노트 그림 스타일. 모든 그림과 수식 이미지는 이 모듈로 만든다.

    import sys; sys.path.insert(0, "<skill>/scripts")
    import figstyle as fs
    fs.setup()                      # 폰트·색·축 스타일 적용
    fig, ax = fs.figure(ratio=0.5)  # 문서 폭에 맞춘 캔버스
    ...
    fs.save(fig, "fig1.svg")
    fs.equation(r"\\sigma = \\frac{\\sqrt{k(G-k)}}{G}", "eq1.svg")

출력은 SVG다. 글자는 윤곽선으로 저장되므로 어느 기기에서 열어도 똑같이 보인다.
"""
import subprocess, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

# 색: 의미가 있을 때만 쓴다. ACCENT=핵심, WARM=주의·문제, GOOD=정상·정답, 나머지는 회색 계열.
INK, MUTED, LINE, CARD = "#1F2328", "#6E7781", "#D0D7DE", "#F3F5F7"
ACCENT, ACCENT_LIGHT = "#3451B2", "#E6EBFA"
WARM, WARM_LIGHT = "#D9480F", "#FFF0E8"
GOOD, GOOD_LIGHT = "#0F7B6C", "#E3F4F1"

KOREAN_OK = False
_CANDIDATES = ["Noto Sans CJK KR", "Noto Sans KR", "NanumGothic", "Malgun Gothic", "AppleGothic"]


def _find_korean_font():
    names = {f.name for f in font_manager.fontManager.ttflist}
    for c in _CANDIDATES:
        if c in names:
            return c
    return None


def setup():
    """폰트와 기본 스타일을 적용한다. 한글 폰트가 없으면 설치를 시도하고, 실패하면 KOREAN_OK=False."""
    global KOREAN_OK
    font = _find_korean_font()
    if font is None:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "koreanize-matplotlib",
                            "--break-system-packages"], check=True, capture_output=True, timeout=120)
            import koreanize_matplotlib  # noqa: F401  (NanumGothic 등록)
            font = "NanumGothic"
        except Exception:
            font = None
    KOREAN_OK = font is not None
    plt.rcParams.update({
        "font.family": [font] if font else ["DejaVu Sans"],
        "axes.unicode_minus": False,
        "font.size": 11,
        "text.color": INK, "axes.labelcolor": INK,
        "xtick.color": MUTED, "ytick.color": MUTED,
        "axes.edgecolor": LINE, "axes.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": False, "legend.frameon": False,
        "figure.facecolor": "white", "savefig.facecolor": "white",
        "mathtext.fontset": "cm",
        "svg.fonttype": "path",
        "svg.hashsalt": "weekly-research-note",
    })
    return KOREAN_OK


def figure(ratio=0.5, ncols=1):
    """문서 본문 폭(약 6.3in)에 맞춘 캔버스. ratio = 높이/폭."""
    w = 7.0
    return plt.subplots(1, ncols, figsize=(w, w * ratio))


def save(fig, path):
    """그림을 SVG로 저장한다 (확장자가 .png면 PNG)."""
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight", pad_inches=0.15, metadata={"Date": None})
    plt.close(fig)
    return path


def equation(latex, path, size=20):
    """matplotlib mathtext로 수식을 PNG로 만든다. \\text 대신 \\mathrm 을 쓴다."""
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, f"${latex}$", fontsize=size, color=INK)
    fig.savefig(path, dpi=250, bbox_inches="tight", pad_inches=0.08, metadata={"Date": None})
    plt.close(fig)
    return path
