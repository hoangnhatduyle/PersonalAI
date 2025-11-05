## myHome (myhome_drexel) — RAG-friendly Project Page

**Tags:** myhome, property-management, aspnet, angular, cloudinary, onesignal
**Last Updated:** 2025-10-10

Short summary
- Full‑stack property and household management application. Backend is ASP.NET Core (API/) with EF Core Identity and repository/unit‑of‑work patterns. Frontend is an Angular SPA (client/) and, in production, built assets are served from `API/wwwroot`.

Primary features
- User authentication & role management (Admin / Member).
- Member profiles, photo uploads with Cloudinary integration, and approval workflow.
- Bills & payments: create/split bills, monthly tracking, record payments.
- Diary, internal messaging, and feedback features for community coordination.
- Financial reports and charts (CanvasJS) for household accounting.
- Email notifications (IEmailService) and OneSignal web push notifications.

Repository layout (key folders)
- `API/` — ASP.NET Core backend (Program.cs, controllers, DataContext, repositories, UnitOfWork, Services).
- `client/` — Angular frontend source (components, services, directives).
- `API/wwwroot/` — production-ready built frontend static assets.

Why this doc
- Provide a compact, RAG‑ready summary that agents can use to answer questions about API endpoints, data model, deployment steps, and evidence to support portfolio or application use cases.

Architecture & dataflow (high level)
1. User interacts with Angular UI (client).
2. Angular issues HTTP requests to API endpoints (e.g., `/api/bills`, `/api/payments`, `/api/users`).
3. Controllers map incoming DTOs to entities and use UnitOfWork / repositories to persist/read via EF Core (DataContext).
4. Media uploads are proxied to Cloudinary; notifications are sent via OneSignal and email services.
5. Built frontend is served by the API in production (static assets under `wwwroot`).

Technology stack (concise)
- Backend: ASP.NET Core, Entity Framework Core, SQLite (or configured provider), Identity for auth.
- Frontend: Angular (v14), Angular Material / ngx‑bootstrap, ngx‑toastr, CanvasJS charts.
- Integrations: Cloudinary (media), OneSignal (push), Email service (IEmailService), Docker for containerization.

API surface (common endpoints)
- Auth & users: `/api/account/*`, `/api/users/*` — register, login, profile, token handling.
- Bills & payments: `/api/bills/*`, `/api/payments/*` — create bills, split, mark payments, report.
- Photos & docs: `/api/photos/*` — upload, approve, list (Cloudinary-backed).
- Messaging / diary: `/api/diary/*`, `/api/messages/*` — create/view notes and messages.

Data model (high level)
- AppUser (Identity extension): FullName, DOB, City, Contact, Credit/Cards*, Points, Roles, Tickets/Payments (if applicable).
- Bill: Owner, participants, amount, due date, status, payment records.
- Payment: BillId, Payer, Amount, Method, Date.
- Photo/Document: Owner, CloudinaryPublicId, Url, ApprovalStatus, Metadata.

Contracts & error handling
- Inputs: JSON DTOs (login/register, bill create, photo metadata). Auth via JWT in Authorization header.
- Outputs: JSON responses with DTOs and HTTP status codes; errors standardized via `Errors/ApiException` and `ExceptionMiddleware`.

Dev & deployment notes
- Local dev: run API with Visual Studio / `dotnet run`, run Angular client with `npm install` + `ng serve` (or use built assets in `wwwroot`).
- Production: build Angular (`ng build --prod`), copy into `API/wwwroot`, `dotnet publish`, and run container (Dockerfile and `deploy_command.txt` present).
- Config: Cloudinary and OneSignal keys, SMTP settings, and DB connection strings should be supplied as environment variables or secure appsettings files.

Evidence & artifacts to collect
- `Data/UserSeedData.json`, `Data/BillSeedData.json`, and `Seed.cs` — seeded demo data for testing.
- `API/Program.cs` and `API/Data/DataContext.cs` — runtime configuration and DB wiring.
- Angular components: `client/src/app/` (notable components: HasRoleDirective, ResidentSumComponent, myhome-document components).
- Deployment artifacts: Dockerfile, `deploy_command.txt`, built files under `API/wwwroot/`.

Risks & edge cases
- Authorization mismatch: ensure client role checks (HasRoleDirective) match server‑side role enforcement.
- Large uploads: set server limits and Cloudinary policies for reliable uploads and error handling.
- Service worker / OneSignal paths: ensure correct registration path when serving from `wwwroot`.
- License & compliance: verify CanvasJS license for distribution.

RAG-friendly metadata (JSON)
```json
{
	"id": "project-myhome",
	"title": "myHome (myhome_drexel) — Property Management App",
	"tags": ["project","myhome","aspnet","angular","cloudinary","onesignal"],
	"short_summary": "Full‑stack property/household management app (ASP.NET Core + Angular) with photo approvals, bill splitting, notifications, and financial reporting.",
	"last_updated": "2025-10-10",
	"source_paths": ["API/","client/","API/wwwroot/"]
}
```