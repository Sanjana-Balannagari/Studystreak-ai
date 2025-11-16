STUDYSTREAK-AI – Phase 1 Kickoff
Goal: Repo live, roles clear, DB ready

Features (MVP)
- Auth (Login / Register)
- Log Session (topic, minutes, date)
- Dashboard → Streak heatmap (7-day), total hrs, top topic
- AI Chat → 4 tools:
   1. log_session(topic, minutes)
   2. get_streak()
   3. create_plan(goal)
   4. generate_motivation()

Bonus (20% creativity): Voice logging via browser mic

Roles
- Backend Lead: [Name]
- Frontend/UI Lead: [Name] → Figma + Tailwind
- AI Specialist: [Name] → OpenAI tools
- DevOps/Docs Lead: [Name] → GitHub + Railway + Video

Next: Repo setup → Figma → DB init

PHASE 2: CORE MVP (4–5 hrs)
Goal: Login → Log → Dashboard (streak) → AI Chat (4 tools)

BRANCHES:
- backend → auth + /log + streak calc
- frontend → templates + Chart.js
- ai → OpenAI tools + /chat
- main ← merge all

TEST: http://localhost:5000
→ Login → Log 30 min Python → Dashboard shows streak → AI: "Motivate me" → "You're on fire!"

Let’s go!
PHASE 3: POLISH & DEPLOY (2 hrs)
Goal: Voice input + Live on Railway + README + Demo

BRANCHES
├─ ui-voice → Web Speech API for Log page
├─ deploy   → Railway config + env
└─ main ← merge all

TEST: https://studystreak-ai.up.railway.app
→ Login → Hold mic → "Log 45 min Python" → AI confirms → Dashboard updates

Let’s ship!
