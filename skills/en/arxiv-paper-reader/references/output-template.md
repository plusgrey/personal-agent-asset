# Output Template

Organize `notes.md` using the structure below. Sections with no substantive content may be removed (for example, a purely empirical paper may have no "Mathematical Derivations" section), but **do not change the order of the top-level sections**.

````markdown
# <Paper Title>

> **arXiv**: [<id>](https://arxiv.org/abs/<id>) · **Authors**: <authors> · **Published**: <date / venue>
> **One-sentence summary**: <State in one sentence: what problem is addressed, what method is used, and what result is achieved>

## TL;DR

- **Problem**: ...
- **Insight**: ...
- **Method**: ...
- **Results**: ...
- **Lessons**: ...

---

## 1. Motivation: Why This Work Was Needed

### 1.1 Background
What is the problem, why does it matter, and where does it fit in the broader landscape?

### 1.2 Existing Approaches and Their Shortcomings
| Method / family | Core idea | Specific shortcoming |
| --- | --- | --- |
| ... | ... | ... |

### 1.3 The Paper's Point of Entry
What crucial observation or insight did the authors identify? Why can this direction address the shortcomings above?
This is the most important section of the notes: explain *why this direction*.

## 2. Method

### 2.1 Overall Framework
Present the full picture first: the pipeline, modules, and data flow. Use Mermaid or ASCII diagrams when useful.

### 2.2 Key Designs
Give each design its own subsection:
- **What it does**
- **Why it is designed this way**: which shortcoming in §1.2 it addresses
- **What alternatives exist and why they were not chosen** (if discussed in the paper or reasonably inferable)

### 2.3 Training / Inference Details
Objective functions, algorithm pseudocode, and key hyperparameters.

## 3. Running Example: <Summarize the example in one sentence>

> **Teaching example**: Unless paper data is explicitly cited, state that the inputs and numbers below were constructed for explanation.

First state which core mechanism the example explains. Then proceed from a concrete input to the output step by step, showing key intermediate states:

- **LLM / deep learning**: input tensor (for example, $B\times L\times C$) → each operation → shape changes → information flow for one token/vector → output
- **Agent**: concrete task → prompt-context composition → harness/runtime and tools → observe/reason/act loop → state updates → termination or error recovery
- **Mathematics / theory**: scalar or low-dimensional concrete values → hand calculation → intuitive phenomenon → generalization to the paper's full equation → limitations of the simple example
- **Systems**: minimal request/query/program → processing stages → queues, caches, communication, and state transitions → output and cost

Do not provide only an analogy, pseudocode, or a list of shapes; readers should be able to reproduce the core process by hand. Mark implementation details the paper does not disclose as "not specified in the paper" rather than inventing them.

## 4. Mathematical Derivations

(Follow math-derivation.md. Give each derivation its own subsection and insert each secondary result at its first use.)

### 4.1 <Derivation goal, for example: From Log-Likelihood to the ELBO>
**Goal**: State what is to be proved or derived.
**Assumptions and notation**: ...

Derivation steps ...

> **Secondary result: <name>**
> ...

**Takeaway**: What does this derivation establish, and what role does it play in the method?

## 5. Experiments and Results

### 5.1 Experimental Setup
Datasets, metrics, baselines, and compute scale.

### 5.2 Main Results
Key numbers (with table/figure references) and comparison with the strongest baseline.

### 5.3 Ablations and Analysis
Which components actually help? Which conclusions have experimental support, and which do not?

### 5.4 Limitations
Limitations acknowledged by the authors plus limitations you identify, such as insufficient evaluation, unfair baselines, or high compute requirements.

## 6. Lessons for General Open-Source Projects

Extract transferable lessons beyond the paper's immediate domain:
- **Reusable ideas / techniques**: for example, "rewrite a difficult optimization objective as a sequence of denoising regression objectives"
- **Engineering practices**: implementation details worth adopting, such as parameterization choices, training-stability techniques, and evaluation methods
- **Adoption guidance**: where to start, pitfalls to avoid, and expected costs when applying the method in your own project
- **Related open-source implementations**: official code / prominent reproductions (include only after confirming they exist)

## 7. Self-Test Questions

List 3–5 questions that test genuine understanding, each with a brief answer.

## Appendix: Notation

| Symbol | Meaning |
| --- | --- |
| ... | ... |
````
