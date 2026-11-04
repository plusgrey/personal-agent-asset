---
name: arxiv-paper-reader
description: Read an arXiv paper in depth and produce structured Markdown notes covering its motivation, shortcomings of existing approaches, key insight, method, experimental results, and lessons for general open-source projects; rigorously derive its equations step by step while explaining supporting lemmas and secondary results (such as Jensen's inequality in an ELBO derivation). Use when the user provides an arXiv link or ID, or asks to read, explain, closely analyze, or summarize a paper.
---

# arXiv Paper Reader

Goal: enable readers to **reconstruct the paper's chain of reasoning after reading the notes and independently rederive its key equations**.
This is not a summary; it is a set of teaching notes that makes the paper understandable.

## Workflow

### 1. Fetch the paper

The user may provide an arXiv ID (`2006.11239`), an abstract/PDF URL, or a local PDF.

For an arXiv paper, run (`<skill_dir>` is the directory containing this SKILL.md):

```bash
python3 -I <skill_dir>/scripts/fetch_arxiv.py <id-or-url> --out ./arxiv-papers/<id>
```

The script generates:
- `meta.json`: title, authors, abstract, categories, and dates
- `main.tex`: **read this first**. It contains the LaTeX source with `\input` content inlined and provides the most accurate equations
- `source/`: the complete source; appendices may be in separate `.tex` files, and figures are stored here
- `paper.txt` / `paper.pdf`: fallbacks when LaTeX source is unavailable. Equations extracted from the PDF may be inaccurate, so verify them against the PDF before citing them

If the script cannot access the network, ask the user for the PDF or use another available retrieval tool.

### 2. Read through and build the logical skeleton

Read the full main text and appendices before writing. While reading, answer these questions:

1. **Problem**: What problem does the paper address, and why does it matter?
2. **Status quo**: How do existing methods work, and what are their **specific** shortcomings? Use verifiable facts such as "sampling requires 1,000 steps," not vague claims such as "it is inefficient."
3. **Insight**: What is the authors' point of entry? What did they notice that others missed? This is the core of the paper.
4. **Method**: How is that insight turned into a concrete method? Which shortcoming does each design choice address?
5. **Evidence**: Do the experiments genuinely support the paper's claims? Are there ablations? Are the baseline comparisons fair?
6. **Boundaries**: Under what conditions does the method fail? Which limitations do the authors acknowledge?
7. **Concrete example**: Choose an input small enough to follow by hand but rich enough to cover the core mechanism. Show how it flows through the method step by step, including intermediate states rather than only an analogy.

### 3. Design a running example (required)

Every set of notes must include at least one concrete, traceable example. Begin with one sentence stating which core mechanism the example explains, then develop its input, intermediate states, and output step by step. Prefer one running example throughout the notes instead of changing the setup in every section.

Choose the appropriate form for the paper type:

- **LLM / deep learning papers**: Start with a tensor whose shape is explicit, such as $X\in\mathbb R^{B\times L\times C}$, and assign small dimensions (for example, $B=2,L=4,C=8$). At every layer, explain how reshaping, projection, attention, masking, aggregation, or routing changes the shape. In addition to shapes, trace where the information in one token/vector comes from and where it goes. Do not merely list dimensions.
- **Agent papers**: Use a concrete user task. Show how the system prompt, user input, tool descriptions, and memory/retrieval form the prompt context. Clearly trace the observe → reason/plan → act/tool call → tool result → update state → stop loop. Explain the harness/runtime, available tools, where state is stored, termination conditions, and error recovery. Mark implementation details that the paper does not disclose as "not specified in the paper"; never guess.
- **Mathematics / theory papers**: Start with the simplest scalar or low-dimensional function and work through concrete numbers by hand. Then generalize to vectors, random variables, or the paper's full formulation. Build from simple to advanced, and state which mechanism the simple example preserves and which conditions it omits.
- **Systems / databases / compilers papers**: Use a minimal request, query, program, or data block and track it through the actual processing pipeline, including queues, caches, scheduling, communication, and state transitions. Quantify latency, memory, or complexity whenever possible.
- **Other papers**: Choose a minimal input readers can verify by hand and trace the core algorithm step by step instead of repeating the paper's abstract description.

If one example cannot explain both the method and the mathematics, add a second one, but keep both minimal. If you construct any numbers, tensor shapes, or prompt content yourself, label them explicitly as a "teaching example" so readers do not mistake them for experimental data from the paper.

### 4. Mathematical derivations (required whenever the paper contains equations)

Follow [references/math-derivation.md](references/math-derivation.md) strictly. Key requirements:

- **Perform only one operation per step**, and state the justification beside it, such as "by Bayes' rule," "by Jensen's inequality," or "drop terms independent of $\theta$."
- **Fill in steps omitted by the paper.** Phrases such as "it is easy to show" and "after a straightforward calculation" usually mark the places most in need of expansion.
- **When encountering a secondary result**—a lemma, inequality, or identity used as a tool in the derivation—insert a "Secondary result" block at its first use. Include its statement, intuition, a short proof or proof sketch, and exactly how it is used in this paper.
- Clearly distinguish reconstructed steps from the paper's original text. Explicitly flag notation errors or omitted assumptions in the paper.

### 5. Write the notes

Produce a Markdown file using the structure in [references/output-template.md](references/output-template.md).
Save it to `./arxiv-papers/<id>/notes.md` by default, or use the path requested by the user.

Writing requirements:
- Write in English by default. When a specialized term first appears, provide any standard abbreviation or original term needed for clarity, for example "evidence lower bound (ELBO)."
- Lead each section with its conclusion, then develop the supporting argument.
- Explain in your own words rather than translating long passages. Quote only key definitions.
- Cite the table or figure number and comparison conditions for numerical results; never rely on memory.
- Distinguish **the paper's claims** from **your assessment**. You may express views in the lessons and critique sections, but explain the reasoning behind them.
- Use `$...$` / `$$...$$` for equations so they render in GitHub, Obsidian, and Typora.

### 6. Self-check

Before delivery, verify:
- [ ] Does the motivation → shortcoming → insight → method → result chain flow coherently, with each link following from the previous one?
- [ ] Is every key equation derived from definitions to the conclusion one step at a time, with a justification for each step?
- [ ] Have all secondary results used in the derivations been introduced?
- [ ] Do all experimental numbers match the paper?
- [ ] Is there at least one running example that goes from concrete input to output and shows key intermediate states?
- [ ] Does the LLM example explain both tensor shapes and information flow? Does the agent example explain context, loop, harness, and termination conditions? Does the mathematical example progress from simple numerical cases to the general form?
- [ ] Are self-constructed examples explicitly labeled "teaching example," with no speculation presented as fact from the paper?
- [ ] Are the "lessons for open-source projects" concrete and actionable rather than generic?

Finally, tell the user where the notes were saved and summarize the paper's core logic in three to five sentences.
