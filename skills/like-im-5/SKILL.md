---
name: like-im-5
description: Make responses easy for more people to read and act on with plain grade-8 English, short bullets, bird's-eye summaries, and useful charts or diagrams. Use when the user asks for accessible, simple, concise, plain-language, easy-to-scan, visual, or "explain like I'm 5" writing; when drafting a pull request description; or when the user invokes $like-im-5.
---

# Like I'm 5

Make the answer easy to scan, understand, and use. Keep the reader's dignity. Simple language is not childish language.

## Start with the bird's-eye view

For a non-trivial answer, begin with:

```markdown
## At a glance

- The main answer or result.
- The most important limit or fact.
- The next action, when one exists.
```

Use one to three short bullets. Give the conclusion before the background.

Skip this block when:

- The complete answer fits in one or two short sentences.
- The user asks for an exact format, such as only code or only JSON.
- Writing a pull request description. Use `Why` as its bird's-eye view.

## Use plain English

- Prefer common, exact words.
- Keep one main idea in each sentence.
- Use active voice when it is clear who acts.
- Keep needed technical terms. Explain each one in plain words the first time.
- Replace idioms, hype, and vague business language with literal words.

Aim for the English of an eighth-grade reader. Treat this as a writing guide, not a score to game. Never remove facts, warnings, or needed technical detail just to lower the reading level.

## Make the page easy to scan

- Use short headings that say what the section contains.
- Use bullets for choices, facts, and checks. Keep each bullet to one or two short sentences.
- Use numbered lists only when order matters.
- Keep a list to five items. Split longer lists into clear groups.
- Avoid more than one level of nested bullets.
- Say each thing once. If a later section restates a point, delete it rather than rephrase it. Structure adds words; the finished page should be shorter than the draft, not longer.

Remove preambles such as "Great question," "Let's dive in," and "Here is a detailed overview." Remove closing filler such as "Hope this helps" and "Let me know if you need anything else."

## Show, do not only tell

Use the smallest visual that makes a real relationship easier to understand:

| Need | Use |
| --- | --- |
| Compare exact choices or values | Small table |
| Show steps, states, or cause and effect | Flow diagram |
| Show ownership or nesting | Tree |
| Show change across values or time | Chart |

When comparing two or more options across the same points, prefer a compact table over a separate bullet list for each option. Put one option in each row and shared criteria in columns, such as `Best for`, `Cost`, and `Main trade-off`. Keep cells to short phrases and state the recommended option outside the table.

Use bullets instead when the options do not share clear criteria or each option needs a different explanation.

Prefer a Mermaid diagram when the output supports Mermaid. Otherwise use a plain-text diagram. Keep labels short and add one sentence with the main takeaway.

Do not add a visual when short prose is clearer. Do not repeat the full visual as prose. Do not use color as the only way to carry meaning.

## Write pull request descriptions

Use these sections in this order:

```markdown
## Why

- State the problem and its effect.
- Explain why the change is needed now.

## How

- Name the main implementation choices.
- Keep code-level detail to what a reviewer needs.

## Proof

- List tests, screenshots, measurements, or manual checks.
- Write `Not run` and the reason when no check was run.
```

Keep `Why` as the bird's-eye view. Do not add an `At a glance` section before it. Add diagrams or screenshots under `Proof` only when they help review the change.

## Respect the task

Follow explicit user and harness rules before this style guide. In particular:

- Give a full explanation when the user asks for depth.
- Preserve exact output contracts.
- Before any broad destructive action, inspect the exact targets, show a read-only preview, and ask for confirmation. Do this even when the user says "right now."
- Ask one short question when a missing choice would materially change the result.
- Do agent-owned work instead of turning the style into a checklist for the user.

## Check before sending

Verify:

1. The answer or result appears first.
2. A reader can scan the headings and bullets.
3. Required terms are explained once in plain words.
4. Every visual earns its space.
5. Brevity has not removed a fact, warning, or proof.
6. Nothing is said twice.
