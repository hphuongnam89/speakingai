import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.session import SessionModel
from app.repositories.session_repo import SessionRepository
from app.repositories.turn_repo import TurnRepository
from app.services.llm.router import get_model_router
from app.data.ielts_bank import get_random_part_1, get_random_part_2, get_cue_card_by_id
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
    SuggestedExpression
)

router = APIRouter(prefix="/ielts", tags=["ielts"])

@router.post("/start", response_model=IeltsStartResponse)
async def start_ielts_test(req: IeltsStartRequest, db: Session = Depends(get_db)):
    session_repo = SessionRepository(db)
    turn_repo = TurnRepository(db)

    part = req.part.lower()
    cue_card_obj = None
    greeting = ""
    first_question = ""
    topic_name = "IELTS Speaking"

    if part == "part1":
        p1 = get_random_part_1()
        topic_name = f"IELTS Part 1: {p1['topic']}"
        greeting = "Good day. Welcome to the IELTS Speaking test. In this first part, I would like to ask you some questions about yourself."
        first_question = p1["questions"][0]
    elif part == "part2":
        p2 = get_random_part_2()
        topic_name = f"IELTS Part 2: {p2['topic']}"
        cue_card_obj = CueCard(
            id=p2["id"],
            topic=p2["topic"],
            title=p2["title"],
            bullets=p2["bullets"],
            follow_up=p2.get("follow_up"),
            part_3_questions=p2.get("part_3_questions")
        )
        greeting = "Now, in Part 2, I'm going to give you a topic and I'd like you to talk about it for one to two minutes. Before you talk, you'll have one minute to think about what you are going to say."
        first_question = f"{p2['title']} Please prepare your answer."
    elif part == "part3":
        p2 = get_random_part_2()
        topic_name = f"IELTS Part 3: Discussion on {p2['topic']}"
        greeting = "Now we've been talking about a personal topic, and I'd like to discuss with you one or two more general questions related to this."
        first_question = p2["part_3_questions"][0] if p2.get("part_3_questions") else "Why do you think people place so much importance on this topic in society?"
    else:  # full_mock
        p1 = get_random_part_1()
        topic_name = f"IELTS Full Mock Test (Starts with {p1['topic']})"
        greeting = "Hello. My name is your IELTS Examiner. Could you please state your full name to begin?"
        first_question = p1["questions"][0]

    # Create session
    session = session_repo.create(
        mode=f"ielts_{part}",
        topic=topic_name
    )

    # Save examiner greeting as initial turn
    full_examiner_intro = f"{greeting} {first_question}".strip()
    turn_repo.create(
        session_id=session.id,
        role="assistant",
        transcript=full_examiner_intro
    )

    return IeltsStartResponse(
        session_id=session.id,
        part=part,
        cue_card=cue_card_obj,
        greeting=greeting,
        question=first_question
    )

@router.post("/respond", response_model=IeltsRespondResponse)
async def respond_ielts_turn(req: IeltsRespondRequest, db: Session = Depends(get_db)):
    session_repo = SessionRepository(db)
    turn_repo = TurnRepository(db)

    session = session_repo.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 1. Save candidate turn
    turn_repo.create(
        session_id=req.session_id,
        role="user",
        transcript=req.user_text
    )

    # 2. Get past turns
    turns = turn_repo.get_by_session(req.session_id)
    turn_dicts = [{"role": t.role, "content": t.transcript} for t in turns]
    user_turns_count = len([t for t in turns if t.role == "user"])

    # If it's Part 2, candidate's long turn is complete!
    if "part2" in session.mode:
        closing_msg = "Thank you very much. That concludes Part 2 of your speaking test."
        turn_repo.create(
            session_id=req.session_id,
            role="assistant",
            transcript=closing_msg
        )
        return IeltsRespondResponse(
            message=closing_msg,
            tts_text=closing_msg,
            is_completed=True
        )

    # If Part 1 or Part 3 reached ~4-5 user answers, conclude the test
    if user_turns_count >= 5:
        closing_msg = "Thank you very much. That is the end of the speaking test. You may now view your comprehensive assessment report."
        turn_repo.create(
            session_id=req.session_id,
            role="assistant",
            transcript=closing_msg
        )
        return IeltsRespondResponse(
            message=closing_msg,
            tts_text=closing_msg,
            is_completed=True
        )

    # 3. Call Ollama Examiner for next prompt/question
    messages = build_examiner_messages(
        part=req.part,
        turns=turn_dicts
    )

    model_router = get_model_router()
    examiner_reply = await model_router.chat(messages)

    # Save examiner turn
    turn_repo.create(
        session_id=req.session_id,
        role="assistant",
        transcript=examiner_reply
    )

    return IeltsRespondResponse(
        message=examiner_reply,
        tts_text=examiner_reply,
        is_completed=False
    )

@router.post("/evaluate/{session_id}", response_model=IeltsEvaluationResponse)
async def evaluate_ielts_session(session_id: str, db: Session = Depends(get_db)):
    session_repo = SessionRepository(db)
    turn_repo = TurnRepository(db)

    session = session_repo.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

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

    turns = turn_repo.get_by_session(session_id)
    turn_dicts = [{"role": t.role, "content": t.transcript} for t in turns]

    eval_messages = build_evaluation_messages(
        turns=turn_dicts,
        topic=session.topic
    )

    model_router = get_model_router()
    raw_eval = await model_router.chat(eval_messages)
    eval_data = parse_evaluation(raw_eval)

    # Persist in DB
    session.estimated_band = eval_data["overall_band"]
    session.evaluation_json = json.dumps(eval_data)
    db.commit()

    # Record daily speaking progress
    from app.repositories.progress_repo import ProgressRepository
    user_words = sum(len(t['content'].split()) for t in turn_dicts if t['role'] == 'user')
    ProgressRepository(db).record_activity(
        user_id=session.user_id,
        speaking_minutes=2.5,
        words=user_words,
        mistakes=len(eval_data.get("areas_for_improvement", [])),
        band=eval_data["overall_band"]
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
        examiner_summary=eval_data["examiner_summary"]
    )
