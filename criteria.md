# Acceptance criteria — TakeMeter

Five criteria that say what "working" means for this classifier, written in
unit 5 **before** anything was trained.

**All five are yours this time.** None are given. You've had two projects of
practice.

An acceptance criterion names a number. *"The model is accurate"* is an
opinion. *"Every label has an F1 of at least 0.60 on the held-out set"* is a
criterion.

Under each, write a sentence or two on **why that number**. A reason that says
something about your data or your taxonomy earns credit — *"I picked 0.60 F1
for `reaction` because it's my smallest label and I only have about 50
examples of it"*. A reason that could be attached to any project does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

Not numbers that sound impressive. Three labels means a coin-flip guesser gets
about 33%, so a target of 0.40 is barely a target. Your number should sit
somewhere you'd honestly call useful.

**Cover at least three of these five areas.** They're here as prompts, not as a
form to fill in — a criterion that fits none of them is fine if it names a
number.

| Area | A question it could answer |
|---|---|
| Overall accuracy | How often does it need to be right to be worth using? |
| Per-label performance | Is one label allowed to be much worse than the others? |
| Balance | How lopsided can your label counts get before it's a problem? |
| Consistency | If someone else labelled the same posts, how often should you agree? |
| Confidence | Should a confident prediction be right more often than an unsure one? |

Two things worth knowing before you pick numbers, because both will affect
whether you hit them:

- **Your smallest label will have the jumpiest score.** If a label has 50
  examples, about 8 land in the test split. An F1 computed on 8 examples moves
  a lot between seeds. A target for that label should be looser than one for
  your biggest label, and saying so is a good reason.
- **Unit 6 tests across three seeds, and the target has to hold across all
  three.** A target of 0.65 against results of 0.71, 0.62, 0.68 is a **miss**.
  Pick with that in mind — it is stricter than it first sounds.

---

## 1.

Overall accuracy on the held-out test set must be at least 0.65.

**Why this target:**

Random guessing on 3 classes gives 33%. A model at 0.65 is meaningfully above chance and represents useful sorting performance. I set the floor at 65% rather than higher because the `analysis`/`hot_take` boundary is genuinely hard—both can contain numbers—and I expect the model to struggle there. 0.65 is honest without being trivially easy.

---

## 2.

Macro F1 on the held-out test set must be at least 0.60

**Why this target:**

Macro F1 averages across labels without weighting by size, so a model that ignores a small label cannot hide behind overall accuracy. My four labels are reasonably balanced (23/21/21/34 after adding extra request examples), but I still want to verify none is being abandoned. 0.60 is demanding enough to catch a collapsed label—F1 of 0.00 on any single label would pull the macro well below 0.60 in a 4-class setting—without requiring near-perfect performance on every boundary.

---

## 3.

F1 for the `analysis` label must be at least 0.65 on the held-out test set.

**Why this target:**

`analysis` is my largest label (70 of 200 examples), which means it gets the most training signal and the most test examples (~10-11). It also has the clearest distinguishing feature—the presence of a specific, checkable fact—making it the label the model has the best chance of learning reliably. I hold it to a higher standard than the other two because if `analysis` underperforms at 0.65, something is structurally wrong with my labeling or the feature signal, not just variance from a small test set.

---

## 4.

F1 for the `hot_take` label must be at least 0.55 on the held-out test set.

**Why this target:**

`hot_take` and `reaction` share surface features: both are often first-person, confident, and emotionally present. The model may confuse them because neither contains the numerical/factual signal that marks `analysis`. I set the floor at 0.55—lower than `analysis`—because this boundary is genuinely harder to learn from text alone. The target has to hold across all three seeds, and with ~10 `hot_take` examples in test, a 0.60 target could fail on a single bad draw.

---

## 5.

F1 for the `reaction` label must be at least 0.55 on the held-out test set.

**Why this target:**

`reaction` posts are about immediacy and present-tense experience, which the model may partially confuse with `hot_take` (both use confident, first-person voice). With 65 examples, I expect roughly 10 in the test split. An F1 computed on 10 examples can swing significantly between seeds—0.55 is the floor below which the model is barely distinguishing `reaction` from random. I chose 0.55 rather than 0.50 because random would score 0.33, and I need a target that actually rules out chance-level performance.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 6 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Every label performs acceptably

         The model performs well on all labels.

         **Why this target:** ...

         > **Revised in unit 6:** Every label has an F1 of at least 0.60 on
         > the held-out set.
         >
         > **Why revised:** "performs well" gave me nothing to check. I
         > couldn't produce a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "Overall accuracy of at least 0.65" → "at least 0.55", because
            0.65 turned out to be optimistic for 200 examples.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
