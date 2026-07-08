"""
main.py - PawPal+ demo script
Testing ground for verifying backend logic in the terminal.
Run with: python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler
from datetime import date


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
# Note: Breakfast starts at 07:00 and takes 10 min (ends 07:10)
#       Heartworm pill starts at 07:05 → deliberate conflict for Step 4 demo
dog.add_task(Task("Breakfast",      10, priority=1, type="feeding",    scheduled_time="07:00", frequency="daily"))
dog.add_task(Task("Heartworm pill",  5, priority=1, type="medication", scheduled_time="07:05", frequency="once"))
dog.add_task(Task("Morning walk",   30, priority=2, type="walk",       scheduled_time="07:30", frequency="daily"))
dog.add_task(Task("Evening walk",   30, priority=2, type="walk",       scheduled_time="18:00", frequency="daily"))

# --- 4. Add tasks to Luna (cat) ---
# Note: Luna's Breakfast also at 07:00 → conflicts with Buddy's Breakfast
cat.add_task(Task("Breakfast",       5, priority=1, type="feeding",    scheduled_time="07:00", frequency="daily"))
cat.add_task(Task("Playtime",       20, priority=4, type="enrichment", scheduled_time="19:00", frequency="daily"))
cat.add_task(Task("Brushing",       15, priority=5, type="grooming",   frequency="weekly"))

# --- 5. Register pets under owner ---
owner.add_pet(dog)
owner.add_pet(cat)

# --- 6. Generate and display schedule (conflict warnings appear automatically) ---
scheduler = Scheduler(owner=owner)
scheduler.generate_plan()
scheduler.display_plan()

# --- 7. Demo: call detect_conflicts() directly to inspect the list ---
print("=== Conflict detection (direct call) ===")
conflicts = scheduler.detect_conflicts()
if conflicts:
    print(f"  {len(conflicts)} conflict(s) found:")
    for w in conflicts:
        print(f"  {w}")
else:
    print("  No conflicts detected.")

# --- 8. Demo: recurring tasks ---
print("\n=== Recurring task demo ===")
print(f"Today: {date.today()}\n")

breakfast = next(t for t in dog.get_tasks() if t.name == "Breakfast" and not t.is_completed)
next_task = dog.mark_task_complete(breakfast)
print(f"Marked '{breakfast.name}' complete (frequency: {breakfast.frequency})")
if next_task:
    print(f"Auto-created next occurrence: due {next_task.due_date}")

pill = next(t for t in dog.get_tasks() if t.name == "Heartworm pill")
result = dog.mark_task_complete(pill)
print(f"\nMarked 'Heartworm pill' complete (frequency: {pill.frequency})")
print(f"New task created: {result is not None}  ← expected False for 'once'")