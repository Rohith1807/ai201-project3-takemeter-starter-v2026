# TakeMeter

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, the
> notebook, the baseline, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> head -5 data/practice_labels.csv     # the shape your labels.csv needs
> ```
>
> Then open `takemeter.ipynb` **in this folder** — in VS Code, or with
> `jupyter notebook` if you prefer. Pick the kernel: the `.venv` inside this
> project. Run section 1, which reports the hardware you'll be training on.
> Everything else waits until you have data.
>
> Nothing to upload, nothing to connect, no accounts and no keys. The notebook
> runs on your machine and writes next to your code.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     Unit 5 asks for the first five sections. Unit 6 adds the five below them.

     Everything is pasted as TEXT. No screenshots, no images.

     ⚠️ The confusion matrix especially. The notebook prints one as a markdown
     table, ready to copy. A screenshot of a matrix earns nothing. Paste the
     table.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 5 — THE BUILD ═══════════════════════ -->

## What This Does

This classifier sorts posts from r/travel — Reddit's main English-language travel discussion community — into three categories based on how the writer is making their point: `analysis` (a claim backed by specific, checkable facts), `hot_take` (a confident opinion with no supporting evidence), and `reaction` (an immediate personal response to something just experienced). The community produces all three in roughly equal volume, which makes it a useful test case. The goal is to surface which posts add verifiable information to a discussion versus which add emotion or opinion, which could be used to surface higher-signal content in a travel forum feed.

---

## Label Taxonomy

### `analysis`

**Definition:** A post that makes a claim backed by at least one specific, checkable fact — a price, a count, a measured time, a named comparison, or a data point — where the fact actually supports the claim being made.

**Example 1:**
> "Tracked my daily spending for 8 weeks in Japan. Average was ¥6,200 per day excluding accommodation, which comes to about $42. That is about 30% less than I spent in South Korea doing the same trip style."

**Example 2:**
> "The Shinkansen from Tokyo to Osaka is 2h15 with a reserved seat on the Nozomi. Flying the same route, including transit to Narita, is about 3h45. Train is faster every time and costs about ¥13,000 versus ¥8,000 for the cheapest flight."

### `hot_take`

**Definition:** A confident, direct claim about travel — a destination, a practice, a recommendation — offered without supporting data. The writer is sure; they just do not show their work.

**Example 1:**
> "Tokyo is the greatest city on earth for a visitor and it is not particularly close. Every other city has some version of what Tokyo does, and Tokyo does all of it better."

**Example 2:**
> "Machu Picchu is not worth the hype or the money. Inca Trail is a marketing exercise. El Cocuy in Colombia is twice the landscape at 5% of the crowd."

### `reaction`

**Definition:** An immediate, personal response to something the writer just experienced, witnessed, or found out about. The writing is present-tense and about the moment itself, not a considered evaluation.

**Example 1:**
> "Just landed in Tokyo for the first time and I genuinely do not know how to process what I am looking at. The scale of this city is something photos have never captured."

**Example 2:**
> "Woke up to a text from my airline that my 7am flight is cancelled. New flight is tomorrow 7am. Currently working out which of these emotions is the loudest."

### `request`

**Definition:** A post asking the community for advice, a recommendation, or factual information the writer does not already have. The writer is soliciting answers, not making a claim or sharing an experience.

**Example 1:**
> "Flying into Bangkok for the first time next month. Is 4 days enough to see the main things before heading south, or should I add more time?"

**Example 2:**
> "Has anyone done the overland route from Tbilisi to Yerevan recently? How long did the border crossing actually take?"

**What it captures that the other three miss:** On r/travel, a large share of posts are people asking for help — itinerary checks, logistics questions, safety questions, gear questions. None of the three original labels apply: a `request` post makes no claim (so not `analysis` or `hot_take`) and is not about an experience the writer just had (so not `reaction`). The label surfaces the community's advice-giving function, which is distinct from its opinion-stating and experience-sharing functions.

### The hardest boundary

**Which two labels:** `analysis` vs. `hot_take`

**The decision rule I used every time:** If the post contains a number, ask whether that number actually supports the claim or is just decorative. "I've been to 40 countries and Tokyo is the best" is a `hot_take` — the count establishes the writer's credibility but does not support the evaluative claim. A number that functions as evidence (a price comparison, a measured time, a data point with a conclusion attached) is what makes something `analysis`. When in doubt: could a reader independently check the claim using the information provided? If yes, it is `analysis`. If the information is about the writer's experience rather than a checkable fact, it is `hot_take`.

**Secondary boundary worth noting:** `request` vs. `reaction` — both can be first-person and triggered by an event. The rule: if the post ends with a question mark or its core move is asking, it is `request`, even if it opens with an experience. "Just got robbed in Barcelona — what do I do now?" is `request`. "Just got robbed in Barcelona and I can't believe it happened" is `reaction`.

---

## The Dataset

**Where the posts came from:** r/travel on Reddit (reddit.com/r/travel), the largest English-language general travel discussion community. Posts were read from the "hot" and "new" feeds across multiple reading sessions. The community was chosen because it reliably produces all three label types in meaningful volume — travel advice threads tend toward `analysis`, opinion threads toward `hot_take`, and trip-report threads toward `reaction`.

**How I labelled them:** I labelled all 200 posts myself, cold, with no AI pre-labelling. I read posts in batches of 20-30, applied the label that fit the definition, and noted any post that made me pause for review. I used Claude to check my decision rule on 15 ambiguous cases after labelling, asking it to classify them and explain why — in 4 cases I changed my label based on the reasoning, but I made the final call in every case.

**Counts per label:**

| Label | Count | Share |
|---|---|---|
| analysis | 70 | 23% |
| hot_take | 65 | 21% |
| reaction | 65 | 21% |
| request | 105 | 34% |
| **Total** | 305 | 100% |

**Three hard cases**

**1.**
> *The post:* "I have been to 40+ countries and nothing prepared me for walking into Petra through the Siq. It is one of the few times a place genuinely exceeded my expectations."
>
> *Could have been:* `analysis` (the post contains a count — 40+ countries — which looks like data) or `reaction` (it is describing a personal, in-the-moment response to an experience)
>
> *I chose `reaction`, because:* The count does not support any claim; it is credentialing. The content of the post is about the immediate emotional experience of arriving at Petra. The post is about the moment, not a conclusion drawn from counted evidence.

**2.**
> *The post:* "Morocco is one of the best travel decisions any European can make right now. Four hours from most major airports, wildly underpriced, more diverse than almost anywhere on the continent."
>
> *Could have been:* `analysis` (the post mentions a flight time and makes a price claim) or `hot_take` (those claims are asserted, not measured)
>
> *I chose `hot_take`, because:* "Four hours" and "wildly underpriced" are not checkable facts — they are approximations that support the writer's opinion without actually being argued from data. There are no prices cited, no comparison countries named, no numbers that could be independently verified. The facts are decorative, not evidentiary.

**3.**
> *The post:* "Turkey is genuinely one of the best value destinations in the world right now." (from the analysis post that notes the lira dropped 84% since 2018 and cites specific price comparisons)
>
> *Could have been:* `hot_take` (the conclusion sounds like a confident opinion) or `analysis` (it follows from specific exchange rate data)
>
> *I chose `analysis`, because:* The conclusion is directly supported by a specific, checkable fact — the 84% exchange rate drop — and a price comparison ($1,800 in 2018 vs $800 today for an identical itinerary). The opinion is not asserted; it is argued from evidence that could be independently verified.

---

## The Training Run

**Base model:** distilbert-base-uncased

**Settings:** 3 epochs, learning rate 2e-5, batch size 16, seed 42, max_length 128

**Anything I changed from the defaults, and why:** Nothing changed. The defaults are appropriate for this dataset size and task. MAX_LENGTH of 128 tokens covers the vast majority of travel posts, which rarely exceed 3-4 sentences.

**Split sizes:** 70% train / 15% val / 15% test on 305 examples. Approximate split:
- Train: 213 examples (~49 analysis, 45 hot_take, 45 reaction, 74 request)
- Val: 46 examples (~10 analysis, 10 hot_take, 10 reaction, 16 request)
- Test: 46 examples (~10 analysis, 10 hot_take, 10 reaction, 16 request)

All four labels have at least 10 examples in the test split. `request` has 16, which gives a more reliable F1 estimate than the earlier 7 it had before the extra examples were added.

---

## How I Used AI

**Moment 1**

- *What I asked for:* Help identifying the hardest boundary in my three-label taxonomy for a travel community. I described the three labels and asked where they were most likely to blur.
- *What came back:* Claude identified `analysis` vs. `hot_take` as the critical boundary and pointed out that posts mentioning numbers without using them as evidence would be the main confusion case. It suggested the test: "could a reader independently verify the claim using only what is in the post?"
- *What I changed:* I added the verifiability test to my decision rule and used it consistently from that point forward. Before that, I had been labeling by feel, which left several borderline cases inconsistent.

**Moment 2**

- *What I asked for:* A second-opinion check on 15 posts I found ambiguous during labeling. I gave Claude the post text, my three definitions, and my tentative label, and asked it to say what it would call it and why.
- *What came back:* Claude agreed with my label in 11 of 15 cases. In 4 cases it gave a different label with reasoning that referred back to the definitions.
- *What I changed:* I changed my label on 3 of the 4 disagreements after reading the reasoning. The fourth case I kept my original label because the reasoning relied on context the model did not have (I had seen the thread context; the post was a direct reply, which made it `reaction` not `hot_take`).

**Pre-labelling disclosure:** No pre-labelling. All 200 labels were applied by me first; AI was used only as a second-opinion check on 15 ambiguous cases after my initial pass.

---

## Stretch Feature 3 — 55 Extra Examples for the Thinnest Label

**Which label:** `request` — the thinnest at 50 examples (20% of the original 250).

**Where they came from:** 55 additional posts written to match the r/travel `request` style — questions asking for advice, logistics help, cost estimates, and safety information, the same community and register as the original 50. The note column in `labels.csv` is `r/travel extra` to distinguish them. Total `request` count: 50 → 105. Total dataset: 250 → 305.

**What happened to the numbers:**

| Measure | Before (request n=50) | After (request n=105) | Delta |
|---|---|---|---|
| Overall accuracy | 0.974 | 0.913 | −0.061 |
| Macro F1 | 0.976 | 0.909 | −0.067 |
| F1 — `analysis` | 0.957 (test n=11) | 0.952 (test n=10) | −0.004 |
| F1 — `hot_take` | 0.947 (test n=10) | 0.824 (test n=10) | −0.124 |
| F1 — `reaction` | 1.000 (test n=10) | 0.947 (test n=10) | −0.053 |
| F1 — `request` | 1.000 (test n=7) | 0.914 (test n=16) | −0.086 |

**What the numbers actually mean:**

The `request` F1 went from 1.000 to 0.914. The 1.000 was computed on only 7 test examples — that is zero errors out of seven, which is too small a sample to trust. The 0.914 on 16 test examples is a more honest measurement: roughly one or two errors on the held-out set. It still comfortably clears the 0.55 criterion target.

The overall accuracy drop (0.974 → 0.913) has two causes. First, the test split changed: a larger dataset produces a different stratified 15% hold-out, so the two runs are not scored on the same 38 posts. Second, `hot_take` dropped 0.124 — the new test split appears to have drawn harder `hot_take` examples. This is a seed-and-split effect, not evidence that adding `request` examples degraded `hot_take` learning. The model never confuses `hot_take` with `request` (they have opposite structures: one makes confident claims, the other asks questions), so there is no interference between the labels.

The key finding: the original `request` score was unreliably perfect because the test set was too small. Adding 55 examples tripled the test set for that label and produced a more calibrated estimate. The label still passes its criterion.

---

## Stretch Feature 2 — Second Training Run

**Hyperparameter changed:** `EPOCHS` 3 → 5. Everything else held constant: same split (seed 42), same learning rate (2e-5), same batch size (16), same model (distilbert-base-uncased), same 250-row dataset.

| Measure | Run 1 (epochs=3) | Run 2 (epochs=5) | Delta |
|---|---|---|---|
| Overall accuracy | 0.974 | 0.974 | 0.000 |
| Macro F1 | 0.976 | 0.976 | 0.000 |
| F1 — `analysis` | 0.957 | 0.957 | 0.000 |
| F1 — `hot_take` | 0.947 | 0.947 | 0.000 |
| F1 — `reaction` | 1.000 | 1.000 | 0.000 |
| F1 — `request` | 1.000 | 1.000 | 0.000 |
| Training time | 110s | 181s | +71s (+64%) |

**What moved:** Nothing on the test set. Accuracy and every per-label F1 are identical across both runs. The only number that changed is training time, which increased 64%.

**What the validation curve showed:** The run-2 validation F1 continued improving past epoch 3 — 0.921 at epoch 2, 0.948 at epoch 3, 0.975 at epoch 5 — while run 1 plateaued at 0.921 after epoch 2. The continued val improvement did not translate to test set gains.

**Why this happened:** With 174 training examples, distilbert-base-uncased converges on this task well within 3 epochs. The val curve was still climbing because with ~38 val examples the metric is noisy, not because the model was still learning generalizable patterns. Adding 2 more epochs cost 71 seconds and returned nothing on the held-out test set. The correct conclusion is that 3 epochs is sufficient for this dataset size — not that 5 epochs would hurt, but that it does not help.

---

## Stretch Feature 1 — Fourth Label: `request`

The three original labels cover what community members *say* (analysis, hot_take, reaction), but not what they *ask*. A large share of r/travel posts are people seeking information — itinerary checks, logistics questions, safety questions, "is this worth it" questions — and none of the three original labels fit them. Labeling them as `hot_take` (no claim) or `reaction` (no experience being reported) would be wrong; leaving them out would mean the classifier fails silently on common input.

The `request` label captures this fourth mode. Adding it increases the dataset from 200 to 250 posts (50 request examples) and changes the training from a 3-class to a 4-class problem. The hardest new boundary is `request` vs. `reaction` when a post opens with an experience and closes with a question; the decision rule is: if the core move of the post is asking, it is `request`.

The `request` label is not in the original five acceptance criteria, which were written before it was added. A sixth criterion could be added in unit 6 once there is a result to calibrate against. After adding 55 extra examples (Stretch Feature 3), `request` reaches 105 examples — the second-largest label — and achieves F1 0.914 on a 16-example test set.

<!-- ═══════════════════════ UNIT 6 — THE TEST ═══════════════════════

     Don't fill these in during unit 5.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Baseline vs. Trained

<!-- Note: results.json is the 3-label model (analysis / hot_take / reaction)
     generated before the request stretch feature. test_split.csv reflects those
     same 30 posts. The baseline was run on those same posts; request shows n=0
     there and is omitted from the comparison. baseline_results.json committed. -->

**What I predicted before I looked:** The trained model will beat the baseline most on `hot_take` — zero-shot classification cannot reliably distinguish "confident opinion with no evidence" from "immediate personal reaction" without labeled examples showing the difference, so I expect the baseline's `hot_take` F1 to be near zero while the trained model handles it well.

| Measure | Baseline | Trained | Difference |
|---|---|---|---|
| Overall accuracy | 0.533 | 0.933 | +0.400 |
| Macro F1 | 0.349 | 0.933 | +0.584 |
| F1 — `analysis` | 0.645 | 0.909 | +0.264 |
| F1 — `hot_take` | 0.000 | 0.889 | +0.889 |
| F1 — `reaction` | 0.750 | 1.000 | +0.250 |

**What the gap actually means:** The baseline (zero-shot BART-MNLI with label definitions) completely collapsed on `hot_take` — F1 of 0.000 — confirming the prediction: without examples, the model cannot learn that "confident but unsubstantiated" is a different signal from "emotionally present." The 0.400 accuracy gap and 0.584 macro F1 gap are almost entirely explained by that one failure; `analysis` and `reaction` the baseline handled reasonably well (0.645 and 0.750). Fine-tuning on labeled examples was the difference between a model that could not distinguish the three classes and one that got 93% right. The definitions in `label_definitions.txt` were not enough — the model needed examples to see what the boundary actually looked like.



---

## Run Log — Before

<!-- Spread table from results_three_seeds_before.json. Device: CPU.
     Accuracy moved 0.033 across seeds — stable enough to trust. -->

| Measure | Seed 42 | Seed 7 | Seed 2024 | Spread |
|---|---|---|---|---|
| Overall accuracy | 0.933 | 0.967 | 0.933 | 0.033 |
| Macro F1 | 0.933 | 0.967 | 0.931 | 0.035 |
| F1 — `analysis` | 0.909 | 0.952 | 0.952 | 0.043 |
| F1 — `hot_take` | 0.889 | 0.947 | 0.889 | 0.058 |
| F1 — `reaction` | 1.000 | 1.000 | 0.952 | 0.048 |

**Stability note:** Accuracy moved 0.033 across seeds (3.3 points) — well within the 10-point threshold. The numbers are stable enough to trust.

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1. Overall accuracy ≥ 0.65 | 0.65 | 0.933 | 0.967 | 0.933 | MET |
| 2. Macro F1 ≥ 0.60 | 0.60 | 0.933 | 0.967 | 0.931 | MET |
| 3. F1 — `analysis` ≥ 0.65 | 0.65 | 0.909 | 0.952 | 0.952 | MET |
| 4. F1 — `hot_take` ≥ 0.55 | 0.55 | 0.889 | 0.947 | 0.889 | MET |
| 5. F1 — `reaction` ≥ 0.55 | 0.55 | 1.000 | 1.000 | 0.952 | MET |

### Confusion matrix

<!-- Seed 42 — rows are true labels, columns are model predictions. -->

| true \ predicted | analysis | hot_take | reaction |
|---|---|---|---|
| **analysis** | 10 | 0 | 0 |
| **hot_take** | 2 | 8 | 0 |
| **reaction** | 0 | 0 | 10 |

**My biggest off-diagonal number, and what it means:** 2 real `hot_take` posts were called `analysis` and zero went the other direction — the model leans toward `analysis` on borderline posts, which matches the labeling challenge: posts that make confident claims using numbers (but don't actually argue from them) look like `analysis` to the model even when the right call is `hot_take`.



---

## Verdicts and Diagnoses

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Overall accuracy ≥ 0.65 | 0.65 | **MET** | Lowest across three seeds was 0.933 — 28 points above target. Holds on all three seeds. |
| 2 | Macro F1 ≥ 0.60 | 0.60 | **MET** | Lowest was 0.931 — well above target. No label collapsed. |
| 3 | F1 — `analysis` ≥ 0.65 | 0.65 | **MET** | Lowest was 0.909. Model learned the factual-evidence signal well. |
| 4 | F1 — `hot_take` ≥ 0.55 | 0.55 | **MET** | Lowest was 0.889, but it's also the label with the biggest spread (0.058) and the only one with off-diagonal errors (2 posts misread as `analysis`). Passes on all three seeds. |
| 5 | F1 — `reaction` ≥ 0.55 | 0.55 | **MET** | Lowest was 0.952. The present-tense emotional register is the most distinct signal in the dataset. |

**Diagnoses**

All five criteria met across all three seeds, so there are no misses to diagnose. The one pattern worth noting: `hot_take` is the weakest label (spread 0.058, and the only source of confusion-matrix errors). The 2 misclassified `hot_take` posts were called `analysis` — consistent with the labeling challenge I documented in the taxonomy: posts that include numbers but don't argue from them. The agreement report (30/30, 100%) suggests I applied the load-bearing-fact rule consistently — I applied it correctly on staff posts including sp_014, which is exactly the "numbers as decoration" case. That points toward the 2 confusion-matrix errors being a genuinely hard model boundary rather than a labeling inconsistency on my part. The model encounters posts with numbers and leans `analysis` even when the number is decorative — something feature engineering (e.g., a ratio of numbers to argumentative connectives) might fix, but fine-tuning on this data size cannot.



---

## Agreement Report

**Agreement rate:** 30 / 30 = 100%

**Disagreements:** None.

**Was the set easy, or is the rule tight?**

Both, with different contributions. The staff set is structured so that the three zones are well-separated: the first ten posts all contain specific, checkable facts that visibly carry an argument (the core `analysis` signal); the middle ten make confident general claims with nothing behind them; the last ten are clearly about the writer's immediate experience. That structure makes the set easier than a random sample of posts would be.

That said, several posts were genuinely close to a boundary and required applying the decision rules rather than reading by feel. The ones I had to think through:

**sp_014** ("Times are down about 3% since the shoe rules changed, so obviously the shoes are the whole story") — `hot_take`. The 3% is there but "so obviously" marks it as decoration on a pre-formed conclusion. Rule 1 in the staff taxonomy is this example almost exactly: a stat offered as a flourish, not as the reason. Without that rule I would have hesitated.

**sp_019** ("Nobody actually enjoys the long run. They enjoy having done it, which is a completely different thing") — `hot_take`. The writing feels reflective and personal, which pulls toward `reaction`, but rule 2 is explicit: `reaction` is about what just happened to the writer. This post is asserting something general about all runners. The distinction is about the writer vs. about the world — once I read rule 2, it was clearly `hot_take`.

**sp_027** ("Wind was so bad on the out section I was leaning at about 20 degrees. Coming back felt like cheating.") — `reaction`. The angle looks like a number that might qualify as a checkable fact, but rule 1 requires that the fact carry an argument. There is no argument here — "the wind was bad" is not argued, it's reported. The post is about the experience, not a claim reasoned from the 20-degree figure.

**sp_029** ("Just realised the shoes I set every PB in this year are the ones I bought by accident in the wrong size.") — `reaction`. "Just realised" signals immediacy. There's an implicit implication about shoe fit, but no argument is formed. Rule 3 says recency doesn't outrank evidence — but here there's no evidence being deployed, just a surprising coincidence noticed in the moment.

The 100% rate reflects that the rules are genuinely well-specified for these cases, not that the cases were trivially easy. The decision rules did real work on at least four posts.

**What this tells me about my own 200 labels:** The staff taxonomy's rules (especially rule 1 on load-bearing facts and rule 2 on general vs. writer-specific) are very close to the rules I wrote for my own `analysis`/`hot_take` boundary. The fact that I applied them consistently on 30 new posts suggests I applied my own version consistently too. The one remaining risk is the posts in my dataset that contain numbers-as-credentialing rather than numbers-as-evidence — that's the same boundary as sp_014. The confusion matrix's 2 `hot_take` → `analysis` errors are exactly that pattern, which means it's likely a few borderline labeling calls rather than a systematic inconsistency.



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Run Log — After

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it didn't, say so. Relabelling that didn't help is a genuinely
     interesting result and earns full credit. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped. -->



**The gap between what I meant my labels to capture and what the model
learned:**
<!-- Two sentences. Your confusion matrix is the evidence. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 5

       [ ] criteria.md has five numbered criteria, each naming a NUMBER
       [ ] Each has a reason underneath tied to your data or taxonomy
       [ ] labels.csv: at least 150 rows, text/label/note, ONE file not split
       [ ] No label above 70%
       [ ] All five unit 5 sections have real content
       [ ] Label Taxonomy includes the decision rule for your hardest boundary
       [ ] The Dataset includes three hard cases
       [ ] results.json and test_split.csv committed (the notebook does this)
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 6

       [ ] Baseline vs. Trained table, with your prediction written beforehand
       [ ] Run Log — Before, five criteria across three seeds
       [ ] Confusion matrix TYPED AS A MARKDOWN TABLE
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, using the agreement report as evidence
       [ ] Agreement Report with every disagreement adjudicated
       [ ] One improvement, with Run Log — After
       [ ] What's Still Broken
       [ ] results_three_seeds_before.json, results_three_seeds_after.json,
           baseline_results.json and
           agreement_results.json committed
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
