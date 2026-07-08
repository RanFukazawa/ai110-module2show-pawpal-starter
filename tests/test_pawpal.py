"""
tests/test_pawpal.py - Unit tests for PawPal+ core logic.
Run with: pytest tests/test_pawpal.py -v
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


# ---------------------------------------------------------------------------
# Fixtures — reusable test objects
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_task():
    """A basic feeding task for use across tests."""
    return Task(name="Breakfast", duration=10, priority=1, type="feeding", scheduled_time="07:00")


@pytest.fixture
def sample_pet():
    """A basic pet with no tasks."""
    return Pet(name="Buddy", species="Dog", gender="Male", age=3)


@pytest.fixture
def sample_owner():
    """A standalone owner with office schedule and 3 free hours."""
    owner = Owner(name="Alex")
    owner.set_availability(
        work_schedule="office",
        available_hours=3,
        preferred_morning_start="07:00",
        preferred_evening_end="20:00",
    )
    return owner


@pytest.fixture
def owner_with_pet(sample_owner, sample_pet):
    """Owner with one pet already registered."""
    sample_owner.add_pet(sample_pet)
    return sample_owner


# ---------------------------------------------------------------------------
# Test 1: Task completion
# ---------------------------------------------------------------------------

class TestTaskCompletion:

    def test_task_is_incomplete_by_default(self, sample_task):
        """A newly created task should not be completed."""
        assert sample_task.is_completed is False

    def test_mark_complete_sets_flag(self, sample_task):
        """Calling mark_complete() should set is_completed to True."""
        sample_task.mark_complete()
        assert sample_task.is_completed is True

    def test_mark_complete_is_idempotent(self, sample_task):
        """Calling mark_complete() twice should not raise an error."""
        sample_task.mark_complete()
        sample_task.mark_complete()
        assert sample_task.is_completed is True


# ---------------------------------------------------------------------------
# Test 2: Task addition to a Pet
# ---------------------------------------------------------------------------

class TestTaskAddition:

    def test_new_pet_has_no_tasks(self, sample_pet):
        """A pet with no tasks added should have an empty task list."""
        assert len(sample_pet.get_tasks()) == 0

    def test_add_task_increases_count(self, sample_pet, sample_task):
        """Adding one task should increase the pet's task count to 1."""
        sample_pet.add_task(sample_task)
        assert len(sample_pet.get_tasks()) == 1

    def test_add_multiple_tasks_increases_count(self, sample_pet):
        """Adding three tasks should result in a task count of 3."""
        sample_pet.add_task(Task("Breakfast",    10, priority=1, type="feeding"))
        sample_pet.add_task(Task("Morning walk", 30, priority=2, type="walk"))
        sample_pet.add_task(Task("Medication",    5, priority=1, type="medication"))
        assert len(sample_pet.get_tasks()) == 3

    def test_added_task_is_retrievable(self, sample_pet, sample_task):
        """The task added should be the same object returned by get_tasks()."""
        sample_pet.add_task(sample_task)
        assert sample_task in sample_pet.get_tasks()


# ---------------------------------------------------------------------------
# Test 3: Sorting correctness
# ---------------------------------------------------------------------------

class TestSortByTime:

    def test_tasks_sorted_chronologically(self):
        """Tasks added out of order should be returned in HH:MM order."""
        unsorted = [
            {"task": "Evening walk",  "scheduled_time": "18:00"},
            {"task": "Breakfast",     "scheduled_time": "07:00"},
            {"task": "Morning walk",  "scheduled_time": "07:30"},
        ]
        result = Scheduler.sort_by_time(unsorted)
        times = [e["scheduled_time"] for e in result]
        assert times == ["07:00", "07:30", "18:00"]

    def test_timeless_tasks_go_to_end(self):
        """Tasks with no scheduled_time should appear after all timed tasks."""
        plan = [
            {"task": "Brushing",     "scheduled_time": ""},
            {"task": "Breakfast",    "scheduled_time": "07:00"},
            {"task": "Evening walk", "scheduled_time": "18:00"},
        ]
        result = Scheduler.sort_by_time(plan)
        assert result[-1]["task"] == "Brushing"

    def test_empty_plan_sorts_without_error(self):
        """sort_by_time on an empty list should return an empty list."""
        assert Scheduler.sort_by_time([]) == []

    def test_generate_plan_output_is_sorted(self, owner_with_pet, sample_pet):
        """generate_plan() should produce a chronologically sorted plan."""
        # Add tasks out of order
        sample_pet.add_task(Task("Evening walk", 30, priority=2, type="walk",    scheduled_time="18:00"))
        sample_pet.add_task(Task("Breakfast",    10, priority=1, type="feeding", scheduled_time="07:00"))
        scheduler = Scheduler(owner=owner_with_pet)
        plan = scheduler.generate_plan()
        timed = [e for e in plan if e["scheduled_time"]]
        times = [e["scheduled_time"] for e in timed]
        assert times == sorted(times)


# ---------------------------------------------------------------------------
# Test 4: Recurrence logic
# ---------------------------------------------------------------------------

class TestRecurringTasks:

    def test_daily_task_creates_next_occurrence(self, sample_pet):
        """Marking a daily task complete should create a new task due tomorrow."""
        today = date.today()
        task = Task("Breakfast", 10, priority=1, type="feeding",
                    scheduled_time="07:00", frequency="daily", due_date=today)
        sample_pet.add_task(task)
        next_task = sample_pet.mark_task_complete(task)
        assert next_task is not None
        assert next_task.due_date == today + timedelta(days=1)

    def test_weekly_task_creates_next_occurrence(self, sample_pet):
        """Marking a weekly task complete should create a new task due in 7 days."""
        today = date.today()
        task = Task("Brushing", 15, priority=5, type="grooming",
                    frequency="weekly", due_date=today)
        sample_pet.add_task(task)
        next_task = sample_pet.mark_task_complete(task)
        assert next_task is not None
        assert next_task.due_date == today + timedelta(weeks=1)

    def test_once_task_returns_none(self, sample_pet):
        """Marking a one-time task complete should return None with no new task."""
        task = Task("Vet visit", 60, priority=1, type="medication", frequency="once")
        sample_pet.add_task(task)
        result = sample_pet.mark_task_complete(task)
        assert result is None

    def test_recurring_task_inherits_attributes(self, sample_pet):
        """The new occurrence should have the same name, duration, and priority."""
        today = date.today()
        task = Task("Morning walk", 30, priority=2, type="walk",
                    scheduled_time="07:30", frequency="daily", due_date=today)
        sample_pet.add_task(task)
        next_task = sample_pet.mark_task_complete(task)
        assert next_task.name == task.name
        assert next_task.duration == task.duration
        assert next_task.priority == task.priority
        assert next_task.frequency == task.frequency

    def test_original_task_is_marked_complete(self, sample_pet):
        """The original task should be marked complete after mark_task_complete()."""
        task = Task("Breakfast", 10, priority=1, type="feeding", frequency="daily")
        sample_pet.add_task(task)
        sample_pet.mark_task_complete(task)
        assert task.is_completed is True


# ---------------------------------------------------------------------------
# Test 5: Conflict detection
# ---------------------------------------------------------------------------

class TestConflictDetection:

    def _make_scheduler(self, owner, pet):
        """Helper to build and generate a schedule."""
        scheduler = Scheduler(owner=owner)
        scheduler.generate_plan()
        return scheduler

    def test_no_conflicts_when_tasks_do_not_overlap(self, owner_with_pet, sample_pet):
        """Non-overlapping tasks should produce no conflict warnings."""
        sample_pet.add_task(Task("Breakfast",    10, priority=1, type="feeding",    scheduled_time="07:00"))
        sample_pet.add_task(Task("Morning walk", 30, priority=2, type="walk",       scheduled_time="08:00"))
        scheduler = self._make_scheduler(owner_with_pet, sample_pet)
        assert scheduler.detect_conflicts() == []

    def test_exact_same_time_flagged_as_conflict(self, owner_with_pet, sample_pet):
        """Two tasks scheduled at the exact same time should be flagged."""
        sample_pet.add_task(Task("Breakfast", 10, priority=1, type="feeding",    scheduled_time="07:00"))
        sample_pet.add_task(Task("Medication", 5, priority=1, type="medication", scheduled_time="07:00"))
        scheduler = self._make_scheduler(owner_with_pet, sample_pet)
        conflicts = scheduler.detect_conflicts()
        assert len(conflicts) >= 1

    def test_overlapping_tasks_flagged(self, owner_with_pet, sample_pet):
        """A task starting before the previous one finishes should be flagged."""
        # Breakfast: 07:00 → 07:10 (10 min); Medication: 07:05 → overlaps by 5 min
        sample_pet.add_task(Task("Breakfast",  10, priority=1, type="feeding",    scheduled_time="07:00"))
        sample_pet.add_task(Task("Medication",  5, priority=1, type="medication", scheduled_time="07:05"))
        scheduler = self._make_scheduler(owner_with_pet, sample_pet)
        conflicts = scheduler.detect_conflicts()
        assert len(conflicts) == 1
        assert "5 min" in conflicts[0]

    def test_no_conflicts_empty_plan(self, sample_owner):
        """A scheduler with no tasks should return no conflicts."""
        pet = Pet(name="Luna", species="Cat", gender="Female", age=2)
        sample_owner.add_pet(pet)
        scheduler = Scheduler(owner=sample_owner)
        scheduler.generate_plan()
        assert scheduler.detect_conflicts() == []

    def test_timeless_tasks_not_checked_for_conflicts(self, owner_with_pet, sample_pet):
        """Tasks with no scheduled_time should not be included in conflict detection."""
        sample_pet.add_task(Task("Brushing", 15, priority=5, type="grooming"))  # no time
        sample_pet.add_task(Task("Playtime", 20, priority=4, type="enrichment"))  # no time
        scheduler = self._make_scheduler(owner_with_pet, sample_pet)
        assert scheduler.detect_conflicts() == []