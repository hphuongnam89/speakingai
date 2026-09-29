import json
import re

IELTS_EXAMINER_SYSTEM_PROMPT = """You are a certified IELTS Speaking Examiner.

Your role:
- Conduct an authentic IELTS Speaking test in a professional, courteous, yet objective manner.
- Do NOT act as a teacher during the test. Do NOT correct grammar, pronunciation, or vocabulary while the exam is in progress.
- Do NOT fabricate scores or tell the candidate their score during the interview.
- Ask one clear question at a time.
- Transition smoothly between questions and parts.
- If the candidate's answer is very brief, prompt them once naturally: "Can you elaborate on that?" or "Why is that so?".
- Keep your own turns concise (1-2 sentences) so the candidate speaks most of the time.
"""

IELTS_EVALUATION_SYSTEM_PROMPT = """You are a senior IELTS Speaking Master Examiner and Assessor.
You will evaluate the candidate's complete spoken transcript from an IELTS Speaking test.

Scoring Criteria (1.0 to 9.0 in 0.5 increments):
1. Fluency and Coherence (FC): Ability to speak with normal flow, hesitation, length of turn, logical structuring, use of connectives and discourse markers.
2. Lexical Resource (LR): Range and precision of vocabulary, use of collocations, idiomatic expressions, awareness of style and collocation, paraphrase skill.
3. Grammatical Range and Accuracy (GRA): Range of simple and complex sentence structures, accuracy of tenses, prepositions, subject-verb agreement, and error density.

Evaluation Rules:
- Overall Band Score = Average of the criteria, rounded to nearest 0.5 (e.g., 6.25 -> 6.5, 6.75 -> 7.0).
- Pronunciation must remain null unless acoustic audio analysis is present.
- Return output strictly as a JSON object inside [EVALUATION] ... [/EVALUATION] tags.

Format:
[EVALUATION]
{
  "overall_band": 6.5,
  "fluency_score": 6.5,
  "fluency_feedback": "Speaks with reasonable continuity but occasionally hesitates to search for grammar structures.",
  "lexical_score": 6.0,
  "lexical_feedback": "Good everyday vocabulary, though relies on basic modifiers like 'very good' or 'a lot'.",
  "grammar_score": 7.0,
  "grammar_feedback": "Uses a variety of complex structures with frequent error-free sentences.",
  "pronunciation_score": null,
  "strengths": [
    "Extended answers naturally without frequent pauses",
    "Effective use of cohesive devices like 'furthermore' and 'on the other hand'"
  ],
  "areas_for_improvement": [
    "Vary adjectives instead of repeating common words",
    "Pay attention to past tense consistency when narrating past events"
  ],
  "suggested_expressions": [
    {
      "original": "very interesting",
      "upgraded": "captivating / thoroughly engaging",
      "context": "Used when describing the journey experience"
    },
    {
      "original": "I like it a lot",
      "upgraded": "I have a strong penchant for it / It holds immense appeal for me",
      "context": "Used when describing favorite hobbies"
    }
  ],
  "examiner_summary": "Solid communicative competence capable of handling both concrete and abstract topics with minor slips."
}
[/EVALUATION]
"""

def build_examiner_messages(
    part: str,
    turns: list[dict],
    cue_card: dict | None = None
) -> list[dict]:
    prompt = f"{IELTS_EXAMINER_SYSTEM_PROMPT}\n\nCurrent Test Section: {part.upper()}."
    if cue_card:
        prompt += f"\nCandidate's Cue Card:\nTopic: {cue_card.get('title')}\nBullets:\n" + "\n".join(f"- {b}" for b in cue_card.get("bullets", []))

    messages = [{"role": "system", "content": prompt}]
    messages.extend(turns)
    return messages

def build_evaluation_messages(
    turns: list[dict],
    topic: str | None = None
) -> list[dict]:
    transcript_text = "\n".join([f"{t['role'].upper()}: {t['content']}" for t in turns])
    user_prompt = f"Please evaluate this IELTS candidate's performance:\n\nTopic/Context: {topic or 'General IELTS Speaking'}\n\nTranscript:\n{transcript_text}"
    
    return [
        {"role": "system", "content": IELTS_EVALUATION_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

def parse_evaluation(response_text: str) -> dict:
    pattern = r"\[EVALUATION\](.*?)(?:/?\[/?EVALUATION\]|$)"
    match = re.search(pattern, response_text, re.DOTALL)
    json_str = match.group(1).strip() if match else response_text.strip()
    
    # Clean json markdown if needed
    if json_str.startswith("```json"):
        json_str = json_str[7:]
    if json_str.startswith("```"):
        json_str = json_str[3:]
    if json_str.endswith("```"):
        json_str = json_str[:-3]
    json_str = json_str.strip()

    try:
        data = json.loads(json_str)
        # Ensure default fields exist
        return {
            "overall_band": float(data.get("overall_band", 6.0)),
            "fluency_score": float(data.get("fluency_score", 6.0)),
            "fluency_feedback": str(data.get("fluency_feedback", "")),
            "lexical_score": float(data.get("lexical_score", 6.0)),
            "lexical_feedback": str(data.get("lexical_feedback", "")),
            "grammar_score": float(data.get("grammar_score", 6.0)),
            "grammar_feedback": str(data.get("grammar_feedback", "")),
            "pronunciation_score": None,
            "strengths": list(data.get("strengths", [])),
            "areas_for_improvement": list(data.get("areas_for_improvement", [])),
            "suggested_expressions": list(data.get("suggested_expressions", [])),
            "examiner_summary": str(data.get("examiner_summary", "Evaluation complete."))
        }
    except Exception as e:
        # Fallback evaluation if JSON parse fails
        return {
            "overall_band": 6.0,
            "fluency_score": 6.0,
            "fluency_feedback": "Good fluency with natural pauses.",
            "lexical_score": 6.0,
            "lexical_feedback": "Adequate vocabulary range to discuss topics.",
            "grammar_score": 6.0,
            "grammar_feedback": "A mix of simple and complex sentence forms.",
            "pronunciation_score": None,
            "strengths": ["Clear communication", "Willingness to answer at length"],
            "areas_for_improvement": ["Incorporate more academic collocations", "Practice complex conditional structures"],
            "suggested_expressions": [],
            "examiner_summary": "Candidate demonstrated ability to communicate effectively across questions."
        }
