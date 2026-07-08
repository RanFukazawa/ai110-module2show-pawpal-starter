"""
app.py - PawPal+ Streamlit UI
Connects the frontend to the backend logic in pawpal_system.py.
"""

import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, normalize_time

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

if st.session_state.owner is not None:
    if st.button("🗑️ Remove owner (clears all pets and tasks)", key="remove_owner"):
        st.session_state.owner = None
        st.session_state.pets = []
        st.session_state.schedule = None
        st.rerun()


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

# Show registered pets with remove buttons
if st.session_state.pets:
    st.markdown("**Registered pets:**")
    for i, p in enumerate(st.session_state.pets):
        col_pet, col_btn = st.columns([5, 1])
        with col_pet:
            st.markdown(f"- {p}")
        with col_btn:
            if st.button("🗑️", key=f"remove_pet_{i}", help=f"Remove {p.name}"):
                # Also remove from owner's pet list
                if st.session_state.owner is not None:
                    st.session_state.owner.pets = [
                        op for op in st.session_state.owner.pets if op.name != p.name
                    ]
                st.session_state.pets.pop(i)
                st.session_state.schedule = None
                st.rerun()


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
            frequency       = st.selectbox("Frequency", ["once", "daily", "weekly"])

        submitted_task = st.form_submit_button("Add task")

    if submitted_task:
        priority_int = int(priority[0])
        normalized_time = normalize_time(scheduled_time)

        # Warn if user entered something but it couldn't be parsed
        if scheduled_time.strip() and not normalized_time:
            st.warning(
                f"⚠️ '{scheduled_time}' is not a valid time format. "
                "Please use HH:MM (e.g. 07:00 or 8:30). Task was not added."
            )
        else:
            task = Task(
                name=task_name,
                duration=int(duration),
                priority=priority_int,
                type=task_type,
                scheduled_time=scheduled_time,  # __post_init__ normalizes automatically
                frequency=frequency,
            )
            for pet in st.session_state.pets:
                if pet.name == assign_to:
                    pet.add_task(task)
                    st.session_state.schedule = None
                    time_display = f" at {task.scheduled_time}" if task.scheduled_time else ""
                    st.success(f"Added task '{task_name}'{time_display} to {assign_to}.")
                    break

    # Show current tasks per pet with remove buttons
    for pet in st.session_state.pets:
        if pet.get_tasks():
            st.markdown(f"**{pet.name}'s tasks:**")
            for i, t in enumerate(pet.get_tasks()):
                col_task, col_btn = st.columns([5, 1])
                with col_task:
                    st.markdown(f"- {t}")
                with col_btn:
                    if st.button("🗑️", key=f"remove_task_{pet.name}_{i}", help=f"Remove {t.name}"):
                        pet.tasks.pop(i)
                        st.session_state.schedule = None
                        st.rerun()


# ---------------------------------------------------------------------------
# Section 4 — Generate schedule
# ---------------------------------------------------------------------------
st.divider()
st.subheader("4. Generate today's plan")

col_gen, col_refresh = st.columns([3, 1])
with col_gen:
    generate_clicked = st.button("Generate schedule", type="primary")
with col_refresh:
    refresh_clicked = st.button("🔄 Refresh plan", help="Regenerate the plan with current tasks")

if generate_clicked or refresh_clicked:
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
    owner = st.session_state.owner

    if plan:
        total        = sum(e["duration"] for e in plan)
        total_avail  = owner.available_hours * 60
        remaining    = total_avail - total

        st.success(f"Plan generated: {len(plan)} task(s) scheduled, {total} min used, {remaining} min remaining.")

        # --- Conflict warnings ---
        conflicts = sched.detect_conflicts()
        if conflicts:
            for warning in conflicts:
                st.warning(warning)

        # --- Skipped task warning ---
        skipped_line = [s for s in sched.reasoning.split(".") if "could not fit" in s]
        if skipped_line:
            st.warning(
                f"⚠️ Some tasks were skipped because they didn't fit in your available time: "
                f"{skipped_line[0].strip()}. Consider increasing your free hours or reducing task durations."
            )

        # --- Combined timeline as table ---
        st.markdown("#### Combined timeline")
        timeline_rows = [
            {
                "Time":      entry["scheduled_time"] if entry["scheduled_time"] else "--:--",
                "Pet":       entry["pet"],
                "Task":      entry["task"],
                "Type":      entry["type"],
                "Duration":  f"{entry['duration']} min",
                "Priority":  Scheduler._priority_label(entry["priority"]),
                "Frequency": entry.get("frequency", "once"),
            }
            for entry in plan
        ]
        st.table(timeline_rows)
        st.markdown(f"**Total time:** {total} min ({total // 60}h {total % 60}m) of {total_avail} min available.")

        # --- Reasoning expander ---
        with st.expander("Why this plan?"):
            st.info(sched.explain_reasoning())

        # --- Per-pet breakdown as tables ---
        st.markdown("#### Breakdown by pet")
        for pet in owner.pets:
            pet_entries = [e for e in plan if e["pet"] == pet.name]
            if not pet_entries:
                continue
            st.markdown(f"**{pet.name}** ({pet.species}, {pet.age} yr old {pet.gender})")
            pet_rows = [
                {
                    "Time":      e["scheduled_time"] if e["scheduled_time"] else "--:--",
                    "Task":      e["task"],
                    "Type":      e["type"],
                    "Duration":  f"{e['duration']} min",
                    "Priority":  Scheduler._priority_label(e["priority"]),
                    "Frequency": e.get("frequency", "once"),
                }
                for e in pet_entries
            ]
            st.table(pet_rows)

    else:
        st.warning("⚠️ No tasks could be scheduled. Try increasing your available hours or shortening task durations.")