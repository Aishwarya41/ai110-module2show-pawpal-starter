# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
The user should be able to add a pet, schedule a walk, see today's tasks.

- What classes did you include, and what responsibilities did you assign to each?
Four classes:

Owner
Attributes: name, contact, pets, preferences
Methods: addPet(), updateInfor()

Pet
Attributes: name, species, breed, tasks
Method: addTask(), removeTask(), getTasks()

Tasks
Attributes: name, duration, priority, category, is Completed(), notes
Methods: editTask(), markCompleted()

Schedule
Attributes: date, scheduledItems, totalTime
Methods: generatePlan(owner, tasks), explainPlan(), getSummary()

**b. Design changes**

- Did your design change during implementation?
Yes

- If yes, describe at least one change and why you made it.

Yes, the design changed in two rounds.

First, Schedule had no start times or reasons. I added a small ScheduledItem dataclass (task, start_time, reason) and made scheduled_items a list of those. The class also became Scheduler, since it does the planning.

Second, when I added the smarter scheduling features, I added:
- Task.due_date, so a recurring task's next copy isn't scheduled until the day it is due.
- next_occurrence() and complete_task(), so finishing a daily or weekly task creates the next one on the same pet.
- filter_tasks() and sort_by_time(), so tasks can be filtered by pet or status and ordered by time.
- detect_conflicts() and a conflicts list, so overlapping tasks produce warnings.

The final design is in diagrams/uml_final.mmd.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
Some constraints that the scheduler considers are:
    - Time budget: the owner's available_minutes caps the total length of the day's plan.
    - Priority: each task is high, medium or low.
    - Preferred time: a task can have a time it should start, such as breakfast at 08:00.
    - Completion status: tasks already done are skipped.

- How did you decide which constraints mattered most?
I decided that the time budget mattered the most, then the priority and then the preferred time. A plan that doesn't fit in the owner's day is useless, so anything that doesn't fit is left out and listed as unscheduled. This order worked because pet care has things that can't be skipped (meds, food) and things that are nice to have (play, brushing). Ranking by priority within the time limit reflects that.


**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
One tradeoff is that the scheduler warns about conflicts but does not resolve them. The scheduler checks whether two tasks' time slots overlap (start time through start time plus duration), not just whether they start at the same minute. It reports a warning like "'Play session' (Mia, 17:00) overlaps 'Nail trim' (Mia, 17:10)". It does not decide which task should move. The planner only pushes the lower-priority task later, so the final plan never double-books.

- Why is that tradeoff reasonable for this scenario?
The scheduler can't know what the owner actually wants. Two tasks at 12:00 might be a real mistake, or the owner might be able to do both at once, like feeding one pet while walking another. A warning keeps the owner in control, never crashes, and is simple enough to test.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used AI at every stage. It helped me design the classes and find gaps in my first UML, then wrote the skeleton and the implementation. Later it added sorting, filtering, recurring tasks and conflict detection, wrote the tests, docstrings and README, and helped me simplify code. I worked in small steps and asked for one change at a time.

- What kinds of prompts or questions were most helpful?
Asking "do you notice any missing relationships or potential logic bottlenecks?" about my own skeleton surfaced real problems, such as the schedule having no start times or reasons. Asking for a list of possible improvements before building anything also helped, because I could choose which ones to keep.

- How did using separate chat sessions for different phases help you stay organized?
I treated the project as phases (design and UML, core logic, scheduling algorithms, then tests and docs) and started a fresh chat for each. Each chat had one clear goal, so the AI wasn't carrying old, half-finished ideas into new work. 

- Summarize what you learned about being the "lead architect" when collaborating with powerful AI tools.
The AI is fast and offers many ideas, but it doesn't know what the project needs. My job was to decide the design, choose which suggestions to keep, and check the results. I kept the design small by turning down extra features, and I chose the more readable code over the cleverer version. I learned to verify everything by running main.py and the tests.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
The AI suggested many additions, including specialNeeds, dueTime, frequency and a separate schedule entry class, and later a long list of scheduling improvements. I only took a subset to keep the design simple, and dropped the per-field getters since plain attributes cover that. When it offered two ways to detect overlaps, I kept the simpler version that is easier to read, even though the other skips some comparisons.

- How did you evaluate or verify what the AI suggested?
I ran main.py and read the actual output. That caught a real mistake: an AI edit shifted a list index, so the wrong tasks were marked done, and I only noticed because the output looked wrong. I also ran the tests with pytest, and checked edge cases by hand before writing them up, which corrected two claims that turned out to be wrong.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
I tested sorting, recurring tasks, conflict detection and plan generation:
    - Sorting: chronological order, flexible tasks last, ties keep their order, empty list.
    - Recurring tasks: daily and weekly tasks create the next copy, "once" tasks don't, and completing twice makes no duplicate.
    - Conflict detection: overlaps are flagged across pets, back-to-back tasks aren't, and a bad time warns instead of crashing.
    - Plan generation: priority order, the time budget, and a task that doesn't fit being skipped.

- Why were these tests important?
A wrong order, a dropped medication or a double-booked slot affects a real pet, and many of these bugs are silent, so only a test would catch them.

**b. Confidence**

- How confident are you that your scheduler works correctly?
Confidence Level: 4 out of 5
All 24 tests pass, and they cover the three required areas: sorting, recurrence and conflict detection. I'm not at 5 because the Streamlit app and unusual input aren't tested.

- What edge cases would you test next if you had more time?
I found these by hand and would turn them into tests:
    - A bad time like "abc" crashes `sort_by_time` and `generate_plan`. I would validate times when a task is created.
    - `complete_task` on a task with no pet creates a next copy that is lost.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied with the scheduling features and how they fit together. Sorting, filtering, recurring tasks and conflict warnings all work from the same Scheduler and show up in both main.py and the app. 

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would make the planner and the conflict check agree. Right now conflicts are only checked on the times the owner asked for, so the planner can move a fixed-time task later with no warning. I would also validate times when a task is created.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

One important thing I learned is that the AI can write code quickly, but I have to decide what the system should do and check that it does it. Small steps, one change at a time, with a run of main.py or the tests after each, caught mistakes early, including some the AI made in its own code. Being clear about the design before asking for code mattered more than anything I typed into a prompt.
