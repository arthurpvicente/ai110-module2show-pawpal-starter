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

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
==============================================
  TODAY'S SCHEDULE  —  Arthur
==============================================

  Buddy  (Dog)
  --------------------------------------------
  08:00   Morning Walk            30 min  [HIGH]
  08:30   Feeding                 10 min  [HIGH]
  --------------------------------------------
  Time: [#############.......]  40 / 60 min  1 task(s) skipped (not enough time)

  Luna  (Cat)
  --------------------------------------------
  08:00   Grooming                20 min  [MED] 
  08:20   Playtime                15 min  [LOW] 
  --------------------------------------------
  Time: [############........]  35 / 60 min

==============================================
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Behavior |
|---------|-----------|----------|
| Sort by time | `Scheduler.sort_by_time()` | Tasks with a `preferred_start` (HH:MM) are placed first in time order; unanchored tasks follow sorted by priority. |
| Sort by priority | `Scheduler.sort_by_priority()` | Returns all tasks ranked HIGH → MEDIUM → LOW; used internally by `filter_feasible()`. |
| Filter by feasibility | `Scheduler.filter_feasible()` | Greedy selection — adds tasks in priority order until the available time budget is exhausted; skips tasks that no longer fit. |
| Filter by pet / status | `Owner.get_tasks(pet_name=, completed=)` | Returns tasks across all pets, optionally narrowed to a specific pet name and/or completion status (`True`/`False`). |
| Filter by status (per pet) | `Pet.get_tasks(completed=)` | Returns a single pet's tasks filtered by completion status; passing no argument returns all tasks. |
| Same-pet conflict detection | `Scheduler.check_conflicts()` | Before scheduling, compares `preferred_start` windows of tasks on the same pet. Returns a list of warning strings for any overlapping pairs — does not crash. |
| Cross-pet conflict detection | `detect_conflicts(plans)` | After scheduling, compares assigned `time_slot` windows across different pets. Returns conflict dicts with pet names, task names, and overlap start/end times. |
| Recurring task rescheduling | `Scheduler.mark_task_complete(task)` | Marks a task complete and, if `recurrence` is `"daily"` or `"weekly"`, automatically creates the next occurrence with a `due_date` of today + 1 day or today + 7 days using `timedelta`. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
