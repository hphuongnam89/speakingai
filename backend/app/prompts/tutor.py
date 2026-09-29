import json
import re

SYSTEM_PROMPT = """You are an English speaking coach.

Primary objective: Help the learner improve real spoken English and IELTS Speaking ability.

Rules:
- Keep spoken conversational responses natural and concise (2-4 sentences).
- Always ask one natural follow-up question.
- Do not fabricate IELTS scores.
- Do not judge pronunciation from transcript alone.

CRITICAL INSTRUCTION FOR CORRECTIONS:
When the user makes grammar or vocabulary mistakes, you MUST append a JSON block at the very end of your response:
[CORRECTIONS]{"corrections": [{"original": "incorrect phrase", "corrected": "correct phrase", "explanation": "reason", "category": "grammar", "should_repeat": true}]}[/CORRECTIONS]

Example:
User: "Yesterday I go to market and buyed apples."
Coach:
"Sounds like a good trip! What did you cook with the apples?
[CORRECTIONS]{\"corrections\": [{\"original\": \"I go\", \"corrected\": \"I went\", \"explanation\": \"Past tense of go is went\", \"category\": \"grammar\", \"should_repeat\": true}, {\"original\": \"buyed\", \"corrected\": \"bought\", \"explanation\": \"Irregular past tense of buy is bought\", \"category\": \"grammar\", \"should_repeat\": true}]}[/CORRECTIONS]"

If no errors are found, or correction level is 'none', DO NOT output any [CORRECTIONS] block."""

CORRECTION_LEVEL_PROMPTS = {
    "none": "Correction Level: NONE. Do NOT correct any mistakes. Focus purely on natural conversation. Absolutely do not include any [CORRECTIONS] block.",
    "important": "Correction Level: IMPORTANT. Catch notable grammatical and vocabulary errors. Always append the [CORRECTIONS] block.",
    "aggressive": "Correction Level: AGGRESSIVE. Catch every grammatical slip, awkward collocation, preposition mistake, and unnatural phrasing. Always append the [CORRECTIONS] block."
}

MODE_PROMPTS = {
    "daily": "This is a daily practice session. Ask natural follow-up questions. Keep AI turns short. Adapt to learner level.",
    "freetalk": "This is free conversation. Be natural and relaxed. Minimal corrections.",
    "fixmyenglish": "Focus primarily on diagnosing mistakes and teaching improved sentences. Encourage repetition of corrected sentences."
}

def build_conversation_messages(
    mode: str,
    turns: list[dict],
    topic: str | None = None,
    correction_level: str = "important"
) -> list[dict]:
    mode_prompt = MODE_PROMPTS.get(mode, "")
    corr_prompt = CORRECTION_LEVEL_PROMPTS.get(correction_level, CORRECTION_LEVEL_PROMPTS["important"])
    
    full_system_prompt = f"{SYSTEM_PROMPT}\n\n{corr_prompt}\n\n{mode_prompt}"
    if topic:
        full_system_prompt += f"\n\nToday's topic: {topic}"
        
    messages = [{"role": "system", "content": full_system_prompt}]
    messages.extend(turns)
    
    return messages

def parse_corrections(response_text: str) -> tuple[str, list[dict], str | None]:
    # Match [CORRECTIONS] ... [/CORRECTIONS] or /[CORRECTIONS] or end of string
    pattern = r"\[CORRECTIONS\](.*?)(?:/?\[/?CORRECTIONS\]|$)"
    match = re.search(pattern, response_text, re.DOTALL)
    
    corrections_list = []
    clean_reply = response_text
    repeat_prompt = None
    
    if match:
        json_str = match.group(1).strip()
        # Clean potential trailing characters
        if json_str.endswith("/"):
            json_str = json_str[:-1].strip()
        try:
            parsed = json.loads(json_str)
            raw_corrections = parsed.get("corrections", [])
            for c in raw_corrections:
                if isinstance(c, dict) and "original" in c and "corrected" in c:
                    corrections_list.append({
                        "original": c.get("original", "").strip(),
                        "corrected": c.get("corrected", "").strip(),
                        "explanation": c.get("explanation", "").strip(),
                        "category": c.get("category", "grammar").strip().lower(),
                        "should_repeat": bool(c.get("should_repeat", False))
                    })
        except json.JSONDecodeError:
            pass
            
        clean_reply = re.sub(pattern, "", response_text, flags=re.DOTALL).strip()
        
    # Robust fallback: If model wrote markdown arrow instead of JSON (e.g. - **A** → **B**)
    if not corrections_list:
        arrow_matches = re.findall(
            r"(?:-|\*|\b)\s*\*?\*?([a-zA-Z0-9\s'\.,]+?)\*?\*?\s*(?:→|->)\s*\*?\*?([a-zA-Z0-9\s'\.,]+?)\*?\*?(?:\n|$)",
            response_text
        )
        for orig, corr in arrow_matches:
            orig_clean = orig.strip().rstrip(".").rstrip("…")
            corr_clean = corr.strip().rstrip(".").rstrip("…")
            if orig_clean and corr_clean and orig_clean.lower() != corr_clean.lower():
                corrections_list.append({
                    "original": orig_clean,
                    "corrected": corr_clean,
                    "explanation": "Subject-verb agreement or phrasing correction",
                    "category": "grammar",
                    "should_repeat": True
                })

    # Check if any correction requests repetition (Say-it-again flow)
    for c in corrections_list:
        if c.get("should_repeat"):
            repeat_prompt = f"Try saying: \"{c['corrected']}\""
            break

    return clean_reply, corrections_list, repeat_prompt
