# Bone Conduction Railing — Senior Design Project

**Tags:** bone-conduction, senior-design, acoustics, embedded, arduino, project
**Last Updated:** 2025-10-09

Short summary
- A senior design prototype that transmits curated campus audio through users' forearm bones using a railing-mounted bone‑conduction system. The installation was developed to create an interactive, private listening experience (audible only to users contacting the railing) inspired by the "Touched Echo" installation in Dresden.
- Primary outcomes: a working prototype (aluminum railing configuration), an Arduino‑based audio playback system that loops audio from an SD card, transducer/amplifier integration, and audio quality testing that guided material choices and speaker selection.

Official link & provenance
- University event listing: https://news.utoledo.edu/index.php/04_26_2023/engineering-students-to-present-senior-design-projects-april-28
- Primary documentation: `Knowledge_Base/Extra/Final Report Assessment.md` (full project report, design diagrams, photos and test results).
- Source code: `Knowledge_Base/Extra/BareMinimumWithDebug_Loop.ino` (Arduino playback loop used for SD‑card audio playback).

Problem statement and motivation
- Problem: provide an engaging, low‑maintenance, privacy‑preserving audio installation for campus visitors that uses bone conduction so only users touching the railing hear content; enable public engagement with campus history while minimizing acoustic leakage.
- Motivation: increase accessibility and create an experiential memorial for campus events; the project also explores how bone conduction can improve audio privacy and offer new public-interaction modalities.

Design goals & requirements
- Audible to users in contact with railing; not audible to passersby (minimize leakage).
- Low cost and reproducible at prototype scale.
- Continuous loop playback with minimal maintenance (power only) and easy content updates via SD card.
- Safe for public use and usable by pedestrians of varying heights.

High-level design
- Mechanical: railing material and mounting — prototypes compared steel vs. aluminum; aluminum selected for final design due to lower acoustic leakage despite slightly reduced conduction intensity.
- Electrical / acoustic: piezoelectric transducers (bone conduction transducers), amplifier and filters, Arduino + SD card for audio storage/playback, wiring to speakers/transducers embedded in the railing.
- Software: Arduino-based loop player (see `BareMinimumWithDebug_Loop.ino`) that reads audio files from SD and plays them in sequence; designed to run continuously and automatically proceed to the next file when playback completes.

Technical highlights
- Material tradeoff: testing showed the aluminum railing configuration reduced air leakage and produced net gain in perceived privacy (measured leakage vs. conduction intensity around key hearing frequencies ~1–3 kHz).
- Audio pipeline: WAV audio files converted and stored on SD; Arduino uses SimpleSDAudio library to stream audio to the amplifier and transducers.
- Observability & testing: contact microphones and ambient mics were used with Room Enhancement Wizard to measure conduction vs. leakage; results informed speaker selection and enclosure tuning.

BareMinimumWithDebug_Loop.ino — code overview
- Location: `Knowledge_Base/Extra/BareMinimumWithDebug_Loop.ino`.
- Purpose: minimal SD‑card audio player built on the SimpleSDAudio library. Plays sequential .AFM (audio) files from SD card in a loop, prints debug information over Serial, and attempts to recover if a file is missing.
- Key behavior:
	- Initializes SD and audio library in `setup()`; attempts to set and play `1.AFM` initially.
	- `loop()` checks `SdPlay.isPlaying()` and when playback finishes, increments `currentFilePlaying` and sets the next file to play; contains recovery logic via `setNextFile()` to skip missing files.
	- Uses Serial debug prints for initialization errors and playback status — useful during commissioning and field troubleshooting.
- How it maps to project goals: enables low‑maintenance audio looping with easy content updates (copy new files to SD), and the debug output supports on‑site troubleshooting during hypercare/testing.

Bill of materials (summary from report)
- Arduino board (ATmega328/ATmega2560 family) and SD‑card shield/module.
- Piezoelectric transducers (bone conduction transducers).
- Amplifier (analogue) and filters.
- SD card with WAV/AFM audio files; wiring, connectors, enclosure for electronics.
- Railing material: tested 1018 steel and aluminum bar options; final prototype used aluminum with powder coating for indoor installation.

Testing approach & results (summary)
- Unit tests: transducer system, amplifier/filter system, and Arduino SD playback tested individually before integration.
- Audio quality testing: used contact mic (for conduction) and ambient sensitive mic (for leakage) to compute conduction:leakage ratios at frequencies of interest; iterated railing material and speaker configurations to minimize leakage.
- Result summary: aluminum railing with two‑speaker system (low‑freq + high‑freq coverage) produced best tradeoff — net gain (~10 dB advantage in relevant range) versus the original steel prototype.

Ethics, standards, and IP
- The project considered IEC 60268‑3 (amplifier characteristics) and ANSI S3.13 (mechanical coupler / bone vibrator measurement) for component selection and testing.
- Patent landscape: project reviewed relevant patents (bone conduction headphones and privacy-oriented transducers) to ensure design awareness of existing IP.

Evidence & artifacts to attach (recommended)
- Final Report: `Knowledge_Base/Extra/Final Report Assessment.md` (design diagrams and photos referenced throughout the report).
- Source: `Knowledge_Base/Extra/BareMinimumWithDebug_Loop.ino` (playback code).
- Images referenced in the report (Extra folder: image.png, image-1.png, … image-9.png) — copy high‑resolution originals into a project `evidence/` folder.
- Measurements: contact mic/ambient mic CSVs or plots (conduction vs. leakage at test frequencies).
- Demo video or short GIF showing someone using the railing and hearing audio only when touching it.
 - Project poster: `Knowledge_Base/Extra/Poster.pdf` (conference/poster presentation materials).

Suggested next steps
1) Create a one‑page case study (architecture diagram, BOM, test graphs, and 3 evidence files) suitable for portfolio and applications — I can draft the first pass.
2) Prepare a short demo video (30–60s) showing the privacy behavior (touch vs. no-touch) for portfolio embedding.
3) Clean up the Arduino code repo: add a README describing wiring, expected SD file names/format (.AFM or WAV conversion), and troubleshooting steps (Serial debug messages). Consider changing filenames to zero‑padded scheme (e.g., 01.AFM) for easier ordering.
4) Add annotated measurement CSVs and test scripts to `Knowledge_Base/Projects/project_3/evidence/` for reproducibility.

RAG-friendly JSON metadata (for embedding ingestion)
```json
{
	"id": "project-bone-conduction-railing",
	"title": "Bone Conduction Railing — Senior Design",
	"tags": ["project","bone-conduction","embedded","arduino","acoustics"],
	"short_summary": "Prototype railing that transmits audio via bone conduction when users touch the rail; Arduino SD playback, transducer/amplifier integration, and measured conduction vs. leakage tests.",
	"last_updated": "2025-10-09",
	"source_files": ["Extra/Final Report Assessment.md","Extra/BareMinimumWithDebug_Loop.ino"]
}
```

Credits
- Project sponsors: College of Arts and Letters and UT Green Fund (per Final Report).
- Team: senior design students (mechanical group + EECS/software group) — see Final Report for full contributor list.

If you want, I can now:
- Draft the one‑page case study with embedded images and an architecture diagram.  
- Create the `Projects/project_3/evidence/` folder and copy selected images and the Arduino file into it (I will not overwrite originals unless you say so).  
- Generate a README for the Arduino code explaining how to produce the `.AFM` files, wiring, and basic commissioning steps.

Which of these should I start?  