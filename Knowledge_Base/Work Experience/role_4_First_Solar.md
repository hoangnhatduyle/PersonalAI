# MES Software Engineer I — First Solar

**Tags:** full-time, MES, software-engineering, manufacturing, AI, .NET, Next.js, PostgreSQL, Docker, Kubernetes
**Last Updated:** 2026-04-05

**Role:** MES Software Engineer I
**Company:** First Solar
**Location:** Perrysburg, Ohio (Remote)
**Dates:** February 2025 – Present (14+ months)
**Employment Type:** Full-time
**Team / Dept:** MES Software Engineering
**Manager:** Aaron Bollinger

---

## Role Overview

MES Software Engineer I at First Solar, one of the world's largest thin-film solar panel manufacturers. Responsible for developing and maintaining software systems that support manufacturing, reliability, and R&D processes. Now 14+ months into the role, having grown from onboarding into being the **main/lead developer** on a key internal project.

---

## Responsibilities

- Develop and modify software systems supporting manufacturing, reliability, and R&D processes.
- Integrate shop-floor systems (vision controllers, PLCs, MES clients) with custom and off-the-shelf enterprise solutions.
- Provide hypercare and expert-level support for global manufacturing applications; act as an escalation point for server, network, and DB admins.
- Design, code, test, and document features and small subsystems; create runbooks and troubleshooting guides for recurring issues.
- Interface with Operations, Data Analytics, and supplier representatives to align technical solutions with operational needs.

---

## Technologies Used

### Current / Active (as of 2026)
- **Backend:** .NET 10, C#, ASP.NET, Entity Framework
- **Frontend:** Next.js, React, HTML/CSS
- **Databases:** PostgreSQL, Microsoft SQL Server
- **Infrastructure & DevOps:** Docker, Kubernetes, Apache Airflow, Fleet/Helm for deployment
- **Platforms:** Azure DevOps, Ignition, Horizon client, Service Fabric, IIS
- **Data / Integration:** PLC/vision controller integration, MQTT, Palantir Foundry ingestion pipelines

### Earlier in Role
- C#, SQL, ASP.NET, Entity Framework, React, HTML/CSS, .NET Framework
- Visual Studio, Azure DevOps, MCP server, MS SQL Server, Virtual Machines (Windows)

---

## Projects & Contributions

### 1. Incident Intelligence Dashboard (Confidential — Internal Project)
**Role:** Main/lead developer (sole engineer on this project)
**Status:** Active development, vibe-coded from the ground up

A proprietary internal platform for First Solar's manufacturing floor that:
- **Collects incident data** from the production floor in real time
- **Generates actionable items** from the collected incident data using data-driven workflows
- **Provides dashboards** for shift managers and supervisors to visualize issues and act accordingly
- Designed to surface operational insights so leadership can make faster, data-backed decisions

This project represents a significant expansion of Hoang's responsibilities beyond assigned development tasks, demonstrating initiative and ownership.

### 2. Image Data Mart & AI Auto Reply (from Annual Review)
Hoang's work in **Image Data Mart** drove significant value, most notably **enabling AI Auto Reply** — an automated response capability that reduced manual operator decisions. This was called out specifically by manager Aaron Bollinger as a high-impact contribution.

### 3. Remote Operations (Remote Reset)
- Goal: Enable operators to make remote decisions after inspection failures by surfacing vision controller images.
- Outcome: Implemented image ingestion to ImageDataMart, coupled UI changes for operator decision flows, reduced unnecessary site visits.
- Role: Design → implement → test → deploy; coordinated with Operations and Data Analytics; created runbooks for hypercare.

### 4. ESD & JB1 Tool Onboarding
Delivered ESD and JB1 tools online, expanding the team's operational capabilities. Mentioned explicitly in annual review as key contribution.

### 5. PLC Tag Discovery & MQTT Publishing Pipeline (Palantir Foundry)
Delivered a PLC tag discovery and MQTT publishing pipeline for **Palantir Foundry** data ingestion within a short time window. This project involved integrating shop-floor PLC data into a cloud-scale analytics platform.

### 6. Module Inventory App
- Goal: Improve module inventory accuracy and traceability.
- Outcome: Backend integrations with MES and MSSQL reduced manual reconciliation steps and improved data quality.

### 7. Dumpster Weight Validation App
- Goal: Validate sensor/weight data and reduce false failure alerts.
- Outcome: Implemented validation and alerting rules that reduced false positive tickets and lowered manual review workload.

---

## Annual Performance Review (2025)

**Manager:** Aaron Bollinger | **Overall Status: Green**

### Demonstrates Excellence
| Competency | Manager Comment Summary |
|---|---|
| Accountability | Takes excellent accountability; stays on task; raises concerns appropriately; doesn't point fingers |
| Agility | Evolves rapidly with changing requirements; changes course week-to-week as needed; intellectually curious |
| Attention to Detail | Reliable sprint delivery; communicates status clearly; high-quality contributions; functional solutions that meet objectives |
| Integrity | High commitment to honesty, transparency, and accountability; respects colleagues; gets along well |
| Logical & Clear Thinker | Naturally talented at thinking through problems; can analyze and rationalize complex information; achieves great results with minimal guidance |
| Problem Solving | Diagnoses problems and prioritizes effective solutions; demonstrated through AI Auto Reply validation; identifies root causes and mitigates future challenges |
| Reality Based Thinking | Takes ownership and accountability; first instinct is to assess own weaknesses before external attribution |

### Delivers Against Expectations (Growth Areas)
| Competency | Growth Direction |
|---|---|
| Analytical Aptitude | Improve ability to turn data into actionable insights that drive business decisions |
| Collaboration | Grow influence over stakeholders and higher-level decisions; develop proactively over time |
| Communication | Learn to drive projects through effective communication; goes hand-in-hand with collaboration |
| Functional Knowledge | Build skills to move toward SE II role; think through entire MES architecture; propose high-level solutions |
| Technical Knowledge | Focus on creative/innovative technical solutions; plan and present architecture; build stakeholder buy-in |

### Overall Manager Summary
> "Hoang Le is a reliable, high-output technical contributor who consistently turns complex work into tangible results. His work in Image Data Mart has driven significant value, most notably enabling capabilities such as AI Auto Reply. His attention to detail and persistence have also been key in bringing new tools like ESD and JB1 online, expanding the team's operational capabilities. He has shown strong agility in managing competing priorities without sacrificing quality. He also delivered the PLC tag discovery and MQTT publishing pipeline for Palantir Foundry ingestion in a short time window."
>
> "I would like to see Hoang Le develop a stronger sense of initiative beyond assigned work. This should include proactively identifying problems, exploring them in depth, and bringing forward proposals that improve how we operate. As he takes on more complex solutions, building the habit of engaging with product management and other stakeholders early in the process will help ensure his technical work stays aligned with broader business needs."
> — Aaron Bollinger, Manager

---

## Technical & Interpersonal Growth

### Challenges Overcome
- Adapted to large corporate company culture, new colleagues, and new communication norms vs. prior startup/SMB environments
- Coordinated changes across Operations, Infrastructure, and product teams while minimizing risk to production-adjacent systems
- Adopted conservative live-change policies, modular architecture to limit blast radius, thorough logging/alerts, runbooks, and clear rollback plans

### What I've Learned
- **Production discipline:** Observability, reversible changes, runbooks, operator-focused communication
- **Cross-stack integration:** Connecting vision controllers, PLCs, MES clients, and enterprise databases reliably
- **Corporate stakeholder navigation:** Engaging product management and operations leadership earlier in the process
- **Full-stack in modern tech:** Migrated from legacy .NET Framework to .NET 10, React to Next.js, MSSQL to PostgreSQL, adding Docker/Kubernetes/Airflow/Fleet

---

## Evidence & Recognition

- Annual review rated **Green** (positive) by manager Aaron Bollinger (full review at `Knowledge_Base/Achievements & Recognition/first_solar_annual_review.md`)
- Named specifically for: Image Data Mart → AI Auto Reply capability, ESD/JB1 onboarding, PLC/MQTT/Palantir Foundry pipeline
- Growing into lead developer role on confidential incident intelligence project

---

## RAG-Friendly Metadata (JSON)
```json
{
    "id": "role-first-solar-20260405",
    "title": "MES Software Engineer I — First Solar",
    "entity_type": "work_experience",
    "tags": ["full-time","MES","manufacturing","AI","dotnet","Next.js","PostgreSQL","Docker","Kubernetes","Airflow","first-solar","current-role"],
    "company": "First Solar",
    "location": "Perrysburg-Ohio-remote",
    "dates": "February-2025-to-Present",
    "duration_months": 14,
    "role_type": "full-time",
    "technologies": [".NET-10","C#","Next.js","PostgreSQL","Docker","Kubernetes","Apache-Airflow","Fleet","Helm","MQTT","Palantir-Foundry","Azure-DevOps"],
    "key_projects": ["Incident-Intelligence-Dashboard","Image-Data-Mart","AI-Auto-Reply","Remote-Reset","ESD-JB1","PLC-MQTT-Palantir","Module-Inventory","Dumpster-Weight-Validation"],
    "annual_review_status": "Green",
    "manager": "Aaron-Bollinger",
    "last_updated": "2026-04-05"
}
```
