"""Tests for voice / typed commands. Run:  python test_voice.py
Speech recognition can't run headless, so these type the same phrases into the command box —
everything after the recognizer is identical."""
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
    pg.goto(HTML + '?mode=step&help=0')
    pg.wait_for_timeout(200)

    def say(phrase):
        box = pg.locator('#cmd'); box.fill(phrase); box.press('Enter'); pg.wait_for_timeout(30)
    tex = lambda: pg.evaluate('SM.latex()')
    heard = lambda: pg.locator('#heard').inner_text()

    def check(name, expected):
        got = tex()
        ok = got == expected
        print(f"{'PASS' if ok else 'FAIL'} {name}: {got!r}" + ('' if ok else f"  expected {expected!r}  | {heard()}"))
        if not ok: failures.append(name)

    # --- editing the example by voice: the same four demo tasks, spoken ---
    say('denominator'); say('select'); say('replace'); say('3'); say('done')
    check('spoken: change denominator to 3', r'\frac{x + 1}{3} = y')
    say('undo'); say('undo')     # replace was one step, the 3 another — same as with the switch
    check('spoken: undo twice', r'\frac{x + 1}{2} = y')
    say('numerator'); say('select'); say('replace'); say('x squared'); say('done')   # the x is scanned first inside the numerator
    check('spoken: x -> x squared', r'\frac{x^{2} + 1}{2} = y')
    say('export')
    ok = pg.locator('#latex').input_value() == r'\frac{x^{2} + 1}{2} = y'
    print(('PASS' if ok else 'FAIL') + ' spoken: export'); ok or failures.append('export')

    # --- dictating whole expressions from a blank screen ---
    pg.evaluate("SM.load('empty')")
    say('x squared plus 1 all over 2 equals y')
    check('dictate: x squared plus 1 all over 2 equals y', r'\frac{x^{2} + 1}{2} = y')
    pg.evaluate("SM.load('empty')"); say('y equals x plus 1 all over 2 plus 3')
    check('dictate: y = (x+1)/2 + 3 — all over stops at relation signs', r'y = \frac{x + 1}{2 + 3}')
    pg.evaluate("SM.load('empty')"); say('1 over 2 plus 3')
    check('dictate: 1 over 2 plus 3 — over binds to one term', r'\frac{1}{2} + 3')
    pg.evaluate("SM.load('empty')"); say('x squared plus 1 all over 2 equals y')
    say('undo')
    check('dictate: one undo step removes the whole phrase', '')

    pg.evaluate("SM.load('empty')")
    say('square root of the quantity b squared minus 4 a c')
    check('dictate: square root of the quantity b squared minus 4 a c', r'\sqrt{b^{2} - 4 a c}')
    pg.evaluate("SM.load('empty')"); say('square root of b squared minus 4 a c')
    check('dictate: without the quantity, the root takes one term', r'\sqrt{b^{2}} - 4 a c')

    pg.evaluate("SM.load('empty')")
    say('sine theta less than or equal to 1')
    check('dictate: sine theta <= 1', r'\sin\left(\theta\right) \leq 1')

    pg.evaluate("SM.load('empty')")
    say('y equals 25 plus 7 times pi')
    check('dictate: y = 25 + 7 × π', r'y = 25 + 7 \times \pi')

    pg.evaluate("SM.load('empty')")
    say('make a fraction'); say('3'); say('denominator'); say('4'); say('done')
    check('dictate: a fraction, 3, denominator, 4', r'\frac{3}{4}')

    pg.evaluate("SM.load('empty')")
    say('open paren a plus b close paren squared over 2')
    check('dictate: (a + b)^2 over 2', r'\frac{\left(a + b\right)^{2}}{2}')

    pg.evaluate("SM.load('empty')")
    say('x to the power the quantity n plus 1 equals 8')
    check('dictate: x^(n+1) = 8', r'x^{n + 1} = 8')

    # --- navigation words ---
    pg.evaluate("SM.load('fraction')")
    i0 = pg.evaluate('SM.state.i'); say('next'); i1 = pg.evaluate('SM.state.i')
    ok = i1 == i0 + 1; print(('PASS' if ok else 'FAIL') + ' spoken: next advances'); ok or failures.append('next')
    pg.evaluate("SM.load('fraction')")
    say('denominator'); inside = pg.locator('#status').inner_text(); say('home'); home = pg.locator('#status').inner_text()
    ok = 'denominator' in inside and 'whole expression' in home
    print(('PASS' if ok else 'FAIL') + f' spoken: denominator / home  ({inside!r} -> {home!r})'); ok or failures.append('home')
    say('blorf'); ok = "didn't understand: blorf" in heard()
    print(('PASS' if ok else 'FAIL') + ' unknown word is reported'); ok or failures.append('ignored')

    # --- the switch still works and the command box does not steal it ---
    pg.evaluate("SM.load('fraction')")
    pg.locator('#cmd').fill('x'); pg.keyboard.press('Space')      # typing a space in the box must not press the switch
    ok = pg.evaluate('SM.presses') == 0; print(('PASS' if ok else 'FAIL') + ' space in the command box is not a switch press'); ok or failures.append('box')
    pg.locator('#cmd').fill('')
    pg.locator('body').click(position={'x': 5, 'y': 5})
    pg.keyboard.down('Space'); pg.wait_for_timeout(700); pg.keyboard.up('Space'); pg.wait_for_timeout(50)
    ok = pg.evaluate('SM.state.mode') == 'parts'; print(('PASS' if ok else 'FAIL') + ' switch still selects after using the box'); ok or failures.append('switch')

    if errors:
        print('page errors:', errors); failures.append('page errors')
    b.close()

print()
print('ALL VOICE TESTS PASS' if not failures else f'FAILED: {", ".join(failures)}')
sys.exit(0 if not failures else 1)
