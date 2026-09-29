import json
import re

ADAPTIVE_PLAN_SYSTEM_PROMPT = """You are an Adaptive Learning Curriculum Director for an IELTS/English speaking coach.
Your job is to inspect the learner's recurring mistakes and create a targeted, personalized daily practice plan.

Rules:
- Identify the learner's top 3 weaknesses directly from the provided mistake history.
- Set a clear, motivating objective for today's practice session.
- Recommend an engaging topic designed specifically to exercise those vulnerable grammar structures or vocabulary.
- Provide 2-3 practical challenge sentences or collocations for the learner to try using today.
- Output MUST be valid JSON enclosed in [ADAPTIVE_PLAN] ... [/ADAPTIVE_PLAN].

JSON Format:
[ADAPTIVE_PLAN]
{
  "today_objective": "Focus on subject-verb agreement with singular subjects and correct irregular past tenses.",
  "top_weaknesses": [
    "Subject-verb agreement (e.g., 'she don't' instead of 'she doesn't')",
    "Irregular past tense verbs in storytelling",
    "Missing prepositions with specific locations"
  ],
  "recommended_topic": "A Childhood Memory or Memorable Weekend",
  "challenge_phrases": [
    "She doesn't usually like...",
    "When I went there last summer...",
    "We stayed at a cozy cottage..."
  ]
}
[/ADAPTIVE_PLAN]
"""

def build_adaptive_plan_messages(mistakes: list[dict], recent_topics: list[str]) -> list[dict]:
    if mistakes:
        mistake_lines = [
            f"- Original: '{m['original_text']}' -> Corrected: '{m['corrected_text']}' (repeated {m.get('occurrence_count', 1)} times, explanation: {m.get('explanation', '')})"
            for m in mistakes[:8]
        ]
        history_text = "\n".join(mistake_lines)
    else:
        history_text = "No severe recurring mistakes recorded yet. General speaking improvement mode."

    topics_text = ", ".join(recent_topics) if recent_topics else "None"

    user_prompt = f"Learner's Recurring Mistakes:\n{history_text}\n\nRecent Topics Practiced: {topics_text}\n\nPlease generate today's adaptive learning objective and challenge."

    return [
        {"role": "system", "content": ADAPTIVE_PLAN_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

def parse_adaptive_plan(response_text: str) -> dict:
    pattern = r"\[ADAPTIVE_PLAN\](.*?)(?:/?\[/?ADAPTIVE_PLAN\]|$)"
    match = re.search(pattern, response_text, re.DOTALL)
    json_str = match.group(1).strip() if match else response_text.strip()

    if json_str.startswith("```json"):
        json_str = json_str[7:]
    if json_str.startswith("```"):
        json_str = json_str[3:]
    if json_str.endswith("```"):
        json_str = json_str[:-3]
    json_str = json_str.strip()

    try:
        data = json.loads(json_str)
        return {
            "today_objective": str(data.get("today_objective", "Practice fluent speaking and eliminate recurring slips.")),
            "top_weaknesses": list(data.get("top_weaknesses", ["Grammar accuracy", "Lexical precision"])),
            "recommended_topic": str(data.get("recommended_topic", "Daily Life & Personal Goals")),
            "challenge_phrases": list(data.get("challenge_phrases", ["I've always believed that...", "In the past, I used to..."]))
        }
    except Exception:
        return {
            "today_objective": "Practice fluent speaking and eliminate recurring grammatical slips.",
            "top_weaknesses": [
                "Subject-verb agreement consistency",
                "Past tense narrative flow",
                "Preposition accuracy"
            ],
            "recommended_topic": "Describe an unforgettable journey or hobby",
            "challenge_phrases": [
                "Although it was challenging, I managed to...",
                "What I found most fascinating was..."
            ]
        }
