# Proactive automations

Three tasks share provider, state, and notification adapters:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m automations.run research-radar --dry-run
python -m automations.run quant-interview --dry-run
python -m automations.run backtest-auditor --dry-run
```

## Configuration

Copy values from `.env.example` into the shell or GitHub Actions secrets; the program does not load `.env` files. The default provider is the official `anthropic` Python SDK, model `claude-opus-5-5`, with adaptive thinking. Set `AGENT_PROVIDER=command` and `EXTERNAL_AGENT_COMMAND='your command'` to use a local/external CLI; it receives the prompt on stdin and must print text on stdout.

The quant interview task generates question candidates and deduplicates them against its own automation state. It does not read or modify an external knowledge repository; review generated questions from stdout or your configured notification target before adding them.

State JSON lives under `automations/state/`, uses SHA-256 content fingerprints for deduplication, and is git-ignored. Stdout is the default notification target; `NOTIFICATION_WEBHOOK_URL` enables a generic JSON webhook.

GitHub Actions runs `research-radar` and `backtest-auditor` sequentially on weekdays and supports manual selection of those tasks. It restores and saves `automations/state/` with the Actions cache so deduplication survives ephemeral runners; concurrency is serialized to avoid state races. Scheduled runs are live, while manual runs default to dry-run.

`quant-interview` remains available for local runs but is not scheduled in GitHub Actions by default.

## Checks

```bash
./scripts/validate.sh
python -m unittest discover -s tests -v
```
