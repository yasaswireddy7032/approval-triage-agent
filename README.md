# Approval Triage Agent

A support-triage agent that reads a routing policy and proposes a queue, summary, and draft reply. The proposal is stored for review. The model has no approval or execution tool.

This project explores the boundary between a model's recommendation and an action: approval is tied to the exact proposal, and a repeated approval must not create another local assignment.

## Run the demo and tests

Requires Python 3.10+; no Python dependencies.

```bash
python app.py
python -m unittest -v
```

The default demo uses **scripted decisions, not a live LLM**. It creates no assignment and cleans up its temporary database. `example-output.json` records the demo. Nine local tests pass, including persistence, approval matching, idempotency, missing policy, and rejected model execution.

## Use a local model

Install/start Ollama separately and pull a model that follows JSON instructions.

```bash
python app.py --model YOUR_INSTALLED_MODEL --ticket-id demo-001 --ticket "My invoice has a duplicate charge." --db triage.db
```

Review the returned queue, summary, reply, and full proposal ID. To approve that exact proposal:

```bash
python app.py --db triage.db --approve FULL_PROPOSAL_ID --confirm FULL_PROPOSAL_ID
```

Approval writes **only a local SQLite assignment**. It does not send a reply, call a ticketing system, or issue a refund. The ID is a payload hash, not an authentication credential.

## Design

```text
Ticket -> model -> policy lookup -> validated proposal -> SQLite pending state
Human CLI confirmation -> transaction -> local assignment + audit -> completed
```

- Model actions are limited to policy lookup, proposal, or escalation.
- Matching policy lookup is required before routing a proposal.
- Six model turns by default prevent an endless tool loop.
- Proposal hashes include the ticket ID and payload. Changed drafts need a new approval.
- SQLite makes the local assignment, state update, and audit write atomic.
- A unique proposal key makes repeated local approval idempotent, including after restart.

## Boundaries

This is a single-user local reference implementation. Anyone who can access the database and CLI can approve; there is no identity provider or role-based authorization. Draft text is not semantically verified, and policy lookup does not prove policy compliance. A human must review the reply, including any requested credentials or commitments. Prompt injection can influence drafts, but cannot expose an approval tool.

The database contains draft content and is not encrypted. Remote ticketing effects would require authenticated approval, an outbox, failure handling, and deduplication at the destination. This does not claim distributed exactly-once execution.

The optional provider uses [Ollama's chat API](https://docs.ollama.com/api/chat). Live-model execution has **not** been tested here; deterministic tests cover the workflow. Provider failures fail the CLI run.

Independent portfolio project, added November 2026. Demonstration tickets and policies only; no employer code or customer data.
