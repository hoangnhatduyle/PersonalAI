Skills in progress

**Tags:** skills-in-progress, learning-plan, AI, LLMs, MLOps, Kubernetes
**Last Updated:** 2025-10-09

## Short summary
Focused on gaining practical AI/LLM skills and production‑grade infrastructure knowledge (Kubernetes, observability, and MLOps). The learning plan balances courses, hands‑on projects, and targeted certifications to convert knowledge into evidence for career growth and applications.

## Current topics being learned
- LLMs and prompt/agent engineering — foundations, retrieval-augmented generation (RAG), and agent orchestration.
- AI / Deep Learning — model basics, fine‑tuning, evaluation, and toolchains (PyTorch/TensorFlow).
- Kubernetes and container orchestration — deploying, operating, and debugging workloads in k8s clusters.
- MLOps patterns — CI/CD for models, feature stores, monitoring models in production.

## 6–12 month roadmap (milestones)
1) Months 0–3 (Foundations)
	- Complete an LLM fundamentals course and a Kubernetes basics course.
	- Build a small RAG proof‑of‑concept: index a repo of docs, create embeddings, and serve simple retrieval + prompt pipeline.
	- Goal: working demo + repo with README.

2) Months 3–6 (Production readiness)
	- Harden the RAG prototype with basic reliability: containerize services, add logging/metrics, and deploy to a k8s namespace (minikube or managed cluster).
	- Learn CI/CD for model/artifact delivery (Azure DevOps pipeline or GitHub Actions) and add automated tests.
	- Goal: reproducible deployment and basic observability dashboards.

3) Months 6–12 (Scale & specialization)
	- Explore fine‑tuning or adapters on a small dataset; implement model evaluation metrics and drift detection.
	- Integrate an agent orchestration framework (e.g., LangChain/Agentic tooling) for a targeted operator‑support workflow.
	- Goal: one end‑to‑end case study (RAG + agent) with documented outcomes and lessons learned.

## Suggested courses & certifications
- LLM / NLP: Hugging Face course (Transformers and course modules), DeepLearning.AI NLP/LLM tracks.
- Deep Learning: Fast.ai or DeepLearning.AI Specializations (PyTorch/TensorFlow).
- Kubernetes: CNCF Certified Kubernetes Application Developer (CKAD) or introductory k8s courses on Pluralsight / Udemy.
- MLOps: Coursera MLOps Specialization or hands‑on MLOps workshops.

## Measurable goals (examples)
- Ship a RAG proof‑of‑concept repo with README and sample data within 8 weeks.
- Deploy service to a k8s namespace with automated pipeline and monitoring within 16 weeks.
- Produce a 1‑page case study with at least one measurable outcome (e.g., response time, accuracy, or operator time saved) within 6 months.

## Learning activities (weekly cadence)
- 4–8 hours/week of structured learning (course videos + notes).
- 4–8 hours/week of hands‑on work (coding, experiments, deployments).
- Weekly short writeups (1–2 paragraphs) summarizing progress and lessons — useful for evidence and portfolio.

## Evidence to collect
- Repositories with clear READMEs and runnable examples (Dockerfile, k8s manifests).
- Short demo videos or GIFs showing the system in action.
- CI/CD pipelines (screenshots or links) and sample logs/metrics dashboards.
- Small notebooks or PRs showing fine‑tuning / evaluation steps.

## Planned certifications / courses
- Hugging Face courses (Transformers / Inference / Fine‑tuning)
- CKAD (or equivalent Kubernetes certification)
- DeepLearning.AI specialization (optional)

## Risks & mitigation
- Risk: scope creep on projects delaying completion — mitigate by defining small, time‑boxed MVPs and clear acceptance criteria.
- Risk: lack of infrastructure access for k8s or GPUs — mitigate by using managed free tiers, local minikube, or lightweight CPU‑based experiments.

## Next steps (practical)
1. Choose the first RAG POC goal and list the minimal dataset and expected user flow — I can draft the repo README and task list.
2. If you want, I can draft a 12‑week learning calendar with weekly milestones and links to courses/resources.
3. I can also generate 3 resume bullets from completed milestones once you tag evidence files in an `evidence/` folder.

Tell me which next step you want me to start: draft the POC README, create the 12‑week calendar, or draft resume bullets from planned outcomes.
