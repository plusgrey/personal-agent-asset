# Proactive automations

Three tasks share provider, state, Notion, and notification adapters:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m automations.run research-radar --dry-run
python -m automations.run quant-interview --fixture tests/fixtures/notion_blocks.json
python -m automations.run backtest-auditor --dry-run
```

## Configuration

Copy values from `.env.example` into the shell or GitHub Actions secrets; the program does not load `.env` files. The default provider is the official `anthropic` Python SDK, model `claude-opus-5-5`, with adaptive thinking. Set `AGENT_PROVIDER=command` and `EXTERNAL_AGENT_COMMAND='your command'` to use a local/external CLI; it receives the prompt on stdin and must print text on stdout.

The quant interview task reads the private Notion page recursively and appends unseen questions. It uses only `NOTION_TOKEN`, defaults to page `38889a37c8408030b9bdcdbd13c618d9`, and sends `Notion-Version: 2026-03-11`. Share that page with the Notion integration first. `--fixture` and `--dry-run` never write to Notion; tests use mock transport/local fixtures only.

State JSON lives under `automations/state/`, uses SHA-256 content fingerprints for deduplication, and is git-ignored. Stdout is the default notification target; `NOTIFICATION_WEBHOOK_URL` enables a generic JSON webhook.

GitHub Actions runs all three tasks sequentially on weekdays and supports manual task selection. It restores and saves `automations/state/` with the Actions cache so deduplication survives ephemeral runners; concurrency is serialized to avoid state races. Configure repository secrets only when enabling live runs. Scheduled runs are live, while manual runs default to dry-run.

## Notion setup

1. Create an internal integration in Notion and enable read/insert content capabilities.
2. Open the Quant Practice page, choose **Connections**, and grant that integration access.
3. Set the integration secret as `NOTION_TOKEN` locally or as a GitHub Actions repository secret. Never put it in `.env.example` or source control.
4. Preview with `--fixture` first. A live `quant-interview` run recursively reviews prior page blocks and silently appends new bullet questions at the end.
5. Because this sends private Notion text to the configured model provider, live runs are blocked by default. Set `ALLOW_PRIVATE_CONTEXT=true` locally—or the GitHub Actions repository variable of the same name—only after explicitly approving that data flow.

## Checks

```bash
./scripts/validate.sh
python -m unittest discover -s tests -v
```
