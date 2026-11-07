"""Build draft v0.2 content and local synthetic WAVs; requires macOS say at authoring time."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "backend/content/learning"


def main():
    manifest = json.loads((ROOT / "manifest.json").read_text())
    entries = []
    for skill in ("reading", "listening", "writing", "speaking"):
        lesson = json.loads((ROOT / f"{skill}-change.json").read_text())
        lesson["version"] = "0.2.0"
        if skill in {"writing", "speaking"}:
            for step in lesson["steps"]:
                if step["kind"] in {"independent", "transfer"}:
                    step["instruction"] = "Tự diễn đạt ý của bạn rồi nộp bài. Nhận góp ý theo mục tiêu sau khi hoàn thành lượt; giữ bản gốc để đối chiếu khi tự sửa."
        if skill == "listening":
            next(s for s in lesson["steps"] if s["kind"] == "self_repair")["instruction"] = "Tự xác định điểm cần kiểm tra: bạn hiểu từ viết không, nghe ra từ không, hay chỉ sai cách viết? Đối chiếu transcript rồi nghe lại. Nếu chưa rõ nguyên nhân, ghi chưa rõ thay vì tự kết luận."
        if skill in {"reading", "listening"}:
            review = lesson["steps"][-1]
            review["instruction"] = "Ôn sau 2/7 ngày: trả lời một câu mới chưa gặp. Nếu đã hết câu mới, cần bổ sung nội dung."
            review["stimulus"] = "We planned to meet on Monday. The meeting is now on Wednesday."
            review["items"] = [{"id": "r1", "prompt": "Ngày họp mới?", "answer": "Wednesday", "evidence": "The meeting is now on Wednesday."}]
            lesson["steps"].append({"id":"review7", "kind":"review", "instruction":review["instruction"],
                "stimulus":"The concert was outside. Because of wind, it will be inside.",
                "items":[{"id":"r2", "prompt":"Buổi hòa nhạc diễn ra ở đâu?", "answer":"inside", "evidence":"Because of wind, it will be inside."}]})
            for step in lesson["steps"]:
                for item in step.get("items", []):
                    if item.get("answer"):
                        item["max_words"] = 3
                        item["answer_variants"] = {"five": ["5"], "eleven": ["11"], "three": ["3"], "twenty": ["20"]}.get(item["answer"], [])
                if skill == "listening" and step.get("stimulus"):
                    filename = f"listening-020-{step['id']}.wav"
                    subprocess.run(["say", "-v", "Samantha", "-r", "145", "--data-format=LEI16@22050", "-o", str(ROOT / filename), step["stimulus"]], check=True)
                    step["audio_file"] = filename
                    step["audio_sha256"] = hashlib.sha256((ROOT / filename).read_bytes()).hexdigest()
        raw = (json.dumps(lesson, ensure_ascii=False, indent=2) + "\n").encode()
        name = f"{skill}-change-020.json"
        (ROOT / name).write_bytes(raw)
        entries.append({"file": name, "sha256": hashlib.sha256(raw).hexdigest()})
    manifest["lessons"] = entries
    manifest["audio_provenance"] = {"method": "macOS say", "voice": "Samantha", "synthetic": True, "human_reviewed": False}
    (ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
