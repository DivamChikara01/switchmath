# Your two features

Two things real homework needs that SwitchMath can't do yet. You write both. Every place you need to
touch in `index.html` is marked with a comment `// [DIVAM n]` — search for `[DIVAM` and you'll find
all 13. The tests tell you when you're done:

```
python test_divam_features.py
```

Both currently fail. Make them pass. Don't change `test_switchmath.py` and keep it passing too.
Before you start, read `insertKey()` and the `case 'exp'` branches — both features copy patterns
that already exist.

---

## Feature 1 — decimal point  (markers 7 and 11, ~10 lines)

Add a `.` key at the end of the digits row so a user can enter 3.14 or 0.5.

Rules:
1. If the user is in the middle of typing a number (there is a "current number" — `p.lastNum` — and
   it is the item just before the cursor, exactly like the digit-append rule), append `.` to it —
   unless that number already contains a `.`, in which case do nothing.
2. If there is no current number, start a new number `"0."` and make it the current number (so
   the next digit appends to it: `.` then `5` gives `0.5`).
3. A trailing `.` is allowed while typing (`3.` is fine; the next digit makes it `3.1`).

Hints: marker 7 adds the key (the `.concat(...)` is written out for you in the comment). Marker 11
is a new `case 'point':` in `insertKey()` — look at `case 'digit':` directly above it; yours is the
same shape with one extra condition. Nothing else needs to change: numbers already render as text
and export as text.

Test expectations (step-scan, see the test file): typing `3 . 1 4` gives LaTeX `3.14`; typing
`3 . .` gives `3.`; typing `. 5` gives `0.5`.

---

## Feature 2 — subscript  (markers 1–6, 8, 9, 10, 12, 13, ~30 lines)

Add a subscript structure so a user can write x₁ or aₙ. It is the exponent feature's twin: the
`pow` node has `{ base: row, exp: row }`; yours is `sub` with `{ base: row, sub: row }`.

Go through the markers in order:
- **1** (comment only) documents the node shape.
- **2** `children()`: a `sub` has two child rows, like `pow`.
- **3** `subrows()`: the two parts a user can scan into: `'base'` and `'subscript'`.
- **4** `tex()`: `x_{1}`. Copy how `pow` decides whether to wrap the base in `{}`.
- **5** `describe()` (spoken): "x sub 1".
- **6** `label()` (the chip text): `'subscript'`.
- **8** palette: add a `subscript` key at the END of the structures row.
- **9** actions menu: add `add subscript` at index 5, before `← back`.
- **10** `actionsSelect()`: a `case 'sub':` — copy `case 'exp'` two lines up, build a `sub` node,
  open the palette on its `.sub` row.
- **12** `insertKey()`: a `case 'sub':` — copy `case 'exp'` below it: if there is an item before the
  cursor, wrap it as the base; otherwise insert an empty `sub` and target its base row.
- **13** `renderNode()`: copy `case 'pow'`, but give the small row the class `'sub'` instead of
  `'exp'`. The CSS (`.sub>.sub`) is already in the stylesheet.
- **14** (in the voice grammar, `parseTokens`): uncomment the `SUB` line so "a sub n" dictates aₙ.

You'll also need a constructor next to `pow`:  `const sub = (b, s) => node('sub', { base: b, sub: s });`

Test expectations: starting from `(x+1)/2 = y`, choosing `x` → `add subscript` → `1` → done gives
`\frac{x_{1} + 1}{2} = y`. From a blank: `a`, then palette `subscript`, then `n`, then done gives
`a_{n}`.

---

## When both pass

Run `python test_switchmath.py` once more, then commit:

```
git add -A
git commit -m "Add decimal point and subscript"
git push
```

Then be ready to explain, out loud, in under a minute each: how the tree is stored, how one
scan step finds the next choice, why undo is a stack of snapshots, and how `tex()` walks the tree.
Those are the judge questions.
