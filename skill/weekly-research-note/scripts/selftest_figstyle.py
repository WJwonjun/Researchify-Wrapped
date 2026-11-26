"""figstyle 모듈이 쓸 만한지 확인한다.

    python selftest_figstyle.py <figstyle.py 경로>

성공하면 OK를 출력하고, 실패하면 원인을 출력하고 1로 끝난다.
"""
import importlib.util, os, sys, tempfile, traceback


def main(path):
    spec = importlib.util.spec_from_file_location("figstyle_under_test", path)
    fs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fs)
    for name in ["setup", "figure", "save", "equation", "INK", "MUTED", "ACCENT", "WARM", "GOOD"]:
        assert hasattr(fs, name), f"{name} 이(가) 없어요 (이름과 인자는 바꾸지 말고 추가만 하세요)"
    fs.setup()
    d = tempfile.mkdtemp()
    fig, ax = fs.figure(ratio=0.5)
    ax.plot([0, 1], [0, 1], color=fs.ACCENT)
    ax.set_xlabel("테스트 라벨")
    outs = [fs.save(fig, os.path.join(d, "t.svg")),
            fs.equation(r"\sigma = \frac{\sqrt{k\,(G-k)}}{G}", os.path.join(d, "e.svg"))]
    for p in outs:
        s = open(p, encoding="utf-8").read()
        assert "<svg" in s, f"{p}: SVG가 아니에요"
        assert "<script" not in s.lower(), f"{p}: 스크립트가 들어 있어요"
        assert len(s.encode()) < 250 * 1024, f"{p}: 250 KB를 넘어요"
    print("OK")


if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except Exception:
        traceback.print_exc()
        print("실패")
        sys.exit(1)
