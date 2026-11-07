"""Versioned server-side authoring catalog; answer keys never go to lesson clients."""
import hashlib
import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.learning import LearningLessonModel
from app.schemas.learning import Lesson

CONTENT_DIR = Path(__file__).resolve().parents[2] / "content" / "learning"


def read_pack(directory: Path = CONTENT_DIR) -> list[Lesson]:
    manifest = json.loads((directory / "manifest.json").read_text())
    lessons = []
    for entry in manifest["lessons"]:
        source = (directory / entry["file"]).resolve()
        if source.parent != directory.resolve() or source.suffix != ".json":
            raise ValueError("Invalid content path")
        raw = source.read_bytes()
        if hashlib.sha256(raw).hexdigest() != entry["sha256"]:
            raise ValueError(f"Checksum mismatch: {source.name}")
        lessons.append(Lesson.model_validate_json(raw))
        for step in lessons[-1].steps:
            if step.audio_file:
                asset = directory / step.audio_file
                if not asset.is_file() or hashlib.sha256(asset.read_bytes()).hexdigest() != step.audio_sha256:
                    raise ValueError("Missing or corrupt audio asset")
    ids = [lesson.id for lesson in lessons]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate lesson ID")
    competencies = set(manifest["competencies"])
    graph = {l.competency_id: l.prerequisites for l in lessons}
    for lesson in lessons:
        if lesson.competency_id not in competencies or not set(lesson.prerequisites) <= competencies:
            raise ValueError("Unknown competency reference")
        checked = set()

        def visit(node, trail):
            if node in trail:
                raise ValueError("Cyclic prerequisites")
            if node in checked:
                return
            for prerequisite in graph.get(node, []):
                visit(prerequisite, trail | {node})
            checked.add(node)

        visit(lesson.competency_id, set())
    return lessons


def import_pack(db: Session, directory: Path = CONTENT_DIR) -> dict:
    lessons = read_pack(directory)
    legacy = [Lesson.model_validate_json(path.read_bytes()) for path in directory.glob("*-change.json")]
    for lesson in legacy + lessons:
        payload = lesson.model_dump_json()
        checksum = hashlib.sha256(payload.encode()).hexdigest()
        existing = db.get(LearningLessonModel, (lesson.id, lesson.version))
        if existing and existing.checksum != checksum and (
            hashlib.sha256(existing.payload_json.encode()).hexdigest() != existing.checksum
            or Lesson.model_validate_json(existing.payload_json).model_dump() != lesson.model_dump()
        ):
            raise ValueError("Content version is immutable; increment version before editing")
        if not existing:
            db.add(LearningLessonModel(id=lesson.id, version=lesson.version, checksum=checksum, payload_json=payload))
    db.commit()
    return {"validated": len(lessons), "approved": sum(l.status in {"approved", "published"} for l in lessons)}


def learner_lesson(lesson: Lesson) -> dict:
    data = lesson.model_dump(exclude={"steps"})
    data["steps"] = [
        {"id": step.id, "kind": step.kind, "instruction": step.instruction,
         "stimulus": "" if lesson.skill == "listening" and step.audio_file else step.stimulus,
         "audio_url": f"/api/v1/learning/media/{lesson.id}/{lesson.version}/{step.id}" if step.audio_file else None,
         "items": [{"id": item.id, "prompt": item.prompt} for item in step.items]}
        for step in lesson.steps
    ]
    return data


if __name__ == "__main__":
    print(json.dumps({"validated": len(read_pack()), "notice": "Validation is not human approval"}))
