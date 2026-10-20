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

Today's Schedule

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

## ✨ Features

- **Priority-based daily planning.** `generate_plan()` orders pending tasks by priority (high, medium, low), then preferred time, then shorter duration. It places them one after another starting at the day's start time.
- **Time budget.** Tasks that would push the day past the owner's `available_minutes` are left out and listed as not scheduled. A shorter task later in the list can still fit into the leftover time.
- **Preferred start times.** A task starts at its preferred time, or right after the previous task if that is later. A task can therefore start later than requested when earlier tasks run long.
- **Plan explanations.** Every scheduled task carries a reason (priority, preferred time, budget), shown by `explain_plan()`. Skipped tasks are listed with why.
- **Sorting by time.** `sort_by_time()` orders tasks by preferred start time, earliest first. Tasks with no time go last, and ties keep their original order.
- **Filtering.** `filter_tasks()` and `get_tasks()` keep tasks by pet name, completion status, or both.
- **Conflict warnings.** `detect_conflicts()` compares every pair of timed tasks and warns when their time slots overlap, whether they belong to the same pet or different pets. Back-to-back tasks aren't flagged. It returns messages and never crashes, and `generate_plan()` includes the warnings in the summary. Conflicts are reported, not automatically resolved.
- **Daily and weekly recurrence.** `complete_task()` marks a task done and adds a new copy to the same pet, due 1 day later for "daily" or 7 days later for "weekly". "Once" tasks don't repeat, and completing a task twice doesn't create duplicates.
- **Due-date awareness.** The planner skips tasks that aren't due yet, so tomorrow's recurring copy doesn't appear in today's plan.
- **Multi-pet support.** The scheduler reads tasks through the owner, so one plan covers all of an owner's pets.

**Not included:** automatic rescheduling to resolve conflicts, weekday-specific recurrence (such as "every Tuesday"), time-format validation when a task is created, and optimal task selection (the planner is greedy, so it doesn't maximize the total value of what fits).

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

### The Streamlit app (`streamlit run app.py`)

The page is a single scrolling screen, top to bottom:

- **Owner:** edit the owner's name and the minutes available today (10 to 1440). This is the time budget the planner works within.
- **Pets:** enter a name and species (dog, cat, other) and click **Add pet**. Empty and duplicate names are rejected with an error.
- **Tasks:** pick a pet, then enter a title, duration, priority and an optional preferred time in `HH:MM`. Click **Add task**. A badly formatted time is rejected with an error.
- **Task list:** a table of every task, always sorted by preferred time with flexible tasks last. Two dropdowns filter it by pet and by status (All, Pending, Completed). Each row shows the repeat setting and due date.
- **Conflict banner:** appears as soon as two timed tasks overlap, before any schedule is built. It lists each overlap, or shows a green "no conflicts" message.
- **Mark done:** choose a pending task and click **Mark done**. Daily and weekly tasks create their next copy, and a message says when it is due.
- **Build Schedule:** click **Generate schedule** to see tasks scheduled, time used and time left, the ordered plan, any conflict warnings, a "Why this plan?" explanation, and an error listing tasks that didn't fit in the day.

### Example workflow

1. Set the owner's name and available time, for example 120 minutes.
2. Add a pet, such as Buddy the dog, then add a second pet, Mia the cat.
3. Add tasks for each pet: a 30-minute high-priority walk at 07:30 for Buddy, and a 5-minute high-priority medication at 12:00 for Mia. Add them in any order.
4. Check the task list. It is sorted by time whatever order you added them in. Filter to Mia's pending tasks to see only hers.
5. Add a second task at 12:00. The conflict banner appears right away and names both tasks.
6. Click **Generate schedule** to see the day's plan and the reasons for each placement. The later of two overlapping tasks starts after the first one finishes.
7. Click **Mark done** on a daily task. The next copy is due tomorrow, so it won't be in today's plan if you generate again.

### Scheduler behaviors on show

- **Sorting by time:** tasks added out of order come back earliest first (`Scheduler.sort_by_time`).
- **Filtering:** the task list and the CLI demo both filter by pet and completion status (`Scheduler.filter_tasks`).
- **Conflict warnings:** overlapping tasks are reported for the same pet and across pets, without crashing (`Scheduler.detect_conflicts`).
- **Priority planning with a time budget:** high-priority tasks are placed first, and anything that doesn't fit is listed as not scheduled (`Scheduler.generate_plan`).
- **Recurring tasks:** completing a daily or weekly task adds the next occurrence (`Scheduler.complete_task`).

### Sample CLI output (`python main.py`)

`main.py` adds tasks out of order, marks two as done, and adds three deliberate conflicts: Vet call and Give medication both at 12:00 (different pets), Clean litter box and Play session both at 17:00 (same pet), and Nail trim at 17:10, which overlaps Play session.

```
All tasks, as added:
  18:00  Brush coat (Buddy, todo)
  --:--  Training (Buddy, todo)
  07:30  Morning walk (Buddy, done)
  12:00  Vet call (Buddy, todo)
  17:00  Play session (Mia, todo)
  12:00  Give medication (Mia, todo)
  08:00  Breakfast (Mia, done)
  17:10  Nail trim (Mia, todo)
  17:00  Clean litter box (Mia, todo)

All tasks, sorted by time:
  07:30  Morning walk (Buddy, done)
  08:00  Breakfast (Mia, done)
  12:00  Vet call (Buddy, todo)
  12:00  Give medication (Mia, todo)
  17:00  Play session (Mia, todo)
  17:00  Clean litter box (Mia, todo)
  17:10  Nail trim (Mia, todo)
  18:00  Brush coat (Buddy, todo)
  --:--  Training (Buddy, todo)

Mia's tasks:
  17:00  Play session (Mia, todo)
  12:00  Give medication (Mia, todo)
  08:00  Breakfast (Mia, done)
  17:10  Nail trim (Mia, todo)
  17:00  Clean litter box (Mia, todo)

Completed tasks:
  07:30  Morning walk (Buddy, done)
  08:00  Breakfast (Mia, done)

Pending tasks:
  18:00  Brush coat (Buddy, todo)
  --:--  Training (Buddy, todo)
  12:00  Vet call (Buddy, todo)
  17:00  Play session (Mia, todo)
  12:00  Give medication (Mia, todo)
  17:10  Nail trim (Mia, todo)
  17:00  Clean litter box (Mia, todo)

Buddy's pending tasks, sorted by time:
  12:00  Vet call (Buddy, todo)
  18:00  Brush coat (Buddy, todo)
  --:--  Training (Buddy, todo)

========================================
Today's Schedule
========================================
Plan for Jordan on 2026-10-19
  12:00  Give medication - Mia (5 min, high)
  12:05  Vet call - Buddy (15 min, medium)
  17:00  Clean litter box - Mia (5 min, medium)
  17:05  Play session - Mia (25 min, medium)
  17:30  Training - Buddy (15 min, medium)
  17:45  Nail trim - Mia (10 min, low)
  18:00  Brush coat - Buddy (20 min, low)
Total: 95 of 120 minutes
Warning: 'Vet call' (Buddy, 12:00) overlaps 'Give medication' (Mia, 12:00) [different pets].
Warning: 'Play session' (Mia, 17:00) overlaps 'Nail trim' (Mia, 17:10) [same pet].
Warning: 'Play session' (Mia, 17:00) overlaps 'Clean litter box' (Mia, 17:00) [same pet].

Conflicts:
Warning: 'Vet call' (Buddy, 12:00) overlaps 'Give medication' (Mia, 12:00) [different pets].
Warning: 'Play session' (Mia, 17:00) overlaps 'Nail trim' (Mia, 17:10) [same pet].
Warning: 'Play session' (Mia, 17:00) overlaps 'Clean litter box' (Mia, 17:00) [same pet].

Why this plan:
12:00 Give medication (Mia): High priority, preferred time 12:00; fits within 120 available minutes
12:05 Vet call (Buddy): Medium priority, preferred time 12:00; fits within 120 available minutes
17:00 Clean litter box (Mia): Medium priority, preferred time 17:00; fits within 120 available minutes
17:05 Play session (Mia): Medium priority, preferred time 17:00; fits within 120 available minutes
17:30 Training (Buddy): Medium priority; fits within 120 available minutes
17:45 Nail trim (Mia): Low priority, preferred time 17:10; fits within 120 available minutes
18:00 Brush coat (Buddy): Low priority, preferred time 18:00; fits within 120 available minutes
```
