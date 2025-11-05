Learning philosophy

**Tags:** learning, learning-philosophy, skills-development, learning-log
**Last Updated:** 2025-10-09

## How I approach learning new tools or frameworks
- Prefer visual, hands‑on learning: follow video lessons (Udemy, Coursera, Hugging Face tutorials) and immediately apply concepts with small examples.
- Learn by building: implement minimal working examples (MVP), then iterate by adding realistic constraints (error handling, logging, tests).
- Learn by reading practical usage: study how libraries or tools are used in real repos and docs, then adapt patterns to your projects.

## What resources and methods work best for me
- Videos + guided courses for fast onboarding (Udemy, Coursera, Hugging Face, YouTube deep dives).
- Project-based learning: short projects that force integration across stack (example: RAG demo, small k8s deployment, property manager app features).
- Code reading & PRs: study high‑quality open‑source code, and create small PRs or forks to internalize patterns.
- Short writeups: after each learning session, write a 1–2 paragraph summary to consolidate understanding.

## How I track and document progress (practical system)
1) Learning log (single-line entry each session)
	- Date | Topic | Resource | Time spent | Key takeaway | Next step
	- Example: 2025-09-01 | RAG retrieval pipeline | Hugging Face tutorial | 2h | Learned embedding API + basic index | Add CI test for embedding ingestion

2) Project evidence
	- Keep a small repo for each project with clear README, Dockerfile, and a short demo GIF or screenshots.

3) Skill inventory
	- Maintain a checklist of skills acquired (e.g., Kubernetes: basics, helm, debugging) and mark completion with date and evidence link.

## Weekly learning cadence (recommended)
- 2–4 focused learning sessions (1–2 hours each) for course + notes.
- 2–4 hands‑on sessions (1–2 hours) for coding, experiments, or deployment.
- Weekly 15–30 minute reflection: update the learning log and capture one short artifact (screenshot, GIF, PR link).

## Turning learning into evidence
- Each completed milestone should produce one small artifact: a runnable repo, a demo video, a documented experiment, or a PR.
- Tag artifacts with date and a short descriptor and place them in an `evidence/` folder (e.g., `Skills/evidence/2025-10-09-rag-poc/`).

## Habits and mindset
- Time‑boxing: keep experiments small and time‑boxed to avoid scope creep.
- Iterative improvement: ship an MVP quickly, then refine based on measurable goals (latency, accuracy, reliability).
- Teach to learn: write short how‑to notes or teach a peer; teaching cements understanding.

## Measurable goals (examples)
- Build and document a RAG proof‑of‑concept repo within 8 weeks.
- Deploy a containerized demo to k8s (minikube or managed) with basic monitoring within 12 weeks.
- Complete one certification (e.g., CKAD or Hugging Face course) within 6 months.

## Quick templates you can copy
- Learning log CSV header: Date,Topic,Resource,TimeSpent,KeyTakeaway,NextStep,ArtifactLink
- Weekly reflection template: "This week I learned X, built Y, and next I will Z because..."

## Next steps (practical)
1. I can create a ready‑to‑use `learning_log.csv` file in `Knowledge_Base/Skills/evidence/` and add the first 6 weekly entries based on your current plan.
2. I can draft a 12‑week calendar mapping courses and POC milestones to specific weeks.
3. I can convert completed milestones into 3 resume bullets when you tag artifacts as evidence.

Which of the next steps should I do for you now? (create the CSV, draft the 12‑week calendar, or create resume bullets from planned milestones)
