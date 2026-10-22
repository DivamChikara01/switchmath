"""Feasibility test for SwitchMath: run ChatGPT's 4-task demo using ONLY the space bar (step-scan:
short press = next, hold = choose) and count presses. Also report what auto-scan would cost
(selections only, since the highlight moves by itself)."""
import time, pathlib, sys
from playwright.sync_api import sync_playwright

HTML = (pathlib.Path(__file__).parent / "index.html").resolve().as_uri()
SHOTS = pathlib.Path(__file__).parent / 'screenshots'; SHOTS.mkdir(exist_ok=True)

results = []
with sync_playwright() as p:
    try:
        b = p.chromium.launch()
    except Exception:
        b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
    pg = b.new_page(viewport={'width': 1240, 'height': 860})
    errors = []
    pg.on('pageerror', lambda e: errors.append(str(e)))
    pg.goto(HTML + '?mode=step&hold=300')
    pg.wait_for_timeout(200)

    counts = {'short': 0, 'long': 0}
    def short(n=1):
        for _ in range(n):
            pg.keyboard.down('Space'); pg.wait_for_timeout(40); pg.keyboard.up('Space'); pg.wait_for_timeout(40)
            counts['short'] += 1
    def long():
        pg.keyboard.down('Space'); pg.wait_for_timeout(400); pg.keyboard.up('Space'); pg.wait_for_timeout(40)
        counts['long'] += 1
    tex = lambda: pg.evaluate('SM.latex()')
    status = lambda: pg.locator('#status').inner_text()
    chips = lambda: [c.strip() for c in pg.locator('#menu .chip').all_inner_texts()]

    def task(name, expected):
        got = tex()
        ok = got == expected
        results.append((name, ok, got, dict(counts)))
        print(f"{'PASS' if ok else 'FAIL'} {name}: {got!r}  presses so far: short={counts['short']} long={counts['long']}")
        if not ok:
            print('   expected', repr(expected), '| status:', status(), '| chips:', chips())
        counts['short'] = counts['long'] = 0
        return ok

    assert tex() == r'\frac{x + 1}{2} = y', tex()
    pg.screenshot(path=str(SHOTS / '0_start.png'))

    # ---- Task 1: change the denominator 2 -> 3 --------------------------------
    long()                     # choose the fraction          -> parts: numerator / denominator
    short(); long()            # -> denominator               -> scanning inside "2"
    long()                     # choose "2"                   -> actions
    long()                     # replace                      -> palette, on DIGITS
    long()                     # open digits
    short(3); long()           # 0 -> 3, choose 3             -> inserted, back on "done"
    pg.screenshot(path=str(SHOTS / '1_palette.png'))
    long()                     # done
    task('T1 replace denominator 2->3', r'\frac{x + 1}{3} = y')

    # ---- Task 2: x -> x^2 -----------------------------------------------------
    # now scanning inside the denominator: [3, add, undo, export, up]
    short(4); long()           # up -> root, landing on the fraction
    long()                     # choose fraction -> parts
    long()                     # numerator -> scanning inside: x + 1
    long()                     # choose x -> actions
    short(); long()            # add exponent -> palette on exponent row, DIGITS
    long()                     # open digits
    short(2); long()           # choose 2
    long()                     # done
    pg.screenshot(path=str(SHOTS / '2_after_exponent.png'))
    task('T2 add exponent x->x^2', r'\frac{x^{2} + 1}{3} = y')

    # ---- Task 3: make a mistake (delete the 2) and undo it ------------------------
    # scanning inside the exponent: [2, add, undo, export, up]
    long()                     # choose 2 -> actions
    short(4); long()           # delete
    assert tex() == r'\frac{x^{} + 1}{3} = y', tex()
    # now [add, undo, export, up] (exponent row is empty)
    short(); long()            # undo
    task('T3 delete then undo', r'\frac{x^{2} + 1}{3} = y')

    # ---- Task 4: export ---------------------------------------------------------
    short(3); long()           # export (available at every level)
    toast = pg.locator('#toast').inner_text()
    ta = pg.locator('#latex').input_value()
    ok = ta == r'\frac{x^{2} + 1}{3} = y' and 'copied' in toast.lower()
    results.append(('T4 export', ok, ta, dict(counts)))
    print(f"{'PASS' if ok else 'FAIL'} T4 export: textarea={ta!r} toast={toast!r} presses: short={counts['short']} long={counts['long']}")
    counts['short'] = counts['long'] = 0
    pg.screenshot(path=str(SHOTS / '3_export.png'))

    # ---- Bonus: build (a+b)^2 / 2 from a blank, exercising fraction + paren + exponent + multi-digit
    pg.evaluate("SM.load('empty')")
    long()                     # [add, undo, export] -> add -> palette DIGITS
    short(3); long()           # structures row
    long()                     # fraction -> palette now targets the numerator
    short(4); long()           # structures
    short(3); long()           # ( ) -> targets inside parens
    short(2); long()           # letters
    short(3); long()           # a
    short(3); long()           # operators
    long()                     # +
    short(2); long()           # letters
    short(4); long()           # b
    long()                     # done -> scanning inside parens, landing on b: [a, +, b, ->fill blank, add, undo, export, up]
    short(5); long()           # up -> inside numerator, on the ( )
    # make the parenthesis a power: use palette 'exponent' after it
    short(2); long()           # [( ), ->fill blank, add, ...] -> add -> palette at end of numerator, DIGITS
    short(3); long()           # structures
    short(); long()            # exponent -> wraps the ( ), targets exponent; lands on done
    short(); long()            # digits
    short(2); long()           # 2
    long()                     # done -> inside exponent [2, ->fill blank, add, undo, export, up]
    short(); long()            # fill blank -> the denominator, palette DIGITS
    long()                     # digits
    short(); long()            # 1
    short(); long()            # digits again
    short(2); long()           # 2  -> appends: 12
    long()                     # done
    task('T5 build (a+b)^2/12 from blank', r'\frac{\left(a + b\right)^{2}}{12}')
    pg.screenshot(path=str(SHOTS / '4_built.png'))

    # ---- auto-scan sanity: highlight advances by itself and a press selects
    pg.goto(HTML + '?mode=auto&speed=300')
    pg.wait_for_timeout(1000)
    i1 = pg.evaluate('SM.state.i'); pg.wait_for_timeout(350); i2 = pg.evaluate('SM.state.i')
    auto_ok = i1 != i2
    pg.keyboard.press('Space'); pg.wait_for_timeout(50)
    auto_ok = auto_ok and pg.evaluate('SM.state.mode') in ('parts', 'actions', 'palette') or pg.evaluate('SM.state.mode') == 'nav'
    print('auto-scan advances by itself:', i1 != i2, '| mode after press:', pg.evaluate('SM.state.mode'))

    # quadratic renders without errors
    pg.evaluate("SM.load('quadratic')"); pg.wait_for_timeout(100)
    pg.screenshot(path=str(SHOTS / '5_quadratic.png'))
    print('quadratic LaTeX:', tex())
    print('page errors:', errors or 'none')
    b.close()

print()
allok = all(r[1] for r in results) and not errors
print('ALL PASSED' if allok else 'SOMETHING FAILED')
sys.exit(0 if allok else 1)
