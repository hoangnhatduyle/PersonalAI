# Cadence — Personal Assistant App

**Tags:** cadence, personal-assistant, nextjs, react, supabase, openai, voice, pwa, rag, productivity
**Last Updated:** 2026-11-12

## Summary
Cadence is a personal productivity and assistant application I built to manage courses, deadlines, tasks, notes, reminders, and appointments in one place, with a voice-driven assistant and cited knowledge lookup. It is a separate project from this portfolio chatbot.

## Key capabilities
- **Planning and tracking:** courses, deadlines, tasks with estimates and progress tracking, checklists, labels, notes, and a calendar view.
- **"Up Next" Gantt view:** a timeline of upcoming work with start dates and a custom hover panel.
- **Voice assistant:** a hands-free "driving" mode with push-to-talk and realtime voice calls, including a usage budget and an automated evaluation suite for both voice paths.
- **Knowledge library:** documents, web pages, and media can be ingested, chunked, embedded, and searched, with answers that cite their sources. Ingestion includes upload validation, SSRF protection, and rate limiting.
- **Weekly review:** an AI-generated narrative summary of the week's progress.
- **Reminders and notifications:** scheduled reminders, push notifications, and email triage.
- **Installable PWA:** works as an installable app with a service worker.

## Technology
- **Frontend and server:** Next.js (App Router), React, TypeScript.
- **Backend services:** Supabase (Postgres, authentication, row-level data access).
- **AI:** OpenAI APIs for embeddings, retrieval-augmented answers, voice, and summaries.
- **Quality:** Vitest unit tests, Playwright end-to-end tests, and a spec-and-test-first development workflow.

## Why it matters
Cadence shows end-to-end product engineering: schema design, secure API routes, retrieval-augmented generation with citations, realtime voice interaction, background jobs, and automated evaluation of AI behavior.
