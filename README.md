# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

```
====================================================
  PawPal+ Daily Plan for Alex (Owner)
====================================================
  07:00 — [Luna] Breakfast (5 min) [priority: high]
  07:00 — [Buddy] Breakfast (10 min) [priority: high]
  07:05 — [Buddy] Heartworm pill (5 min) [priority: high]
  07:30 — [Buddy] Morning walk (30 min) [priority: high]
  18:00 — [Buddy] Evening walk (30 min) [priority: high]
  19:00 — [Luna] Playtime (20 min) [priority: low]
  --:-- — [Luna] Brushing (15 min) [priority: low]

  Total time: 115 min (1h 55m)
  Reasoning: Tasks were sorted by priority (high → medium → low), then by duration (shorter first). Owner 'Alex' has 3h (180 min) available on a office day. 7 task(s) scheduled (5 high, 0 medium, 2 low), using 115 min.

  ⚠️  Conflict: [Buddy] 'Breakfast' at 07:00 overlaps with [Luna] 'Breakfast' at 07:00 by 5 min.
  ⚠️  Conflict: [Buddy] 'Heartworm pill' at 07:05 overlaps with [Buddy] 'Breakfast' at 07:00 by 5 min.

────────────────────────────────────────────────────
  Breakdown by pet
────────────────────────────────────────────────────

  Buddy (Dog, 3 yr old Male)
    07:00 — Breakfast (10 min) [priority: high]
    07:05 — Heartworm pill (5 min) [priority: high]
    07:30 — Morning walk (30 min) [priority: high]
    18:00 — Evening walk (30 min) [priority: high]

  Luna (Cat, 2 yr old Female)
    07:00 — Breakfast (5 min) [priority: high]
    19:00 — Playtime (20 min) [priority: low]
    --:-- — Brushing (15 min) [priority: low]

====================================================

=== Conflict detection (direct call) ===
  2 conflict(s) found:
  ⚠️  Conflict: [Buddy] 'Breakfast' at 07:00 overlaps with [Luna] 'Breakfast' at 07:00 by 5 min.
  ⚠️  Conflict: [Buddy] 'Heartworm pill' at 07:05 overlaps with [Buddy] 'Breakfast' at 07:00 by 5 min.

=== Recurring task demo ===
Today: 2026-07-07

Marked 'Breakfast' complete (frequency: daily)
Auto-created next occurrence: due 2026-07-08

Marked 'Heartworm pill' complete (frequency: once)
New task created: False  ← expected False for 'once'
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest tests/test_pawpal.py

# Run with verbose output (shows each test name):
python -m pytest tests/test_pawpal.py -v

# Run a specific test class only:
python -m pytest tests/test_pawpal.py::TestConflictDetection -v

# Run with coverage (requires pytest-cov):
python -m pytest --cov
```

### What the tests cover

| Test class | What it verifies |
|---|---|
| `TestTaskCompletion` | `mark_complete()` sets the flag correctly and is idempotent |
| `TestTaskAddition` | Adding tasks to a pet increases count and tasks are retrievable |
| `TestSortByTime` | Tasks are returned in chronological order; timeless tasks go to the end |
| `TestRecurringTasks` | Daily/weekly tasks auto-create the next occurrence; one-time tasks do not |
| `TestConflictDetection` | Overlapping and same-time tasks are flagged; clean schedules return no warnings |

### Sample test output

```
======================================================= test session starts ========================================================
platform darwin -- Python 3.14.2, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/ranfukazawa/Desktop/CodePath/AI110/Project/ai110-module2show-pawpal-starter
plugins: anyio-4.14.0
collected 21 items

tests/test_pawpal.py .....................                                                                                   [100%]

======================================================== 21 passed in 0.05s ========================================================
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Schedule.sort_by_time()` | Sorts tasks chronologically by `scheduled_time` (HH:MM); tasks with no scheduled time are pushed to the end |
| Task prioritisation | `Schedule.generate_plan()` | Tasks are sorted by priority (1 = high → 5 = low) then by duration (shorter first) before being fitted into the owner's available hours |
| Filtering | `Schedule.filter_plan()` | Filters the generated plan by pet name, completion status, or both; returns a subset of `generated_plan` |
| Conflict detection | `Schedule.detect_conflicts()` | Scans the sorted plan for overlapping time slots; returns warning messages when a task starts before the previous one finishes |
| Recurring tasks | `Pet.mark_task_complete()` | When a daily or weekly task is marked complete, a new instance is automatically created with the next due date using `timedelta` |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
