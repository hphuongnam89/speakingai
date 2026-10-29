import json
import re
from typing import Dict, Any, List

PLACEMENT_QUESTIONS = [
    {
        "id": 1,
        "level": "A2-B1",
        "title": "Part 1: Personal Life & Habits",
        "question": "Can you introduce yourself and tell me what you usually like to do in your free time?",
        "focus": "Kiểm tra phản xạ cơ bản, thì hiện tại đơn, câu đơn và từ vựng đời sống."
    },
    {
        "id": 2,
        "level": "B1-B2",
        "title": "Part 2: Past Experience Narrative",
        "question": "Could you describe a memorable trip or an interesting experience you had in the past? What happened?",
        "focus": "Kiểm tra thì quá khứ đơn/tiếp diễn, khả năng kết nối câu chuyện và độ trôi chảy."
    },
    {
        "id": 3,
        "level": "B2-C1",
        "title": "Part 3: Abstract Opinion & Argumentation",
        "question": "Do you believe modern technology makes our daily lives more convenient, or does it bring more stress? Why?",
        "focus": "Kiểm tra khả năng lập luận trừu tượng, liên từ phức và từ vựng nâng cao."
    }
]

PLACEMENT_EVALUATION_SYSTEM_PROMPT = """You are a Senior IELTS Examiner and Chief Academic Director.
You are evaluating a diagnostic placement test consisting of 3 spoken answers from a learner.
Your job is to:
1. Provide an objective, realistic IELTS Speaking Band (1.0 to 9.0 in 0.5 increments) across all 4 official IELTS criteria: Fluency & Coherence (fluency_score), Lexical Resource (lexical_score), Grammatical Range & Accuracy (grammar_score), and Pronunciation (pronunciation_score).
2. Provide a thorough, constructive academic assessment for Pronunciation (pronunciation_feedback in Vietnamese), focusing on ending consonants (/s/, /z/, /t/, /d/, /ed/), word stress, sentence stress, and natural rhythm/intonation.
3. Identify top 3 specific key weaknesses (in Vietnamese).
4. Identify 2 key strengths (in Vietnamese).
5. Provide a clear academic assessment (examiner_verdict in Vietnamese).
6. Build a realistic 3-phase roadmap tailored to:
   - Current Band vs Target Band
   - Daily minutes and duration in months

Return strictly valid JSON inside [PLACEMENT_RESULT]...[/PLACEMENT_RESULT] tags with the following structure:
[PLACEMENT_RESULT]
{
  "estimated_band": 5.0,
  "fluency_score": 5.0,
  "lexical_score": 5.0,
  "grammar_score": 5.0,
  "pronunciation_score": 5.0,
  "pronunciation_feedback": "Phát âm nhìn chung dễ hiểu (Intelligible), các từ cơ bản rõ ràng. Tuy nhiên thí sinh thường xuyên nuốt âm đuôi (final sounds như /s/, /t/, /ed/), trọng âm từ đa âm tiết chưa chuẩn xác và ngữ điệu còn hơi đều (flat tone). Cần chú trọng luyện bật âm đuôi và ngắt nghỉ theo cụm nghĩa (chunking).",
  "key_weaknesses": [
    "Thường quên chia động từ thì quá khứ khi kể chuyện",
    "Hay nuốt âm đuôi (/s/, /z/, /ed/) và phát âm thiếu trọng âm từ",
    "Câu trả lời còn ngắn, thiếu liên từ nối ý"
  ],
  "strengths": [
    "Trả lời đúng trọng tâm câu hỏi, phát âm cơ bản rõ ràng",
    "Tự tin diễn đạt ý kiến chính"
  ],
  "examiner_verdict": "Trình độ hiện tại ở mức B1 (IELTS 5.0). Nền tảng giao tiếp cơ bản tốt nhưng cần bổ sung vốn từ vựng học thuật, câu phức và chuẩn hóa ngữ điệu, âm đuôi để đạt mục tiêu.",
  "roadmap": {
    "total_hours": 30.0,
    "feasibility": "Rất khả thi nếu kiên trì 20 phút mỗi ngày",
    "phases": [
      {
        "phase_name": "Giai đoạn 1: Chuẩn hóa âm đuôi & Ngữ pháp nền tảng",
        "target_band": 5.5,
        "focus_areas": [
          "Bật rõ âm đuôi /s/, /z/, /ed/ và sửa lỗi thì quá khứ",
          "Công thức trả lời 3 câu: Trực tiếp -> Lý do -> Ví dụ",
          "Nạp từ vựng B2 theo các chủ đề cơ bản"
        ]
      },
      {
        "phase_name": "Giai đoạn 2: Tăng tốc IELTS Part 2 & Ngữ điệu tự nhiên",
        "target_band": 6.5,
        "focus_areas": [
          "Luyện nói liên tục 2 phút theo Cue Card",
          "Sử dụng collocations và từ nối tự nhiên",
          "Kiểm soát ngữ điệu và giảm các âm đệm 'um/ah'"
        ]
      },
      {
        "phase_name": "Giai đoạn 3: Phản biện Part 3 & Về đích",
        "target_band": 7.0,
        "focus_areas": [
          "Tư duy phản biện 2 chiều cho câu hỏi trừu tượng",
          "Mô phỏng bài thi thật 15 phút với giám khảo AI",
          "Tối ưu độ chính xác và trôi chảy ở tốc độ cao"
        ]
      }
    ]
  }
}
[/PLACEMENT_RESULT]
"""


def build_placement_eval_messages(
    answers: List[Dict[str, Any]],
    target_band: float,
    daily_minutes: int,
    duration_months: int
) -> List[Dict[str, str]]:
    total_hours = round((daily_minutes / 60.0) * (duration_months * 30), 1)

    user_content = f"""LEARNER COMMITMENT:
- Target Band: {target_band}
- Daily Study Time: {daily_minutes} minutes/day
- Target Timeline: {duration_months} months
- Calculated Total Dedicated Speaking Hours: {total_hours} hours

CANDIDATE'S 3 DIAGNOSTIC ANSWERS:
"""
    for i, item in enumerate(answers, 1):
        q = item.get("question", "")
        a = item.get("answer", "")
        user_content += f"\n--- Question {i} ---\nPrompt: {q}\nCandidate Answer: \"{a}\"\n"

    user_content += "\nPlease analyze the 3 answers carefully, score the candidate objectively, and generate their personalized roadmap in Vietnamese."

    return [
        {"role": "system", "content": PLACEMENT_EVALUATION_SYSTEM_PROMPT},
        {"role": "user", "content": user_content}
    ]


def parse_placement_result(response_text: str) -> Dict[str, Any]:
    pattern = r"\[PLACEMENT_RESULT\](.*?)\[/PLACEMENT_RESULT\]"
    match = re.search(pattern, response_text, re.DOTALL)
    raw = match.group(1).strip() if match else response_text.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback extraction of JSON block if tags were slightly misformatted
        json_pattern = r"\{.*\}"
        json_match = re.search(json_pattern, response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except Exception:
                pass

        # Safe fallback structure
        return {
            "estimated_band": 5.0,
            "fluency_score": 5.0,
            "lexical_score": 5.0,
            "grammar_score": 5.0,
            "pronunciation_score": 5.0,
            "pronunciation_feedback": "Phát âm rõ ràng, dễ nghe hiểu. Cần chú ý nhấn đúng trọng âm từ và bật rõ âm cuối /s/, /t/, /ed/ khi nói.",
            "key_weaknesses": [
              "Cần mở rộng câu trả lời dài hơn",
              "Cần chú ý chia thì động từ chính xác",
              "Cần cải thiện âm đuôi và ngữ điệu tự nhiên"
            ],
            "strengths": ["Phản xạ trả lời tự tin", "Phát âm cơ bản rõ ràng"],
            "examiner_verdict": "Đã hoàn thành bài kiểm tra đầu vào. Trình độ hiện tại ước lượng Band 5.0.",
            "roadmap": {
              "total_hours": 30.0,
              "feasibility": "Khả thi với sự kiên trì luyện tập hằng ngày.",
              "phases": [
                {
                  "phase_name": "Giai đoạn 1: Nền tảng & Ngữ pháp",
                  "target_band": 5.5,
                  "focus_areas": ["Ngữ pháp cơ bản", "Từ vựng thông dụng"]
                },
                {
                  "phase_name": "Giai đoạn 2: IELTS Part 2",
                  "target_band": 6.5,
                  "focus_areas": ["Nói theo cue card 2 phút", "Collocations"]
                },
                {
                  "phase_name": "Giai đoạn 3: Phản xạ nâng cao",
                  "target_band": 7.0,
                  "focus_areas": ["Part 3 luận đề", "Thi thử toàn diện"]
                }
              ]
            }
        }
