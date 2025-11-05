# Air3550 Flight Management System - RAG-Friendly Documentation

## System Overview
**Project Name**: Air3550 Flight Management System  
**System Type**: Full-stack airline management platform  
**Architecture**: ASP.NET Core Web API backend with Angular frontend  
**Primary Purpose**: Comprehensive flight booking, user management, and airline operations system  

## Technology Stack

### Backend Technologies
- **Framework**: ASP.NET Core 7.0
- **Database**: SQLite with Entity Framework Core 7.0
- **Authentication**: JWT Bearer tokens with ASP.NET Core Identity
- **ORM**: Entity Framework Core with Code First migrations
- **Object Mapping**: AutoMapper for DTO mapping
- **Architecture Pattern**: Repository Pattern with Unit of Work implementation
# Air3550 — Flight Management System (RAG-friendly)

**Tags:** air3550, project, flight-management, aspnet, angular, ragnb
**Last Updated:** 2025-10-10

Short summary
- Air3550 is a full‑stack flight reservation and operations system built for a senior software engineering project. It demonstrates end‑to‑end features: user accounts, booking, flight scheduling, inventory (planes), payment recording, points/credit system, and administrative workflows (manifests, reporting).
- Implementation highlights: ASP.NET Core Web API backend (Entity Framework Core + SQLite), Angular frontend, JWT authentication, repository/unit‑of‑work patterns, and seeded demo data for testing and evaluation. Primary source artifacts: `Extra/Air3550 Design Document/`, `Extra/Air3550 Project Requirement/`, and `Extra/Air3550 Test Plan.xlsx`.

Why this doc
- This RAG‑friendly project page extracts the most important facts, API contract, data model, use cases, and test/acceptance criteria so downstream agents and retrieval systems can answer focused questions quickly (e.g., "how to seed dev data", "how to cancel a ticket", "what are the business rules for check‑in").

Quick links (sources)
- Design document (full): `Knowledge_Base/Extra/Air3550 Design Document/Air3550 Design Document.md`
- Requirements: `Knowledge_Base/Extra/Air3550 Project Requirement/Air3550 Project Requirement.md`
- Test plan: `Knowledge_Base/Extra/Air3550 Test Plan.xlsx`
- Project repo snapshot (client + API): `Knowledge_Base/Extra/Air3550/Air3550/`

Core capabilities (at a glance)
- User management: registration, login, profile management, password change.
- Booking flow: search flights, select itineraries, book (one‑way/round‑trip), payment, points accrual/redemption.
- Flight operations: create/edit flights, assign aircraft (MarketingManager), print manifests (FlightManager), manage airports.
- Financials: payment recording, reporting for accounting role, points/credit system.
- Administrative: role/permission management, seeded demo accounts and data for testing.

System architecture (concise)
- Frontend: Angular SPA (v14) with Angular Material for UI components, ngx‑toastr for notifications, and JWT token storage for auth flows.
- Backend: ASP.NET Core Web API (target .NET 7), EF Core (Code First), JWT + Identity for user authentication and role management, repository & UnitOfWork patterns for data access.
- Data: SQLite for dev/demo; Data seeding on startup creates users, roles, cities, flight paths, and sample flights (see `API/Data/UserSeedData.json`).

API overview (selected endpoints & behavior)
- Authentication
    - POST /api/account/register — create account (default Member role)
    - POST /api/account/login — returns JWT token
    - PUT /api/account/changepassword — authenticated password change
- Booking & ticketing
    - POST /api/users/add-new-ticket — book ticket; validates booking windows and dates; supports payment by cash/points/credit
    - PUT /api/users/cancel-ticket/{id} — cancel ticket (only allowed >1 hour before departure)
    - PUT /api/users/checkin-ticket/{id} — check-in up to 24 hours before departure
    - GET /api/users/get-ticket — list tickets for authenticated user
- Flight management
    - GET /api/flight/all-flights — list flights (role restricted)
    - PUT /api/flight/edit-flight-time/{flightNumber}/{leaveTime} — update schedule
    - PUT /api/flight/edit-flight-model/{flightNumber}/{model}/{capacity} — update aircraft
- Admin & reporting
    - GET /api/admin/users-with-roles — (Admin) list users + roles
    - GET /api/admin/get-flight-manifest/{flightNumber} — (FlightManager) export manifest (CSV option)

Data model (summary)
- AppUser — Identity user extended (FullName, DOB, City, Country, Address, CreditCardNumber*, PointsAvailable, PointsUsed, Credit, Tickets[])
- Flight — FlightNumber, Origin, Destination, LeaveTime, ArriveTime, TravelDistance, TravelDuration, Model, Capacity, Occupied
- Ticket — Flights[], Payment, Type (one-way/round-trip), Amount, Points, Status (check-in/canceled/complete)
- City — Name, State, Airport, Latitude, Longitude
- Payment — Method (Cash/Credit), PayDate, Amount, CreditCardNumber*

Important business rules (short)
- Bookings allowed up to 6 months in advance; no past-date bookings.
- Round-trip return date must be after departure date.
- Cancellation allowed only if now + 1 hour < departure time.
- Check-in allowed within 24 hours before departure.
- Loyalty points: 10 points per $1 spent; redemption: 10 points = $1 (see requirement doc for edge cases).

Use cases (mapped to requirements)
- Book ticket (Customer): select origin/destination, date(s), system proposes flight path, calculates price and points, completes payment and ticket creation.
- Manage flights (LoadEngineer/FlightManager): add/edit/delete flights, assign plane models according to distance.
- Financial reporting (Accountant): export flight income, capacity reports, and company income summaries.
- Admin user management (Admin): create roles, seed users, view role assignments.

Testing & acceptance (summary from Test Plan)
- Test artifacts: `Knowledge_Base/Extra/Air3550 Test Plan.xlsx` (contains test cases covering: auth flows, booking flows, cancellation/check-in windows, flight management, seeding, and reporting).
- Recommended smoke tests:
    - Authentication: register/login + token validation.
    - Booking flow: search→book→verify payment & points credited.
    - Cancellation/check-in edge cases: try cancel within 1 hour (expect failure) and outside window (expect success).
    - Flight manifest export: verify CSV content and counts.

Deployment & run (developer notes)
- Local dev: run API (Visual Studio / dotnet run) with SQLite; run Angular client (`npm install` then `ng serve`). Seed data runs on startup.
- Environment variables: JWT signing key, connection strings. Production should use a managed SQL server and secure the JWT key and secrets.
- Build: `dotnet publish` for API; Angular `ng build --prod` for frontend.

Security & privacy notes
- Mask or encrypt credit card information in stored artifacts; do not include raw cards in archival evidence.
- Use HTTPS in production and secure JWT signing keys. Consider token lifetime and refresh strategy for long sessions.

Artifacts & evidence to collect (recommended)
- `Knowledge_Base/Extra/Air3550 Design Document/Air3550 Design Document.md` (diagrams + architecture)
- `Knowledge_Base/Extra/Air3550 Project Requirement/Air3550 Project Requirement.md` (use cases + acceptance)
- `Knowledge_Base/Extra/Air3550 Test Plan.xlsx` (test cases)
- Seed data: `Knowledge_Base/Extra/Air3550/Air3550/API/Data/UserSeedData.json`
- Demo: short screencast showing booking → payment → manifest export

Suggested next steps (pick one)
1. Create a 1‑page technical README with commands to run the full stack locally (I can draft this now).
2. Convert the Test Plan spreadsheet into runnable unit/integration tests (xunit + Playwright) and add a small CI task.
3. Produce 3 resume bullets derived from this project (impact + technologies).

RAG metadata (JSON)
```json
{
    "id": "project-air3550",
    "title": "Air3550 Flight Management System",
    "tags": ["project","airline","aspnet","angular","booking-system"],
    "short_summary": "A full‑stack flight reservation and operations system (ASP.NET Core + Angular) built as a senior project. Includes booking, flight management, payments, and admin workflows.",
    "last_updated": "2025-10-10",
    "source_paths": ["Extra/Air3550 Design Document","Extra/Air3550 Project Requirement","Extra/Air3550 Test Plan.xlsx","Extra/Air3550/Air3550"]
}
```

If you want, I can start on any of the suggested next steps (README, test conversion, or resume bullets). Which should I do first?
- **Cancellation Window**: Tickets can only be cancelled 1+ hours before departure

- **Check-in Window**: Flights can be checked in up to 24 hours before departure



### Flight Operations Logic
