import json
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.session import SessionModel
from app.repositories.session_repo import SessionRepository
from app.repositories.turn_repo import TurnRepository
from app.services.llm.router import get_model_router
from app.data.ielts_bank import (
    get_random_part_1,
    get_random_part_2,
    get_cue_card_by_id,
    find_part_1_by_topic,
    find_cue_card_by_topic,
    get_topics_catalog
)
from app.prompts.ielts import (
    build_examiner_messages,
    build_evaluation_messages,
    parse_evaluation
)
from app.schemas.ielts import (
    IeltsStartRequest,
    IeltsStartResponse,
    IeltsRespondRequest,
    IeltsRespondResponse,
    IeltsEvaluationResponse,
    CueCard,
    SuggestedExpression,
    EvaluationFeedbackRequest
)
from app.models.scoring import EvaluationFeedbackModel
from app.core.auth import get_current_user_id, get_current_principal_id

router = APIRouter(prefix="/ielts", tags=["ielts"])

@router.get("/topics")
def list_topics():
    return get_topics_catalog()

@router.post("/start", response_model=IeltsStartResponse)
async def start_ielts_test(req: IeltsStartRequest, request: Request, db: Session = Depends(get_db)):
    session_repo = SessionRepository(db)
    turn_repo = TurnRepository(db)

    owner_user_id = get_current_principal_id(request)
    user_id = get_current_user_id(request)

    part = req.part.lower()
    cue_card_obj = None
    greeting = ""
    first_question = ""
    topic_name = "IELTS Speaking"
    session_mode = f"ielts_{part}"

    if part == "part1":
        p1 = find_part_1_by_topic(req.topic) if req.topic else None
        if not p1:
            p1 = get_random_part_1()
        topic_name = f"IELTS Part 1: {p1['topic']}"
        session_mode = f"ielts_part1:0:{p1['topic']}"
        greeting = "Good day. Welcome to the IELTS Speaking test. In this first part, I would like to ask you some questions about yourself."
        first_question = p1["questions"][0]
    elif part == "part2":
        p2 = find_cue_card_by_topic(req.topic) if req.topic else None
        if not p2:
            p2 = get_random_part_2()
        topic_name = f"IELTS Part 2: {p2['topic']}"
        session_mode = f"ielts_part2_prep:{p2['id']}"
        cue_card_obj = CueCard(
            id=p2["id"],
            topic=p2["topic"],
            title=p2["title"],
            bullets=p2["bullets"],
            follow_up=p2.get("follow_up"),
            part_3_questions=p2.get("part_3_questions")
        )
        greeting = "Now, in Part 2, I'm going to give you a topic and I'd like you to talk about it for one to two minutes. Before you talk, you'll have one minute to think about what you are going to say. You can make some notes if you wish. Here is your cue card:"
        first_question = f"{p2['title']} Please prepare for 1 minute, then speak for 1 to 2 minutes."
    elif part == "part3":
        p2 = find_cue_card_by_topic(req.topic) if req.topic else None
        if not p2:
            p2 = get_random_part_2()
        topic_name = f"IELTS Part 3: Discussion on {p2['topic']}"
        session_mode = f"ielts_part3:0:{p2['id']}"
        greeting = "Now we've been talking about a personal topic, and I'd like to discuss with you one or two more general questions related to this."
        first_question = p2["part_3_questions"][0] if p2.get("part_3_questions") else f"Why do you think people place so much importance on {p2['topic']} in modern society?"
    else:  # full_mock
        p1 = find_part_1_by_topic(req.topic) if req.topic else None
        if not p1:
            p1 = get_random_part_1()
        p2 = find_cue_card_by_topic(req.topic) if req.topic else None
        if not p2:
            p2 = get_random_part_2()
        topic_name = f"IELTS Full Mock Test ({p1['topic']} & {p2['topic']})"
        session_mode = f"ielts_full_mock:part1:0:{p2['id']}:{p1['topic']}"
        greeting = "Good day. My name is your IELTS Examiner. This is the speaking assessment for the International English Language Testing System. In Part 1, I'd like to ask you some questions about yourself."
        first_question = p1["questions"][0]

    # Create session with owner validation
    session = session_repo.create(
        mode=session_mode,
        topic=topic_name,
        user_id=user_id,
        owner_user_id=owner_user_id
    )

    # Save examiner greeting as initial turn
    full_examiner_intro = f"{greeting} {first_question}".strip()
    turn_repo.create(
        session_id=session.id,
        role="assistant",
        transcript=full_examiner_intro,
        owner_user_id=owner_user_id
    )

    return IeltsStartResponse(
        session_id=session.id,
        part=part,
        cue_card=cue_card_obj,
        greeting=greeting,
        question=first_question
    )

@router.post("/respond", response_model=IeltsRespondResponse)
async def respond_ielts_turn(req: IeltsRespondRequest, request: Request, db: Session = Depends(get_db)):
    session_repo = SessionRepository(db)
    turn_repo = TurnRepository(db)

    owner_user_id = get_current_principal_id(request)
    user_id = get_current_user_id(request)
    session = session_repo.get(req.session_id, user_id, owner_user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.ended_at is not None:
        raise HTTPException(
            status_code=400,
            detail={"error_code": "SESSION_ALREADY_FINISHED", "message": "This IELTS session is already ended."}
        )

    # 1. Save candidate turn
    turn_repo.create(
        session_id=req.session_id,
        role="user",
        transcript=req.user_text,
        owner_user_id=owner_user_id
    )

    mode = session.mode or "ielts_part1"
    words_count = len(req.user_text.split())

    # ==========================================================
    # FLOW 1: STANDALONE PART 2
    # ==========================================================
    if mode.startswith("ielts_part2"):
        timing_warning = None
        if words_count < 75:
            timing_warning = "⚠️ Cảnh báo thời gian: Bài nói dưới 1 phút. Trong kỳ thi IELTS Part 2 thực tế, bạn cần nói liên tục từ 1-2 phút (100-150 từ) để đạt tiêu chí Fluency."
            closing_msg = f"Thank you. Your response was under one minute. Remember that IELTS Part 2 requires speaking continuously for 1 to 2 minutes. That concludes Part 2 of your speaking test."
        else:
            closing_msg = "Thank you very much. That concludes Part 2 of your speaking test. You may now generate your evaluation report."

        turn_repo.create(
            session_id=req.session_id,
            role="assistant",
            transcript=closing_msg,
            owner_user_id=owner_user_id
        )
        session.mode = "ielts_part2:completed"
        db.commit()

        return IeltsRespondResponse(
            message=closing_msg,
            tts_text=closing_msg,
            is_completed=True,
            next_part="completed",
            timing_warning=timing_warning
        )

    # ==========================================================
    # FLOW 2: FULL MOCK TEST STATE MACHINE (Part 1 -> Part 2 -> Part 3)
    # ==========================================================
    if mode.startswith("ielts_full_mock:"):
        parts = mode.split(":")
        stage = parts[1]

        # Stage 2.1: Part 1 Interview (3-4 questions)
        if stage == "part1":
            q_idx = int(parts[2]) if len(parts) > 2 else 0
            p2_id = parts[3] if len(parts) > 3 else "cue_card_1"
            p1_topic = parts[4] if len(parts) > 4 else "Hometown"

            p1_bank = find_part_1_by_topic(p1_topic) or get_random_part_1()
            questions = p1_bank.get("questions", [])

            if q_idx < min(len(questions) - 1, 3):
                # Ask next Part 1 question
                next_q = questions[q_idx + 1]
                session.mode = f"ielts_full_mock:part1:{q_idx + 1}:{p2_id}:{p1_topic}"
                db.commit()
                turn_repo.create(session_id=req.session_id, role="assistant", transcript=next_q, owner_user_id=owner_user_id)
                return IeltsRespondResponse(message=next_q, tts_text=next_q, is_completed=False, next_part="part1")
            else:
                # Part 1 Complete -> Transition smoothly to Part 2!
                p2 = get_cue_card_by_id(p2_id) or get_random_part_2()
                cue_obj = CueCard(
                    id=p2["id"],
                    topic=p2["topic"],
                    title=p2["title"],
                    bullets=p2["bullets"],
                    follow_up=p2.get("follow_up"),
                    part_3_questions=p2.get("part_3_questions")
                )
                transition_msg = (
                    f"Thank you. That brings us to the end of Part 1.\n\n"
                    f"Now, for Part 2, I am going to give you a topic and I would like you to talk about it for one to two minutes. "
                    f"Before you speak, you will have one minute to think about what you are going to say. You can make some notes if you wish.\n\n"
                    f"Here is your topic: {p2['title']}"
                )
                session.mode = f"ielts_full_mock:part2_speak:{p2['id']}"
                db.commit()
                turn_repo.create(session_id=req.session_id, role="assistant", transcript=transition_msg, owner_user_id=owner_user_id)
                return IeltsRespondResponse(
                    message=transition_msg,
                    tts_text=transition_msg,
                    is_completed=False,
                    next_part="part2",
                    cue_card=cue_obj
                )

        # Stage 2.2: Part 2 Speech Submitted -> Transition to Part 3
        if stage == "part2_speak":
            p2_id = parts[2] if len(parts) > 2 else "cue_card_1"
            p2 = get_cue_card_by_id(p2_id) or get_random_part_2()
            p3_questions = p2.get("part_3_questions") or [
                f"How has modern society changed people's perspective on {p2['topic']}?"
            ]

            timing_warning = None
            if words_count < 75:
                timing_warning = "⚠️ Cảnh báo Part 2: Bài nói dưới 1 phút. Hãy chú ý cấu trúc mở rộng (Mind-map 4 gợi ý) để nói trọn vẹn 1-2 phút."

            first_p3_q = p3_questions[0]
            transition_to_p3 = (
                f"Thank you very much. That concludes Part 2.\n\n"
                f"Now in Part 3, we have been talking about a personal experience related to {p2['topic']}, "
                f"and I'd like to discuss with you one or two more general questions related to this.\n\n"
                f"{first_p3_q}"
            )
            session.mode = f"ielts_full_mock:part3:{p2_id}:0"
            db.commit()
            turn_repo.create(session_id=req.session_id, role="assistant", transcript=transition_to_p3, owner_user_id=owner_user_id)
            return IeltsRespondResponse(
                message=transition_to_p3,
                tts_text=transition_to_p3,
                is_completed=False,
                next_part="part3",
                timing_warning=timing_warning
            )

        # Stage 2.3: Part 3 In-depth Discussion (3 questions)
        if stage == "part3":
            p2_id = parts[2] if len(parts) > 2 else "cue_card_1"
            q_idx = int(parts[3]) if len(parts) > 3 else 0
            p2 = get_cue_card_by_id(p2_id) or get_random_part_2()
            p3_questions = p2.get("part_3_questions") or []

            if q_idx < min(len(p3_questions) - 1, 2):
                next_p3_q = p3_questions[q_idx + 1]
                session.mode = f"ielts_full_mock:part3:{p2_id}:{q_idx + 1}"
                db.commit()
                turn_repo.create(session_id=req.session_id, role="assistant", transcript=next_p3_q, owner_user_id=owner_user_id)
                return IeltsRespondResponse(message=next_p3_q, tts_text=next_p3_q, is_completed=False, next_part="part3")
            else:
                # Full Mock Complete!
                closing_msg = (
                    "Thank you very much. That is the end of the speaking test. "
                    "You have successfully completed all three parts of the IELTS Speaking Mock Test. "
                    "You may now click 'Xem đánh giá chi tiết' to generate your comprehensive 4-criteria Band report."
                )
                session.mode = "ielts_full_mock:completed"
                db.commit()
                turn_repo.create(session_id=req.session_id, role="assistant", transcript=closing_msg, owner_user_id=owner_user_id)
                return IeltsRespondResponse(
                    message=closing_msg,
                    tts_text=closing_msg,
                    is_completed=True,
                    next_part="completed"
                )

    # ==========================================================
    # FLOW 3: STANDALONE PART 1 OR PART 3
    # ==========================================================
    turns = turn_repo.get_by_session(req.session_id, owner_user_id)
    user_turns_count = len([t for t in turns if t.role == "user"])

    if user_turns_count >= 4:
        closing_msg = "Thank you very much. That is the end of the speaking test. You may now view your comprehensive assessment report."
        turn_repo.create(
            session_id=req.session_id,
            role="assistant",
            transcript=closing_msg,
            owner_user_id=owner_user_id
        )
        session.mode = f"{mode}:completed"
        db.commit()
        return IeltsRespondResponse(
            message=closing_msg,
            tts_text=closing_msg,
            is_completed=True,
            next_part="completed"
        )

    # Call AI Examiner for dynamic next prompt
    turn_dicts = [{"role": t.role, "content": t.transcript} for t in turns]
    messages = build_examiner_messages(
        part=req.part,
        turns=turn_dicts
    )

    model_router = get_model_router()
    examiner_reply = await model_router.chat(messages)

    turn_repo.create(
        session_id=req.session_id,
        role="assistant",
        transcript=examiner_reply,
        owner_user_id=owner_user_id
    )

    return IeltsRespondResponse(
        message=examiner_reply,
        tts_text=examiner_reply,
        is_completed=False,
        next_part=req.part
    )

@router.post("/evaluate/{session_id}", response_model=IeltsEvaluationResponse)
async def evaluate_ielts_session(session_id: str, request: Request, db: Session = Depends(get_db)):
    session_repo = SessionRepository(db)
    turn_repo = TurnRepository(db)

    owner_user_id = get_current_principal_id(request)
    user_id = get_current_user_id(request)
    session = session_repo.get(session_id, user_id, owner_user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Guard: Full Mock must not be evaluated if incomplete
    if session.mode and session.mode.startswith("ielts_full_mock") and session.mode != "ielts_full_mock:completed":
        raise HTTPException(
            status_code=400,
            detail={"error_code": "FULL_MOCK_INCOMPLETE", "message": "Full Mock test is incomplete. You must complete Part 1, Part 2, and Part 3 before generating an evaluation."}
        )

    # If already evaluated, return cached result
    if session.evaluation_json:
        try:
            cached_data = json.loads(session.evaluation_json)
            return IeltsEvaluationResponse(
                session_id=session.id,
                **cached_data
            )
        except Exception:
            pass

    turns = turn_repo.get_by_session(session_id, owner_user_id)
    turn_dicts = [{"role": t.role, "content": t.transcript} for t in turns]

    eval_messages = build_evaluation_messages(
        turns=turn_dicts,
        topic=session.topic
    )

    model_router = get_model_router()
    raw_eval = await model_router.chat(
        eval_messages,
        options={"timeout": settings.LLM_TIMEOUT},
    )
    eval_data = parse_evaluation(raw_eval)

    # Calculate actual speaking minutes from user turns (no hardcoding)
    user_words = sum(len(t['content'].split()) for t in turn_dicts if t['role'] == 'user')
    total_audio_ms = sum(t.duration_ms for t in turns if t.role == 'user' and t.duration_ms)
    if total_audio_ms > 0:
        actual_speaking_minutes = round(total_audio_ms / 60000.0, 2)
    else:
        # Standard IELTS rate ~120 words per minute
        actual_speaking_minutes = round(max(user_words / 120.0, 0.5), 2)

    # Persist in DB
    session.estimated_band = eval_data["overall_band"]
    session.evaluation_json = json.dumps(eval_data)
    session.total_speaking_ms = int(round(actual_speaking_minutes * 60000))
    session_repo.finish(session.id, user_id, owner_user_id)
    db.commit()

    # Record daily speaking progress with measured speaking minutes
    from app.repositories.progress_repo import ProgressRepository
    ProgressRepository(db).record_activity(
        user_id=session.user_id,
        speaking_minutes=actual_speaking_minutes,
        words=user_words,
        mistakes=len(eval_data.get("areas_for_improvement", [])),
        band=eval_data["overall_band"],
        owner_user_id=owner_user_id
    )

    return IeltsEvaluationResponse(
        session_id=session.id,
        overall_band=eval_data["overall_band"],
        fluency_score=eval_data["fluency_score"],
        fluency_feedback=eval_data["fluency_feedback"],
        lexical_score=eval_data["lexical_score"],
        lexical_feedback=eval_data["lexical_feedback"],
        grammar_score=eval_data["grammar_score"],
        grammar_feedback=eval_data["grammar_feedback"],
        pronunciation_score=eval_data["pronunciation_score"],
        strengths=eval_data["strengths"],
        areas_for_improvement=eval_data["areas_for_improvement"],
        suggested_expressions=[SuggestedExpression(**s) for s in eval_data["suggested_expressions"]],
        examiner_summary=eval_data["examiner_summary"],
        disclaimer="Estimated score — provisional practice estimate, not an official IELTS result.",
        score_status=eval_data.get("score_status", "provisional"),
        confidence=eval_data.get("confidence", 0.25),
        confidence_range=eval_data.get("confidence_range", "±1.0 band; calibration pending"),
        limitation=eval_data.get("limitation", "Pronunciation is not scored from transcript alone."),
        scoring_version=eval_data.get("scoring_version", "phase8-v1"),
        model_id=eval_data.get("model_id"),
        prompt_version=eval_data.get("prompt_version", "ielts-evaluation-v1")
    )

@router.post("/evaluate/{session_id}/feedback")
def submit_evaluation_feedback(session_id: str, data: EvaluationFeedbackRequest, request: Request, db: Session = Depends(get_db)):
    allowed = {"useful", "incorrect", "too_harsh", "too_vague"}
    if data.flag not in allowed:
        raise HTTPException(status_code=422, detail="Unsupported feedback flag")
    session = SessionRepository(db).get(session_id, get_current_user_id(request), get_current_principal_id(request))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    feedback = EvaluationFeedbackModel(
        session_id=session_id,
        owner_user_id=get_current_principal_id(request),
        flag=data.flag,
        comment=data.comment,
        scoring_version="phase8-v1",
    )
    db.add(feedback)
    db.commit()
    return {"status": "recorded", "flag": feedback.flag}
