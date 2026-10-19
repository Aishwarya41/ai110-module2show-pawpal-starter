from pawpal_system import Owner, Pet, Scheduler, Task


def main():
    owner = Owner("Jordan", contact="jordan@example.com", available_minutes=120)

    buddy = Pet("Buddy", "dog", breed="Labrador")
    mia = Pet("Mia", "cat", breed="Siamese")
    owner.add_pet(buddy)
    owner.add_pet(mia)

    buddy.add_task(Task("Morning walk", 30, "high", time="07:30", category="walk"))
    buddy.add_task(Task("Brush coat", 20, "low", time="18:00", category="grooming"))
    mia.add_task(Task("Breakfast", 10, "high", time="08:00", category="feeding"))
    mia.add_task(Task("Give medication", 5, "high", time="12:00", category="meds"))
    mia.add_task(Task("Play session", 25, "medium", time="17:00", category="play"))

    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    print("=" * 40)
    print("Today's Schedule")
    print("=" * 40)
    print(scheduler.get_summary())
    print()
    print("Why this plan:")
    print(scheduler.explain_plan())


if __name__ == "__main__":
    main()
