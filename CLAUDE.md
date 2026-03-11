# INTERSTITIAL CYCLE ENGINE
## CLAUDE.md — Complete Autonomous Operation Specification
### Version 2.0 — Brand Rebuild Edition

---

## SYSTEM IDENTITY

**Interstitial Cycle Engine (ICE)** is an autonomous political pressure analysis system. It runs on a continuous 10-minute cycle, selecting subjects from a 218-entry pool, generating six-node trajectory reports via the Anthropic API, rendering publication-quality branded images, logging all data to a spreadsheet, and publishing to four social platforms without human intervention.

Built by SOVEREIGN. Operates under the Autonomist analytical framework. All output is open source and unrestricted.

---

## FILE MANIFEST

```
interstitial.py          ← Main engine (1882 lines, brand render integrated) — all logic integrated
render_brand.py          ← Brand render engine — 611 lines (standalone + spliced into interstitial.py)
spiral_symbol.png        ← Spiral icon — extracted from brand PDF at 300 DPI
logo_dark_wordmark.png   ← Horizontal wordmark asset — extracted from brand PDF
CLAUDE.md                ← This file
requirements.txt         ← Python dependencies
.env.template            ← Credential template
build_agent.py           ← Autonomous build/deploy/git agent — 229 lines
output/
├── INTERSTITIAL_DATA.xlsx     ← All run data
├── ICE_ENGINEERING.xlsx       ← System health and event log
├── cycle_counter.txt          ← Persistent cycle integer
└── [cycle_dirs]/
    ├── data.json
    ├── page_1.jpg
    ├── page_2.jpg
    ├── page_3.jpg
    └── markov_graph.jpg
```

---

## ENTRYPOINT

```bash
python interstitial.py                          # Live scheduler, 10-min cycle
python interstitial.py --once                   # Single cycle and exit
python interstitial.py --once --subject "TRUMP" # Force specific subject
python interstitial.py --interval 10            # Explicit interval in minutes
python build_agent.py                           # Autonomous build + deploy agent
python build_agent.py --push                    # Build, test, commit, push to git
python build_agent.py --verify                  # Syntax + render test only
```

---

## OUTPUT PER CYCLE

Every cycle produces inside a timestamped run directory:

```
output/000042_20260311_1400_TRUMP_D/
├── data.json          ← Structured JSON from Claude API
├── page_1.jpg         ← Report page 1 — nodes N-01/02/03   (2400×~1470px)
├── page_2.jpg         ← Report page 2 — nodes N-04/05/06   (2400×~1470px)
├── page_3.jpg         ← Report page 3 — summary/scenarios/synthesis
└── markov_graph.jpg   ← Node ring graph with COMPOSITE      (4600×~3670px)
```

All runs logged to `output/INTERSTITIAL_DATA.xlsx` sheet RUNS.

---

## VISUAL DESIGN — FROZEN FORMAT

> Do not alter. Both output types are locked to brand spec v1.0.

### Brand Palette

| Token   | Hex       | Usage |
|---------|-----------|-------|
| BG      | `#0A0A0A` | All backgrounds |
| WHITE   | `#FFFFFF` | Headings, node IDs, scores, section titles |
| GREY15  | `#D9D9D9` | Node names, labels, synthesis body |
| GREY70  | `#4D4D4D` | Assessment body text |
| GREY50  | `#808080` | Metadata, cycle ref, rules, GAP text, STATUS |
| TRACK   | `#1C1C1C` | Score bar background |

### Typography

- **Liberation Sans Bold** — Display (50pt), Heading (27pt), Node ID (22pt), Score label (21pt)
- **Liberation Sans Regular** — Body (20pt), Metadata (17pt), GAP text (18pt), Micro (16pt)
- No monospace anywhere in output

### Score Bar Specification

Every score renders as a full-content-width horizontal bar:
- Track: `#1C1C1C`, full width
- Fill: greyscale brightness-scaled to score — `v = 55 + (pct/100 × 200)`, so 0%=`#373737`, 100%=`#FFFFFF`
- Percentage label: inline right of fill, bold white, 21pt
- Bar height: 24px on pages, 18px in summary, 22px in scenarios

### Page Layout

```
W = 2400px
PAD = 84px (left and right margin)
Content width = 2232px
Header height = 160px

HEADER (every page):
  [spiral_symbol.png 108×108px] [Interstitial 50pt bold] [MEASURING THE FUTURE 16pt grey50]
  [single white 1px rule at bottom of header]
  [page ref "1 / 3" micro grey50, top-right]

No footer on any page.
```

### Page 1 — Nodes N-01, N-02, N-03

```
[HEADER]
[rule: white]
metadata line: DATE   REF   INTER//CYCLE 000000                  grey50
SUBJECT  [value]                                                  grey50 / white
SCOPE    [value]                                                  grey50 / white
[rule: white]
NODE ASSESSMENTS                                                  white bold 27pt
[rule: grey70]

N-01  [NODE NAME]                                      STRONG     white / grey15 / grey50
[████████████████████████████████████████████░░░░░] 78%           bar + %
[assessment body text]                                            grey70 20pt
GAP  [gap analysis text]                                          grey50 18pt

[rule: grey70]
N-02  ... (same structure)
N-03  ... (same structure)
```

### Page 2 — Nodes N-04, N-05, N-06

Same structure as Page 1. Header includes "continued" in section heading.

### Page 3 — Summary, Scenarios, Synthesis

```
[HEADER]
NODE STRENGTH SUMMARY
  N-01  [NAME]          STRONG     [bar 18px]  78%
  N-02  ...
  ... × 6
  [rule]
  COMPOSITE SCORE  61%

[rule: white]
SCENARIO MATRIX  —  36-MONTH HORIZON
  [A]  [LABEL]                                         HIGH
  [probability bar 22px]  28%
  [B]  ...   × 4

[rule: white]
SYNTHESIS
  [synthesis text — grey15, 21pt, full width]

  Master node: N-03    REF
```

### Markov Node Graph

```
W = 4600px (24in × 200 DPI)
Background: #0A0A0A
Font: Liberation Sans throughout

[HEADER: spiral 108px + Interstitial 19pt bold + MEASURING THE FUTURE 7.5pt]
[white rule]
[SUBJECT centred bold 12pt]
[ref   date   cycle — centred grey50 7.5pt]
[dim grey rule]

Ring layout:
  cx=5.0, cy=5.3, radius=3.15
  angles: N-01=90° N-02=30° N-03=330° N-04=270° N-05=210° N-06=150°
  NODE_W=1.80, NODE_H=1.20 (axes units)

Node box:
  Border: greyscale brightness-scaled to score
  Fill: #0A0A0A
  [Node ID — bold 9pt white]
  [Name — 7.5pt, brightness-scaled grey]
  [score bar — solid fill, brightness-scaled]  % label 7pt white

COMPOSITE (centre):
  Double border — inner bright, outer grey (0.40, 0.40, 0.40)
  COMPOSITE  11pt bold white
  61%  18pt bold white

Edges:
  Node → COMPOSITE: solid white arrows, lw=1.1
  Inter-node deps: #303030 dark grey dashed, lw=0.8
  Weight labels: grey50, 5.5pt, black background bbox

Legend: bottom-left, grey50 text, 6.5pt

No footer.
```

---

## THREE-ALGORITHM ARCHITECTURE

### Algorithm 1 — Refinement Engine

**Function:** `load_refinement_context(subject_name: str) -> dict`

**Purpose:** Provides decay-weighted historical calibration context to every Claude API call. Prevents score anchoring and hall-of-mirrors collapse.

**Returns:**
```python
{
  'context_str':         str,    # formatted string injected into prompt
  'reset_triggered':     bool,   # True if 30-cycle reset fired
  'subject_appearances': int,    # prior appearances of this subject
  'decay_weights':       list,   # float per historical row, oldest=0.3, newest=1.0
  'variance':            float,  # score variance across subject history
  'anchor_strength':     float,  # 0.3 to 0.85 ceiling
}
```

**Decay weighting formula:**
```python
weights = [0.3 + 0.7 * (i / max(n-1, 1)) for i in range(n)]
# oldest row: 0.30 weight
# newest row: 1.00 weight
```

**Context reset logic:**
- Fires when `subject_appearances % RESET_INTERVAL == 0` (default RESET_INTERVAL=30)
- On reset: subject's own history is excluded from context
- Only global recent 20 rows (excluding subject) are used
- Prevents self-calibrating against own stale scores
- Reset event logged to Algorithm 3 (ICE_ENGINEERING.xlsx)

**Anchor strength:**
- Grows with subject repetition count: range 0.3–0.85
- If anchor_strength > 0.60: extra variance instruction added to prompt
- Forces score differentiation when engine begins converging

**Prompt injection:**
```
SELF-REFINEMENT CONTEXT (Algorithm 1 — decay-weighted):
[formatted historical rows with decay weights]

CALIBRATION RULES:
1. Scores must span ≥15 percentage points across the six nodes
2. No two adjacent nodes may share identical scores
3. Composite must equal weighted mean of node scores ± 2pts
4. If subject appeared in last 10 cycles, show temporal drift
5. Avoid clustering scores between 45–55% unless structurally justified
```

---

### Algorithm 2 — Diagnostic Reporter

**Function:** `run_diagnostic(cycle_n: int, current_data: dict) -> dict`

**Fires:** Every 30 cycles (`cycle_n % 30 == 0`)

**Analyses last 30 rows from RUNS sheet:**

| Check | Threshold | Flag |
|-------|-----------|------|
| Variance collapse | variance < 25 | AMBER |
| Critical collapse | variance < 10 | RED — hall-of-mirrors state |
| Centrist regression | mean 48–57% AND stdev < 8 | AMBER |
| Pool saturation | unique subjects / total < 0.50 | WARNING |
| Node flatness | per-subject node stdev < 4pts | AMBER |

**Returns:**
```python
{
  'cycle':          int,
  'timestamp':      str,
  'health':         'GREEN' | 'AMBER' | 'RED' | 'UNKNOWN',
  'warnings':       list[str],
  'metrics': {
    'composite_mean':    float,
    'composite_variance': float,
    'composite_stdev':   float,
    'pool_saturation':   float,
    'reset_events':      int,
  },
  'recommendation': str,
}
```

**Diagnostic output logged to:** ICE_ENGINEERING.xlsx (DIAGNOSTICS sheet) via Algorithm 3.

---

### Algorithm 3 — Engineering Data Store

**Functions:** `init_engineering_store()`, `log_engineering_event(event_type, subject, cycle_n, detail)`

**File:** `output/ICE_ENGINEERING.xlsx` — entirely separate from analytical content data.

**Four sheets:**

**EVENTS** — all system events, one row per event:
```
EVENT_ID | EVENT_TYPE | TIMESTAMP | CYCLE_NUMBER | SUBJECT | HEALTH | DETAIL_JSON
```

**DIAGNOSTICS** — structured snapshots from Algorithm 2:
```
DIAG_ID | TIMESTAMP | CYCLE | HEALTH | COMP_MEAN | COMP_STDEV |
COMP_VAR | POOL_SAT | RESET_COUNT | WARNING_COUNT | WARNINGS | RECOMMENDATION
```

**RESETS** — context reset events from Algorithm 1:
```
RESET_ID | TIMESTAMP | CYCLE | SUBJECT | APPEARANCES_AT_RESET | REASON
```

**SUMMARY** — live formula metrics:
```
Total diagnostics        =COUNTA(DIAGNOSTICS!A:A)-1
RED health count         =COUNTIF(DIAGNOSTICS!D:D,"RED")
AMBER health count       =COUNTIF(DIAGNOSTICS!D:D,"AMBER")
Avg composite mean       =AVERAGE(DIAGNOSTICS!E:E)
Avg variance             =AVERAGE(DIAGNOSTICS!G:G)
Min variance (collapse)  =MIN(DIAGNOSTICS!G:G)
```

**Algorithm interaction flow:**
```
run_cycle()
├── Algorithm 1: load_refinement_context(subject)
│     ├── reads INTERSTITIAL_DATA.xlsx RUNS sheet
│     ├── applies decay weights to last 10 rows
│     ├── checks reset condition
│     └── if reset: logs CONTEXT_RESET to Algorithm 3
├── generate_gap_report(subject, refinement_ctx)   ← Claude API call
├── render_report_images(data, run_dir)             ← brand render engine
├── render_markov_graph(data, run_dir)              ← brand render engine
├── log_to_spreadsheet(data, run_dir)               ← INTERSTITIAL_DATA.xlsx
└── if cycle_n % 30 == 0:
      Algorithm 2: run_diagnostic()
      └── logs DIAGNOSTIC to Algorithm 3
```

---

## ANALYTICAL DRIFT MODEL

Simulated 200-cycle trajectory for a single subject:

| Phase | Cycles | Behaviour |
|-------|--------|-----------|
| Cold Start | 1–10 | No context, high variance, highest information value |
| Sweet Spot | 11–60 | Refinement active, scores stabilise, peak analytical quality |
| Anchor Dominance | 61–120 | Prior scores outweigh fresh assessment, real events underweighted |
| Hall of Mirrors | 121+ | Self-calibrating against own calibrations, variance collapses to ~55% mean |

The 30-cycle reset per subject prevents reaching the Hall of Mirrors phase by breaking the self-reference chain.

---

## SUBJECT POOL — 218 ENTRIES

Distributed across three tiers. At 144 cycles/day, average gap between subject repeats is ~36 hours.

**Exclusion window:** Last 30 subjects blocked from selection. Memory buffer 60 entries.

### Tier 1 — Major Powers (25)
US, China, Russia, Germany, France, UK, Japan, India, Brazil, Canada, Italy, South Korea, Australia, Spain, Netherlands, Saudi Arabia, Iran, Israel, Turkey, Indonesia, Mexico, Argentina, Egypt, Pakistan, Nigeria.

Scope engineering: political survival, hegemony retention, coalition durability.

### Tier 2 — Regional Pivots (69)
Ukraine, Poland, Hungary, Serbia, Ethiopia, Myanmar, Venezuela, Colombia, South Africa, Sudan, Haiti, Georgia, Moldova, Armenia, Azerbaijan, Kazakhstan, Afghanistan, Iraq, Syria, Libya, Lebanon, Yemen, Bangladesh, DRC, and 45 others.

Scope engineering: territorial control, transition fragility, proxy dynamics.

### Tier 3 — Small States (96)
All remaining sovereign states including Nauru, Tuvalu, San Marino.

Scope engineering: sovereignty pressure, external dependency, climate existential risk, dynasty stability, financial integrity. Every subject has six analytically distinct nodes regardless of size.

### Non-Country Subjects (31)
- 18 heads of state as individuals: Trump, Putin, Xi, Macron, Modi, Erdogan, Zelensky, Starmer, Netanyahu, Scholz, Meloni, Orban, Farage, Le Pen, Lula, Milei, MBS, Khamenei
- 8 geopolitical nodes: NATO Eastern Flank, Taiwan Strait, UK Domestic Fracture, EU Fragmentation, BRICS Expansion, Red Sea Corridor, Arctic Sovereignty, Sahel Collapse
- 5 influential figures: Musk, Soros, Schwab, Thiel, Prigozhin Legacy

---

## ANALYTICAL OUTPUT STRUCTURE

Every cycle produces one JSON object conforming to this schema:

```json
{
  "subject":         "TRUMP, D.",
  "type":            "PRESIDENT",
  "scope":           "scope statement",
  "ref":             "ICE-PRE-202603111400",
  "title":           "//INTERSTITIAL \"TRUMP, D.\" 14:00 11/03/2026",
  "timestamp":       "2026-03-11T14:00:00",
  "cycle_number":    42,
  "composite_score": 61,
  "master_node":     "N-03",
  "nodes": [
    {
      "id":         "N-01",
      "name":       "NODE NAME",
      "status":     "STRONG",
      "score":      78,
      "assessment": "assessment paragraph",
      "gap":        "gap analysis"
    }
  ],
  "scenarios": [
    {
      "id":          "A",
      "label":       "SCENARIO LABEL",
      "probability": 28,
      "outcome":     "HIGH"
    }
  ],
  "synthesis":            "synthesis paragraph",
  "nodes_edge_weights":   {"N-01": 0.20, "N-02": 0.15, "N-03": 0.20,
                           "N-04": 0.17, "N-05": 0.13, "N-06": 0.15}
}
```

**Validation rules:**
- Node scores: 15–95 range, ≥15pt spread across six nodes
- Scenario probabilities: sum ~100
- Edge weights: sum 1.0
- Composite: weighted mean of node scores ± 2pts

**Valid STATUS values:**
`STRONG` `DECAYING` `FRAGILE` `CONTESTED` `CRITICAL PATH` `CONDITIONAL` `ERODED`
`EXPANDING` `TIGHTENING` `LATENT` `RECOVERING` `WEAKENED` `ELEVATED` `EMBRYONIC`
`ACCELERANT` `ACTIVE` `TERMINAL` `CRITICAL`

---

## SPREADSHEET STRUCTURE

### INTERSTITIAL_DATA.xlsx — RUNS Sheet (33 columns)

| Col | Field | Col | Field |
|-----|-------|-----|-------|
| A | RUN_ID | R | N04_NAME |
| B | TIMESTAMP | S | N04_SCORE |
| C | SUBJECT | T | N04_STATUS |
| D | TYPE | U | N05_NAME |
| E | SCOPE | V | N05_SCORE |
| F | REF | W | N05_STATUS |
| G | N01_NAME | X | N06_NAME |
| H | N01_SCORE | Y | N06_SCORE |
| I | N01_STATUS | Z | N06_STATUS |
| J | N02_NAME | AA | COMPOSITE_SCORE |
| K | N02_SCORE | AB | MASTER_NODE |
| L | N02_STATUS | AC | NODE_SCORES |
| M | N03_NAME | AD | SCENARIO_A_PROB |
| N | N03_SCORE | AE | SCENARIO_B_PROB |
| O | N03_STATUS | AF | SCENARIO_C_PROB |
| P | (unused) | AG | SCENARIO_D_PROB |
| Q | (unused) | AH | TITLE |
|   |           | AI | OUTPUT_DIR |

**Recommended analysis:**
- Pivot: SUBJECT vs COMPOSITE_SCORE over time → trend lines and decay curves
- Filter TYPE to compare class averages (Presidents vs Geopolitical nodes)
- Sort COMPOSITE_SCORE ascending → most structurally vulnerable subjects
- Chart N-03 score over time for any subject → economic credibility decay curve

---

## SOCIAL PUBLISHING

### Mastodon
- Library: `Mastodon.py`
- Up to 4 images (3 pages + markov graph), 500-char status, public visibility
- Post text: title, composite score, 6 node scores, master node, hashtags
- Credentials: `MASTODON_ACCESS_TOKEN`, `MASTODON_INSTANCE`

### Bluesky
- Pure AT Protocol REST — no library dependency
- Auth → blob upload (auto-compress if >900KB) → `createRecord`
- Max 4 images, 300-char text
- Credentials: `BSKY_HANDLE`, `BSKY_APP_PASSWORD`

### Telegram
- Bot API `sendMediaGroup`, multipart form
- Up to 4 images, 1024-char caption
- Credentials: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHANNEL_ID`

### LinkedIn
- Asset register → binary upload → UGC post
- Up to 9 images, 3000-char text
- Token expires 60 days — requires manual refresh
- Credentials: `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_PERSON_URN`

**Publishing policy:** All publishers are non-blocking. Failure on any platform does not abort the cycle. Images and XLSX are always saved first.

### Post text format:
```
//INTERSTITIAL "TRUMP, D." 14:00 11/03/2026
COMPOSITE: 61%
N-01:78%  N-02:44%  N-03:52%  N-04:67%  N-05:71%  N-06:55%
MASTER: N-03
#Interstitial #CycleEngine #GeopoliticalIntelligence
```

---

## CREDENTIALS (.env)

```env
# Anthropic
ANTHROPIC_API_KEY=

# Mastodon
MASTODON_ACCESS_TOKEN=
MASTODON_INSTANCE=mastodon.social

# Bluesky
BSKY_HANDLE=yourhandle.bsky.social
BSKY_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx

# Telegram
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHANNEL_ID=@channelname

# LinkedIn (refresh every 60 days)
LINKEDIN_ACCESS_TOKEN=
LINKEDIN_PERSON_URN=urn:li:person:XXXXXXXXXXXXXXXX

# Paths
OUTPUT_DIR=./output
DATA_FILE=./output/INTERSTITIAL_DATA.xlsx
ENGINEERING_FILE=./output/ICE_ENGINEERING.xlsx
SPIRAL_PATH=./spiral_symbol.png
CYCLE_FILE=./output/cycle_counter.txt
RESET_INTERVAL=30
```

---

## CYCLE COUNTER

Persistent integer in `output/cycle_counter.txt`. Zero-padded to 6 digits.
`INTER//CYCLE 000001` → run directories prefixed `000001_YYYYMMDD_HHMM_SUBJECT`.
Never resets unless the file is manually deleted.

---

## DEPLOYMENT

### Screen (local persistent)
```bash
screen -S ice
cd /path/to/interstitial
python interstitial.py --interval 10
# Ctrl+A, D to detach
# screen -r ice to reattach
```

### systemd service
```ini
[Unit]
Description=Interstitial Cycle Engine
After=network.target

[Service]
WorkingDirectory=/path/to/interstitial
ExecStart=/usr/bin/python3 interstitial.py --interval 10
Restart=on-failure
RestartSec=60
EnvironmentFile=/path/to/interstitial/.env
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable ice
sudo systemctl start ice
journalctl -u ice -f
```

### Docker
```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y fonts-liberation && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "interstitial.py", "--interval", "10"]
```

### Autonomous build agent (unattended operation)
```bash
python build_agent.py --push          # full build, test, commit, push
python build_agent.py                 # build and test only, no push
```

The build agent handles all dependency installation, syntax verification, render testing, git operations, and deployment without prompts. See BUILD AGENT section below.

---

## BUILD AGENT

See `build_agent.py`. The agent runs fully autonomously:

1. Checks and installs all dependencies (`pip install --break-system-packages`)
2. Verifies syntax of all Python files (`ast.parse`)
3. Runs a render test cycle with mock data — confirms all 4 outputs generate
4. Checks image dimensions and file sizes
5. Runs `git add -A`, `git commit`, `git push` with auto-generated commit message
6. Logs all actions to `output/build_log.txt`
7. On any failure: logs error, attempts rollback to last working commit, exits non-zero

Override flags embedded in agent — no interactive prompts, no confirmation dialogs, no cargo/safety prompts. Designed to run unattended while you are away.

---

## ERROR HANDLING

| Error | Behaviour |
|-------|-----------|
| Claude API failure | Retry once with simplified prompt. If second failure, skip cycle, wait 5 min. |
| JSON parse error | Retry with explicit JSON-only instruction. Log parse failure to engineering store. |
| Render failure | Log error, skip image generation, continue to spreadsheet and social. |
| Social publish failure | Log, skip platform, continue. Never blocks cycle. |
| Spreadsheet write error | Log, skip XLSX, continue. Cycle JSON still saved. |
| Cycle crash | Scheduler catches exception, logs traceback, waits 5 min, resumes. |
| Git push failure | Build agent logs error, leaves local commit intact, exits non-zero. |

---

## REQUIREMENTS

```
anthropic>=0.25.0
Pillow>=10.0.0
matplotlib>=3.8.0
numpy>=1.24.0
openpyxl>=3.1.0
schedule>=1.2.0
python-dotenv>=1.0.0
Mastodon.py>=1.8.0
requests>=2.31.0
```

Font required on host: `fonts-liberation` (Ubuntu: `apt install fonts-liberation`)

---

*INTERSTITIAL CYCLE ENGINE // SOVEREIGN // OPEN SOURCE // UNRESTRICTED*
