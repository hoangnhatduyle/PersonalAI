"use client";

import { useEffect, useState } from "react";

interface Props {
  topic: string;
}

function Badge({ label, color = "zinc" }: { label: string; color?: string }) {
  const colorMap: Record<string, string> = {
    zinc:   "bg-zinc-700 text-zinc-300",
    indigo: "bg-indigo-900/60 text-indigo-300 border border-indigo-700/40",
    blue:   "bg-blue-900/60 text-blue-300 border border-blue-700/40",
    violet: "bg-violet-900/60 text-violet-300 border border-violet-700/40",
    emerald:"bg-emerald-900/60 text-emerald-300 border border-emerald-700/40",
    amber:  "bg-amber-900/60 text-amber-300 border border-amber-700/40",
    rose:   "bg-rose-900/60 text-rose-300 border border-rose-700/40",
    teal:   "bg-teal-900/60 text-teal-300 border border-teal-700/40",
  };
  return (
    <span className={`inline-block text-xs px-2 py-0.5 rounded-full font-medium ${colorMap[color] ?? colorMap.zinc}`}>
      {label}
    </span>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mt-4">
      <p className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider mb-2">{title}</p>
      {children}
    </div>
  );
}

function Divider() {
  return <div className="my-4 border-t border-zinc-800" />;
}

// ── Card content per topic ─────────────────────────────

function GeneralCard() {
  return (
    <>
      <Section title="Quick Stats">
        <div className="grid grid-cols-2 gap-2">
          {[
            ["14+ mo", "at First Solar"],
            ["8+", "projects built"],
            ["Full-Stack", "+ AI/ML"],
            ["Toledo, OH", "📍"],
          ].map(([val, label]) => (
            <div key={val} className="bg-zinc-800/60 rounded-lg p-2 text-center">
              <p className="text-sm font-semibold text-white">{val}</p>
              <p className="text-[10px] text-zinc-500">{label}</p>
            </div>
          ))}
        </div>
      </Section>
      <Section title="Top Skills">
        <div className="flex flex-wrap gap-1.5">
          {["Python","C# / .NET","Next.js","React","PostgreSQL","Docker","LangChain","OpenAI"].map(s => (
            <Badge key={s} label={s} color="indigo" />
          ))}
        </div>
      </Section>
      <Section title="Links">
        <div className="flex flex-col gap-1.5">
          <a href="https://github.com/hoangnhatduyle" target="_blank" rel="noreferrer"
            className="flex items-center gap-2 text-xs text-zinc-400 hover:text-white transition-colors">
            <span className="w-5 h-5 rounded bg-zinc-800 flex items-center justify-center text-[10px]">GH</span>
            github.com/hoangnhatduyle
          </a>
          <a href="https://linkedin.com/in/hoangnhatduyle" target="_blank" rel="noreferrer"
            className="flex items-center gap-2 text-xs text-zinc-400 hover:text-white transition-colors">
            <span className="w-5 h-5 rounded bg-zinc-800 flex items-center justify-center text-[10px]">in</span>
            linkedin.com/in/hoangnhatduyle
          </a>
        </div>
      </Section>
    </>
  );
}

function WorkCard() {
  return (
    <>
      <Section title="Current Role">
        <div className="bg-zinc-800/60 rounded-lg p-3">
          <p className="text-sm font-semibold text-white">First Solar</p>
          <p className="text-xs text-zinc-400">MES Software Engineer</p>
          <p className="text-[10px] text-zinc-500 mt-0.5">Mar 2024 – Present · Toledo, OH</p>
        </div>
      </Section>
      <Section title="Active Projects">
        <ul className="space-y-1.5 text-xs text-zinc-400">
          {[
            "Floor Incident Dashboard (Next.js + PG)",
            "Image Data Mart → AI Auto Reply",
            "PLC-MQTT → Palantir Foundry pipeline",
            "ESD & JB1 system onboarding",
          ].map(p => (
            <li key={p} className="flex gap-2"><span className="text-indigo-400 mt-0.5">▸</span>{p}</li>
          ))}
        </ul>
      </Section>
      <Section title="Stack at Work">
        <div className="flex flex-wrap gap-1.5">
          {[".NET 10","C#","Next.js","PostgreSQL","Docker","Kubernetes","Airflow","MQTT"].map(s => (
            <Badge key={s} label={s} color="blue" />
          ))}
        </div>
      </Section>
      <Divider />
      <div className="flex items-center gap-2 text-xs text-emerald-400">
        <span className="w-2 h-2 rounded-full bg-emerald-400" />
        Annual review: Rated <span className="font-semibold ml-0.5">Green ✓</span>
      </div>
    </>
  );
}

function ProjectsCard() {
  const projects = [
    {
      name: "Multi-Agent Trading Platform",
      desc: "5 AI traders + auditor agent, genetic optimizer, 233+ tests",
      stack: ["Python","FastAPI","PostgreSQL","Redis","Next.js"],
      url: "https://github.com/hoangnhatduyle",
      color: "violet" as const,
      badge: "🔒 private",
    },
    {
      name: "Personal AI",
      desc: "This chatbot — LangChain RAG + OpenAI streaming + Next.js",
      stack: ["LangChain","ChromaDB","FastAPI","Next.js"],
      url: "https://github.com/hoangnhatduyle",
      color: "indigo" as const,
      badge: "⭐ you're here",
    },
    {
      name: "Inventory Tracking App",
      desc: "Mobile-first inventory management with Angular + Capacitor",
      stack: ["Angular","TypeScript","Ionic","Capacitor"],
      url: "https://github.com/hoangnhatduyle/Inventory_Tracking_App",
      color: "blue" as const,
      badge: null,
    },
    {
      name: "DSUT Club Website",
      desc: "Data Science UToledo student organization site",
      stack: ["HTML","CSS","JavaScript"],
      url: "https://github.com/hoangnhatduyle/DSUT",
      color: "teal" as const,
      badge: null,
    },
    {
      name: "UT Sesquicentennial",
      desc: "University of Toledo 150th anniversary website",
      stack: ["Next.js","Tailwind","JavaScript"],
      url: "https://github.com/hoangnhatduyle/UT_Sesquicentennial",
      color: "emerald" as const,
      badge: null,
    },
  ];

  return (
    <div className="space-y-3 mt-1">
      {projects.map(p => (
        <div key={p.name} className="bg-zinc-800/60 rounded-lg p-3 border border-zinc-700/50 hover:border-zinc-600 transition-colors">
          <div className="flex items-start justify-between gap-1">
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-white leading-snug">{p.name}</p>
              {p.badge && (
                <span className="text-[10px] text-zinc-500">{p.badge}</span>
              )}
            </div>
            <a href={p.url} target="_blank" rel="noreferrer"
               className="text-[10px] text-zinc-500 hover:text-indigo-400 transition-colors flex-shrink-0 mt-0.5 ml-1">
              ↗
            </a>
          </div>
          <p className="text-[11px] text-zinc-500 mt-1 mb-2">{p.desc}</p>
          <div className="flex flex-wrap gap-1">
            {p.stack.map(s => <Badge key={s} label={s} color={p.color} />)}
          </div>
        </div>
      ))}
      <a href="https://github.com/hoangnhatduyle" target="_blank" rel="noreferrer"
         className="flex items-center justify-center gap-1.5 text-[11px] text-zinc-500 hover:text-indigo-400 transition-colors py-1">
        View all on GitHub ↗
      </a>
    </div>
  );
}

function EducationCard() {
  return (
    <>
      <Section title="Degree">
        <div className="bg-zinc-800/60 rounded-lg p-3">
          <p className="text-sm font-semibold text-white">B.S. Computer Science</p>
          <p className="text-xs text-zinc-400">University of Toledo</p>
          <p className="text-[10px] text-zinc-500 mt-0.5">Class of 2022 · Ohio, USA</p>
        </div>
      </Section>
      <Section title="Certifications">
        <ul className="space-y-1.5 text-xs">
          {[
            { label: "LLM Engineering", done: true },
            { label: "Agentic AI", done: true },
            { label: "ML Specialization", done: false, note: "in progress" },
            { label: "Docker & Kubernetes", done: false, note: "59%" },
          ].map(c => (
            <li key={c.label} className="flex items-center gap-2">
              <span className={c.done ? "text-emerald-400" : "text-amber-400"}>{c.done ? "✓" : "◐"}</span>
              <span className={c.done ? "text-zinc-300" : "text-zinc-500"}>{c.label}</span>
              {c.note && <span className="text-[10px] text-zinc-600 ml-auto">{c.note}</span>}
            </li>
          ))}
        </ul>
      </Section>
      <Section title="Graduate School Applications">
        <div className="flex flex-wrap gap-1.5">
          {["UToledo","UCincinnati","Miami Univ","Kent State"].map(s => (
            <Badge key={s} label={s} color="emerald" />
          ))}
        </div>
        <p className="text-[10px] text-zinc-500 mt-2">MS CS/CSE · Target: Fall 2026</p>
      </Section>
    </>
  );
}

function SkillsCard() {
  const groups = [
    { label: "Backend",       color: "blue"   as const, skills: [".NET / C#","Python","FastAPI","Node.js","Laravel"] },
    { label: "Frontend",      color: "violet" as const, skills: ["Next.js","React","TypeScript","Tailwind"] },
    { label: "AI / ML",       color: "indigo" as const, skills: ["LangChain","OpenAI","HuggingFace","RAG","Agents"] },
    { label: "Infrastructure",color: "amber"  as const, skills: ["Docker","Kubernetes","Azure DevOps","Airflow"] },
    { label: "Data",          color: "teal"   as const, skills: ["PostgreSQL","SQL Server","ChromaDB","MQTT","Palantir"] },
  ];
  return (
    <div className="mt-1 space-y-3">
      {groups.map(g => (
        <div key={g.label}>
          <p className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider mb-1.5">{g.label}</p>
          <div className="flex flex-wrap gap-1.5">
            {g.skills.map(s => <Badge key={s} label={s} color={g.color} />)}
          </div>
        </div>
      ))}
    </div>
  );
}

function CareerCard() {
  return (
    <>
      <Section title="Visa Status">
        <div className="bg-zinc-800/60 rounded-lg p-3 space-y-1.5">
          <div className="flex justify-between text-xs">
            <span className="text-zinc-400">F-1 OPT STEM</span>
            <span className="text-amber-400 font-medium">ends May 2026</span>
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-zinc-400">H1B FY2027</span>
            <span className="text-rose-400">Not selected</span>
          </div>
        </div>
      </Section>
      <Section title="Next Steps">
        <ul className="space-y-1.5 text-xs text-zinc-400">
          {[
            "Return to school — Fall 2026",
            "MS CS/CSE applications pending",
            "Long-term: Senior/Staff Engineer",
            "Focus: AI/ML systems & architecture",
          ].map(g => (
            <li key={g} className="flex gap-2"><span className="text-indigo-400 mt-0.5">▸</span>{g}</li>
          ))}
        </ul>
      </Section>
      <Section title="Applications Under Review">
        <div className="flex flex-wrap gap-1.5">
          {["UToledo","UCincinnati"].map(s => (
            <Badge key={s} label={s} color="rose" />
          ))}
        </div>
        <div className="flex flex-wrap gap-1.5 mt-1.5">
          {["Miami Univ","Kent State"].map(s => (
            <Badge key={s} label={s} color="zinc" />
          ))}
        </div>
      </Section>
    </>
  );
}

function ContactCard() {
  return (
    <>
      <Section title="Find Me Online">
        <div className="space-y-2">
          <a href="https://github.com/hoangnhatduyle" target="_blank" rel="noreferrer"
            className="flex items-center gap-3 p-2.5 rounded-lg bg-zinc-800/60 hover:bg-zinc-800 transition-colors group">
            <span className="w-7 h-7 rounded-md bg-zinc-700 flex items-center justify-center text-xs font-bold text-white">GH</span>
            <div>
              <p className="text-xs font-medium text-zinc-300 group-hover:text-white transition-colors">GitHub</p>
              <p className="text-[10px] text-zinc-500">hoangnhatduyle</p>
            </div>
          </a>
          <a href="https://linkedin.com/in/hoangnhatduyle" target="_blank" rel="noreferrer"
            className="flex items-center gap-3 p-2.5 rounded-lg bg-zinc-800/60 hover:bg-zinc-800 transition-colors group">
            <span className="w-7 h-7 rounded-md bg-blue-700 flex items-center justify-center text-xs font-bold text-white">in</span>
            <div>
              <p className="text-xs font-medium text-zinc-300 group-hover:text-white transition-colors">LinkedIn</p>
              <p className="text-[10px] text-zinc-500">hoangnhatduyle</p>
            </div>
          </a>
        </div>
      </Section>
      <Divider />
      <div className="bg-indigo-900/30 border border-indigo-700/40 rounded-lg p-3 text-center">
        <p className="text-xs text-indigo-300 font-medium mb-1">Want to connect?</p>
        <p className="text-[11px] text-zinc-500">
          Type <span className="text-indigo-400 font-mono">&ldquo;I&apos;d like to reach out&rdquo;</span> in the chat to leave your email!
        </p>
      </div>
    </>
  );
}

// ── Topic config ────────────────────────────────────────

const TOPICS: Record<string, { icon: string; title: string; subtitle: string; card: React.ReactNode }> = {
  general:   { icon: "👋", title: "Hoang Nhat Duy Le", subtitle: "MES Software Engineer @ First Solar", card: <GeneralCard /> },
  work:      { icon: "💼", title: "Work Experience",   subtitle: "First Solar · Mar 2024–Present",      card: <WorkCard /> },
  projects:  { icon: "🚀", title: "Projects",          subtitle: "8+ shipped projects",                 card: <ProjectsCard /> },
  education: { icon: "🎓", title: "Education",         subtitle: "B.S. CS · Univ. of Toledo, 2022",     card: <EducationCard /> },
  skills:    { icon: "⚙️", title: "Tech Stack",         subtitle: "Full-Stack + AI/ML + Infra",          card: <SkillsCard /> },
  career:    { icon: "🎯", title: "Career Goals",       subtitle: "F-1 OPT → Grad School Fall 2026",     card: <CareerCard /> },
  contact:   { icon: "📫", title: "Get in Touch",       subtitle: "GitHub · LinkedIn · Email",           card: <ContactCard /> },
};

export default function ProfileCard({ topic }: Props) {
  const [displayed, setDisplayed] = useState(topic);
  const [fading, setFading] = useState(false);

  useEffect(() => {
    if (topic === displayed) return;
    setFading(true);
    const t = setTimeout(() => {
      setDisplayed(topic);
      setFading(false);
    }, 180);
    return () => clearTimeout(t);
  }, [topic, displayed]);

  const cfg = TOPICS[displayed] ?? TOPICS.general;

  return (
    <div className={`transition-opacity duration-200 ${fading ? "opacity-0" : "opacity-100"} h-full flex flex-col`}>
      {/* Card header */}
      <div className="p-4 border-b border-zinc-800 flex-shrink-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-lg">{cfg.icon}</span>
          <h2 className="text-sm font-semibold text-white leading-tight">{cfg.title}</h2>
        </div>
        <p className="text-[11px] text-zinc-500">{cfg.subtitle}</p>
      </div>

      {/* Card body */}
      <div className="flex-1 overflow-y-auto p-4">
        {cfg.card}
      </div>
    </div>
  );
}
