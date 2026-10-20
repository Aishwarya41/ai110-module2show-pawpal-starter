from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task

TODAY = date(2026, 10, 19)


def make_scheduler(*tasks, available_minutes=480):
    """Build an owner with one pet holding the given tasks, plus a scheduler for TODAY."""
    owner = Owner("Sam", available_minutes=available_minutes)
    pet = Pet("Buddy", "dog")
    for task in tasks:
        pet.add_task(task)
    owner.add_pet(pet)
    return Scheduler(owner, date=TODAY), pet


def test_mark_completed_changes_status():
    task = Task("Morning walk", 30, "high")
    assert task.is_completed is False

    task.mark_completed()

    assert task.is_completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Buddy", "dog")
    assert len(pet.get_tasks()) == 0

    pet.add_task(Task("Morning walk", 30, "high"))
    assert len(pet.get_tasks()) == 1

    pet.add_task(Task("Brush coat", 20, "low"))
    assert len(pet.get_tasks()) == 2


# ---------- Sorting correctness ----------

def test_sort_by_time_returns_chronological_order():
    late = Task("Dinner", 20, time="18:00")
    early = Task("Walk", 30, time="07:30")
    mid = Task("Meds", 5, time="13:00")

    result = Scheduler.sort_by_time([late, early, mid])

    assert [t.name for t in result] == ["Walk", "Meds", "Dinner"]


def test_sort_by_time_compares_numerically_not_as_strings():
    # As strings "10:00" < "9:00", but 9:00 is earlier.
    ten = Task("Ten", 10, time="10:00")
    nine = Task("Nine", 10, time="9:00")

    result = Scheduler.sort_by_time([ten, nine])

    assert [t.name for t in result] == ["Nine", "Ten"]


def test_sort_by_time_puts_flexible_tasks_last():
    flexible = Task("Play", 15)
    timed = Task("Walk", 30, time="23:59")

    result = Scheduler.sort_by_time([flexible, timed])

    assert [t.name for t in result] == ["Walk", "Play"]


def test_sort_by_time_is_stable_and_does_not_mutate_input():
    a = Task("A", 10, time="09:00")
    b = Task("B", 10, time="09:00")
    original = [b, a]

    result = Scheduler.sort_by_time(original)

    assert result == [b, a]  # equal times keep original order
    assert original == [b, a]  # input list untouched


def test_sort_by_time_empty_list():
    assert Scheduler.sort_by_time([]) == []


def test_generate_plan_orders_by_priority_then_time():
    low_early = Task("Low early", 10, "low", time="08:00")
    high_late = Task("High late", 10, "high", time="12:00")
    med = Task("Medium", 10, "medium", time="09:00")
    scheduler, _ = make_scheduler(low_early, high_late, med)

    scheduler.generate_plan()

    assert [i.task.name for i in scheduler.scheduled_items] == [
        "High late", "Medium", "Low early"]


# ---------- Recurrence logic ----------

def test_completing_daily_task_creates_task_for_next_day():
    task = Task("Walk", 30, frequency="daily", due_date=TODAY)
    scheduler, pet = make_scheduler(task)

    next_task = scheduler.complete_task(task)

    assert task.is_completed is True
    assert next_task is not None
    assert next_task.due_date == TODAY + timedelta(days=1)
    assert next_task.is_completed is False
    assert next_task.name == "Walk"
    assert next_task.pet_name == "Buddy"
    assert next_task in pet.tasks
    assert len(pet.tasks) == 2


def test_completing_weekly_task_creates_task_seven_days_later():
    task = Task("Bath", 20, frequency="weekly", due_date=TODAY)
    scheduler, _ = make_scheduler(task)

    next_task = scheduler.complete_task(task)

    assert next_task.due_date == TODAY + timedelta(days=7)


def test_completing_once_task_creates_no_new_task():
    task = Task("Vet visit", 60, frequency="once", due_date=TODAY)
    scheduler, pet = make_scheduler(task)

    assert scheduler.complete_task(task) is None
    assert len(pet.tasks) == 1


def test_completing_task_twice_does_not_duplicate():
    task = Task("Walk", 30, frequency="daily", due_date=TODAY)
    scheduler, pet = make_scheduler(task)

    scheduler.complete_task(task)
    second = scheduler.complete_task(task)

    assert second is None
    assert len(pet.tasks) == 2


def test_daily_recurrence_rolls_over_year_end():
    task = Task("Walk", 30, frequency="daily", due_date=date(2026, 12, 31))

    assert task.next_occurrence().due_date == date(2027, 1, 1)


def test_next_day_plan_includes_recurring_copy_but_today_does_not():
    task = Task("Walk", 30, frequency="daily", due_date=TODAY)
    scheduler, _ = make_scheduler(task)
    scheduler.complete_task(task)

    scheduler.generate_plan()
    assert scheduler.scheduled_items == []  # copy is due tomorrow

    tomorrow = Scheduler(scheduler.owner, date=TODAY + timedelta(days=1))
    tomorrow.generate_plan()
    assert [i.task.name for i in tomorrow.scheduled_items] == ["Walk"]


# ---------- Conflict detection ----------

def test_detect_conflicts_flags_duplicate_times():
    a = Task("Walk", 30, time="09:00")
    b = Task("Vet call", 15, time="09:00")
    scheduler, _ = make_scheduler(a, b)

    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "Walk" in warnings[0] and "Vet call" in warnings[0]


def test_generate_plan_records_conflicts():
    scheduler, _ = make_scheduler(Task("Walk", 30, time="09:00"),
                                  Task("Feed", 10, time="09:00"))

    scheduler.generate_plan()

    assert len(scheduler.conflicts) == 1


def test_detect_conflicts_flags_overlap_across_pets():
    owner = Owner("Sam")
    dog = Pet("Buddy", "dog")
    cat = Pet("Mia", "cat")
    dog.add_task(Task("Walk", 30, time="09:00"))
    cat.add_task(Task("Groom", 30, time="09:15"))
    owner.add_pet(dog)
    owner.add_pet(cat)

    warnings = Scheduler(owner, date=TODAY).detect_conflicts()

    assert len(warnings) == 1
    assert "different pets" in warnings[0]


def test_detect_conflicts_ignores_back_to_back_tasks():
    scheduler, _ = make_scheduler(Task("Walk", 30, time="09:00"),
                                  Task("Feed", 10, time="09:30"))

    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_ignores_flexible_tasks():
    scheduler, _ = make_scheduler(Task("Walk", 30), Task("Feed", 10))

    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_invalid_time_warns_instead_of_raising():
    scheduler, _ = make_scheduler(Task("Walk", 30, time="9am"))

    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "invalid time" in warnings[0]


# ---------- Plan generation ----------

def test_generate_plan_respects_budget_and_still_fits_later_short_task():
    big = Task("Long hike", 90, "high")
    small = Task("Quick feed", 10, "low")
    scheduler, _ = make_scheduler(big, small, available_minutes=60)

    scheduler.generate_plan()

    assert [i.task.name for i in scheduler.scheduled_items] == ["Quick feed"]
    assert scheduler.unscheduled_tasks == [big]
    assert scheduler.total_time == 10


def test_generate_plan_budget_boundary_is_inclusive():
    scheduler, _ = make_scheduler(Task("A", 30), Task("B", 30),
                                  available_minutes=60)

    scheduler.generate_plan()

    assert scheduler.total_time == 60
    assert scheduler.unscheduled_tasks == []


def test_generate_plan_is_repeatable():
    scheduler, _ = make_scheduler(Task("A", 30, "high"), Task("B", 20))

    scheduler.generate_plan()
    first = [(i.task.name, i.start_time) for i in scheduler.scheduled_items]
    scheduler.generate_plan()
    second = [(i.task.name, i.start_time) for i in scheduler.scheduled_items]

    assert first == second
    assert scheduler.total_time == 50


def test_generate_plan_with_no_tasks():
    scheduler, _ = make_scheduler()

    scheduler.generate_plan()

    assert scheduler.scheduled_items == []
    assert scheduler.explain_plan() == "No tasks were scheduled."
