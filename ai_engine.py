"""
BUILDER AI Intelligence Engine (Ollama / Gemini).
Synthesizes Business Model Canvases, ICP (Ideal Customer Profiles), Pricing Tiers, GTM Roadmaps, and 10-Slide Pitch Decks.
"""

import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, Optional, Generator

CONFIG_FILE = Path.home() / ".builder_config.json"

DEFAULT_CONFIG = {
    "llm_provider": "ollama",
    "ollama_host": "http://localhost:11434",
    "ollama_llm_model": "llama3.2:3b",
    "gemini_api_key": "",
    "gemini_model": "gemini-2.5-flash"
}

def load_config() -> Dict[str, Any]:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(cfg: Dict[str, Any]):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

def generate_ai_response(system_prompt: str, user_prompt: str, config: Optional[Dict[str, Any]] = None) -> str:
    cfg = config or load_config()
    llm_provider = cfg.get("llm_provider", "ollama")
    
    if llm_provider == "ollama":
        host = cfg.get("ollama_host", "http://localhost:11434").rstrip("/")
        model = cfg.get("ollama_llm_model", "llama3.2:3b")
        url = f"{host}/api/generate"
        payload = json.dumps({
            "model": model,
            "prompt": user_prompt,
            "system": system_prompt,
            "stream": False
        }).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("response", "").strip()
        except Exception as e:
            return f"❌ Ollama AI Error ({model}): {e}\nEnsure Ollama is running (`ollama serve`)."
            
    elif llm_provider == "gemini":
        api_key = cfg.get("gemini_api_key", "").strip()
        model = cfg.get("gemini_model", "gemini-2.5-flash")
        if not api_key:
            return "❌ Gemini API Key is missing. Configure it in BUILDER Settings."
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = json.dumps({
            "contents": [{"parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}]
        }).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            return f"❌ Gemini API Error: {e}"
            
    return "❌ Unknown LLM Provider."

def stream_ai_response(system_prompt: str, user_prompt: str, config: Optional[Dict[str, Any]] = None) -> Generator[Dict[str, Any], None, None]:
    cfg = config or load_config()
    llm_provider = cfg.get("llm_provider", "ollama")
    
    if llm_provider == "ollama":
        host = cfg.get("ollama_host", "http://localhost:11434").rstrip("/")
        model = cfg.get("ollama_llm_model", "llama3.2:3b")
        url = f"{host}/api/generate"
        payload = json.dumps({
            "model": model,
            "prompt": user_prompt,
            "system": system_prompt,
            "stream": True
        }).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                for line in resp:
                    if line:
                        chunk = json.loads(line.decode("utf-8"))
                        token = chunk.get("response", "")
                        yield {"type": "token", "token": token}
            yield {"type": "done", "model": f"ollama:{model}"}
        except Exception as e:
            yield {"type": "error", "error": str(e)}
            
    elif llm_provider == "gemini":
        res = generate_ai_response(system_prompt, user_prompt, config)
        yield {"type": "token", "token": res}
        yield {"type": "done", "model": f"gemini:{cfg.get('gemini_model')}"}

# ==========================================
# BUSINESS BUILDING SYNTHESIZERS
# ==========================================

def generate_business_canvas(venture_name: str, industry: str, audience: str, model: str, summary: str) -> str:
    system_prompt = (
        "You are BUILDER AI, an elite Silicon Valley venture architect and startup strategist. "
        "Generate a comprehensive, structured Business Model Canvas for the startup."
    )
    user_prompt = f"""### Startup Profile:
- **Name**: {venture_name}
- **Industry**: {industry}
- **Target Market**: {audience}
- **Business Model**: {model}
- **Summary**: {summary}

Generate a clear, high-density 9-Box Business Model Canvas formatted in Markdown:
1. **Value Propositions** (Core differentiators & pain points solved)
2. **Customer Segments** (Ideal Customer Profiles & buyer personas)
3. **Channels** (Acquisition & distribution funnels)
4. **Customer Relationships** (Retention & onboarding strategy)
5. **Revenue Streams** (Monetization tiers, pricing & unit economics)
6. **Key Resources** (Tech stack, IP, data assets, talent)
7. **Key Activities** (Engineering, sales, marketing, partnerships)
8. **Key Partnerships** (Vendors, APIs, distributors, integrations)
9. **Cost Structure** (Fixed vs variable, COGS, CAC & burn rate)

Be specific, practical, and highly strategic. Avoid generic startup jargon."""
    return generate_ai_response(system_prompt, user_prompt)

def generate_pitch_deck(venture_name: str, industry: str, audience: str, summary: str) -> str:
    system_prompt = (
        "You are BUILDER AI, a top-tier Venture Capitalist and pitch deck expert (Y Combinator & Sequoia style). "
        "Generate a compelling, investor-ready 10-Slide Pitch Deck outline."
    )
    user_prompt = f"""### Startup Profile:
- **Name**: {venture_name}
- **Industry**: {industry}
- **Audience**: {audience}
- **Summary**: {summary}

Generate a 10-Slide Pitch Deck Outline formatted in Markdown:
- **Slide 1: Problem** (The urgent, expensive pain point)
- **Slide 2: Solution** (Our unfair advantage & product offering)
- **Slide 3: Market Size (TAM/SAM/SOM)** (Total addressable market)
- **Slide 4: Product & Demo** (Core workflows & technical architecture)
- **Slide 5: Business Model & Pricing** (Unit economics, LTV/CAC)
- **Slide 6: Go-to-Market (GTM)** (Acquisition channels & viral loops)
- **Slide 7: Competitive Landscape** (2x2 Matrix & defensive moats)
- **Slide 8: Financial Projections** (Year 1-3 ARR, margins & milestones)
- **Slide 9: Team & Execution** (Key execution capabilities)
- **Slide 10: The Ask** (Target seed round, runway & milestones)"""
    return generate_ai_response(system_prompt, user_prompt)

def generate_gtm_roadmap(venture_name: str, industry: str, audience: str, summary: str) -> str:
    system_prompt = (
        "You are BUILDER AI, a master Growth Hacker and B2B/B2C Go-To-Market architect. "
        "Create an actionable 90-Day GTM execution roadmap."
    )
    user_prompt = f"""### Startup Profile:
- **Name**: {venture_name}
- **Industry**: {industry}
- **Target Audience**: {audience}
- **Summary**: {summary}

Generate an actionable **90-Day Go-To-Market Roadmap**:
- **Days 1-30: Pre-Launch & Alpha Validation** (Landing page, cold outreach, 20 discovery interviews)
- **Days 31-60: Beta Launch & Initial Traction** (Product Hunt, Hacker News, niche communities, first 50 paid users)
- **Days 61-90: Scaling & Retention Engine** (Content SEO, affiliate loops, outbound email sequences, referral mechanics)
- **Key Metrics & North Star KPI to track**"""
    return generate_ai_response(system_prompt, user_prompt)
