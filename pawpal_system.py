"""
pawpal_system.py - PawPal+ logic layer
Skeleton classes translated from UML. Method bodies to be implemented in later phases.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Owner:
    """Represents a pet owner and their scheduling availability."""
    name: str
    work_schedule: str = ""           # e.g. "office", "remote", "off"
    available_hours: int = 8          # total free hours in the day
    preferred_morning_start: str = "" # e.g. "07:00"
    preferred_evening_end: str = ""   # e.g. "21:00"

    def get_name(self) -> str:
        """Return the owner's name."""
        pass

    def get_availability(self) -> dict:
        """Return a dict summarising the owner's availability and preferences."""
        pass

    def set_availability(
        self,
        work_schedule: str,
        available_hours: int,
        preferred_morning_start: str,
        preferred_evening_end: str,
    ) -> None:
        """Update the owner's availability and scheduling preferences."""
        pass


@dataclass
class Pet:
    """Represents a pet and its associated care tasks."""
    name: str
    species: str
    gender: str
    age: int
    owner: Owner = field(default=None)
    health_history: str = ""
    medical_needs: str = ""
    tasks: List[Task] = field(default_factory=list)

    def get_name(self) -> str:
        """Return the pet's name."""
        pass

    def get_species(self) -> str:
        """Return the pet's species."""
        pass

    def get_age(self) -> int:
        """Return the pet's age."""
        pass

    def get_medical_needs(self) -> str:
        """Return the pet's medical needs."""
        pass

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list."""
        pass

    def get_tasks(self) -> List[Task]:
        """Return all tasks associated with this pet."""
        pass


@dataclass
class Task:
    """Represents a single pet care task (feeding, walk, medication, etc.)."""
    name: str
    duration: int                     # in minutes
    priority: int                     # e.g. 1 (high) to 5 (low)
    type: str                         # e.g. "feeding", "walk", "medication"
    scheduled_time: str = ""          # e.g. "08:00"
    is_completed: bool = False

    def get_name(self) -> str:
        """Return the task name."""
        pass

    def get_duration(self) -> int:
        """Return the task duration in minutes."""
        pass

    def get_priority(self) -> int:
        """Return the task priority level."""
        pass

    def get_type(self) -> str:
        """Return the task type."""
        pass

    def set_priority(self, priority: int) -> None:
        """Update the task's priority level."""
        pass

    def mark_complete(self) -> None:
        """Mark the task as completed."""
        pass


@dataclass
class Schedule:
    """Generates and displays a daily care plan based on tasks and owner constraints."""
    owner: Owner
    pets: List[Pet] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)
    generated_plan: List[dict] = field(default_factory=list)
    reasoning: str = ""

    def generate_plan(self) -> List[dict]:
        """
        Build a daily schedule by sorting and fitting tasks within the
        owner's available hours, respecting priority and preferences.
        Returns the generated plan as an ordered list of task dicts.
        """
        pass

    def explain_reasoning(self) -> str:
        """Return a human-readable explanation of how the plan was generated."""
        pass

    def display_plan(self) -> None:
        """Print or return the daily plan in a readable format."""
        pass