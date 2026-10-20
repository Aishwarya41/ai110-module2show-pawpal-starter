import streamlit as st
from datetime import datetime

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

PRIORITY_BADGE = {"high": "🔴 high", "medium": "🟡 medium", "low": "🟢 low"}


def priority_badge(priority: str) -> str:
    return PRIORITY_BADGE.get(priority, priority)

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# One Owner lives in session_state so it survives Streamlit reruns.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
owner = st.session_state.owner

st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value=owner.name)
with col2:
    available = st.number_input(
        "Time available today (minutes)", min_value=10, max_value=1440, value=owner.available_minutes
    )
owner.update_info(name=owner_name, available_minutes=int(available))

st.subheader("Pets")
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    st.write("")
    add_pet_clicked = st.button("Add pet")

if add_pet_clicked:
    if not pet_name.strip():
        st.error("Pet name can't be empty.")
    elif any(p.name == pet_name.strip() for p in owner.pets):
        st.error(f"You already have a pet named {pet_name.strip()}.")
    else:
        owner.add_pet(Pet(pet_name.strip(), species))

if owner.pets:
    st.write("Your pets: " + ", ".join(f"{p.name} ({p.species})" for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")

if owner.pets:
    col1, col2 = st.columns(2)
    with col1:
        task_pet = st.selectbox("For pet", [p.name for p in owner.pets])
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    task_time = st.text_input("Preferred time (HH:MM, optional)", value="")

    if st.button("Add task"):
        try:
            if task_time.strip():
                datetime.strptime(task_time.strip(), "%H:%M")
        except ValueError:
            st.error("Preferred time must look like 08:30.")
        else:
            pet = next(p for p in owner.pets if p.name == task_pet)
            pet.add_task(Task(task_title, int(duration), priority, time=task_time.strip()))
else:
    st.caption("Add a pet first, then you can add tasks for it.")

scheduler = Scheduler(owner)

if owner.get_all_tasks():
    st.subheader("Task list")
    col1, col2 = st.columns(2)
    with col1:
        pet_filter = st.selectbox("Show pet", ["All pets"] + [p.name for p in owner.pets])
    with col2:
        status_filter = st.selectbox("Show status", ["All", "Pending", "Completed"])

    shown = scheduler.get_tasks(
        pet_name=None if pet_filter == "All pets" else pet_filter,
        completed={"All": None, "Pending": False, "Completed": True}[status_filter],
    )
    if shown:
        st.caption(f"{len(shown)} task(s), sorted by preferred time. Tasks with no time are listed last.")
        st.table(
            [
                {
                    "Time": t.time or "Flexible",
                    "Pet": t.pet_name,
                    "Task": t.name,
                    "Duration": f"{t.duration} min",
                    "Priority": priority_badge(t.priority),
                    "Repeats": t.frequency,
                    "Due": str(t.due_date) if t.due_date else "Today",
                    "Status": "✅ Done" if t.is_completed else "⏳ Pending",
                }
                for t in Scheduler.sort_by_time(shown)
            ]
        )
    else:
        st.info("No tasks match those filters.")

    # Surface overlapping tasks as soon as they exist, not only after generating a schedule.
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        st.warning(
            f"⚠️ {len(conflicts)} scheduling conflict(s). You can only do one thing at a time, "
            "so consider changing one of the times:\n\n" + "\n".join(f"- {c.removeprefix('Warning: ')}" for c in conflicts)
        )
    elif any(t.time for t in scheduler.get_tasks(completed=False)):
        st.success("No scheduling conflicts between your timed tasks.")

    pending = scheduler.get_tasks(completed=False)
    if pending:
        to_complete = st.selectbox(
            "Mark a task done",
            pending,
            format_func=lambda t: f"{t.name} ({t.pet_name})" + (f" at {t.time}" if t.time else ""),
        )
        if st.button("Mark done"):
            next_task = scheduler.complete_task(to_complete)
            if next_task:
                st.session_state.flash = (
                    f"Done! Next '{next_task.name}' ({next_task.frequency}) is due {next_task.due_date}."
                )
            else:
                st.session_state.flash = f"Done! '{to_complete.name}' doesn't repeat."
            st.rerun()  # redraw the table above with the updated tasks
    if "flash" in st.session_state:
        st.success(st.session_state.pop("flash"))
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    scheduler.generate_plan()
    if scheduler.scheduled_items:
        st.success(f"Plan ready for {owner.name} on {scheduler.date}.")
        col1, col2, col3 = st.columns(3)
        col1.metric("Tasks scheduled", len(scheduler.scheduled_items))
        col2.metric("Time used", f"{scheduler.total_time} min")
        col3.metric("Time left", f"{owner.available_minutes - scheduler.total_time} min")
        st.table(
            [
                {
                    "Start": item.start_time,
                    "Pet": item.task.pet_name,
                    "Task": item.task.name,
                    "Duration": f"{item.task.duration} min",
                    "Priority": priority_badge(item.task.priority),
                }
                for item in scheduler.scheduled_items
            ]
        )
        if scheduler.conflicts:
            st.warning(
                "Some preferred times overlapped, so later tasks were pushed back to avoid double-booking:\n\n"
                + "\n".join(f"- {c.removeprefix('Warning: ')}" for c in scheduler.conflicts)
            )
        with st.expander("Why this plan?", expanded=True):
            st.text(scheduler.explain_plan())
    else:
        st.warning("Nothing to schedule yet. Add a pet and some tasks.")
    if scheduler.unscheduled_tasks:
        st.error(
            "Not enough time today for: "
            + ", ".join(f"{t.name} ({t.pet_name}, {t.duration} min)" for t in scheduler.unscheduled_tasks)
            + ". Increase your available time or shorten a task."
        )
