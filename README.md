# SwitchMath

**Equation editing with one switch.**

For students who operate a computer with a single switch — a head switch, a sip-and-puff, one big
button — and still have algebra homework to do. The entire editor is driven by one key: the space
bar (or Enter, the on-screen PRESS button, or any switch interface that sends a key).

Live: https://divamchikara01.github.io/switchmath/

## Why

Math is two-dimensional; a switch user gets one input. Today they either dictate to an aide or type
linear syntax (`\frac{x+1}{2}`) through a scanning on-screen keyboard — 60+ keys per scan cycle, and
one missing brace breaks the equation.

SwitchMath scans the **structure** of the expression instead: *fraction → denominator → the "2" →
replace → 3*. Every list is 3–8 choices, the expression is always valid, and undo and export are one
step away at every level.

## How to use it

Open `index.html` in any browser. Nothing is installed and nothing leaves the computer.

- **Auto-scan** (default): the yellow highlight moves on its own; press when it is on what you want.
- **Step-scan**: short press = next, hold the switch = choose.
- The **Setup** panel (for a helper) sets the mode, scan speed, hold time, math size, spoken choices,
  and loads example expressions.
- **Export** copies the equation as LaTeX. Paste it into Word (Insert → Equation → LaTeX), Google
  Docs, or Overleaf.

Editing works the same at every level: scan the items of the current row, choose one. A structure
(fraction, exponent, root, parentheses) opens its parts; a symbol opens actions (replace, add
exponent, make fraction, insert after, delete). The symbol palette scans in groups: ✓ done, digits,
letters, operators, structures, ⌫ remove last.

## Measured on the prototype

Driving the editor with only the space bar (see `test_switchmath.py`):

| task | presses, step-scan | selections, auto-scan |
|---|---|---|
| change the denominator of (x+1)/2 to 3 | 11 | 7 |
| turn x into x² | 15 | 8 |
| delete the 2 by mistake, undo | 8 | 3 |
| export to LaTeX | 4 | 1 |
| build (a+b)²/12 from a blank screen | 68 | 25 |

## Run the tests

```
pip install playwright
python test_switchmath.py
```

The test opens `index.html` in headless Chromium, presses nothing but the space bar, and checks the
LaTeX after each task.

## Files

- `index.html` — the whole app: expression tree, renderer, scanning, palette, undo, LaTeX export.
- `test_switchmath.py` — the space-bar-only test.

## Status and limitations

Prototype built for the 2026 Congressional App Challenge. Not yet tested with switch users — that is
the next step. Missing symbols that real homework needs: decimals, subscripts, Greek letters, trig
functions, inequalities (in progress).

## AI disclosure

_(Divam writes this section.)_

## License

MIT
