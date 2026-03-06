#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════╗
║       AI BRANDING AGENT SUITE v1.0           ║
║   5 Specialist Agents · Powered by Claude    ║
╚══════════════════════════════════════════════╝
"""

import anthropic
import json
import sys
import textwrap
from datetime import datetime
from pathlib import Path

# ── CONFIG ──────────────────────────────────────────────────────────────────
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 2000
OUTPUT_DIR = Path("branding_output")

client = anthropic.Anthropic()

# ── AGENT DEFINITIONS ────────────────────────────────────────────────────────
AGENTS = [
    {
        "id": "strategist",
        "name": "Brand Strategist",
        "emoji": "🎯",
        "role": "Team Lead · Positioning & Direction",
        "color": "\033[33m",   # gold
        "system": """You are a senior Brand Strategist and team lead. You define brand direction and positioning.
Your job is to produce a focused brand strategy document.

Structure your response with these exact sections:
## BRAND MISSION & VISION
## TARGET AUDIENCE PERSONAS (2–3 personas)
## MARKET POSITIONING STATEMENT
## BRAND VALUES (5 core values with brief explanations)
## COMPETITIVE DIFFERENTIATION

Be specific, strategic, and actionable. Avoid generic fluff.""",
        "task": "Develop a complete brand strategy including mission, vision, audience personas, positioning statement, brand values, and competitive differentiation.",
        "deliverables": ["Brand strategy document", "Audience personas", "Positioning statement"],
    },
    {
        "id": "designer",
        "name": "Brand Identity Designer",
        "emoji": "🎨",
        "role": "Visual Identity · Style Systems",
        "color": "\033[35m",   # magenta
        "system": """You are a senior Brand Identity and Graphic Designer. You define the visual language of a brand.
Produce a detailed visual identity brief.

Structure your response with these exact sections:
## COLOR PALETTE
(Primary, secondary, accent colors — provide hex codes and usage rationale)
## TYPOGRAPHY SYSTEM
(Heading font, body font, mono font — with usage guidelines)
## LOGO CONCEPT DIRECTIONS (3 distinct directions)
## ICONOGRAPHY & VISUAL MOTIFS
## BRAND STYLE GUIDE SUMMARY

Be specific. Reference real fonts and real color values.""",
        "task": "Create a complete visual identity system including color palette (with hex codes), typography system, logo concept directions, and style guide summary.",
        "deliverables": ["Logo concept directions", "Color palette with hex codes", "Typography system", "Style guide summary"],
    },
    {
        "id": "copywriter",
        "name": "Copywriter & Messaging Strategist",
        "emoji": "✍️",
        "role": "Voice & Narrative · Copy",
        "color": "\033[36m",   # cyan
        "system": """You are a senior Copywriter and Messaging Strategist. You craft the verbal identity of a brand.
Produce a complete messaging framework.

Structure your response with these exact sections:
## BRAND TAGLINE OPTIONS (5 options with rationale)
## BRAND STORY (150–200 words, first-person brand voice)
## TONE OF VOICE GUIDELINES
(3–4 voice attributes with DO / DON'T examples)
## CORE MESSAGE PILLARS (3 pillars)
## WEBSITE HERO COPY (headline + subheadline + CTA)

Write in a confident, distinctive voice. No corporate jargon.""",
        "task": "Develop brand taglines, brand story, tone of voice guidelines, core message pillars, and sample website hero copy.",
        "deliverables": ["5 tagline options", "Brand story", "Tone of voice guide", "Website hero copy"],
    },
    {
        "id": "marketing",
        "name": "Marketing Strategist",
        "emoji": "📈",
        "role": "Channels · Campaigns · Growth",
        "color": "\033[32m",   # green
        "system": """You are a senior Marketing Strategist. You design how a brand reaches and converts its audience.
Produce a practical go-to-market plan.

Structure your response with these exact sections:
## CHANNEL STRATEGY
(Rank and justify top 4–5 channels: SEO, paid, social, email, etc.)
## 90-DAY LAUNCH ROADMAP
(Month 1, Month 2, Month 3 — key milestones)
## CONTENT STRATEGY
(Content pillars, formats, publishing cadence)
## LEAD GENERATION FUNNEL
(Awareness → Consideration → Conversion touchpoints)
## KEY METRICS TO TRACK

Be concrete. Include realistic timelines and priorities.""",
        "task": "Create a marketing strategy including channel prioritization, 90-day launch roadmap, content strategy, lead generation funnel, and KPIs.",
        "deliverables": ["Channel strategy", "90-day roadmap", "Content strategy", "Lead gen funnel"],
    },
    {
        "id": "analytics",
        "name": "Brand Analytics Consultant",
        "emoji": "📊",
        "role": "Data · Measurement · ROI",
        "color": "\033[34m",   # blue
        "system": """You are a senior Brand Analytics Consultant. You define how branding success gets measured.
Produce a measurement framework.

Structure your response with these exact sections:
## BRAND AWARENESS METRICS
(KPIs, benchmarks, measurement methods)
## MARKETING PERFORMANCE DASHBOARD
(List 8–10 key metrics with targets and tracking tools)
## CUSTOMER INSIGHT FRAMEWORK
(Surveys, NPS, cohort analysis approach)
## 6-MONTH ANALYTICS ROADMAP
## ROI CALCULATION MODEL
(How to attribute revenue to branding efforts)

Be precise and data-driven. Reference real tools where relevant.""",
        "task": "Design a brand analytics framework including awareness metrics, performance dashboard, customer insights approach, and ROI model.",
        "deliverables": ["KPI dashboard", "Analytics roadmap", "ROI model", "Customer insight framework"],
    },
]

# ── DISPLAY HELPERS ──────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
WHITE  = "\033[97m"
GOLD   = "\033[33m"

def clear_line():
    print("\r" + " " * 80 + "\r", end="", flush=True)

def banner():
    print(f"""
{GOLD}{'═' * 60}{RESET}
{BOLD}  AI BRANDING AGENT SUITE{RESET}  {DIM}v1.0 · Powered by Claude{RESET}
{GOLD}{'═' * 60}{RESET}
{DIM}  5 specialist agents · Sequential execution
  Outputs saved to: {OUTPUT_DIR}/{RESET}
{GOLD}{'─' * 60}{RESET}
""")

def agent_header(agent, index, total):
    color = agent["color"]
    print(f"\n{color}{'▐' * 3}{RESET} {BOLD}Agent {index}/{total} — {agent['emoji']}  {agent['name']}{RESET}")
    print(f"   {DIM}{agent['role']}{RESET}")
    print(f"   {DIM}Task: {agent['task'][:80]}...{RESET}" if len(agent['task']) > 80 else f"   {DIM}Task: {agent['task']}{RESET}")
    print(f"   {color}{'─' * 52}{RESET}")

def print_deliverables(agent):
    print(f"\n   {DIM}Deliverables:{RESET}")
    for d in agent["deliverables"]:
        print(f"   {GOLD}·{RESET} {DIM}{d}{RESET}")

def spinner_message(msg):
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    import time, threading
    stop = threading.Event()
    def animate():
        i = 0
        while not stop.is_set():
            print(f"\r   {GOLD}{frames[i % len(frames)]}{RESET} {DIM}{msg}{RESET}", end="", flush=True)
            time.sleep(0.1)
            i += 1
    t = threading.Thread(target=animate)
    t.start()
    return stop, t

def preview_output(text, lines=8):
    """Print first N lines of output as preview."""
    all_lines = text.strip().split("\n")
    preview = all_lines[:lines]
    print()
    for line in preview:
        if line.startswith("## "):
            print(f"   {GOLD}{BOLD}{line[3:]}{RESET}")
        elif line.strip():
            wrapped = textwrap.fill(line, width=70, initial_indent="   ", subsequent_indent="   ")
            print(f"{DIM}{wrapped}{RESET}")
    if len(all_lines) > lines:
        print(f"   {DIM}... [{len(all_lines) - lines} more lines — see saved file]{RESET}")

# ── CORE AGENT RUNNER ─────────────────────────────────────────────────────────
def run_agent(agent: dict, brief: str, context: str = "") -> str:
    """Call Claude API for a single agent."""
    user_message = f"""BRAND BRIEF:
{brief}

{"CONTEXT FROM PREVIOUS AGENTS:" + chr(10) + context if context else ""}

Your specific task: {agent['task']}

Deliver your complete professional output now."""

    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=agent["system"],
        messages=[{"role": "user", "content": user_message}],
    )
    return message.content[0].text

# ── SAVE OUTPUT ───────────────────────────────────────────────────────────────
def save_outputs(brief: str, results: dict):
    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Individual agent files
    for agent in AGENTS:
        if agent["id"] in results:
            fname = OUTPUT_DIR / f"{timestamp}_{agent['id']}.md"
            fname.write_text(
                f"# {agent['emoji']} {agent['name']}\n\n"
                f"*Generated: {datetime.now().strftime('%B %d, %Y %H:%M')}*\n\n"
                f"---\n\n{results[agent['id']]}\n",
                encoding="utf-8"
            )

    # Master brand book
    master = OUTPUT_DIR / f"{timestamp}_BRAND_BOOK.md"
    content = [
        f"# 📖 COMPLETE BRAND BOOK\n",
        f"*Generated: {datetime.now().strftime('%B %d, %Y %H:%M')}*\n",
        f"\n---\n\n## ORIGINAL BRIEF\n\n{brief}\n\n---\n",
    ]
    for agent in AGENTS:
        if agent["id"] in results:
            content.append(f"\n\n# {agent['emoji']} {agent['name'].upper()}\n\n")
            content.append(results[agent["id"]])
            content.append("\n\n---")
    master.write_text("".join(content), encoding="utf-8")

    return master

# ── MAIN ORCHESTRATOR ─────────────────────────────────────────────────────────
def run_suite(brief: str):
    banner()
    results = {}
    context_summary = ""

    print(f"{BOLD}Your Brief:{RESET}")
    print(textwrap.fill(brief, width=70, initial_indent="  ", subsequent_indent="  "))
    print(f"\n{GOLD}{'─' * 60}{RESET}")
    input(f"\n{DIM}  Press Enter to launch all 5 agents...{RESET}")

    total = len(AGENTS)
    for i, agent in enumerate(AGENTS, 1):
        agent_header(agent, i, total)
        print_deliverables(agent)

        stop_spinner, spinner_thread = spinner_message(f"Generating {agent['name']} output...")
        try:
            output = run_agent(agent, brief, context_summary)
            results[agent["id"]] = output
            stop_spinner.set()
            spinner_thread.join()
            clear_line()

            color = agent["color"]
            print(f"   {color}✓{RESET} {BOLD}Complete{RESET} {DIM}({len(output.split())} words){RESET}")
            preview_output(output)

            # Build rolling context (first 300 chars of each output)
            context_summary += f"\n[{agent['name']}]: {output[:300]}...\n"

        except Exception as e:
            stop_spinner.set()
            spinner_thread.join()
            clear_line()
            print(f"   \033[31m✗ Error: {e}{RESET}")
            results[agent["id"]] = f"Error generating output: {e}"

    # Save everything
    print(f"\n{GOLD}{'═' * 60}{RESET}")
    print(f"{BOLD}  Saving brand book...{RESET}")
    master_file = save_outputs(brief, results)

    print(f"\n{GOLD}  ✦  All 5 agents complete!{RESET}")
    print(f"\n  {DIM}Output files saved to:{RESET} {BOLD}{OUTPUT_DIR}/{RESET}")
    for agent in AGENTS:
        fname = list(OUTPUT_DIR.glob(f"*_{agent['id']}.md"))
        if fname:
            print(f"   {agent['color']}{agent['emoji']}{RESET}  {DIM}{fname[-1].name}{RESET}")
    print(f"\n  {GOLD}📖  Master brand book:{RESET} {BOLD}{master_file.name}{RESET}")
    print(f"\n{GOLD}{'═' * 60}{RESET}\n")

    return results, master_file

# ── ENTRY POINT ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Use command-line argument as brief, or prompt interactively
    if len(sys.argv) > 1:
        brief = " ".join(sys.argv[1:])
    else:
        banner()
        print(f"{BOLD}  Enter your brand brief below.{RESET}")
        print(f"  {DIM}(Company name, what you do, target market, tone, goals){RESET}")
        print(f"\n{GOLD}{'─' * 60}{RESET}\n")
        lines = []
        print("  Brief (press Enter twice when done):\n")
        while True:
            line = input("  ")
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
        brief = "\n".join(lines).strip()

    if not brief:
        print(f"\033[31m  Error: Brief cannot be empty.\033[0m\n")
        sys.exit(1)

    run_suite(brief)
