from dataclasses import dataclass, field
from datetime import date as Date


@dataclass
class Task:
    name: str
    duration: int  # minutes
    priority: str  # "high", "medium", "low"
    category: str = ""
    is_completed: bool = False
    notes: str = ""
    pet_name: str = ""  # which pet this task is for; set by Pet.add_task

    def edit_task(self, name=None, duration=None, priority=None, category=None, notes=None):
        """Update any of the task's fields that are provided."""
        pass

    def mark_completed(self):
        """Mark this task as done."""
        pass


@dataclass
class Pet:
    name: str
    species: str
    breed: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Add a task to this pet and set task.pet_name to this pet's name."""
        pass

    def remove_task(self, task: Task):
        """Remove a task from this pet."""
        pass

    def get_tasks(self) -> list[Task]:
        """Return this pet's tasks."""
        pass


class Owner:
    def __init__(self, name: str, contact: str = "", preferences: str = ""):
        self.name = name
        self.contact = contact
        self.preferences = preferences
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet):
        """Add a pet to this owner."""
        pass

    def update_info(self, name=None, contact=None, preferences=None):
        """Update any of the owner's fields that are provided."""
        pass


@dataclass
class ScheduledItem:
    task: Task
    start_time: str  # e.g. "08:00"
    reason: str = ""  # why the task was placed here


class Schedule:
    def __init__(self, date: Date, owner: Owner):
        self.date = date
        self.owner = owner  # whose plan this is
        self.scheduled_items: list[ScheduledItem] = []
        self.total_time: int = 0  # minutes

    def generate_plan(self, owner: Owner, tasks: list[Task]):
        """Build the day's plan from the tasks, ordered by priority.

        Each task becomes a ScheduledItem with a start_time and a reason.
        """
        pass

    def explain_plan(self) -> str:
        """Return the reasoning for why each task was scheduled (from each item's reason)."""
        pass

    def get_summary(self) -> str:
        """Return a displayable summary of the plan."""
        pass
