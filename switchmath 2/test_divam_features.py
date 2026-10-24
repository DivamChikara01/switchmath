"""Tests for Divam's two features (see DIVAM_TODO.md). Run:  python test_divam_features.py
Both fail until the features exist. Step-scan: short press = next, hold = choose."""
import pathlib, sys
from playwright.sync_api import sync_playwright

HTML = (pathlib.Path(__file__).parent / "index.html").resolve().as_uri()
failures = []

with sync_playwright() as p:
    try:
        b = p.chromium.launch()
    except Exception:
        b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
    pg = b.new_page()
    errors = []
    pg.on('pageerror', lambda e: errors.append(str(e)))
    pg.goto(HTML + '?mode=step&hold=300&help=0')
    pg.wait_for_timeout(200)

    def short(n=1):
        for _ in range(n):
            pg.keyboard.down('Space'); pg.wait_for_timeout(40); pg.keyboard.up('Space'); pg.wait_for_timeout(40)
    def long():
        pg.keyboard.down('Space'); pg.wait_for_timeout(400); pg.keyboard.up('Space'); pg.wait_for_timeout(40)
    tex = lambda: pg.evaluate('SM.latex()')

    def check(name, expected):
        got = tex()
        print(f"{'PASS' if got == expected else 'FAIL'} {name}: got {got!r}, expected {expected!r}")
        if got != expected:
            failures.append(name)

    # ---------- Feature 1: decimal point ----------
    # Palette digits row must have 11 keys: 0-9 then '.'  (the '.' is key index 10)
    pg.evaluate("SM.load('empty')")
    long()                    # add -> palette, on digits
    long()                    # open digits
    short(3); long()          # 3        (palette lands on done)
    short(); long()           # digits
    short(10); long()         # .
    short(); long()           # digits
    short(1); long()          # 1
    short(); long()           # digits
    short(4); long()          # 4
    long()                    # done
    check('decimal: 3 . 1 4 -> 3.14', '3.14')

    pg.evaluate("SM.load('empty')")
    long(); long()
    short(3); long()          # 3
    short(); long(); short(10); long()   # .
    short(); long(); short(10); long()   # .  (ignored: already has one)
    long()                    # done
    check('decimal: 3 . . -> 3.', '3.')

    pg.evaluate("SM.load('empty')")
    long(); long()
    short(10); long()         # .  -> starts "0."
    short(); long(); short(5); long()    # 5
    long()                    # done
    check('decimal: . 5 -> 0.5', '0.5')

    # ---------- Feature 2: subscript ----------
    pg.evaluate("SM.load('fraction')")
    long()                    # fraction -> parts
    long()                    # numerator -> inside x + 1
    long()                    # x -> actions
    short(5); long()          # add subscript (index 5) -> palette on the subscript row, digits
    long()                    # open digits
    short(1); long()          # 1
    long()                    # done
    check('subscript via actions: x -> x_1', r'\frac{x_{1} + 1}{2} = y')

    pg.evaluate("SM.load('empty')")
    long()                    # add -> palette digits
    short(); long()           # letters
    short(3); long()          # a
    short(4); long()          # structures
    short(4); long()          # subscript (index 4, at the END of the structures row) -> wraps a, targets subscript row
    short(2); long()          # letters
    short(2); long()          # n
    long()                    # done
    check('subscript via palette: a n -> a_n', r'a_{n}')

    if errors:
        print('page errors:', errors)
        failures.append('page errors')
    b.close()

print()
print('ALL DIVAM FEATURES PASS' if not failures else f'NOT YET: {len(failures)} failing -> ' + ', '.join(failures))
sys.exit(0 if not failures else 1)
