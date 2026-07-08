"""
pawpal_system.py - PawPal+ logic layer
Full implementation of all four core classes.
"""
 
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date, timedelta
 
 
@dataclass
class Owner:
    """Represents a pet owner and their scheduling availability."""
    name: str
    work_schedule: str = "off"        # "office", "remote", "off"
    available_hours: int = 8          # total free hours in the day
    preferred_morning_start: str = "07:00"
    preferred_evening_end: str = "21:00"
    pets: List[Pet] = field(default_factory=list)
 
    def get_name(self) -> str:
        """Return the owner's name."""
        return self.name
 
    def get_availability(self) -> dict:
        """Return a dict summarising the owner's availability and preferences."""
        return {
            "work_schedule": self.work_schedule,
            "available_hours": self.available_hours,
            "preferred_morning_start": self.preferred_morning_start,
            "preferred_evening_end": self.preferred_evening_end,
        }
 
    def set_availability(
        self,
        work_schedule: str,
        available_hours: int,
        preferred_morning_start: str,
        preferred_evening_end: str,
    ) -> None:
        """Update the owner's availability and scheduling preferences."""
        valid_schedules = {"office", "remote", "off"}
        if work_schedule not in valid_schedules:
            raise ValueError(f"work_schedule must be one of {valid_schedules}.")
        if not 0 <= available_hours <= 24:
            raise ValueError("available_hours must be between 0 and 24.")
        self.work_schedule = work_schedule
        self.available_hours = available_hours
        self.preferred_morning_start = preferred_morning_start
        self.preferred_evening_end = preferred_evening_end
 
    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        pet.owner = self
        self.pets.append(pet)
 
    def get_all_tasks(self) -> List[Task]:
        """Return every task across all pets owned."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks
 
    def __str__(self) -> str:
        return (
            f"{self.name} | {self.work_schedule} day | "
            f"{self.available_hours}h available | "
            f"{len(self.pets)} pet(s)"
        )
 
 
@dataclass
class Pet:
    """Represents a pet and its associated care tasks."""
    name: str
    species: str
    gender: str
    age: int
    owner: Optional[Owner] = field(default=None)
    health_history: str = ""
    medical_needs: str = ""
    tasks: List[Task] = field(default_factory=list)
 
    def get_name(self) -> str:
        """Return the pet's name."""
        return self.name
 
    def get_species(self) -> str:
        """Return the pet's species."""
        return self.species
 
    def get_age(self) -> int:
        """Return the pet's age."""
        return self.age
 
    def get_medical_needs(self) -> str:
        """Return the pet's medical needs."""
        return self.medical_needs
 
    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list."""
        self.tasks.append(task)
 
    def get_tasks(self) -> List[Task]:
        """Return all tasks associated with this pet."""
        return self.tasks
 
    def get_pending_tasks(self) -> List[Task]:
        """Return only tasks that have not been completed."""
        return [t for t in self.tasks if not t.is_completed]

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Mark a task complete and auto-create the next occurrence for recurring tasks."""
        task.mark_complete()
        if task.frequency == "daily":
            next_due = task.due_date + timedelta(days=1)
        elif task.frequency == "weekly":
            next_due = task.due_date + timedelta(weeks=1)
        else:
            return None
        next_task = Task(
            name=task.name,
            duration=task.duration,
            priority=task.priority,
            type=task.type,
            scheduled_time=task.scheduled_time,
            frequency=task.frequency,
            due_date=next_due,
        )
        self.add_task(next_task)
        return next_task
 
    def __str__(self) -> str:
        return (
            f"{self.name} ({self.species}, {self.age} yr old {self.gender}) — "
            f"{len(self.tasks)} task(s)"
        )
 
 
@dataclass
class Task:
    """Represents a single pet care activity."""
    name: str
    duration: int                     # in minutes
    priority: int                     # 1 (highest) to 5 (lowest)
    type: str                         # "feeding", "walk", "medication", "grooming", "enrichment"
    scheduled_time: str = ""          # e.g. "08:00"
    is_completed: bool = False
    frequency: str = "once"           # "once", "daily", "weekly"
    due_date: date = field(default_factory=date.today)
 
    def get_name(self) -> str:
        """Return the task name."""
        return self.name
 
    def get_duration(self) -> int:
        """Return the task duration in minutes."""
        return self.duration
 
    def get_priority(self) -> int:
        """Return the task priority level."""
        return self.priority
 
    def get_type(self) -> str:
        """Return the task type."""
        return self.type
 
    def set_priority(self, priority: int) -> None:
        """Update the task's priority level. Must be between 1 and 5."""
        if not 1 <= priority <= 5:
            raise ValueError("Priority must be between 1 (highest) and 5 (lowest).")
        self.priority = priority
 
    def mark_complete(self) -> None:
        """Mark the task as completed."""
        self.is_completed = True
 
    def __str__(self) -> str:
        time_label = f" at {self.scheduled_time}" if self.scheduled_time else ""
        status = "✓" if self.is_completed else "○"
        return (
            f"[{status}] {self.name}{time_label} "
            f"({self.duration} min, priority {self.priority}, {self.frequency}, due {self.due_date})"
        )
 
 
@dataclass
class Schedule:
    """Sorts and fits all pet tasks within the owner's available hours to produce a daily plan."""
    owner: Owner
    pets: List[Pet] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)
    generated_plan: List[dict] = field(default_factory=list)
    reasoning: str = ""
 
    def _collect_tasks(self) -> List[Task]:
        """Gather all pending tasks from all pets."""
        all_tasks = []
        for pet in self.owner.pets:
            for task in pet.get_pending_tasks():
                all_tasks.append((pet, task))
        return all_tasks
 
    def generate_plan(self) -> List[dict]:
        """Sort all pending tasks by priority and duration, fit them into available hours, and return the plan."""
        available_minutes = self.owner.available_hours * 60
        pet_task_pairs = self._collect_tasks()
 
        # Sort: priority ascending (1 first), then duration ascending
        pet_task_pairs.sort(key=lambda pt: (pt[1].priority, pt[1].duration))
 
        plan = []
        scheduled_minutes = 0
        skipped = []
 
        for pet, task in pet_task_pairs:
            if scheduled_minutes + task.duration <= available_minutes:
                plan.append({
                    "pet": pet.name,
                    "task": task.name,
                    "type": task.type,
                    "duration": task.duration,
                    "priority": task.priority,
                    "scheduled_time": task.scheduled_time,
                    "is_completed": task.is_completed,
                })
                scheduled_minutes += task.duration
            else:
                skipped.append(f"{task.name} for {pet.name}")
 
        self.generated_plan = plan
        self.tasks = [pt[1] for pt in pet_task_pairs]

        # Sort the final plan chronologically by scheduled_time
        self.generated_plan = self.sort_by_time(self.generated_plan)
 
        # Build reasoning string
        priority_counts = {"high": 0, "medium": 0, "low": 0}
        for entry in plan:
            label = self._priority_label(entry["priority"])
            priority_counts[label] += 1

        reasons = [
            f"Tasks were sorted by priority (high → medium → low), then by duration (shorter first).",
            f"Owner '{self.owner.name}' has {self.owner.available_hours}h "
            f"({available_minutes} min) available on a {self.owner.work_schedule} day.",
            f"{len(plan)} task(s) scheduled ({priority_counts['high']} high, "
            f"{priority_counts['medium']} medium, {priority_counts['low']} low), "
            f"using {scheduled_minutes} min.",
        ]
        if skipped:
            reasons.append(
                f"{len(skipped)} task(s) could not fit and were skipped: {', '.join(skipped)}."
            )
        self.reasoning = " ".join(reasons)
 
        return self.generated_plan
 
    def detect_conflicts(self) -> List[str]:
        """
        Scan the sorted plan for overlapping tasks.
        A conflict occurs when a task's start time falls before the previous task finishes.
        Returns a list of warning strings (empty list = no conflicts).
        """
        warnings = []
        # Only check tasks that have a real scheduled_time
        timed = [e for e in self.generated_plan if e["scheduled_time"]]

        for i in range(1, len(timed)):
            prev = timed[i - 1]
            curr = timed[i]

            # Convert "HH:MM" to total minutes for arithmetic
            prev_start = self._time_to_minutes(prev["scheduled_time"])
            prev_end   = prev_start + prev["duration"]
            curr_start = self._time_to_minutes(curr["scheduled_time"])

            if curr_start < prev_end:
                overlap = prev_end - curr_start
                warnings.append(
                    f"⚠️  Conflict: [{curr['pet']}] '{curr['task']}' at {curr['scheduled_time']} "
                    f"overlaps with [{prev['pet']}] '{prev['task']}' at {prev['scheduled_time']} "
                    f"by {overlap} min."
                )

        return warnings

    @staticmethod
    def _time_to_minutes(time_str: str) -> int:
        """Convert a 'HH:MM' string to total minutes since midnight."""
        hours, minutes = map(int, time_str.split(":"))
        return hours * 60 + minutes

    @staticmethod
    def sort_by_time(plan: List[dict]) -> List[dict]:
        """Sort a plan list chronologically; tasks with no scheduled_time go to the end."""
        return sorted(
            plan,
            # "99:99" sentinel sorts after any real HH:MM, pushing timeless tasks to the end
            key=lambda entry: entry["scheduled_time"] if entry["scheduled_time"] else "99:99"
        )

    def filter_plan(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> List[dict]:
        """Return a filtered subset of the generated plan by pet name and/or completion status."""
        result = self.generated_plan
        if pet_name is not None:
            result = [e for e in result if e["pet"].lower() == pet_name.lower()]
        if completed is not None:
            result = [e for e in result if e.get("is_completed", False) == completed]
        return result

    def detect_conflicts(self) -> List[str]:
        """Scan the sorted plan for overlapping tasks; return a list of warning strings."""
        warnings = []
        timed = [e for e in self.generated_plan if e["scheduled_time"]]
        for i in range(1, len(timed)):
            prev = timed[i - 1]
            curr = timed[i]
            prev_start = self._time_to_minutes(prev["scheduled_time"])
            prev_end   = prev_start + prev["duration"]
            curr_start = self._time_to_minutes(curr["scheduled_time"])
            if curr_start < prev_end:
                overlap = prev_end - curr_start
                warnings.append(
                    f"⚠️  Conflict: [{curr['pet']}] '{curr['task']}' at {curr['scheduled_time']} "
                    f"overlaps with [{prev['pet']}] '{prev['task']}' at {prev['scheduled_time']} "
                    f"by {overlap} min."
                )
        return warnings

    @staticmethod
    def _time_to_minutes(time_str: str) -> int:
        """Convert a 'HH:MM' string to total minutes since midnight."""
        hours, minutes = map(int, time_str.split(":"))
        return hours * 60 + minutes

    def explain_reasoning(self) -> str:
        """Return a human-readable explanation of how the plan was generated."""
        if not self.reasoning:
            return "No plan has been generated yet. Call generate_plan() first."
        return self.reasoning
 
    @staticmethod
    def _priority_label(priority: int) -> str:
        """Convert numeric priority to a human-readable label."""
        return {1: "high", 2: "high", 3: "medium", 4: "low", 5: "low"}.get(priority, str(priority))
 
    def display_plan(self) -> None:
        """Print the daily plan to the console in a readable format."""
        if not self.generated_plan:
            print("No plan generated yet. Call generate_plan() first.")
            return
 
        total = sum(e["duration"] for e in self.generated_plan)
 
        # --- Combined timeline ---
        print(f"\n{'='*52}")
        print(f"  PawPal+ Daily Plan for {self.owner.name} (Owner)")
        print(f"{'='*52}")
        for entry in self.generated_plan:
            time_label = entry["scheduled_time"] if entry["scheduled_time"] else "--:--"
            priority_label = self._priority_label(entry["priority"])
            print(
                f"  {time_label} — [{entry['pet']}] {entry['task']} "
                f"({entry['duration']} min) [priority: {priority_label}]"
            )
        print(f"\n  Total time: {total} min ({total // 60}h {total % 60}m)")
        print(f"  Reasoning: {self.reasoning}")

        # --- Conflict warnings ---
        conflicts = self.detect_conflicts()
        if conflicts:
            print()
            for warning in conflicts:
                print(f"  {warning}")

        # --- Per-pet breakdown ---
        print(f"\n{'─'*52}")
        print("  Breakdown by pet")
        print(f"{'─'*52}")
        for pet in self.owner.pets:
            pet_entries = [e for e in self.generated_plan if e["pet"] == pet.name]
            if not pet_entries:
                continue
            print(f"\n  {pet.name} ({pet.species}, {pet.age} yr old {pet.gender})")
            for entry in pet_entries:
                time_label = entry["scheduled_time"] if entry["scheduled_time"] else "--:--"
                priority_label = self._priority_label(entry["priority"])
                print(
                    f"    {time_label} — {entry['task']} "
                    f"({entry['duration']} min) [priority: {priority_label}]"
                )
        print(f"\n{'='*52}\n")