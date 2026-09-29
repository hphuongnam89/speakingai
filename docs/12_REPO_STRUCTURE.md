# Recommended Repository Structure

```text
ielts-speaking-ai/
├── android/
│   ├── app/
│   ├── core/
│   └── feature/
│
├── backend/
│   ├── app/
│   ├── tests/
│   └── requirements.txt
│
├── docs/
│   ├── 00_MASTER_PLAN.md
│   ├── 01_ARCHITECTURE.md
│   ├── 02_DATABASE_SCHEMA.md
│   ├── 03_API_SPEC.md
│   └── ...
│
├── prompts/
├── scripts/
├── docker/
├── .env.example
├── docker-compose.yml
├── Makefile
└── README.md
```

## Recommended Branches
- main
- develop
- phase/1-core
- phase/2-tutor
- phase/3-ielts
- phase/4-progress
- phase/5-pronunciation

## MVP Environment Variables
```text
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3.5:9b
DEEPSEEK_API_KEY=
DEEPSEEK_ENABLED=false
DATABASE_URL=sqlite:///./data/app.db
```
