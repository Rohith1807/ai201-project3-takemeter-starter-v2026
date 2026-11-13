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

## Capstone — classify.py acceptance criteria

Five criteria for the capstone extension (Gemini as a second classifier).
Written before the acceptance tests are run.

---

### C1. Gemini zero-shot accuracy ≥ 0.75 on the held-out test set

Gemini, given only the four taxonomy definitions as its prompt and no training
examples, must correctly classify at least 75 % of the 51 posts in
`test_split.csv`.

**Why this target:**

Random guessing on four balanced classes gives 0.25. The fine-tuned DistilBERT
hit 0.980 on the same posts, but it had 200 labelled examples to learn from.
Gemini gets only the definitions — the same text a human labeller would read
before starting. A capable large language model applying a clear written rule
should beat chance by a wide margin; 0.75 is the floor I'd call "the definitions
are doing real work." Setting it higher (0.90+) would be unrealistic for a
zero-shot classifier on boundaries like `hot_take` vs. `reaction` that require
close reading; setting it lower (0.60) would barely distinguish the model from an
above-chance guesser.

---

### C2. Gemini–DistilBERT agreement rate ≥ 0.80 on the held-out test set

When both classifiers run without errors on the same post, they must agree on the
label for at least 80 % of posts.

**Why this target:**

Both models are applying the same taxonomy. High agreement (≥ 80 %) means the
two strategies are reading the same signal in the text — the definitions are
precise enough that a trained model and a prompted LLM land on the same label
most of the time. If agreement falls below 80 %, either the definitions are
ambiguous enough that reasonable interpretations diverge, or one classifier is
making systematic errors that need to be diagnosed. I chose 80 % rather than
90 % because genuine boundary cases (posts that reasonably fit two labels) will
produce real disagreement, and the goal is a useful check, not perfect overlap.

---

### C3. Estimated API cost for one full run (51 posts) ≤ $0.005

The dollar cost printed at the end of `python classify.py` must be at most
$0.005 for the default run over `test_split.csv`.

**Why this target:**

The observed cost from the initial run was $0.001338. The $0.005 ceiling is a
3.7× safety margin above that baseline — tight enough to catch runaway token
usage (for example, if a prompt change triples input tokens or the API returns
unexpectedly verbose output), but loose enough to absorb normal variance in
response length. Gemini-3.5-flash-lite is priced at $0.10/M input tokens and
$0.40/M output tokens; at the current prompt length (~250 tokens per post), a
full run costs about 0.1 of a cent. If the cost exceeds $0.005, the per-post
token counts in the log should be audited before treating the run as routine.

---

### C4. Invalid API key → structured error record written and clean exit (no unhandled exception)

When `classify.py` is run with an invalid or missing `GOOGLE_API_KEY`, the
script must: (a) write at least one JSON record to the log file containing
`"error": true` and the exception type in the `gemini` field, and (b) print a
human-readable warning to the terminal — without raising an unhandled Python
exception or leaving the log file in a partially-written, unparseable state.

**Why this target:**

An unhandled traceback mid-batch drops all subsequent records and corrupts the
per-post chain of evidence that Path B relies on. Invalid API keys are the most
common real-world failure (key expires, quota exhausted, copied with a trailing
space), so this is the bad path most likely to be hit. The requirement is binary:
either a structured error record appears in the JSONL and the process exits
cleanly, or the criterion fails. There is no softer version — a partial record or
a swallowed exception both fail.

---

### C5. Every successful record in `classify_log.jsonl` contains all required fields with non-null values

A "successful" record is one where `error` is absent or `false`. Every such
record must include: `timestamp`, `text`, `ground_truth`, `gemini.label`,
`gemini.latency_ms`, `gemini.input_tokens`, `gemini.output_tokens`,
`gemini_correct`; and when DistilBERT ran without error: `distilbert.label`,
`distilbert.confidence`, `distilbert.latency_ms`, `distilbert_correct`,
`agreement`. None of these fields may be `null`.

**Why this target:**

The JSONL log is the sole deliverable for Path B — there is no hosted endpoint,
only the file as evidence. If `input_tokens` is `null` in a successful record
(for example, because the API changed its response schema), the cost calculation
silently undercounts. If `agreement` is missing, the agreement-rate criterion
(C2) cannot be verified from the log alone. Schema completeness is the first
thing to check when summary numbers look wrong, and it is verifiable by
spot-reading any record — which makes it a real criterion, not a vague quality
standard.

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
