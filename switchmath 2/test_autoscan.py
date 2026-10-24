"""Measures the four demo tasks in AUTO-SCAN: the highlight moves by itself, the test waits until it is on
the wanted choice and presses once, exactly as a switch user would. Reports presses per task.
Run:  python test_autoscan.py        (scan step is set to 200 ms so a full run takes ~1 minute)"""
import pathlib, sys, time
from playwright.sync_api import sync_playwright

HTML = (pathlib.Path(__file__).parent / "index.html").resolve().as_uri()
STEP_MS = 200

with sync_playwright() as p:
    try:
        b = p.chromium.launch()
    except Exception:
        b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
    pg = b.new_page()
    errors = []; pg.on('pageerror', lambda e: errors.append(str(e)))
    pg.goto(HTML + f'?mode=auto&speed={STEP_MS}&help=0'); pg.wait_for_timeout(300)
    tex = lambda: pg.evaluate('SM.latex()')

    presses = 0
    def press_when(choice, mode=None):
        """Wait for the highlight to reach `choice` (optionally in `mode`), then press the switch once."""
        global presses
        deadline = time.time() + 15
        while time.time() < deadline:
            cur, m = pg.evaluate('[SM.choice(), SM.state.mode]')
            if cur == choice and (mode is None or m == mode):
                pg.keyboard.press('Space'); presses += 1
                pg.wait_for_timeout(60)
                return
            pg.wait_for_timeout(8)
        raise AssertionError(f'highlight never reached {choice!r} (mode {mode}); last seen {cur!r} in {m}')

    results = []
    def task(name, expected):
        global presses
        got = tex(); ok = got == expected
        results.append((name, ok, presses)); print(f"{'PASS' if ok else 'FAIL'} {name}: {presses} presses -> {got!r}")
        presses = 0
        return ok

    assert tex() == r'\frac{x + 1}{2} = y', tex()
    t0 = time.time()
    # T1: change the denominator 2 -> 3
    press_when('fraction', 'nav'); press_when('denominator', 'parts'); press_when('2', 'nav')
    press_when('replace', 'actions'); press_when('digits', 'palette'); press_when('3', 'palette'); press_when('✓ finish inserting', 'palette')
    task('T1 denominator 2 -> 3', r'\frac{x + 1}{3} = y')
    # T2: x -> x^2
    press_when('↑ back to fraction', 'nav'); press_when('fraction', 'nav'); press_when('numerator', 'parts'); press_when('x', 'nav')
    press_when('add exponent', 'actions'); press_when('digits', 'palette'); press_when('2', 'palette'); press_when('✓ finish inserting', 'palette')
    task('T2 x -> x^2', r'\frac{x^{2} + 1}{3} = y')
    # T3: delete the 2 by mistake, undo
    press_when('2', 'nav'); press_when('delete', 'actions'); press_when('↶ undo', 'nav')
    task('T3 delete then undo', r'\frac{x^{2} + 1}{3} = y')
    # T4: export
    press_when('⤓ export', 'nav'); pg.wait_for_timeout(300)
    last = pg.evaluate('SM.lastExport')
    ok4 = last is not None and last['text'] == r'\frac{x^{2} + 1}{3} = y'
    results.append(('T4 export', ok4, presses)); print(f"{'PASS' if ok4 else 'FAIL'} T4 export: {presses} presses -> {'copied' if last and last['copied'] else 'fallback (clipboard unavailable here)'}")
    presses = 0
    elapsed = time.time() - t0
    total = sum(r[2] for r in results)
    print(f"\nAuto-scan, {STEP_MS} ms per step: {total} presses for the four tasks, {elapsed:.0f} s wall time including waiting for the highlight.")
    if errors: print('page errors:', errors)
    b.close()

ok = all(r[1] for r in results) and not errors
print('ALL AUTO-SCAN TASKS PASS' if ok else 'SOMETHING FAILED')
sys.exit(0 if ok else 1)
