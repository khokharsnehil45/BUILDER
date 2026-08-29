#!/usr/bin/env python3
"""
BUILDER - AI-Powered Venture Architect & Business Model Engine CLI.
Retro dual-tone cyberpunk design with interactive business model canvas generators, pitch deck synthesizers, and GTM planners.
"""

import os
import sys
from pathlib import Path

import questionary
from questionary import Style
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.markdown import Markdown

import db
import ai_engine

console = Console()

CUSTOM_STYLE = Style([
    ('qmark', 'fg:#00e5ff bold'),
    ('question', 'bold fg:#00e5ff'),
    ('answer', 'fg:#50fa7b bold'),
    ('pointer', 'fg:#ff79c6 bold'),
    ('highlighted', 'fg:#ff79c6 bold'),
    ('selected', 'fg:#50fa7b bold'),
    ('separator', 'fg:#6272a4'),
    ('instruction', 'fg:#8be9fd italic'),
    ('text', 'fg:#f8f8f2'),
])

def render_banner(subtitle: str = "🚀 AI-Powered Venture Architect & Business Strategy Engine 🚀"):
    """Renders the retro 3D-styled BUILDER banner with Cyberpunk Cyan & Electric Neon gradient."""
    banner_lines = [
        r"██████╗ ██╗   ██╗██╗██╗     ██████╗ ███████╗██████╗ ",
        r"██╔══██╗██║   ██║██║██║     ██╔══██╗██╔════╝██╔══██╗",
        r"██████╔╝██║   ██║██║██║     ██║  ██║█████╗  ██████╔╝",
        r"██╔══██╗██║   ██║██║██║     ██║  ██║██╔══╝  ██╔══██╗",
        r"██████╔╝╚██████╔╝██║███████╗██████╔╝███████╗██║  ██║",
        r"╚═════╝  ╚═════╝ ╚═╝╚══════╝╚═════╝ ╚══════╝╚═╝  ╚═╝"
    ]
    
    banner_text = Text()
    colors = ["#00e5ff", "#38bdf8", "#818cf8", "#a855f7", "#c084fc", "#bd93f9"]
    for i, line in enumerate(banner_lines):
        banner_text.append(line + "\n", style=f"bold {colors[i % len(colors)]}")
        
    banner_text.append(f"  {subtitle}", style="italic #8be9fd")
    
    ventures = db.get_ventures()
    cfg = ai_engine.load_config()
    model_str = f"LLM: {cfg.get('llm_provider', 'ollama').upper()}"
    
    console.print(Panel(
        banner_text,
        border_style="#00e5ff",
        subtitle=f"[bold #bd93f9]v1.0.0 • {len(ventures)} Startups • {model_str}[/bold #bd93f9]",
        subtitle_align="right",
        padding=(1, 2)
    ))

def print_wizard_box(title: str, subtitle: str):
    content = Text()
    content.append(f"{title}\n", style="bold #00e5ff")
    content.append(f"{subtitle}", style="dim #8be9fd")
    console.print(Panel(content, border_style="#00e5ff", padding=(0, 1)))

def pause_prompt():
    questionary.press_any_key_to_continue("Press any key to return to the main menu...").ask()

# ==========================================
# ACTIONS
# ==========================================

def action_create_venture():
    console.clear()
    render_banner()
    print_wizard_box("✨ Create New Business Venture", "Define startup name, industry, target customer, and business model.")
    
    name = questionary.text("Venture / Startup Name (e.g. NexusFlow AI):", style=CUSTOM_STYLE).ask()
    if not name or not name.strip():
        return
        
    tagline = questionary.text("One-liner Tagline (optional):", style=CUSTOM_STYLE).ask()
    industry = questionary.select(
        "Industry Sector:",
        choices=["💻 AI & Developer Tools", "💳 FinTech & Payments", "🛍️ E-Commerce & D2C", "🏥 HealthTech & Bio", "🎓 EdTech", "⚙️ B2B SaaS", "🌐 Web3 / Crypto", "📦 Other"],
        style=CUSTOM_STYLE
    ).ask()
    if not industry:
        return
        
    target_market = questionary.text("Target Customer (e.g. Remote Engineering Teams, Indie Hackers, Dentists):", style=CUSTOM_STYLE).ask()
    business_model = questionary.select(
        "Monetization & Business Model:",
        choices=["Subscription (SaaS)", "Usage-Based / API", "Marketplace Take Rate", "Agency / Retainer", "Direct Sales (D2C)", "Freemium Open Core"],
        style=CUSTOM_STYLE
    ).ask()
    
    summary = questionary.text("Problem & Solution Summary (1-2 sentences):", multiline=True, style=CUSTOM_STYLE).ask()
    
    vid = db.create_venture(
        name=name.strip(),
        tagline=tagline or "",
        industry=industry,
        target_market=target_market or "B2B",
        business_model=business_model or "SaaS",
        summary=summary or ""
    )
    
    console.print(f"\n[bold green]✓ Startup '{name}' (#vid: {vid}) created in BUILDER![/bold green]\n")
    
    gen_now = questionary.confirm("🚀 Generate Business Model Canvas with AI now?").ask()
    if gen_now:
        action_generate_module(vid, "canvas")
    else:
        pause_prompt()

def action_generate_module(venture_id: int, module_type: str):
    v = db.get_venture_by_id(venture_id)
    if not v:
        return
        
    console.clear()
    render_banner()
    type_name = "Business Model Canvas" if module_type == "canvas" else ("10-Slide Pitch Deck" if module_type == "pitch_deck" else "90-Day GTM Roadmap")
    print_wizard_box(f"🧠 Synthesizing {type_name} — [{v['name']}]", "BUILDER AI is architecting strategy, unit economics, and execution funnels...")
    
    console.print("\n[bold cyan]⚡ Running AI strategy generation...[/bold cyan]\n")
    
    res_text = ""
    title = type_name
    if module_type == "canvas":
        res_text = ai_engine.generate_business_canvas(v["name"], v["industry"], v["target_market"], v["business_model"], v["summary"])
    elif module_type == "pitch_deck":
        res_text = ai_engine.generate_pitch_deck(v["name"], v["industry"], v["target_market"], v["summary"])
    elif module_type == "gtm":
        res_text = ai_engine.generate_gtm_roadmap(v["name"], v["industry"], v["target_market"], v["summary"])
        
    db.save_venture_module(venture_id, module_type, title, {"markdown": res_text})
    
    console.print(Panel(
        Markdown(res_text),
        border_style="#00e5ff",
        title=f"[bold #bd93f9]{v['name']} — {title}[/bold #bd93f9]",
        padding=(1, 2)
    ))
    console.print("\n[bold green]✓ Saved to Venture Dossier![/bold green]\n")
    pause_prompt()

def action_select_venture():
    console.clear()
    render_banner()
    print_wizard_box("📂 Browse & Manage Ventures", "Select a startup to view dossier, generate decks, or roadmaps.")
    
    ventures = db.get_ventures()
    if not ventures:
        console.print("\n[yellow]No ventures created yet. Click 'Create New Business Venture' to start![/yellow]\n")
        pause_prompt()
        return
        
    choices = [questionary.Choice(f"🚀 {v['name']} ({v['industry']} • {v['business_model']})", value=v) for v in ventures]
    choices.append(questionary.Choice("🔙 Back to Main Menu", value=None))
    
    sel = questionary.select("Select Venture:", choices=choices, style=CUSTOM_STYLE).ask()
    if not sel:
        return
        
    v = db.get_venture_by_id(sel["id"])
    
    while True:
        console.clear()
        render_banner()
        print_wizard_box(
            f"🏢 {v['name']} — Dossier",
            f"Industry: {v['industry']} | Model: {v['business_model']} | Stage: {v['stage']}\nTagline: {v['tagline'] or '-'}"
        )
        
        act = questionary.select(
            "Select Venture Action:",
            choices=[
                "📊 Generate 9-Box Business Model Canvas",
                "🎯 Generate 10-Slide Pitch Deck Outline",
                "🚀 Generate 90-Day Go-To-Market Roadmap",
                "📜 View Saved Strategic Modules",
                "🗑️ Delete Venture",
                "🔙 Back to Venture List"
            ],
            style=CUSTOM_STYLE
        ).ask()
        
        if not act or act == "🔙 Back to Venture List":
            break
        elif "Business Model Canvas" in act:
            action_generate_module(v["id"], "canvas")
        elif "Pitch Deck" in act:
            action_generate_module(v["id"], "pitch_deck")
        elif "Go-To-Market" in act:
            action_generate_module(v["id"], "gtm")
        elif "View Saved" in act:
            v_fresh = db.get_venture_by_id(v["id"])
            if not v_fresh["modules"]:
                console.print("\n[yellow]No modules generated yet.[/yellow]\n")
                pause_prompt()
            else:
                m_choices = [questionary.Choice(m["title"], value=m) for m in v_fresh["modules"]]
                m_sel = questionary.select("Select module to view:", choices=m_choices, style=CUSTOM_STYLE).ask()
                if m_sel:
                    import json
                    content_obj = json.loads(m_sel["content_json"])
                    console.clear()
                    render_banner()
                    console.print(Panel(Markdown(content_obj.get("markdown", "")), border_style="#00e5ff", title=m_sel["title"]))
                    pause_prompt()
        elif "Delete" in act:
            if questionary.confirm(f"Are you sure you want to delete '{v['name']}'?").ask():
                db.delete_venture(v["id"])
                console.print("[bold green]✓ Venture deleted.[/bold green]")
                pause_prompt()
                break

def action_launch_gui():
    console.clear()
    render_banner()
    print_wizard_box("🚀 Launching BUILDER Web Dashboard", "Starting local server at http://localhost:8700")
    console.print("\n[bold cyan]Opening your browser to BUILDER GUI...[/bold cyan]")
    console.print("[dim]Press Ctrl+C anytime to stop GUI server and return to terminal.[/dim]\n")
    import server
    server.launch_server(port=8700, open_browser=True)

# ==========================================
# MAIN LOOP
# ==========================================

def main():
    if len(sys.argv) > 1 and sys.argv[1].lower() in ["gui", "web", "--gui", "-g"]:
        action_launch_gui()
        return

    db.init_db()
    
    while True:
        console.clear()
        render_banner()
        print_wizard_box(
            "⚡ BUILDER — AI Venture Architect & Startup Builder",
            "Turn startup ideas into validated business models, pitch decks, and GTM execution roadmaps."
        )
        
        choice = questionary.select(
            "Select BUILDER Action: (Use arrow keys)",
            choices=[
                questionary.Choice("✨  Create New Business Venture   — Start a new venture blueprint (Name, ICP, Model)", value="create"),
                questionary.Choice("📂  Manage & Architect Ventures   — Synthesize Canvases, Pitch Decks & GTM Plans", value="manage"),
                questionary.Choice("💻  Launch BUILDER Web GUI       — Minimalist browser workspace & deck generator", value="gui"),
                questionary.Separator(),
                questionary.Choice("🚪  Exit BUILDER", value="exit")
            ],
            style=CUSTOM_STYLE
        ).ask()
        
        if choice is None or choice == "exit":
            console.print("\n[bold magenta]Keep building the future! Goodbye! 👋[/bold magenta]\n")
            sys.exit(0)
        elif choice == "create":
            action_create_venture()
        elif choice == "manage":
            action_select_venture()
        elif choice == "gui":
            action_launch_gui()

if __name__ == "__main__":
    main()
