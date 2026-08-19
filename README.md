# like-im-5

Getting an AI answer is easy. Understanding it should be too.

`like-im-5` is an Agent Skill that makes AI output easier to scan, understand, and use. It starts with the big picture, uses plain English, writes sentences with one meaning, and adds a visual only when the visual helps.

## At a glance

- Uses grade-8 English without talking down to the reader.
- Keeps needed technical words and explains them once.
- Writes sentences with one meaning, following ASD-STE100.
- Works with Codex, Claude Code, Gemini CLI, Qwen Code, Kimi, Pi, and other Agent Skills tools.

## What changes

| Problem | Typical AI output | With `like-im-5` |
| --- | --- | --- |
| Buried answer | “Several factors may cause this build error…” | “`config/app.json` is missing. Create it, then rebuild.” |
| Too many words | “To begin the installation process, navigate to your terminal…” | “Run `npm install`.” |
| Unexplained jargon | “Transient read-after-write inconsistency may occur.” | “A saved change may take a few seconds to appear.” |
| Unclear flow | “The request passes through several infrastructure layers.” | `Browser → CDN → App → Database` |
| Lost hedge | “The export failed.” | “The export may have failed. Nobody has confirmed it yet.” |

## Install

### Codex

```bash
codex plugin marketplace add sorinmircea/like-im-5 --ref main
codex plugin add like-im-5@like-im-5
```

Verify with `codex plugin list`, then invoke the skill with `$like-im-5`.

### Claude Code

```bash
claude plugin marketplace add sorinmircea/like-im-5
claude plugin install like-im-5@like-im-5
```

Verify with `claude plugin list`, then invoke the skill with `/like-im-5`.

For Gemini CLI, Qwen Code, Kimi, Pi, Antigravity, Copilot, Zed, Hermes, and other Agent Skills hosts, see [INSTALL.md](INSTALL.md).

## Use it

Ask for simple or accessible writing, or invoke the skill by name:

```text
$like-im-5 Explain how OAuth works.
$like-im-5 Rewrite this release note for a wider audience.
$like-im-5 Draft the pull request description for these changes.
$like-im-5 Write the docstring for this function.
```

Hosts that support model-invoked skills can also load it when a request asks for plain, concise, easy-to-scan, or visual writing.

## Sentence rules

Plain words are not enough. A short sentence can still carry two meanings:

- Keep instructions under 20 words. Keep explanations under 25.
- Use one plain verb: `start`, not `spin up`.
- Use one name for one thing. Do not switch between `user`, `customer`, and `client`.
- Keep hedges such as `may`. Removing one states a stronger claim than the source made.

These follow the structural rules of [ASD-STE100](https://www.asd-ste100.org/) (Simplified Technical English) Issue 9. Its approved-word dictionary is not reproduced here.

## Code comments

The same rules apply to comments and docstrings. The page structure does not: no summary block, no headings, no bullets, no diagrams. A comment uses the name the code uses, so `accountId` is `account`, not `client`.

## Pull request format

```markdown
## Why

- What problem does this solve?
- Who or what does the problem affect?

## How

- What changed?
- What choices matter to the reviewer?

## Proof

- What tests, screenshots, or checks show it works?
```

## Develop

```bash
python3 scripts/run_evals.py validate
python3 -m unittest discover -s tests
```

The evaluation suite checks clarity without allowing correctness, safety, or required detail to get worse.
