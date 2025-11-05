Role Overview

**Job Title:** MES Software Engineer I
**Company:** First Solar
**Location:** Perrysburg, Ohio
**Dates:** February 2025 - Present
**Employment type:** Full-time
**Team / Dept:** MES Software Engineering

## Responsibilities (core duties)
- Develop and modify software systems supporting manufacturing, reliability, and R&D processes.
- Integrate shop‑floor systems (vision controllers, PLCs, MES clients) with custom and off‑the‑shelf enterprise solutions.
- Provide hypercare and expert‑level support for global manufacturing applications; act as an escalation point for server, network, and DB admins.
- Design, code, test, and document features and small subsystems; create runbooks and troubleshooting guides for recurring issues.
- Interface with Operations, Data Analytics, and supplier representatives to align technical solutions with operational needs.
- Maintain safety and housekeeping standards while exercising clear communication and team collaboration.
- Current focus: Remote Operations (Remote Reset) — surfacing vision controller images to operators and storing images in ImageDataMart to enable remote decision making.

## Systems, stakeholders & technologies
- Systems / products: ImageDataMart, Remote Reset (Remote Operations), Module Inventory App, Dumpster Weight Validation App.
- Stakeholders: MES Software Engineering team, Operations (operators & supervisors), Data Analytics team, Infra/Admin teams, Database Administrator Team.
- Languages & frameworks: C#, SQL, ASP.NET, Entity Framework, React, HTML/CSS, .NET Framework.
- Tools & platforms: Ignition, Horizon client, Service Fabric, Azure DevOps, Visual Studio, IIS, MCP server.
- Databases / infra: MS SQL Server, Virtual Machines (Windows), on‑prem integration with PLC/vision systems.

## Achievements & impact
- Remote Operations (Remote Reset): delivered image capture and delivery pipeline from vision controllers to ImageDataMart and operator UIs to enable remote inspection workflows. Suggested KPIs to record: remote‑decision count, average time‑to‑decision, reduction in onsite visits.
- Observability & triage improvements: introduced structured logging, alerting, and runbooks for recurring incidents used by server/DB/network admins, which improved time‑to‑diagnosis.
- Operational efficiency: contributed code and integration to Module Inventory and Dumpster Weight Validation apps to reduce manual reconciliation and false positive tickets.
- Cross‑team support: regularly assisted administrators during enterprise incidents and documented fixes to prevent recurrence.
- Evidence of impact: feature rollouts and hypercare ownership increased operational trust and reduced escalations (collect PRs, incident tickets, and manager notes as evidence).

## Projects (key contributions)
1) Remote Operations (Remote Reset)
	- Goal: enable operators to make remote decisions after inspection failures by surfacing images and context.
	- Outcome: implemented image ingestion to ImageDataMart, coupled UI changes for operator decision flows, and reduced unnecessary site visits.
	- Role: design→implement→test→deploy; coordinated with Operations and Data Analytics; created runbooks for hypercare.

2) Module Inventory App
	- Goal: improve module inventory accuracy and traceability.
	- Outcome: backend integrations with MES and MSSQL reduced manual reconciliation steps; improved data quality.
	- Role: contributed backend services and integration logic.

3) Dumpster Weight Validation App
	- Goal: validate sensor/weight data and reduce false failure alerts.
	- Outcome: implemented validation and alerting rules that reduced false positive tickets and lowered manual review workload.
	- Role: designed checks, implemented server logic, and collaborated with analytics for thresholds.

## Technical & interpersonal challenges
- Challenge: coordinating change across Operations, Infrastructure, and product while minimizing risk to production‑adjacent systems. Changing job and new environment, new colleagues, new way of communication, adaptation with large corporate company
- How overcome: adopted conservative live‑change policies, built modular architecture to limit blast radius, added thorough logging/alerts, prepared runbooks, and communicated clear rollbacks and testing plans with stakeholders. Improve communication, as time goes by I make more impact, more confidence

## What I learned / growth
- Strengthened production discipline: observability, reversible changes, and the value of runbooks and operator‑focused communication.
- Improved cross‑stack integration skills: connecting vision controllers, PLCs, MES clients, and enterprise databases reliably.
- Identified opportunities to apply RAG/agent tooling to support operator decision making and reduce manual work.

## Awards, recognition & evidence to collect
- No formal awards recorded in the workspace yet; evidence to collect for performance reviews or EB‑2: PRs, incident tickets (MTTR), runbooks, screenshots/demos of ImageDataMart flows, manager testimonial or LinkedIn recommendation.

## Suggested links / artifacts
- Internal PR list or repo links for Remote Reset and Module Inventory work.
- Short demo video or screenshot walkthrough of ImageDataMart and operator UI flows.
- Incident ticket excerpts showing resolution and MTTR improvements.

## Next steps (practical)
1. Turn these outcomes into 3–5 resume bullets (I can draft them now).
2. Prepare a 1‑page project summary for Remote Operations (includes architecture, timeline, and evidence). I can draft the first pass.
3. Collect evidence artifacts (PRs, runbooks, tickets) and place them in an `evidence/` folder under this role for future applications.

If you'd like, tell me which next step to do: resume bullets, 1‑page case study, or collect/organize evidence files.
