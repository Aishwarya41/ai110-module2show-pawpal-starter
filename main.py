from pawpal_system import Owner, Pet, Scheduler, Task


def main():
    owner = Owner("Jordan", contact="jordan@example.com", available_minutes=120)

    buddy = Pet("Buddy", "dog", breed="Labrador")
    mia = Pet("Mia", "cat", breed="Siamese")
    owner.add_pet(buddy)
    owner.add_pet(mia)

    # Tasks are deliberately added out of time order (and one has no time at all).
    buddy.add_task(Task("Brush coat", 20, "low", time="18:00", category="grooming"))
    mia.add_task(Task("Play session", 25, "medium", time="17:00", category="play"))
    buddy.add_task(Task("Training", 15, "medium", category="training"))
    mia.add_task(Task("Give medication", 5, "high", time="12:00", category="meds"))
    buddy.add_task(Task("Morning walk", 30, "high", time="07:30", category="walk"))
    mia.add_task(Task("Breakfast", 10, "high", time="08:00", category="feeding"))

    # Mark a couple done so the completion filter has something to show.
    buddy.tasks[-1].mark_completed()  # Morning walk
    mia.tasks[-1].mark_completed()    # Breakfast

    # Deliberate conflicts: same start time on different pets (12:00), same start time
    # on one pet (17:00), and a partial overlap on one pet (17:10).
    buddy.add_task(Task("Vet call", 15, "medium", time="12:00", category="vet"))
    mia.add_task(Task("Nail trim", 10, "low", time="17:10", category="grooming"))
    mia.add_task(Task("Clean litter box", 5, "medium", time="17:00", category="cleaning"))

    scheduler = Scheduler(owner)

    def show(title, tasks):
        print(f"{title}:")
        for t in tasks:
            status = "done" if t.is_completed else "todo"
            print(f"  {t.time or '--:--'}  {t.name} ({t.pet_name}, {status})")
        print()

    show("All tasks, as added", scheduler.get_tasks())
    show("All tasks, sorted by time", scheduler.sort_by_time(scheduler.get_tasks()))
    show("Mia's tasks", scheduler.filter_tasks(scheduler.get_tasks(), pet_name="Mia"))
    show("Completed tasks", scheduler.filter_tasks(scheduler.get_tasks(), completed=True))
    show("Pending tasks", scheduler.filter_tasks(scheduler.get_tasks(), completed=False))
    show("Buddy's pending tasks, sorted by time",
         scheduler.sort_by_time(scheduler.filter_tasks(scheduler.get_tasks(),
                                                       pet_name="Buddy", completed=False)))

    scheduler.generate_plan()

    print("=" * 40)
    print("Today's Schedule")
    print("=" * 40)
    print(scheduler.get_summary())
    print()
    print("Conflicts:")
    print("\n".join(scheduler.conflicts) or "None")
    print()
    print("Why this plan:")
    print(scheduler.explain_plan())


if __name__ == "__main__":
    main()
