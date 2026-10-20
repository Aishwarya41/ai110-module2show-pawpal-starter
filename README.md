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

**Known limits:** conflicts are reported as warnings but not resolved, priority is a plain string (`high`, `medium`, `low`), and times are not validated when a task is created. See Smarter Scheduling below for what the scheduler does beyond the basic plan.

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

Run the full test suite from the project root:

```bash
python -m pytest
```

Add `-v` to list each test by name. The tests are in `tests/test_pawpal.py` and cover the scheduling logic in `pawpal_system.py`:

- **Sorting:** tasks come back in chronological order, times compare as numbers ("9:00" before "10:00"), flexible tasks go last, ties keep their original order, and the input list isn't changed. The plan itself orders by priority, then time.
- **Recurring tasks:** completing a daily task adds a copy due the next day to the same pet, weekly tasks recur 7 days later, "once" tasks don't recur, completing a task twice creates no duplicate, and year-end dates roll over. Tomorrow's copy is left out of today's plan.
- **Conflict detection:** duplicate start times and overlaps are flagged, including across different pets. Back-to-back tasks, flexible tasks and unreadable times don't cause false alarms or crashes.
- **Plan generation:** the daily time budget is respected (inclusive at the limit), a task that doesn't fit is skipped while a later short one is still scheduled, regenerating the plan gives the same result, and an empty plan is handled.

Expected result:
```
================ 24 passed in 0.13s ======================
```

Confidence Level: 4 out of 5
All 24 tests pass, and they cover the three required areas: sorting, recurrence and conflict detection.

## 📐 Smarter Scheduling

All of these live in `pawpal_system.py`. `main.py` demonstrates each one in the terminal.

| Feature | Method(s) | What it does |
|---------|-----------|--------------|
| Sorting by time | `Scheduler.sort_by_time()` | Orders tasks by preferred start time, earliest first |
| Filtering | `Scheduler.filter_tasks()`, `Scheduler.get_tasks()` | Keeps tasks matching a pet name and/or completion status |
| Conflict detection | `Scheduler.detect_conflicts()` | Returns a warning for each pair of overlapping timed tasks |
| Recurring tasks | `Task.next_occurrence()`, `Task.mark_completed()`, `Scheduler.complete_task()` | Creates the next daily or weekly task when one is completed |

### Sorting by time: `Scheduler.sort_by_time(tasks)`

- Compares times as minutes since midnight rather than as text.
- A time that isn't in `HH:MM` form raises a `ValueError`.
- Tasks with no preferred time (flexible) go last.
- Tasks with the same time keep the order they were added in.
- Returns a new list and leaves the original unchanged.

This is separate from the plan's own ordering. `generate_plan()` still sorts by priority first (via `Scheduler._sort_key`), then preferred time, then duration.

### Filtering: `Scheduler.filter_tasks(tasks, pet_name=None, completed=None)`

- `pet_name="Mia"` keeps only Mia's tasks.
- `completed=True` keeps finished tasks and `completed=False` keeps pending ones.
- A filter left as `None` is ignored, and when both are given a task must match both.
- `Scheduler.get_tasks(pet_name, completed)` applies the same filters to all of the owner's pets' tasks.
- Filtering and sorting chain: `Scheduler.sort_by_time(scheduler.filter_tasks(tasks, pet_name="Buddy", completed=False))`.

### Conflict detection: `Scheduler.detect_conflicts(tasks=None)`

- Each task with a preferred time occupies the slot from its start to start + duration. Two tasks conflict when each starts before the other ends, so a task that starts exactly when another ends is not a conflict.
- It checks every pair of tasks, both for the same pet and across different pets, because the owner can only do one thing at a time.
- It returns warning strings and never raises. A task with an unreadable time gets its own warning and is skipped.
- `generate_plan()` runs it automatically and stores the result in `scheduler.conflicts`. `get_summary()` prints the warnings.

Example warnings:

```
Warning: 'Vet call' (Buddy, 12:00) overlaps 'Give medication' (Mia, 12:00) [different pets].
Warning: 'Play session' (Mia, 17:00) overlaps 'Nail trim' (Mia, 17:10) [same pet].
```

Tradeoff: conflicts are only reported. The planner still moves the later task back so the final schedule never double-books, but it does not ask the owner which task should win.

### Recurring tasks

- `Task.next_occurrence()` builds the next copy of a task. `"daily"` adds 1 day and `"weekly"` adds 7 days to its `due_date` (or to today if it has none). `"once"` tasks return `None`.
- `Task.mark_completed()` marks the task done and returns that next copy. Completing a task a second time returns `None`, so it can't create duplicates.
- `Scheduler.complete_task(task)` is the method to call in the app. It marks the task done and adds the new copy to the same pet.
- `generate_plan()` skips tasks whose `due_date` is after the plan's date, so tomorrow's copy doesn't appear in today's plan.

```python
scheduler.complete_task(walk)   # walk is done; a new walk due tomorrow is added to the same pet
```

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

