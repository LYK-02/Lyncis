# Lyncis — Documentation Set

Lyncis is an AI website builder: describe an idea, get a complete responsive site, customize it, publish it.

| # | File | What it answers |
|---|------|-----------------|
| 01 | `01-PRD.md` | What are we building, for whom, and how do we know it works |
| 02 | `02-TRD.md` | How it is built: architecture, data model, AI pipeline, APIs |
| 03 | `03-PHASES.md` | In what order, with exit criteria per phase |
| 04 | `04-RULES.md` | Coding, structure, and AI-assisted-coding rules |
| 05 | `05-SECURITY.md` | Threat model and required controls |
| 06 | `06-APP-FLOW.md` | Screens, routes, user flows, state machines |
| 07 | `07-ANIMATION.md` | Motion system and per-screen animation specs |
| 08 | `08-DEPLOYMENT.md` | Environments, CI/CD, infra, launch and rollback |
| 09 | `09-PRODUCTION-PRACTICES.md` | Quality bars, observability, release, incident practice |
| 10 | `10-DESIGN.md` | Visual system based on the uploaded theme |

## How to use
- Put this folder in the repo at `/docs`. Point your AI coding tool (Cursor, Claude Code) at `04-RULES.md` and `02-TRD.md` first.
- Treat items marked **ASSUMPTION** or **VERIFY** as open decisions. Vendor prices and free-tier limits change often: check them on the vendor's page before relying on them.
- When a decision changes, update the doc in the same PR as the code.

## Decisions still open
1. Payment gateway: Stripe vs Razorpay (affects India billing, GST, UPI).
2. Final domain names (app domain and a separate domain for published sites).
3. LLM provider mix and monthly AI budget.
4. Whether marketing claims ("10x faster", "100% responsive") are measured before launch.
