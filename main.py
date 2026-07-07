"""
main.py - PawPal+ demo script
Testing ground for verifying backend logic in the terminal.
Run with: python main.py
"""

from pawpal_system import Owner, Pet, Task, Schedule


# --- 1. Create owner and set availability ---
owner = Owner(name="Alex")
owner.set_availability(
    work_schedule="office",
    available_hours=3,
    preferred_morning_start="07:00",
    preferred_evening_end="20:00",
)

# --- 2. Create pets ---
dog = Pet(name="Buddy", species="Dog", gender="Male", age=3)
cat = Pet(name="Luna",  species="Cat", gender="Female", age=2)

# --- 3. Add tasks to Buddy (dog) ---
dog.add_task(Task("Breakfast",      10, priority=1, type="feeding",    scheduled_time="07:00"))
dog.add_task(Task("Heartworm pill",  5, priority=1, type="medication", scheduled_time="07:05"))
dog.add_task(Task("Morning walk",   30, priority=2, type="walk",       scheduled_time="07:30"))
dog.add_task(Task("Evening walk",   30, priority=2, type="walk",       scheduled_time="18:00"))

# --- 4. Add tasks to Luna (cat) ---
cat.add_task(Task("Breakfast",       5, priority=1, type="feeding",    scheduled_time="07:00"))
cat.add_task(Task("Playtime",       20, priority=4, type="enrichment", scheduled_time="19:00"))
cat.add_task(Task("Brushing",       15, priority=5, type="grooming"))

# --- 5. Register pets under owner ---
owner.add_pet(dog)
owner.add_pet(cat)

# --- 6. Generate and display today's schedule ---
scheduler = Schedule(owner=owner)
scheduler.generate_plan()
scheduler.display_plan()