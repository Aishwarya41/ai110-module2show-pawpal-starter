# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🛠️ Implementation Summary

The core logic lives in `pawpal_system.py` (backend only, no UI yet). `main.py` is a demo script that runs it in the terminal.

**Classes**

- `Task` (dataclass): one activity with a name, duration, priority, optional preferred time, frequency and completion status. `mark_completed()` and `edit_task()` update it.
- `Pet` (dataclass): pet details plus its own list of tasks. `add_task()` also stamps the task with the pet's name.
- `Owner`: holds a list of pets and a daily time budget (`available_minutes`). `get_all_tasks()` returns every pet's tasks in one list.
- `Scheduler`: the "brain". It reads tasks through `owner.get_all_tasks()`, so it works across all of an owner's pets, not just one.

**How they work together**

1. An `Owner` has many `Pet`s, and each `Pet` has many `Task`s.
2. `Scheduler` is created with an owner and asks it for all tasks, skipping completed ones.
3. `generate_plan()` sorts the tasks by priority, then preferred time, then duration, and places them starting at 08:00 (or at their preferred time if later).
4. Tasks that no longer fit in the owner's `available_minutes` go to `unscheduled_tasks`.
5. Each placed task becomes a `ScheduledItem` (task, start time, reason). `get_summary()` and `explain_plan()` print the plan and the reasoning.

**Known limits:** `frequency` is stored but not acted on yet (no recurring tasks), preferred times are soft hints with no conflict detection, and priority is a plain string (`high`, `medium`, `low`).

## 🖥️ Sample Output

========================================
Today's Schedule
========================================
Plan for Jordan on 2026-10-19
  08:00  Morning walk - Buddy (30 min, high)
  08:30  Breakfast - Mia (10 min, high)
  12:00  Give medication - Mia (5 min, high)
  17:00  Play session - Mia (25 min, medium)
  18:00  Brush coat - Buddy (20 min, low)
Total: 90 of 120 minutes

Why this plan:
08:00 Morning walk (Buddy): High priority, preferred time 07:30; fits within 120 available minutes
08:30 Breakfast (Mia): High priority, preferred time 08:00; fits within 120 available minutes
12:00 Give medication (Mia): High priority, preferred time 12:00; fits within 120 available minutes
17:00 Play session (Mia): Medium priority, preferred time 17:00; fits within 120 available minutes
18:00 Brush coat (Buddy): Low priority, preferred time 18:00; fits within 120 available minutes

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

