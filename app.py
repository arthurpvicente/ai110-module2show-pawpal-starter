import streamlit as st
from pawpal_system import Owner, Pet, Priority, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")

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

st.subheader("Owner")
owner_name = st.text_input("Owner name", value=st.session_state.owner.name)
st.session_state.owner.name = owner_name

st.markdown("### Pets")
with st.form("add_pet_form"):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    add_pet = st.form_submit_button("Add pet")

if add_pet:
    new_pet = Pet(name=pet_name, species=species)
    st.session_state.owner.add_pet(new_pet)
    st.success(f"Added {new_pet.name}.")

owner_pets = st.session_state.owner.get_pets()

if owner_pets:
    st.write("Current pets:")
    st.table(
        [
            {"name": pet.name, "species": pet.species, "task_count": len(pet.get_tasks())}
            for pet in owner_pets
        ]
    )
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")

if owner_pets:
    pet_options = [pet.name for pet in owner_pets]
    selected_pet_name = st.selectbox("Pet", pet_options)
    selected_pet = owner_pets[pet_options.index(selected_pet_name)]

    with st.form("add_task_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            task_title = st.text_input("Task title", value="Morning walk")
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        with col3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        add_task = st.form_submit_button("Add task")

    if add_task:
        selected_pet.add_task(
            Task(title=task_title, duration=int(duration), priority=Priority(priority))
        )
        st.success(f"Added {task_title} for {selected_pet.name}.")

    if selected_pet.get_tasks():
        st.write(f"Tasks for {selected_pet.name}:")
        st.table(
            [
                {
                    "title": task.title,
                    "duration_minutes": task.duration,
                    "priority": task.priority.value,
                    "completed": task.completed,
                }
                for task in selected_pet.get_tasks()
            ]
        )
    else:
        st.info(f"No tasks yet for {selected_pet.name}.")
else:
    st.info("Add a pet before scheduling tasks.")

st.divider()

st.subheader("Build Schedule")
if owner_pets:
    schedule_pet_name = st.selectbox("Schedule for", [pet.name for pet in owner_pets])
    schedule_pet = owner_pets[[pet.name for pet in owner_pets].index(schedule_pet_name)]
    available_time = st.number_input(
        "Available time (minutes)", min_value=1, max_value=480, value=60
    )

    if st.button("Generate schedule"):
        scheduler = Scheduler(pet=schedule_pet, available_time=int(available_time))
        plan = scheduler.generate()
        st.write(plan.summary())

        if plan.slots:
            st.table(
                [
                    {
                        "time": entry["time_slot"],
                        "task": entry["task"].title,
                        "duration_minutes": entry["task"].duration,
                        "priority": entry["task"].priority.value,
                    }
                    for entry in plan.slots
                ]
            )
        else:
            st.info("No tasks fit into the available time.")
else:
    st.info("Add a pet and task before generating a schedule.")
