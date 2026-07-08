"""
app.py - PawPal+ Streamlit UI
Connects the frontend to the backend logic in pawpal_system.py.
"""

import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("A smart daily care planner for your pets.")
st.divider()

# ---------------------------------------------------------------------------
# Session state initialisation
# Keep owner, pets, and tasks alive across Streamlit reruns.
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pets" not in st.session_state:
    st.session_state.pets = []       # list of Pet objects
if "schedule" not in st.session_state:
    st.session_state.schedule = None


# ---------------------------------------------------------------------------
# Section 1 — Owner setup
# ---------------------------------------------------------------------------
st.subheader("1. Owner info & availability")

with st.form("owner_form"):
    owner_name = st.text_input("Your name", placeholder="e.g. Alex")
    col1, col2 = st.columns(2)
    with col1:
        work_schedule = st.selectbox("Today's schedule", ["office", "remote", "off"])
        morning_start = st.text_input("Morning start time", value="07:00")
    with col2:
        available_hours = st.slider("Free hours today", min_value=1, max_value=16, value=3)
        evening_end = st.text_input("Evening end time", value="21:00")

    submitted_owner = st.form_submit_button("Save owner")

if submitted_owner:
    owner = Owner(name=owner_name)
    owner.set_availability(
        work_schedule=work_schedule,
        available_hours=available_hours,
        preferred_morning_start=morning_start,
        preferred_evening_end=evening_end,
    )
    # Re-attach any existing pets to the new owner object
    for pet in st.session_state.pets:
        owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.schedule = None  # reset schedule on owner change
    st.success(f"Saved: {owner}")


# ---------------------------------------------------------------------------
# Section 2 — Add a pet
# ---------------------------------------------------------------------------
st.divider()
st.subheader("2. Add a pet")

with st.form("pet_form"):
    col1, col2 = st.columns(2)
    with col1:
        pet_name    = st.text_input("Pet name", placeholder="e.g. Buddy")
        species     = st.selectbox("Species", ["Dog", "Cat", "Rabbit", "Bird", "Other"])
        gender      = st.selectbox("Gender", ["Male", "Female"])
    with col2:
        age             = st.number_input("Age (years)", min_value=0, max_value=30, value=0)
        health_history  = st.text_input("Health history (optional)", placeholder="e.g. Neutered, no known allergies")
        medical_needs   = st.text_input("Medical needs (optional)", placeholder="e.g. Heartworm medication daily")

    submitted_pet = st.form_submit_button("Add pet")

if submitted_pet:
    if st.session_state.owner is None:
        st.warning("Please save owner info first.")
    else:
        pet = Pet(
            name=pet_name,
            species=species,
            gender=gender,
            age=age,
            health_history=health_history,
            medical_needs=medical_needs,
        )
        st.session_state.owner.add_pet(pet)
        st.session_state.pets.append(pet)
        st.session_state.schedule = None  # reset schedule on pet change
        st.success(f"Added pet: {pet}")

# Show registered pets
if st.session_state.pets:
    st.markdown("**Registered pets:**")
    for p in st.session_state.pets:
        st.markdown(f"- {p}")


# ---------------------------------------------------------------------------
# Section 3 — Add tasks
# ---------------------------------------------------------------------------
st.divider()
st.subheader("3. Add tasks")

if not st.session_state.pets:
    st.info("Add at least one pet above before adding tasks.")
else:
    with st.form("task_form"):
        col1, col2 = st.columns(2)
        with col1:
            assign_to   = st.selectbox("Assign to pet", [p.name for p in st.session_state.pets])
            task_name   = st.text_input("Task name", placeholder="e.g. Morning walk")
            task_type   = st.selectbox("Type", ["walk", "feeding", "medication", "grooming", "enrichment"])
        with col2:
            duration        = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=15)
            priority        = st.selectbox("Priority", ["1 — high", "2 — high", "3 — medium", "4 — low", "5 — low"])
            scheduled_time  = st.text_input("Scheduled time (optional)", placeholder="e.g. 07:00")

        submitted_task = st.form_submit_button("Add task")

    if submitted_task:
        priority_int = int(priority[0])
        task = Task(
            name=task_name,
            duration=int(duration),
            priority=priority_int,
            type=task_type,
            scheduled_time=scheduled_time,
        )
        # Find the right pet and add the task
        for pet in st.session_state.pets:
            if pet.name == assign_to:
                pet.add_task(task)
                st.session_state.schedule = None  # reset schedule on task change
                st.success(f"Added task '{task_name}' to {assign_to}.")
                break

    # Show current tasks per pet
    for pet in st.session_state.pets:
        if pet.get_tasks():
            st.markdown(f"**{pet.name}'s tasks:**")
            for t in pet.get_tasks():
                st.markdown(f"- {t}")


# ---------------------------------------------------------------------------
# Section 4 — Generate schedule
# ---------------------------------------------------------------------------
st.divider()
st.subheader("4. Generate today's plan")

if st.button("Generate schedule", type="primary"):
    if st.session_state.owner is None:
        st.warning("Please save owner info first.")
    elif not st.session_state.pets:
        st.warning("Please add at least one pet.")
    elif not any(p.get_tasks() for p in st.session_state.pets):
        st.warning("Please add at least one task.")
    else:
        scheduler = Scheduler(owner=st.session_state.owner)
        scheduler.generate_plan()
        st.session_state.schedule = scheduler

if st.session_state.schedule:
    sched = st.session_state.schedule
    plan  = sched.generated_plan

    if plan:
        total = sum(e["duration"] for e in plan)

        # --- Combined timeline ---
        st.markdown("#### Combined timeline")
        for entry in plan:
            time_label     = entry["scheduled_time"] if entry["scheduled_time"] else "--:--"
            priority_label = Scheduler._priority_label(entry["priority"])
            st.markdown(
                f"`{time_label}` — **[{entry['pet']}]** {entry['task']} "
                f"({entry['duration']} min) `priority: {priority_label}`"
            )
        st.markdown(f"**Total time:** {total} min ({total // 60}h {total % 60}m)")

        # --- Reasoning ---
        with st.expander("Why this plan?"):
            st.info(sched.explain_reasoning())

        # --- Per-pet breakdown ---
        st.markdown("#### Breakdown by pet")
        for pet in st.session_state.owner.pets:
            pet_entries = [e for e in plan if e["pet"] == pet.name]
            if not pet_entries:
                continue
            st.markdown(f"**{pet.name}** ({pet.species}, {pet.age} yr old {pet.gender})")
            for entry in pet_entries:
                time_label     = entry["scheduled_time"] if entry["scheduled_time"] else "--:--"
                priority_label = Scheduler._priority_label(entry["priority"])
                st.markdown(
                    f"&nbsp;&nbsp;&nbsp;&nbsp;`{time_label}` — {entry['task']} "
                    f"({entry['duration']} min) `priority: {priority_label}`"
                )
    else:
        st.warning("No tasks could be scheduled. Try increasing available hours or reducing task durations.")