import streamlit as st
from datetime import datetime

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

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

all_tasks = owner.get_all_tasks()
if all_tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "pet": t.pet_name,
                "task": t.name,
                "duration (min)": t.duration,
                "priority": t.priority,
                "preferred time": t.time or "-",
                "done": t.is_completed,
            }
            for t in all_tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    if scheduler.scheduled_items:
        st.success(f"Plan for {owner.name}: {scheduler.total_time} of {owner.available_minutes} minutes used")
        st.table(
            [
                {
                    "start": item.start_time,
                    "pet": item.task.pet_name,
                    "task": item.task.name,
                    "duration (min)": item.task.duration,
                    "priority": item.task.priority,
                }
                for item in scheduler.scheduled_items
            ]
        )
        with st.expander("Why this plan?", expanded=True):
            st.text(scheduler.explain_plan())
    else:
        st.warning("Nothing to schedule yet. Add a pet and some tasks.")
    if scheduler.unscheduled_tasks:
        st.warning(
            "Not enough time for: " + ", ".join(f"{t.name} ({t.pet_name})" for t in scheduler.unscheduled_tasks)
        )
