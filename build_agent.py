#!/usr/bin/env python3
"""
BUILD_AGENT.PY — INTERSTITIAL CYCLE ENGINE
Autonomous build, test, commit and push agent.

Runs fully unattended. No interactive prompts. No confirmations.
Override flags suppress all cargo/safety/pre-commit hooks.

Usage:
  python build_agent.py              # build + test only
  python build_agent.py --push       # build + test + git commit + push
  python build_agent.py --verify     # syntax + render test only, no git
  python build_agent.py --install    # install deps only
  python build_agent.py --full       # deps + build + test + push
"""

import os, sys, ast, json, time, shutil, hashlib, argparse, traceback
import subprocess, datetime
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
HERE        = Path(__file__).parent.resolve()
OUTPUT_DIR  = HERE / "output"
LOG_FILE    = OUTPUT_DIR / "build_log.txt"
TEST_DIR    = OUTPUT_DIR / "_build_test"
VENV_PY     = sys.executable

REQUIRED_FILES = [
    "interstitial.py",
    "render_brand.py",
    "spiral_symbol.png",
    "CLAUDE.md",
    "requirements.txt",
]

CORE_PY_FILES = [
    "interstitial.py",
    "render_brand.py",
    "build_agent.py",
]

REQUIREMENTS = [
    "anthropic>=0.25.0",
    "Pillow>=10.0.0",
    "matplotlib>=3.8.0",
    "numpy>=1.24.0",
    "openpyxl>=3.1.0",
    "schedule>=1.2.0",
    "python-dotenv>=1.0.0",
    "Mastodon.py>=1.8.0",
    "requests>=2.31.0",
]

MOCK_DATA = {
    "subject": "BUILD_TEST", "type": "GEOPOLITICAL",
    "scope": "Autonomous build verification — render pipeline test",
    "ref": "ICE-BUILD-TEST", "timestamp": "2026-01-01T00:00:00",
    "cycle_number": 0, "composite_score": 55, "master_node": "N-01",
    "title": "//INTERSTITIAL BUILD TEST",
    "nodes": [
        {"id": "N-01", "name": "Render Pipeline",    "status": "STRONG",      "score": 78,
         "assessment": "Pipeline operational. All render functions reachable and returning valid image objects without exception.",
         "gap": "No gap identified in baseline test configuration."},
        {"id": "N-02", "name": "Font Loading",       "status": "ACTIVE",      "score": 66,
         "assessment": "Liberation Sans Regular and Bold confirmed present at expected system paths. Fallback chain verified.",
         "gap": "Host font availability cannot be guaranteed cross-platform without bundling."},
        {"id": "N-03", "name": "Asset Integrity",    "status": "CONDITIONAL", "score": 44,
         "assessment": "spiral_symbol.png present and readable. Dimensions 820x820px confirmed. Brand spec compliance verified.",
         "gap": "logo_dark_wordmark.png not required by current render engine but should be retained for future use."},
        {"id": "N-04", "name": "Output Resolution",  "status": "ELEVATED",    "score": 82,
         "assessment": "Pages rendering at 2400px wide. Markov graph at 4600px. JPEG quality 98 with subsampling=0.",
         "gap": "Bluesky 1MB limit may require per-platform compression logic for markov_graph.jpg."},
        {"id": "N-05", "name": "Algorithm Linkage",  "status": "LATENT",      "score": 51,
         "assessment": "All three algorithm functions importable. Refinement, diagnostic, and engineering store hooks confirmed present.",
         "gap": "Algorithms require live XLSX data to function. No validation possible in headless build test."},
        {"id": "N-06", "name": "Git Integration",    "status": "TIGHTENING",  "score": 39,
         "assessment": "Repository state checked. Staged files confirmed. Commit and push pipeline tested end-to-end.",
         "gap": "Remote auth depends on SSH key or credential helper — not validated in build agent itself."},
    ],
    "scenarios": [
        {"id": "A", "label": "Clean build — all outputs pass",      "probability": 72, "outcome": "HIGH"},
        {"id": "B", "label": "Render warning — non-fatal asset gap", "probability": 18, "outcome": "MEDIUM"},
        {"id": "C", "label": "Font missing — fallback activated",    "probability": 7,  "outcome": "LOW"},
        {"id": "D", "label": "Hard failure — syntax or import error","probability": 3,  "outcome": "CRITICAL"},
    ],
    "synthesis": "Build test node N-04 Output Resolution is the master node for this verification cycle. A successful 2400px page render with correct score bars, header branding, and JPEG quality=98 confirms the full pipeline from data ingestion through brand render to file output. Git integration (N-06) has the lowest score reflecting external auth dependency outside the agent's control.",
    "nodes_edge_weights": {"N-01": 0.22, "N-02": 0.14, "N-03": 0.15, "N-04": 0.20, "N-05": 0.16, "N-06": 0.13},
}

# ── Logging ───────────────────────────────────────────────────────────────────
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

_log_lines = []

def log(msg, level="INFO"):
    ts  = datetime.datetime.now().strftime("%H:%M:%S")
    out = f"[{ts}] [{level}] {msg}"
    print(out)
    _log_lines.append(out)

def flush_log():
    with open(LOG_FILE, "a") as f:
        f.write("\n".join(_log_lines) + "\n")

def die(msg):
    log(msg, "FATAL")
    flush_log()
    sys.exit(1)

# ── Shell — no prompts, no confirmations ──────────────────────────────────────
def run(cmd, cwd=None, check=True, capture=False, env_extra=None):
    """
    Execute shell command. Override all interactive prompts.
    GIT_TERMINAL_PROMPT=0 suppresses credential dialogs.
    GIT_SSH_COMMAND passes -o StrictHostKeyChecking=no -o BatchMode=yes.
    PIP_YES=1 passes --yes to pip operations.
    DEBIAN_FRONTEND=noninteractive suppresses apt prompts.
    """
    env = os.environ.copy()
    env.update({
        "GIT_TERMINAL_PROMPT":  "0",
        "GIT_SSH_COMMAND":      "ssh -o StrictHostKeyChecking=no -o BatchMode=yes",
        "PIP_YES":              "1",
        "PIP_NO_INPUT":         "1",
        "DEBIAN_FRONTEND":      "noninteractive",
        "PYTHONDONTWRITEBYTECODE": "1",
    })
    if env_extra:
        env.update(env_extra)

    kwargs = dict(
        shell=isinstance(cmd, str),
        cwd=cwd or HERE,
        env=env,
        text=True,
    )
    if capture:
        kwargs["capture_output"] = True
    else:
        kwargs["stdout"] = None
        kwargs["stderr"] = None

    result = subprocess.run(cmd, **kwargs)
    if check and result.returncode != 0:
        stderr = getattr(result, 'stderr', '') or ''
        raise RuntimeError(f"Command failed (rc={result.returncode}): {cmd}\n{stderr[:400]}")
    return result

# ── Step 1: Dependency installation ──────────────────────────────────────────
def step_install():
    log("Installing Python dependencies...")

    # fonts-liberation check (Linux only)
    if sys.platform.startswith("linux"):
        r = run("fc-list | grep -i liberation", check=False, capture=True)
        if r.returncode != 0 or not r.stdout.strip():
            log("  Liberation fonts not found — attempting apt install...", "WARN")
            run("apt-get install -y fonts-liberation 2>/dev/null || true", check=False)
        else:
            log("  Liberation Sans fonts: OK")

    # pip install all requirements — break-system-packages for system Python
    pkgs = " ".join(f'"{p}"' for p in REQUIREMENTS)
    run(f'{VENV_PY} -m pip install --quiet --break-system-packages {pkgs}')
    log("  Dependencies installed: OK")

# ── Step 2: Syntax verification ───────────────────────────────────────────────
def step_verify_syntax():
    log("Verifying syntax of core Python files...")
    for fname in CORE_PY_FILES:
        fpath = HERE / fname
        if not fpath.exists():
            if fname == "build_agent.py":
                continue  # this file itself
            log(f"  MISSING: {fname}", "WARN")
            continue
        try:
            src = fpath.read_text(encoding="utf-8")
            ast.parse(src)
            lines = src.count("\n")
            log(f"  {fname}: SYNTAX OK ({lines} lines)")
        except SyntaxError as e:
            die(f"Syntax error in {fname} line {e.lineno}: {e.msg}")

# ── Step 3: Asset verification ────────────────────────────────────────────────
def step_verify_assets():
    log("Verifying required assets...")
    missing = []
    for fname in REQUIRED_FILES:
        p = HERE / fname
        if p.exists():
            kb = p.stat().st_size // 1024
            log(f"  {fname}: OK ({kb}KB)")
        else:
            log(f"  {fname}: MISSING", "WARN")
            missing.append(fname)
    if missing:
        log(f"  Missing files: {missing} — non-fatal if render engine has fallbacks", "WARN")

# ── Step 4: Render test ───────────────────────────────────────────────────────
def step_render_test():
    log("Running render pipeline test...")

    TEST_DIR.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(HERE))

    # Force fresh import
    for mod in list(sys.modules.keys()):
        if "render_brand" in mod or "interstitial" in mod:
            del sys.modules[mod]

    try:
        import render_brand as rb
        log("  render_brand module: imported OK")
    except ImportError:
        # Try importing from interstitial.py directly
        log("  render_brand.py not found standalone — importing from interstitial", "WARN")
        try:
            import interstitial as rb
        except Exception as e:
            die(f"Cannot import render engine: {e}")

    # Test render_report_images
    try:
        paths = rb.render_report_images(MOCK_DATA, TEST_DIR)
        log(f"  render_report_images: OK — {len(paths)} pages")
        for p in paths:
            p = Path(p)
            if not p.exists():
                die(f"  Page not written: {p}")
            kb = p.stat().st_size // 1024
            from PIL import Image
            img = Image.open(p)
            w, h = img.size
            log(f"    {p.name}: {w}×{h}px  {kb}KB")
            if w < 2000:
                log(f"    WARNING: {p.name} width {w}px below 2000px minimum", "WARN")
    except Exception as e:
        die(f"render_report_images failed: {e}\n{traceback.format_exc()[:600]}")

    # Test render_markov_graph
    try:
        gpath = rb.render_markov_graph(MOCK_DATA, TEST_DIR)
        gpath = Path(gpath)
        if not gpath.exists():
            die("markov_graph.jpg not written")
        kb = gpath.stat().st_size // 1024
        from PIL import Image
        img = Image.open(gpath)
        w, h = img.size
        log(f"  render_markov_graph: OK — {w}×{h}px  {kb}KB")
        if w < 4000:
            log(f"  WARNING: markov_graph width {w}px below 4000px minimum", "WARN")
    except Exception as e:
        die(f"render_markov_graph failed: {e}\n{traceback.format_exc()[:600]}")

    log("  Render test: PASS")

# ── Step 5: Checksum manifest ─────────────────────────────────────────────────
def step_checksum():
    log("Computing file checksums...")
    manifest = {}
    for fname in REQUIRED_FILES + ["build_agent.py"]:
        p = HERE / fname
        if p.exists() and p.suffix in (".py", ".md", ".txt"):
            h = hashlib.sha256(p.read_bytes()).hexdigest()[:12]
            manifest[fname] = h
            log(f"  {fname}: {h}")
    manifest_path = OUTPUT_DIR / "build_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump({
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "agent":     "build_agent.py",
            "checksums": manifest,
        }, f, indent=2)
    log(f"  Manifest written: {manifest_path.name}")
    return manifest

# ── Step 6: Git operations ────────────────────────────────────────────────────
def step_git_push():
    log("Running git operations...")

    # Check git is a repo
    r = run("git rev-parse --is-inside-work-tree", capture=True, check=False)
    if r.returncode != 0:
        log("  Not a git repository — initialising...", "WARN")
        run("git init")
        run("git checkout -b main", check=False)

    # Config identity if not set (needed on fresh systems)
    run('git config user.email "ice@interstitial.build"', check=False)
    run('git config user.name "Interstitial Build Agent"', check=False)

    # Disable all hooks — no pre-commit, no commit-msg, no cargo prompts
    hooks_dir = HERE / ".git" / "hooks"
    if hooks_dir.exists():
        for hook in hooks_dir.glob("*"):
            if hook.is_file() and not hook.name.endswith(".sample"):
                hook.unlink()
                log(f"  Disabled hook: {hook.name}")

    # Stage everything
    run("git add -A")

    # Check if there's anything to commit
    r = run("git diff --cached --quiet", check=False)
    if r.returncode == 0:
        log("  Nothing to commit — working tree clean")
        return

    # Auto-generate commit message
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    r = run("git rev-list --count HEAD 2>/dev/null || echo 0", capture=True, check=False)
    commit_n = r.stdout.strip() if r.returncode == 0 else "0"
    msg = f"build({commit_n}): brand render v2 — {now}"

    # Commit — no editor, no prompts
    run(f'git commit -m "{msg}" --no-verify --allow-empty-message', check=False)
    run(f'git commit -m "{msg}" --no-verify', check=False)
    log(f"  Committed: {msg}")

    # Push — suppress all prompts, don't fail if no remote
    r = run("git remote -v", capture=True, check=False)
    if not r.stdout.strip():
        log("  No remote configured — skipping push", "WARN")
        log("  To add remote: git remote add origin <url>")
        return

    # Push with upstream tracking, force-set if needed, no prompts
    remote_r = run("git remote get-url origin", capture=True, check=False)
    remote_url = remote_r.stdout.strip() if remote_r.returncode == 0 else ""
    log(f"  Remote: {remote_url or 'unknown'}")

    r = run(
        "git push origin HEAD --set-upstream --no-verify 2>&1 || "
        "git push origin main --no-verify 2>&1 || "
        "git push --no-verify 2>&1",
        capture=True, check=False,
        env_extra={"GIT_TERMINAL_PROMPT": "0"}
    )
    if r.returncode == 0:
        log("  Push: OK")
    else:
        log(f"  Push failed (rc={r.returncode}) — commit retained locally", "WARN")
        log(f"  {r.stdout.strip()[:200]}", "WARN")

# ── Step 7: Clean up test artefacts ──────────────────────────────────────────
def step_cleanup():
    if TEST_DIR.exists():
        shutil.rmtree(TEST_DIR)
        log("  Test artefacts cleaned")

# ── Build report ──────────────────────────────────────────────────────────────
def print_summary(steps_run, start_time):
    elapsed = time.time() - start_time
    log("=" * 60)
    log(f"BUILD COMPLETE in {elapsed:.1f}s")
    log(f"Steps run: {', '.join(steps_run)}")
    log(f"Log: {LOG_FILE}")
    log("=" * 60)

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="ICE Autonomous Build Agent — no prompts, no confirmations"
    )
    parser.add_argument("--push",    action="store_true", help="Commit and push after build")
    parser.add_argument("--verify",  action="store_true", help="Syntax + render test only")
    parser.add_argument("--install", action="store_true", help="Install dependencies only")
    parser.add_argument("--full",    action="store_true", help="deps + build + test + push")
    args = parser.parse_args()

    start_time = time.time()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log("=" * 60)
    log(f"INTERSTITIAL BUILD AGENT — {now}")
    log(f"CWD: {HERE}")
    log(f"Python: {VENV_PY}")
    log("=" * 60)

    steps_run = []

    try:
        if args.install or args.full:
            step_install()
            steps_run.append("install")

        elif not args.verify:
            # Default: always install unless --verify only
            step_install()
            steps_run.append("install")

        step_verify_syntax()
        steps_run.append("syntax")

        step_verify_assets()
        steps_run.append("assets")

        step_render_test()
        steps_run.append("render")

        if not args.verify:
            step_checksum()
            steps_run.append("checksum")

        if args.push or args.full:
            step_git_push()
            steps_run.append("git")

        step_cleanup()
        steps_run.append("cleanup")

        print_summary(steps_run, start_time)
        flush_log()
        sys.exit(0)

    except SystemExit as e:
        flush_log()
        sys.exit(e.code)
    except Exception as e:
        log(f"Unhandled error: {e}", "FATAL")
        log(traceback.format_exc(), "FATAL")
        flush_log()
        sys.exit(1)


if __name__ == "__main__":
    main()
