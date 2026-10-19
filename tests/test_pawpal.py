from pawpal_system import Pet, Task


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
