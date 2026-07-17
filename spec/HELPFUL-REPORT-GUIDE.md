# Helpful Report Content Guide

This guide defines the transformation that makes the output more useful than raw validator output. It is normative where it uses **shall**, **should**, or **may**.

## 1. Two layers, two purposes

The report **shall** have two clearly separated layers:

1. **Fix guide** — a practitioner-oriented explanation organised by root cause and recommended edit.
2. **Validator record** — a complete, lossless record of every authoritative validator finding, using lossless identical-message grouping where useful.

The fix guide **shall not** repeat the validator output finding by finding. The validator record **shall not** contain invented interpretation.

## 2. Root-cause grouping

The generator **shall** inspect the TTML and group related findings into fix recipes when they appear to share one correction. For example, ten findings caused by one missing root attribute should produce one fix recipe linked to ten validator records.

Each recipe **shall** state:

- what is wrong in plain language;
- how many validator findings it explains;
- whether it blocks delivery or represents a recommendation;
- where the shared cause occurs in the TTML;
- why the current markup causes the reported result;
- the exact edit to make;
- a contextual before-and-after example drawn from the supplied TTML;
- what should change on revalidation; and
- the IDs of all validator records covered by the recipe.

If findings do not share a defensible cause, they **shall** remain separate recipes. Grouping **shall not** weaken traceability.

## 3. Explanation quality

Explanations **shall** add information that is not already obvious from the validator message. Merely rewording the message does not satisfy this requirement.

A strong explanation answers at least two of these questions:

- What TTML construct is the validator evaluating?
- Why does the supplied value or structure fail that check?
- What effect could it have on processing or presentation?
- Why is the proposed replacement appropriate for this document?
- Are other elements or references affected by the same edit?

When the evidence does not support an answer, the report **shall** say what cannot be determined instead of adding generic filler.

## 4. Corrections

Every proposed correction **shall** be anchored in the original TTML. The report **shall not** provide a generic example when a safe contextual example can be produced.

Before-and-after snippets **shall** include enough surrounding markup to locate the edit, preserve unrelated content, identify the changed line or attribute using text as well as colour, remain concise, and be labelled “Proposed — revalidate after applying”.

The recommended action **shall** be imperative and testable, such as “Add `xml:lang="en-GB"` to the root `tt:tt` element,” rather than “Consider checking the language.”

## 5. Priorities and workflow

The report **shall** provide an ordered remediation plan based on dependency and impact, not simply validator order. A fix that may resolve many downstream findings **should** appear before isolated fixes.

The plan **shall** use these stages when applicable: fix document structure and declarations; fix references, styles, and regions; fix timing and content instances; revalidate the entire document; then review separately labelled editorial guidance.

The generator **shall not** promise that a recipe will resolve a finding. It **should** state the expected revalidation outcome and any uncertainty.

## 6. BBC guidance

BBC guidance **shall** support the explanation of a relevant recipe; it shall not appear as a decorative citation list. A guidance card **should** answer “How does BBC practice help me make this edit?”

Technical requirements and presentation guidance **shall** be labelled distinctly. Editorial advice **shall not** be used to inflate validator severity or imply a validation failure.

## 7. Tone

Use calm, specific, professional language. Address the work directly rather than blaming the author. Prefer “The region references `style_2`, which is not defined” to “You used an invalid style.”

Avoid stock phrases such as “This issue indicates that”, “It is important to note”, and “To resolve this issue, you should”. Avoid repeated caveats and conclusions that merely repeat the summary. State shared caveats once, then use compact labels within recipes.

## 8. Minimum usefulness test

Before returning the report, the generator **shall** confirm that a practitioner can locate and perform each edit without reopening the validator output; every recipe explains something beyond its validator message; repeated symptoms are consolidated sensibly; every recipe traces to all relevant findings; and the next action is obvious within ten seconds.

Completeness outranks presentation. The generator **shall not** spend its output budget on decorative prose and then truncate the validator record. It **shall** use concise recipes and lossless identical-message grouping to preserve complete coverage.
