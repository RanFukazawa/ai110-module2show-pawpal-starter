"""
tests/test_pawpal.py - Unit tests for PawPal+ core logic.
Run with: pytest tests/test_pawpal.py -v
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from pawpal_system import Owner, Pet, Task, Schedule


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
def sample_owner(sample_pet):
    """An owner with one pet and office schedule."""
    owner = Owner(name="Alex")
    owner.set_availability(
        work_schedule="office",
        available_hours=3,
        preferred_morning_start="07:00",
        preferred_evening_end="20:00",
    )
    owner.add_pet(sample_pet)
    return owner


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