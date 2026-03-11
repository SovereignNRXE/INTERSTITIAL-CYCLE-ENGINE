# INTERSTITIAL CYCLE ENGINE — SETUP

## 1. Unzip
Extract this zip into your project folder. Keep all files together.

## 2. Create .env
Rename `.env.template` to `.env`
Open it and add your Anthropic API key:
  ANTHROPIC_API_KEY=your_key_here

## 3. Install and test
Open terminal in the project folder and run:
  python build_agent.py

## 4. Connect to GitHub (optional)
  git init
  git remote add origin https://YOUR_TOKEN@github.com/SovereignNRXE/INTERSTITIAL-CYCLE-ENGINE.git
  git branch -M main
  python build_agent.py --push

## 5. Run the engine
  python interstitial.py --once          # single test cycle
  python interstitial.py --interval 10   # live, every 10 minutes

## Run in background (Linux)
  screen -S ice
  python interstitial.py --interval 10
  Ctrl+A then D to detach
  screen -r ice to return

## In Claude Code
  cd to your project folder, then launch:
  claude
  Then tell it: run build_agent.py
