import httpx

prompt = """You are an English speaking coach.
Keep spoken responses natural and concise (2-3 sentences).
Always ask one follow-up question.

CRITICAL FORMAT REQUIREMENT:
When you notice errors, you MUST append [CORRECTIONS]...[/CORRECTIONS] at the very end of your response.

Example:
User: "Yesterday I go to market and buyed apples."
Assistant:
Sounds like a productive day! What did you make with the apples?
[CORRECTIONS]{"corrections": [{"original": "I go", "corrected": "I went", "explanation": "Past tense", "category": "grammar", "should_repeat": true}, {"original": "buyed", "corrected": "bought", "explanation": "Irregular verb", "category": "grammar", "should_repeat": true}]}[/CORRECTIONS]
"""

res = httpx.post("http://localhost:11434/api/chat", json={
    "model": "ornith-1.5:9b",
    "messages": [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "She don't like playing tennis with us on Sunday."}
    ],
    "stream": False
}, timeout=30)

print(res.json().get("message", {}).get("content", ""))
