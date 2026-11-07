from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LearningItem(StrictModel):
    id: str = Field(min_length=1, max_length=100)
    prompt: str = Field(min_length=1, max_length=2000)
    answer: str | None = Field(default=None, max_length=2000)
    evidence: str = Field(default="", max_length=2000)
    answer_variants: list[str] = Field(default_factory=list, max_length=20)
    max_words: int | None = Field(default=None, ge=1, le=200)


class LessonStep(StrictModel):
    id: str = Field(min_length=1, max_length=100)
    kind: Literal["explain", "worked_example", "guided", "independent", "feedback", "self_repair", "transfer", "review"]
    instruction: str = Field(min_length=1, max_length=5000)
    stimulus: str = Field(default="", max_length=5000)
    hints: list[str] = Field(default_factory=list, max_length=4)
    items: list[LearningItem] = Field(default_factory=list, max_length=12)
    audio_file: str | None = Field(default=None, pattern=r"^[a-z0-9_-]+\.wav$")
    audio_sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")


class Provenance(StrictModel):
    source: str
    license: str
    ai_assisted: bool
    reviewer_id: str | None = None
    reviewed_at: str | None = None


class Lesson(StrictModel):
    id: str = Field(min_length=1, max_length=100)
    version: str = Field(min_length=1, max_length=60)
    unit_id: str
    title: str
    skill: Literal["listening", "reading", "writing", "speaking"]
    objective: str
    competency_id: str
    prerequisites: list[str]
    status: Literal["draft", "validated", "pending_review", "approved", "published", "retired"]
    estimated_minutes: int = Field(ge=1, le=120)
    provenance: Provenance
    steps: list[LessonStep] = Field(min_length=8, max_length=32)

    @model_validator(mode="after")
    def check_content(self):
        required = {"explain", "worked_example", "guided", "independent", "feedback", "self_repair", "transfer", "review"}
        if not required.issubset({s.kind for s in self.steps}):
            raise ValueError("Lesson requires the complete learning cycle")
        step_ids = [s.id for s in self.steps]
        item_ids = [i.id for s in self.steps for i in s.items]
        if len(set(step_ids)) != len(step_ids) or len(set(item_ids)) != len(item_ids):
            raise ValueError("Duplicate step/item ID")
        for step in self.steps:
            for item in step.items:
                if item.answer is not None and (not item.evidence or item.evidence not in step.stimulus):
                    raise ValueError("Deterministic answers require stimulus evidence")
        independent = next(s for s in self.steps if s.kind == "independent")
        transfer = next(s for s in self.steps if s.kind == "transfer")
        if independent.stimulus and independent.stimulus.strip() == transfer.stimulus.strip():
            raise ValueError("Transfer must use a new stimulus")
        if self.status in {"approved", "published"}:
            if not self.provenance.reviewer_id or not self.provenance.reviewed_at or self.provenance.license.startswith("unassigned"):
                raise ValueError("Release requires reviewer, review date and license")
        return self


class AttemptCreate(StrictModel):
    lesson_id: str = Field(min_length=1, max_length=100)
    version: str = Field(min_length=1, max_length=60)
    request_id: str = Field(min_length=8, max_length=100)


class DraftUpdate(StrictModel):
    expected_revision: int = Field(ge=0)
    step_id: str = Field(min_length=1, max_length=100)
    draft: str = Field(max_length=12000)
    item_id: str | None = Field(default=None, max_length=100)
    evidence: str | None = Field(default=None, max_length=2000)


class ActivityRequest(StrictModel):
    request_id: str = Field(min_length=8, max_length=100)
    step_id: str = Field(min_length=1, max_length=100)


class SubmitRequest(ActivityRequest):
    item_id: str = Field(min_length=1, max_length=100)
    text: str = Field(min_length=1, max_length=12000)
    evidence: str = Field(default="", max_length=2000)
    turn_id: str | None = Field(default=None, max_length=100)


class ExposureRequest(ActivityRequest):
    kind: Literal["transcript", "replay"]


class RescheduleRequest(StrictModel):
    days: int = Field(ge=1, le=30)


class TutorRequest(ActivityRequest):
    question: str = Field(min_length=1, max_length=2000)


class TutorFeedback(StrictModel):
    claim_type: Literal["explanation", "error", "suggestion", "valid_alternative"]
    explanation: str = Field(min_length=1, max_length=4000)
    next_action: str = Field(min_length=1, max_length=1000)
    source_step_id: str


class ObjectiveFeedbackRequest(ActivityRequest):
    item_id: str = Field(min_length=1, max_length=100)


class Annotation(StrictModel):
    start: int = Field(ge=0)
    end: int = Field(ge=1)
    quote: str = Field(min_length=1, max_length=2000)
    comment: str = Field(min_length=1, max_length=1000)


class ObjectiveFeedback(TutorFeedback):
    criteria: list[str] = Field(min_length=1, max_length=3)
    annotations: list[Annotation] = Field(default_factory=list, max_length=3)
