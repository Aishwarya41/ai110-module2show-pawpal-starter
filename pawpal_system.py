from dataclasses import dataclass, field, replace
from datetime import date as Date, timedelta
from itertools import combinations

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
RECURRENCE_DAYS = {"daily": 1, "weekly": 7}


def _to_minutes(hhmm: str) -> int:
    """Convert an "HH:MM" string to minutes since midnight."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


def _to_hhmm(minutes: int) -> str:
    """Convert minutes since midnight to an "HH:MM" string."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


@dataclass
class Task:
    name: str
    duration: int  # minutes
    priority: str = "medium"  # "high", "medium", "low"
    time: str = ""  # preferred start time "HH:MM"; empty means flexible
    frequency: str = "daily"  # "once", "daily", "weekly"
    category: str = ""
    is_completed: bool = False
    notes: str = ""
    pet_name: str = ""  # set by Pet.add_task
    due_date: Date | None = None  # day the task is due; None means always due

    def edit_task(self, name=None, duration=None, priority=None, time=None,
                  frequency=None, category=None, notes=None):
        """Update any of the task's fields that are provided."""
        updates = {"name": name, "duration": duration, "priority": priority,
                   "time": time, "frequency": frequency, "category": category,
                   "notes": notes}
        for attr, value in updates.items():
            if value is not None:
                setattr(self, attr, value)

    def next_occurrence(self) -> "Task | None":
        """Build the next instance of a recurring task.

        Looks up the task's frequency in RECURRENCE_DAYS ("daily" -> 1 day,
        "weekly" -> 7 days) and returns a copy that is not completed and whose
        due_date is that many days after this task's due_date (or after today if
        it has none). The copy keeps every other field, including pet_name.

        Returns:
            The new Task, or None if the frequency doesn't recur (e.g. "once").
        """
        days = RECURRENCE_DAYS.get(self.frequency)
        if days is None:
            return None
        base = self.due_date or Date.today()
        return replace(self, is_completed=False, due_date=base + timedelta(days=days))

    def mark_completed(self) -> "Task | None":
        """Mark this task as done and return its next occurrence, if it recurs.

        The returned task is not attached to a pet; use Scheduler.complete_task
        to also add it to the pet.

        Returns:
            The next occurrence from next_occurrence(), or None if the task
            doesn't recur or was already completed (so repeat calls can't
            create duplicate copies).
        """
        if self.is_completed:
            return None
        self.is_completed = True
        return self.next_occurrence()


@dataclass
class Pet:
    name: str
    species: str
    breed: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Add a task to this pet and set task.pet_name to this pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task):
        """Remove a task from this pet."""
        if task in self.tasks:
            self.tasks.remove(task)

    def get_tasks(self) -> list[Task]:
        """Return this pet's tasks."""
        return list(self.tasks)


class Owner:
    def __init__(self, name: str, contact: str = "", preferences: str = "",
                 available_minutes: int = 480):
        """Create an owner with no pets and a daily time budget in minutes."""
        self.name = name
        self.contact = contact
        self.preferences = preferences
        self.available_minutes = available_minutes  # time per day for pet care
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet):
        """Add a pet to this owner."""
        if pet not in self.pets:
            self.pets.append(pet)

    def update_info(self, name=None, contact=None, preferences=None, available_minutes=None):
        """Update any of the owner's fields that are provided."""
        if name is not None:
            self.name = name
        if contact is not None:
            self.contact = contact
        if preferences is not None:
            self.preferences = preferences
        if available_minutes is not None:
            self.available_minutes = available_minutes

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.get_tasks()]


@dataclass
class ScheduledItem:
    task: Task
    start_time: str  # "HH:MM"
    reason: str = ""  # why the task was placed here


class Scheduler:
    def __init__(self, owner: Owner, date: Date | None = None, day_start: str = "08:00"):
        """Create a scheduler for an owner with an empty plan."""
        self.owner = owner
        self.date = date or Date.today()
        self.day_start = day_start
        self.scheduled_items: list[ScheduledItem] = []
        self.unscheduled_tasks: list[Task] = []
        self.total_time: int = 0  # minutes
        self.conflicts: list[str] = []  # warnings from the latest generate_plan

    def get_tasks(self, pet_name: str | None = None, completed: bool | None = None) -> list[Task]:
        """Get all tasks from the owner's pets, optionally filtered by pet or completion."""
        return self.filter_tasks(self.owner.get_all_tasks(), pet_name, completed)

    def complete_task(self, task: Task) -> Task | None:
        """Mark a task done and, if it recurs, add its next occurrence to the same pet.

        Searches the owner's pets for the one holding `task` and appends the new
        occurrence to that pet, which also sets its pet_name.

        Args:
            task: A task belonging to one of the owner's pets.

        Returns:
            The newly created task, or None if the task doesn't recur or was
            already completed.
        """
        next_task = task.mark_completed()
        if next_task is not None:
            for pet in self.owner.pets:
                if task in pet.tasks:
                    pet.add_task(next_task)
                    break
        return next_task

    @staticmethod
    def filter_tasks(tasks: list[Task], pet_name: str | None = None,
                     completed: bool | None = None) -> list[Task]:
        """Return the tasks matching the given pet name and/or completion status.

        Args:
            tasks: The tasks to filter; the list is not modified.
            pet_name: Keep only tasks for this pet. None means any pet.
            completed: True keeps finished tasks, False keeps pending ones.
                None means either.

        Returns:
            A new list in the original order. When both filters are given a
            task must match both.
        """
        return [t for t in tasks
                if (pet_name is None or t.pet_name == pet_name)
                and (completed is None or t.is_completed == completed)]

    @staticmethod
    def sort_by_time(tasks: list[Task]) -> list[Task]:
        """Return the tasks sorted by preferred start time, earliest first.

        Times are compared as minutes since midnight, not as strings. Tasks with
        no preferred time (flexible) go last, and tasks with equal times keep
        their original relative order (the sort is stable).

        Args:
            tasks: The tasks to sort; the list is not modified.

        Returns:
            A new sorted list. Raises ValueError if a task's time isn't "HH:MM".
        """
        return sorted(tasks, key=lambda t: _to_minutes(t.time) if t.time else 24 * 60)

    @staticmethod
    def _sort_key(task: Task):
        """Sort by priority, then preferred time (earliest first), then shorter duration."""
        return (PRIORITY_ORDER.get(task.priority, len(PRIORITY_ORDER)),
                _to_minutes(task.time) if task.time else 24 * 60,
                task.duration)

    def detect_conflicts(self, tasks: list[Task] | None = None) -> list[str]:
        """Return a warning message for each pair of timed tasks whose slots overlap.

        Each task with a preferred time occupies the slot [start, start + duration).
        Two tasks conflict when each starts before the other ends, so back-to-back
        tasks (one ends at 12:15, the next starts at 12:15) are not flagged. Every
        pair is compared, which is O(n^2) but fine for one day's tasks. Flexible
        tasks (no time) are ignored. Conflicts are reported between different pets
        as well as within one pet, because the owner can only do one thing at a time.

        This only reports problems; it never changes the tasks or the plan, and it
        never raises. A task whose time can't be parsed produces its own warning
        and is left out of the comparison.

        Args:
            tasks: The tasks to check. Defaults to pending tasks due on or before
                the scheduler's date.

        Returns:
            A list of warning strings; empty if there are no conflicts.
        """
        if tasks is None:
            tasks = [t for t in self.get_tasks(completed=False)
                     if t.due_date is None or t.due_date <= self.date]

        warnings = []
        slots = []  # (start, end, task)
        for task in tasks:
            if not task.time:
                continue  # flexible tasks can't conflict
            try:
                start = _to_minutes(task.time)
            except ValueError:
                warnings.append(f"Warning: '{task.name}' ({task.pet_name}) has an "
                                f"invalid time '{task.time}'; skipped conflict check.")
                continue
            slots.append((start, start + task.duration, task))

        for (start_a, end_a, a), (start_b, end_b, b) in combinations(slots, 2):
            if start_a < end_b and start_b < end_a:
                scope = "same pet" if a.pet_name == b.pet_name else "different pets"
                first, second = sorted([(start_a, a), (start_b, b)], key=lambda x: x[0])
                warnings.append(
                    f"Warning: '{first[1].name}' ({first[1].pet_name}, {_to_hhmm(first[0])}) "
                    f"overlaps '{second[1].name}' ({second[1].pet_name}, {_to_hhmm(second[0])}) [{scope}].")
        return warnings

    def generate_plan(self):
        """Build the day's plan from all pending tasks due today, ordered by priority.

        Greedy algorithm:
          1. Reset the plan and record time conflicts in self.conflicts.
          2. Take pending tasks whose due_date is None or on/before self.date and
             sort them with _sort_key (priority, then preferred time, then duration).
          3. For each task, skip it into unscheduled_tasks if it would push the
             total past the owner's available_minutes; otherwise start it at the
             later of the running clock and its preferred time.
          4. Advance the clock to the task's end and add its duration to total_time.

        Because the clock only moves forward, a task can start later than its
        preferred time when earlier tasks run long. Tasks that don't fit are
        skipped, but later shorter tasks are still tried. Results are stored on
        self.scheduled_items, self.unscheduled_tasks, self.total_time and
        self.conflicts.
        """
        self.scheduled_items = []
        self.unscheduled_tasks = []
        self.total_time = 0
        self.conflicts = self.detect_conflicts()

        budget = self.owner.available_minutes
        clock = _to_minutes(self.day_start)

        due = [t for t in self.get_tasks(completed=False)
               if t.due_date is None or t.due_date <= self.date]
        for task in sorted(due, key=self._sort_key):
            if self.total_time + task.duration > budget:
                self.unscheduled_tasks.append(task)
                continue

            start = clock
            if task.time:
                start = max(clock, _to_minutes(task.time))
            reason = f"{task.priority.capitalize()} priority"
            if task.time:
                reason += f", preferred time {task.time}"
            reason += f"; fits within {budget} available minutes"

            self.scheduled_items.append(ScheduledItem(task, _to_hhmm(start), reason))
            self.total_time += task.duration
            clock = start + task.duration

    def explain_plan(self) -> str:
        """Return the reasoning for why each task was scheduled (from each item's reason)."""
        if not self.scheduled_items:
            return "No tasks were scheduled."
        lines = [f"{item.start_time} {item.task.name} ({item.task.pet_name}): {item.reason}"
                 for item in self.scheduled_items]
        for task in self.unscheduled_tasks:
            lines.append(f"Skipped {task.name} ({task.pet_name}): not enough time left.")
        return "\n".join(lines)

    def get_summary(self) -> str:
        """Return a displayable summary of the plan."""
        lines = [f"Plan for {self.owner.name} on {self.date}"]
        for item in self.scheduled_items:
            task = item.task
            lines.append(f"  {item.start_time}  {task.name} - {task.pet_name} "
                         f"({task.duration} min, {task.priority})")
        lines.append(f"Total: {self.total_time} of {self.owner.available_minutes} minutes")
        if self.unscheduled_tasks:
            names = ", ".join(t.name for t in self.unscheduled_tasks)
            lines.append(f"Not scheduled: {names}")
        lines.extend(self.conflicts)
        return "\n".join(lines)
