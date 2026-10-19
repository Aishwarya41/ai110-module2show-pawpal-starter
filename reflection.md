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
- If yes, describe at least one change and why you made it.

Schedule had no start times or reasons.
The change was to add a small ScheduledItem dataclass (task, start_time, reason) and make scheduled_items a list of those.

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
One tradeoff that this scheduler makes is that it sorts by priority first and places tasks in that order, one after another. It does not check for overlaps with a task's preferred time. A lower-priority task with an earlier preferred time can end up after a higher-priority one, and a task's start time can be pushed later than the owner asked for.

- Why is that tradeoff reasonable for this scenario?
This tradeoff is reasonable because it keeps the logic simple and predictable, which suits a first version. It guarantees the important tasks get done within the available time, which matters more than hitting an exact minute.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used AI at each stage. It helped me design the classes, pointed out gaps in my first UML, wrote the skeleton and then the implementation, and helped with the tests. I worked in small steps and asked it to fix one issue at a time.

- What kinds of prompts or questions were most helpful?
Asking "do you notice any missing relationships or potential logic bottlenecks?" about my own skeleton. That surfaced real problems, such as the schedule having no start times or reasons and no link between a task and its pet.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
A moment I didn't accept an AI suggestion as-is was with selective adoption. I suggested many additions, including specialNeeds, dueTime, frequency and a separate Schedule entry class. I only took a subset into my UML to keep the design simple. I also took the advice to drop the per-field getters, since plain attributes cover that.


- How did you evaluate or verify what the AI suggested?
I ran main.py and read the actual output. I wrote tests for task completion and for adding tasks to a pet, and ran them with pytest. I confirmed the Scheduler reads tasks through the Owner's get_all_tasks() and not from a single pet, since the project requires multi-pet support.


---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
