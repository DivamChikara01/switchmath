"""Documents, menu, pause, export fallback and grouping. Run:  python test_documents.py
Uses the space bar (step-scan) plus typed commands where that is shorter; checks persistence by reloading."""
import pathlib, sys
from playwright.sync_api import sync_playwright

HTML = (pathlib.Path(__file__).parent / "index.html").resolve().as_uri()
failures = []
def check(name, ok, detail=''):
    print(f"{'PASS' if ok else 'FAIL'} {name}" + (f"  [{detail}]" if detail and not ok else ''))
    if not ok: failures.append(name)

with sync_playwright() as p:
    try:
        b = p.chromium.launch()
    except Exception:
        b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
    ctx = b.new_context(accept_downloads=True)
    pg = ctx.new_page()
    errors = []
    pg.on('pageerror', lambda e: errors.append(str(e)))
    URL = HTML + '?mode=step&hold=300&help=0'
    pg.goto(URL); pg.wait_for_timeout(300)

    def say(t): box = pg.locator('#cmd'); box.fill(t); box.press('Enter'); pg.wait_for_timeout(40)
    def short(n=1):
        for _ in range(n): pg.keyboard.down('Space'); pg.wait_for_timeout(40); pg.keyboard.up('Space'); pg.wait_for_timeout(40)
    def long(): pg.keyboard.down('Space'); pg.wait_for_timeout(400); pg.keyboard.up('Space'); pg.wait_for_timeout(40)
    tex = lambda: pg.evaluate('SM.latex()')
    docs = lambda: pg.evaluate('SM.docs()')
    status = lambda: pg.locator('#status').inner_text()
    pill = lambda: pg.locator('#docpill').inner_text()
    def wait_saved():
        for _ in range(40):
            if not docs()['dirty']: return True
            pg.wait_for_timeout(50)
        return False

    # ---- 1. first run: one document with the example, saved ----
    d = docs()
    check('first run creates "Equation 1" and saves it', d['names'] == ['Equation 1'] and d['storageOk'] and wait_saved(), str(d))
    check('pill shows the document and save state', pill() == 'Equation 1 · saved', pill())

    # ---- 2. edit, then reload: the edit survives ----
    say('denominator'); say('select'); say('replace'); say('7'); say('done')
    check('edit applied', tex() == r'\frac{x + 1}{7} = y', tex())
    check('autosave lands', wait_saved())
    pg.reload(); pg.wait_for_timeout(300)
    check('edit survives a reload', tex() == r'\frac{x + 1}{7} = y', tex())
    check('reload keeps the same document', docs()['names'] == ['Equation 1'])

    # ---- 3. two documents hold different content ----
    say('menu'); check('menu opens', pg.evaluate('SM.state.mode') == 'menu')
    short(1); long()                     # new equation
    check('new document is blank and current', tex() == '' and docs()['names'] == ['Equation 1', 'Equation 2'] and pill().startswith('Equation 2'), pill())
    say('y equals 3')
    check('content goes into the new document', tex() == 'y = 3', tex())
    wait_saved()
    pg.reload(); pg.wait_for_timeout(300)
    check('after reload the second document is still current with its content', tex() == 'y = 3' and pill().startswith('Equation 2'), tex() + ' | ' + pill())
    # open Equation 1 through the scan menu: menu -> open -> first entry
    say('menu'); short(2); long()         # open…
    check('document list shows both', [c.strip() for c in pg.locator('#menu .chip').all_inner_texts()][:2] == ['Equation 1', 'Equation 2 (open now)'], str(pg.locator('#menu .chip').all_inner_texts()))
    long()                                # Equation 1 (index 0)
    check('opening Equation 1 restores its content', tex() == r'\frac{x + 1}{7} = y' and pill().startswith('Equation 1'), tex())

    # ---- 4. delete needs a confirmation; "no" keeps it ----
    say('menu'); short(3); long()         # delete this equation -> confirm
    check('confirm list: no first, yes second', [c.strip() for c in pg.locator('#menu .chip').all_inner_texts()] == ['no, keep it', 'yes, delete “Equation 1”'])
    long()                                # no
    check('"no" keeps the document and returns to the menu', docs()['names'] == ['Equation 1', 'Equation 2'] and pg.evaluate('SM.state.mode') == 'menu')
    long()                                # (menu index 3 = delete) -> confirm again
    short(1); long()                      # yes
    check('"yes" deletes it and opens the remaining one', docs()['names'] == ['Equation 2'] and tex() == 'y = 3', str(docs()) + ' ' + tex())
    wait_saved(); pg.reload(); pg.wait_for_timeout(300)
    check('deletion persists', docs()['names'] == ['Equation 2'])

    # ---- 5. menu is reachable from every mode, and "back" returns to where you were ----
    pg.evaluate("SM.load('fraction')")
    long()                                # fraction -> parts
    labels = [c.strip() for c in pg.locator('#menu .chip').all_inner_texts()]
    check('parts list ends with the menu', labels[-1] == '≡ menu', str(labels))
    short(len(labels) - 1); long()        # menu from parts
    check('menu from parts', pg.evaluate('SM.state.mode') == 'menu')
    short(8); long()                      # back
    check('back returns to parts', pg.evaluate('SM.state.mode') == 'parts')
    long()                                # numerator -> nav
    long()                                # x -> actions
    labels = [c.strip() for c in pg.locator('#menu .chip').all_inner_texts()]
    check('actions list ends with the menu', labels[-1] == '≡ menu', str(labels))
    short(len(labels) - 1); long(); short(8); long()
    check('menu from actions and back', pg.evaluate('SM.state.mode') == 'actions')
    long()                                # replace -> palette
    rows = pg.locator('#menu .prow').count()
    short(rows - 2); long()               # from digits (row 1) to the ≡ menu row (second to last: voice row is hidden when voice is off... check)
    check('menu from the palette', pg.evaluate('SM.state.mode') == 'menu', pg.evaluate('SM.state.mode'))
    short(8); long()
    check('back returns to the palette with the cursor intact', pg.evaluate('SM.state.mode') == 'palette' and pg.evaluate('SM.state.pal.pos') == 0)
    say('done')

    # ---- 6. pause: the timer stops, status says so, the next press only resumes ----
    pg.goto(HTML + '?mode=auto&speed=200&help=0'); pg.wait_for_timeout(300)
    say('pause')
    check('pause reported', pg.evaluate('SM.paused') and status().startswith('Paused'), status())
    i1 = pg.evaluate('SM.state.i'); pg.wait_for_timeout(500); i2 = pg.evaluate('SM.state.i')
    check('highlight does not move while paused', i1 == i2)
    before = tex(); mode_before = pg.evaluate('SM.state.mode')
    pg.keyboard.press('Space'); pg.wait_for_timeout(50)
    check('a press while paused resumes without selecting anything', not pg.evaluate('SM.paused') and tex() == before and pg.evaluate('SM.state.mode') == 'nav', pg.evaluate('SM.state.mode'))
    check('resume press is not counted', pg.evaluate('SM.presses') == 0)

    # ---- 7. export: clipboard is denied here, so the fallback must download a .tex file and say so ----
    pg.goto(URL); pg.wait_for_timeout(300)
    with pg.expect_download(timeout=5000) as dl:
        say('export')
    download = dl.value
    body = pathlib.Path(download.path()).read_text()
    last = pg.evaluate('SM.lastExport')
    check('clipboard failure -> switchmath.tex downloaded with the LaTeX', download.suggested_filename == 'switchmath.tex' and body == tex(), body)
    check('export reports the truth (not copied)', last['copied'] is False and 'not available' in pg.locator('#exportmsg').inner_text(), pg.locator('#exportmsg').inner_text())

    # ---- 8. grouping: a power of a power, and a compound base, show and export with parentheses ----
    pg.evaluate("SM.load('empty')"); say('x squared cubed')
    check('(x^2)^3 exports with parentheses', tex() == r'\left(x^{2}\right)^{3}', tex())
    check('(x^2)^3 displays parentheses', pg.locator('#canvas').inner_text().replace(' ', '').startswith('(x2)3') or '(' in pg.locator('#canvas').inner_text(), pg.locator('#canvas').inner_text())
    pg.evaluate("SM.load('empty')"); say('open paren x plus 1 close paren squared')
    check('(x+1)^2 keeps its parentheses once', tex() == r'\left(x + 1\right)^{2}', tex())
    pg.evaluate("SM.load('empty')"); say('sine x')
    short(1); long()          # add -> palette
    short(3); long()          # structures
    short(1); long()          # exponent wraps sin( )
    short(1); long()          # digits
    short(2); long()          # 2
    long()                    # finish
    check('sin(x)^2 via the palette needs no extra parentheses', tex() == r'\sin\left(x\right)^{2}', tex())

    # ---- 9. input never latches: a lost release must not block the next press ----
    pg.goto(URL); pg.wait_for_timeout(300)
    pg.keyboard.down('Space'); pg.evaluate('window.dispatchEvent(new Event("blur"))'); pg.wait_for_timeout(50)
    pg.keyboard.up('Space')               # ignored: isDown was reset by blur
    pg.keyboard.down('Space'); pg.wait_for_timeout(400); pg.keyboard.up('Space'); pg.wait_for_timeout(50)
    check('switch works after the window lost focus mid-press', pg.evaluate('SM.state.mode') == 'parts', pg.evaluate('SM.state.mode'))

    if errors: print('page errors:', errors); failures.append('page errors')
    b.close()

print()
print('ALL DOCUMENT TESTS PASS' if not failures else f'FAILED: {", ".join(failures)}')
sys.exit(0 if not failures else 1)
