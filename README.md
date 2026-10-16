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
| analysis | 70 | 28% |
| hot_take | 65 | 26% |
| reaction | 65 | 26% |
| request | 50 | 20% |
| **Total** | 250 | 100% |

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

**Split sizes:** 70% train / 15% val / 15% test on 250 examples. Approximate split:
- Train: 175 examples (~49 analysis, 45 hot_take, 45 reaction, 35 request)
- Val: 37 examples (~10-11 per label)
- Test: 38 examples (~10-11 per label)

All four labels have approximately 10 examples in the test split. That is enough to compute F1 but small enough that a single mislabeled post can move the number by 10 points between seeds, which is why per-label criteria are set at 0.55 rather than higher.

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

The `request` label is not in the original five acceptance criteria, which were written before it was added. A sixth criterion could be added in unit 6 once there is a result to calibrate against.

<!-- ═══════════════════════ UNIT 6 — THE TEST ═══════════════════════

     Don't fill these in during unit 5.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Baseline vs. Trained

<!-- Both models on the same posts. `python baseline.py --trained results.json`
     prints this table for you. -->

| Measure | Baseline | Trained | Difference |
|---|---|---|---|
| Overall accuracy |  |  |  |
| Macro F1 |  |  |  |
| F1 — `label_one` |  |  |  |
| F1 — `label_two` |  |  |  |

**What I predicted before I looked:**
<!-- Milestone 1 asks you to write this BEFORE seeing the trained numbers. A
     prediction made afterwards isn't one. -->

**What the gap actually means:**
<!-- If the baseline matched your trained model, your fine-tuning added
     nothing — and that is a real finding, not a failure. Say it plainly. -->



---

## Run Log — Before

<!-- Five criteria across three seeds. The notebook's section 6 prints the
     spread table; the Target and Verdict columns are yours. -->

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

### Confusion matrix

<!-- ⚠️ TYPED AS A MARKDOWN TABLE. The notebook prints one ready to paste.
     An image of a matrix earns nothing. -->

| true \ predicted |  |  |  |
|---|---|---|---|
| **** |  |  |  |
| **** |  |  |  |
| **** |  |  |  |

**My biggest off-diagonal number, and what it means:**
<!-- Not "the model made mistakes" — WHICH boundary it didn't learn, and which
     direction. "7 real analysis posts were called hot_take and only 3 went the
     other way" is a direction, not just an error rate. -->



---

## Verdicts and Diagnoses

<!-- MET or MISSED against LAST UNIT's target. The target has to hold across
     all three seeds, not turn up sometimes. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**

<!-- For each miss: the cause, and how you know. The four common causes are:
     too few examples for a label, a boundary you applied inconsistently, a
     genuinely hard label pair, and a task the model can't reach from this
     much data.

     ⚠️ Use your agreement report as evidence. It is the only instrument you
     have that can tell a LABELLING problem from a MODEL problem, and this
     section is graded on whether you used it that way. -->



---

## Agreement Report

<!-- Your rate against the staff set, and every disagreement adjudicated.

     Remember you labelled these 30 under the STAFF taxonomy in
     data/staff_taxonomy.md, not your own — so every argument below is made
     from those definitions and those decision rules. -->

**Agreement rate:** ___ / 30 = ___%

<!-- Nobody grades this number. A 60% who argues every disagreement from the
     stated rules beats a 95% who wrote "staff was right" nine times. Several
     of the 30 were chosen because they're genuinely ambiguous — you should be
     winning some of these. -->

**Disagreements**

<!-- Three lines each: the post, both labels, and who you think is right and
     why — grounded in the staff definitions you were both applying.

     Then sort each into one of three piles:
       (a) the rule covered it and I applied it loosely → a consistency problem
       (b) the rule genuinely doesn't say               → a gap in the definitions
       (c) the rule is ambiguous here and my reading is defensible → argue it.
           This is a legitimate win.

     Pile (a) is the one that matters most for your diagnosis: if you applied a
     written rule two different ways on 30 posts, that is direct evidence about
     what you did across your own 200. -->

**1.**
> *The post:*
>
> *Staff said / I said:*
>
> *My call, and why:*
>
> *Which pile:*

**2.**
> *The post:*
>
> *Staff said / I said:*
>
> *My call, and why:*
>
> *Which pile:*

**What the pattern in my disagreements tells me:**



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
