# Install like-im-5

## At a glance

- Install the repository with your assistant's normal skill or plugin command.
- Start a new session after installing or updating.
- Invoke `like-im-5` directly, or ask for plain and accessible writing.

Activation differs by host. Model-invoked means the assistant can load the skill when the request matches its description. Explicit means you name the skill in the request or use the host's skill command.

## Codex

```bash
codex plugin marketplace add sorinmircea/like-im-5 --ref main
codex plugin add like-im-5@like-im-5
```

Verify with `codex plugin list`. Use `$like-im-5` directly; matching plain-language requests may also activate it.

Update with `codex plugin marketplace upgrade like-im-5`, then remove and add the plugin again. Remove it with `codex plugin remove like-im-5` and `codex plugin marketplace remove like-im-5`.

## Claude Code

```bash
claude plugin marketplace add sorinmircea/like-im-5
claude plugin install like-im-5@like-im-5
```

Verify with `claude plugin list`. Invoke `/like-im-5` or ask for accessible, plain-language output.

Update with `claude plugin marketplace update like-im-5`. Remove with `claude plugin uninstall like-im-5` and `claude plugin marketplace remove like-im-5`.

## Gemini CLI

```bash
gemini extensions install https://github.com/sorinmircea/like-im-5
```

Verify with `gemini extensions list`, then run `/skills list`. Gemini discovers the canonical skill from `skills/` and loads it when the request matches. Name `like-im-5` in the request when you want to force the style.

Update with `gemini extensions update like-im-5`. Remove with `gemini extensions uninstall like-im-5`.

## Qwen Code

```bash
qwen extensions install sorinmircea/like-im-5
```

Verify with `qwen extensions list` and `/skills`. Qwen can load the skill from the request or run it directly with `/like-im-5`.

Update with `qwen extensions update like-im-5`. Remove with `qwen extensions uninstall like-im-5`.

## Kimi Code CLI

Inside Kimi Code CLI, run:

```text
/plugins install https://github.com/sorinmircea/like-im-5
```

Start a new session, then use `/skill:like-im-5` or ask for accessible writing. Verify with `/plugins list`. Remove with `/plugins remove like-im-5`.

## Pi

```bash
pi install https://github.com/sorinmircea/like-im-5
```

Start a new session. Pi discovers the skill through `package.json`; use `/skill:like-im-5` or name it in the request. Verify with `pi list`, update with `pi update https://github.com/sorinmircea/like-im-5`, and remove with `pi remove https://github.com/sorinmircea/like-im-5`.

## Antigravity

```bash
agy plugin install https://github.com/sorinmircea/like-im-5
```

Verify with `agy plugin list`. Disable with `agy plugin disable like-im-5` or remove with `agy plugin uninstall like-im-5`.

## Copilot and other Agent Skills hosts

Use the cross-agent installer:

```bash
npx skills add sorinmircea/like-im-5
```

Add the host flag supported by your installer to target Copilot, Cursor, or another assistant. You can also copy `skills/like-im-5` into a skill directory the host scans.

- GitHub Copilot: `.github/skills/like-im-5` for a project or `~/.copilot/skills/like-im-5` for a user.
- Zed: import `https://github.com/sorinmircea/like-im-5/blob/main/skills/like-im-5/SKILL.md` in the Skills manager.
- Hermes: `hermes skills install sorinmircea/like-im-5/skills/like-im-5`.

The skill is portable because every host reads the same `skills/like-im-5/SKILL.md` file.
