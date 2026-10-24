# SwitchMath

**Equation editing with one switch.**

For students who operate a computer with a single switch — a head switch, a sip-and-puff, one big
button — and still have algebra homework to do. The whole editor is driven by one key: the space bar
(or Enter, the on-screen PRESS button, or a switch interface configured to send Space or Enter).

Live: https://divamchikara01.github.io/switchmath/

## Why

Math is two-dimensional; a switch user gets one input. Today they either dictate to an aide or type
linear syntax (`\frac{x+1}{2}`) through a scanning on-screen keyboard, where one missing brace breaks
the equation.

SwitchMath scans the **structure** of the expression instead: *fraction → denominator → the "2" →
replace → 3*. The editor keeps the expression's structure intact while you work (a blank slot is
shown as a dashed box until you fill it), and undo, export and a menu are in every list.

## How to use it

Open `index.html` in any browser. Nothing is installed. Equations are saved in that browser on that
device; with Voice off, nothing leaves the computer.

- **Auto-scan** (default): the yellow highlight moves on its own; press when it is on what you want.
- **Step-scan**: short press = next, hold the switch = choose.
- The status line always says where you are and what a press will choose, e.g.
  *Editing the denominator of the fraction · press to choose: 2*.
- The **Setup** panel (for a helper) sets the mode, scan speed, hold time, math size, spoken choices,
  Voice, and loads example expressions. Helpers with a mouse can also click any choice.

Editing works the same at every level: scan the items of the current row, choose one. A structure
(fraction, exponent, root, parentheses, a function like sin) opens its parts; a symbol opens actions
(replace, add exponent, make fraction, insert after, delete). The symbol palette scans in groups:
✓ finish inserting · digits · letters (including π and θ) · operators (+ − × · = < > ≤ ≥ ≠) ·
structures · functions (sin cos tan log ln) · ⌫ remove last · ≡ menu.

**The menu** (≡, in every list) pauses scanning (the next press only resumes), starts a new equation,
opens a saved one, deletes the current one (with a yes/no step), changes speed, exports, and opens
the guide.

**Documents.** Every change is saved automatically in the browser (localStorage) under an automatic
name — "Equation 1", "Equation 2" — so nobody has to type a title with a switch. The header shows the
document name and *saved / saving… / not saved — storage unavailable*. One equation per document.

**Export** copies the equation as LaTeX and says whether the copy succeeded. If the clipboard is not
available, a `switchmath.tex` file is downloaded instead and the text is selected. Tested destination:
Word (Insert → Equation → LaTeX) and Overleaf; paste the LaTeX there.

The header also counts presses and the seconds between the first and last press. That is a
debugging aid for one task, not a comparison with other editors.

## Voice (optional)

Some switch users can speak. In **Setup → Voice** choose *Push-to-talk* (a **🎤 say it** choice appears in
every list, so the switch starts the microphone) or *Always listening*. Say math — “x squared plus one
all over two equals y”, “the square root of the quantity b squared minus 4 a c”, “sine theta” — and it is
parsed into the same tree and inserted at the cursor. Say commands — “denominator”, “select”, “next”,
“back”, “replace”, “delete”, “undo”, “export”, “done”, “menu”, “pause” — to drive the editor. “over”
binds to one term (“1 over 2 plus 3” is ½ + 3); “all over” takes everything since the last equals
sign; “the quantity … end quantity” groups. The same text can be typed into the command box, which is
how `test_voice.py` tests it.

The browser does the speech recognition; everything after that is a small deterministic grammar in
`index.html`. Voice is off by default because in Chrome the browser sends audio to Google's speech
service. Recognition can mishear; the status line shows what was heard and what it did, and undo
removes a whole misheard phrase in one step.

## Measured on this version

Driving the editor with only the space bar, in **auto-scan** (`test_autoscan.py`, 200 ms per step)
and in step-scan (`test_switchmath.py`, every press counted):

| task | presses, auto-scan | presses, step-scan |
|---|---|---|
| change the denominator of (x+1)/2 to 3 | 7 | 11 |
| turn x into x² | 8 | 15 |
| delete the 2 by mistake, undo | 3 | 8 |
| export to LaTeX | 1 | 4 |
| build (a+b)²/12 from a blank screen | — | 68 |

These measure this editor on these tasks. They are not a comparison with other editors.

## Run the tests

```
pip install playwright
python test_switchmath.py      # the four demo tasks and a from-blank build, step-scan
python test_autoscan.py        # the same four tasks in auto-scan, pressing only when the highlight is right
python test_documents.py       # saving, reopening, deleting, the menu from every mode, pause, export fallback, grouping
python test_voice.py           # spoken/typed phrases and commands
python test_divam_features.py  # decimal point and subscript
```

Each test opens `index.html` in headless Chromium and presses nothing but the space bar (or types the
phrase a user would say).

## Files

- `index.html` — the whole app: expression tree, renderer, scanning, palette, menu, documents, undo,
  LaTeX export, voice grammar.
- `test_*.py` — the tests above.

## Status and limitations

Prototype built for the 2026 Congressional App Challenge. Not yet tested with students who use
switches — that is the next step. Decimal numbers and subscripts are in progress. Nested roots render
roughly. No integrals, sums or matrices.

## AI disclosure

_(Divam writes this section.)_

## License

MIT
