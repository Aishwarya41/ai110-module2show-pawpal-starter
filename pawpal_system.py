from dataclasses import dataclass, field
from datetime import date as Date

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


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

    def edit_task(self, name=None, duration=None, priority=None, time=None,
                  frequency=None, category=None, notes=None):
        """Update any of the task's fields that are provided."""
        """Update any of the task's fields that are provided."""
        updates = {"name": name, "duration": duration, "priority": priority,
                   "time": time, "frequency": frequency, "category": category,
                   "notes": notes}
        for attr, value in updates.items():
            if value is not None:
                setattr(self, attr, value)

    def mark_completed(self):
        """Mark this task as done."""
        self.is_completed = True


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

    def get_tasks(self, pet_name: str | None = None, completed: bool | None = None) -> list[Task]:
        """Get all tasks from the owner's pets, optionally filtered by pet or completion."""
        tasks = self.owner.get_all_tasks()
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name == pet_name]
        if completed is not None:
            tasks = [t for t in tasks if t.is_completed == completed]
        return tasks

    @staticmethod
    def _sort_key(task: Task):
        """Sort by priority, then preferred time (earliest first), then shorter duration."""
        return (PRIORITY_ORDER.get(task.priority, len(PRIORITY_ORDER)),
                _to_minutes(task.time) if task.time else 24 * 60,
                task.duration)

    def generate_plan(self):
        """Build the day's plan from all pending tasks, ordered by priority."""
        self.scheduled_items = []
        self.unscheduled_tasks = []
        self.total_time = 0

        budget = self.owner.available_minutes
        clock = _to_minutes(self.day_start)

        for task in sorted(self.get_tasks(completed=False), key=self._sort_key):
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
        return "\n".join(lines)
