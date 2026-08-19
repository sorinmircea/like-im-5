# like-im-5

Getting an AI answer is easy. Understanding it should be too.

`like-im-5` is an Agent Skill that makes AI output easier to scan, understand, and use. It starts with the big picture, uses plain English, keeps bullets short, and adds a visual only when the visual helps.

## At a glance

- Uses grade-8 English without talking down to the reader.
- Keeps needed technical words and explains them once.
- Works with Codex, Claude Code, Gemini CLI, Qwen Code, Kimi, Pi, and other Agent Skills tools.

## What changes

| Problem | Typical AI output | With `like-im-5` |
| --- | --- | --- |
| Buried answer | “Several factors may cause this build error…” | “`config/app.json` is missing. Create it, then rebuild.” |
| Too many words | “To begin the installation process, navigate to your terminal…” | “Run `npm install`.” |
| Unexplained jargon | “Transient read-after-write inconsistency may occur.” | “A saved change may take a few seconds to appear.” |
| Unclear flow | “The request passes through several infrastructure layers.” | `Browser → CDN → App → Database` |

The answer becomes easier to find, understand, and use.

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
```

Hosts that support model-invoked skills can also load it when a request asks for plain, concise, easy-to-scan, or visual writing.

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

## Sentence rules

The sentence-level rules follow the structural rules of ASD-STE100 (Simplified Technical English), Issue 9. The standard's approved-word dictionary is not reproduced here.

## Develop

```bash
python3 scripts/run_evals.py validate
python3 -m unittest discover -s tests
```

The evaluation suite checks clarity without allowing correctness, safety, or required detail to get worse.
