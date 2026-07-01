import streamlit as st
from pawpal_system import Owner, Pet, Priority, Scheduler, Task, detect_conflicts

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")

with st.expander("Scenario", expanded=False):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
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

        col4, col5 = st.columns(2)
        with col4:
            preferred_start = st.text_input("Preferred start (HH:MM, optional)", value="")
        with col5:
            recurrence = st.selectbox("Recurrence", ["none", "daily", "weekly"])

        add_task = st.form_submit_button("Add task")

    if add_task:
        start = preferred_start.strip() if preferred_start.strip() else None
        rec = recurrence if recurrence != "none" else None
        selected_pet.add_task(
            Task(
                title=task_title,
                duration=int(duration),
                priority=Priority(priority),
                preferred_start=start,
                recurrence=rec,
            )
        )
        st.success(f"Added '{task_title}' for {selected_pet.name}.")

    if selected_pet.get_tasks():
        sort_by_priority = st.checkbox("Sort tasks by priority (HIGH → LOW)")
        if sort_by_priority:
            scheduler_preview = Scheduler(pet=selected_pet, available_time=9999)
            tasks_to_show = scheduler_preview.sort_by_priority()
        else:
            tasks_to_show = selected_pet.get_tasks()

        st.write(f"Tasks for **{selected_pet.name}**:")
        st.table(
            [
                {
                    "title": task.title,
                    "duration (min)": task.duration,
                    "priority": task.priority.value,
                    "preferred start": task.preferred_start or "—",
                    "recurrence": task.recurrence or "none",
                    "completed": task.completed,
                }
                for task in tasks_to_show
            ]
        )

        # Show same-pet conflict warnings immediately
        conflict_checker = Scheduler(pet=selected_pet, available_time=9999)
        conflicts = conflict_checker.check_conflicts()
        if conflicts:
            for msg in conflicts:
                st.warning(f"⚠️ Conflict detected: {msg}")
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

        st.info(f"📋 {plan.summary()}")

        if plan.slots:
            scheduled_titles = {entry["task"].title for entry in plan.slots}
            all_tasks = schedule_pet.get_tasks()
            skipped = [t for t in all_tasks if not t.completed and t.title not in scheduled_titles]

            st.table(
                [
                    {
                        "time": entry["time_slot"],
                        "task": entry["task"].title,
                        "duration (min)": entry["task"].duration,
                        "priority": entry["task"].priority.value,
                    }
                    for entry in plan.slots
                ]
            )

            if skipped:
                st.warning(
                    "⏭️ These tasks didn't fit in the available time: "
                    + ", ".join(f"**{t.title}**" for t in skipped)
                )
        else:
            st.info("No tasks fit into the available time.")

        # Cross-pet conflict detection
        if len(owner_pets) > 1:
            all_plans = []
            for pet in owner_pets:
                s = Scheduler(pet=pet, available_time=int(available_time))
                all_plans.append(s.generate())

            cross_conflicts = detect_conflicts(all_plans)
            with st.expander("🐾 Cross-pet conflict check", expanded=True):
                if cross_conflicts:
                    for c in cross_conflicts:
                        st.error(
                            f"**{c['pet_a']}** ({c['task_a']} {c['overlap_start']}–{c['overlap_end']}) "
                            f"overlaps **{c['pet_b']}** ({c['task_b']} {c['overlap_start']}–{c['overlap_end']})"
                        )
                else:
                    st.success("No scheduling conflicts across pets!")
else:
    st.info("Add a pet and task before generating a schedule.")
