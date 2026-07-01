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

Run the test suite from the project root:

```bash
python -m pytest tests/test_pawpal.py -v
```

### What the tests cover

| Test | What it verifies |
|------|-----------------|
| `test_mark_complete_changes_status` | `Task.mark_complete()` flips `completed` to `True` |
| `test_add_task_increases_count` | `Pet.add_task()` appends to the task list |
| `test_sort_by_priority_happy_path` | `Scheduler.sort_by_priority()` returns HIGH → MEDIUM → LOW |
| `test_filter_feasible_respects_time_budget` | Greedy selection stays within `available_time` |
| `test_filter_feasible_zero_time_returns_empty` | No tasks scheduled when time budget is 0 |
| `test_check_conflicts_detects_same_start_time` | Two tasks at the same time generate a conflict warning |
| `test_check_conflicts_no_conflict_with_one_task` | Single task produces no conflicts |
| `test_mark_task_complete_recurring_creates_new_task` | Completing a `recurrence="daily"` task creates a new copy |
| `test_mark_task_complete_non_recurring_returns_none` | Non-recurring task completion returns `None` |
| `test_owner_get_tasks_aggregates_across_pets` | `Owner.get_tasks()` collects tasks from all pets |
| `test_owner_get_tasks_filters_completed` | `completed=False` excludes finished tasks |
| `test_owner_get_tasks_no_pets_returns_empty` | Owner with no pets returns an empty list |

### Sample test output

```
collected 12 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  8%]
tests/test_pawpal.py::test_add_task_increases_count PASSED               [ 16%]
tests/test_pawpal.py::test_sort_by_priority_happy_path PASSED            [ 25%]
tests/test_pawpal.py::test_filter_feasible_respects_time_budget PASSED   [ 33%]
tests/test_pawpal.py::test_filter_feasible_zero_time_returns_empty PASSED [ 41%]
tests/test_pawpal.py::test_check_conflicts_detects_same_start_time PASSED [ 50%]
tests/test_pawpal.py::test_check_conflicts_no_conflict_with_one_task PASSED [ 58%]
tests/test_pawpal.py::test_mark_task_complete_recurring_creates_new_task PASSED [ 66%]
tests/test_pawpal.py::test_mark_task_complete_non_recurring_returns_none PASSED [ 75%]
tests/test_pawpal.py::test_owner_get_tasks_aggregates_across_pets PASSED [ 83%]
tests/test_pawpal.py::test_owner_get_tasks_filters_completed PASSED      [ 91%]
tests/test_pawpal.py::test_owner_get_tasks_no_pets_returns_empty PASSED  [100%]

============================== 12 passed in 0.01s ==============================
```

### Confidence Level

⭐⭐⭐⭐ (4/5)

The core scheduling behaviors — priority sorting, time filtering, conflict detection, and recurring tasks — are all tested and passing. The main gap is that the Streamlit UI layer and the `generate()` / `detect_conflicts()` end-to-end flow are not covered by automated tests, so full system behavior under real user input remains manually verified only.

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

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Owner & pet management** | Create an owner profile and add multiple pets (dog, cat, or other). Each pet holds its own task list. |
| **Task creation** | Add tasks with a title, duration (minutes), priority (HIGH / MEDIUM / LOW), optional preferred start time, and optional daily or weekly recurrence. |
| **Priority-based sorting** | `Scheduler.sort_by_priority()` ranks all tasks HIGH → MEDIUM → LOW so the most important care always gets considered first. |
| **Time-anchored sorting** | `Scheduler.sort_by_time()` places tasks with a `preferred_start` (HH:MM) in chronological order; unanchored tasks follow, sorted by priority. |
| **Greedy feasibility filtering** | `Scheduler.filter_feasible()` iterates tasks in priority order and keeps adding them until the owner's available-time budget is exhausted — guaranteeing the schedule never over-commits. |
| **Same-pet conflict warnings** | `Scheduler.check_conflicts()` compares `preferred_start` windows for tasks on the same pet and reports any overlapping pairs before the schedule is built. |
| **Cross-pet conflict detection** | `detect_conflicts(plans)` compares assigned `time_slot` windows across different pets and returns structured conflict dicts with overlap start/end times. |
| **Daily recurrence** | Completing a task marked `recurrence="daily"` automatically creates the next occurrence due tomorrow via `timedelta`. |
| **Weekly recurrence** | Same flow for `recurrence="weekly"` — next occurrence is due in 7 days. |
| **Schedule generation & display** | `Scheduler.generate()` produces a `DailyPlan` with per-pet timeline rows, a progress bar showing minutes used vs. available, and a count of skipped tasks. |
| **Streamlit UI** | A browser-based form interface lets users manage owners, pets, and tasks, then generate and view a formatted daily plan with conflict warnings — no CLI required. |

## 📸 Demo Walkthrough

### Main UI features

The Streamlit app (`app.py`) has four sections:

- **Owner** — set or update the owner's name.
- **Pets** — add pets by name and species; a live table shows each pet's task count.
- **Tasks** — pick a pet, then fill in a task form (title, duration, priority, preferred start, recurrence) and submit.
- **Generate Schedule** — set the available-time budget per pet and click "Generate" to see the daily plan, conflict warnings, and recurring-task status.

### Example workflow

1. Open the app (`streamlit run app.py`) and enter your name as the owner.
2. Add two pets: **Buddy** (Dog) and **Luna** (Cat).
3. For Buddy, add:
   - "Morning Walk" — 30 min, HIGH priority, preferred start 08:00
   - "Vet Check" — 20 min, HIGH priority, preferred start 08:15 *(intentional overlap)*
   - "Feeding" — 10 min, HIGH priority, daily recurrence
   - "Bath Time" — 25 min, MEDIUM priority
4. For Luna, add:
   - "Grooming" — 20 min, MEDIUM priority, preferred start 08:10
   - "Playtime" — 15 min, LOW priority, weekly recurrence
5. Set Buddy's time budget to **90 min** and Luna's to **30 min**, then click **Generate Schedule**.
6. The app displays Buddy's plan sorted by start time, flags the 08:00–08:15 overlap as a conflict warning, and shows Luna's plan with Playtime omitted (budget exhausted after Grooming).
7. Completing "Feeding" from the task list automatically schedules the next feeding for tomorrow.

### Key scheduler behaviors

- **Sorting by time**: Tasks with a `preferred_start` appear first in chronological order; tasks without one follow in priority order.
- **Conflict warnings**: The same-pet checker catches overlapping `preferred_start` windows (e.g., Morning Walk 08:00–08:30 vs. Vet Check 08:15–08:35) and surfaces them as human-readable warnings before the schedule is committed.
- **Greedy budget enforcement**: Tasks are evaluated highest-priority-first; any task that would exceed the remaining time budget is skipped and counted in the summary.
- **Daily recurrence**: Marking "Feeding" complete creates a new "Feeding" task due the next day, keeping the daily routine intact without manual re-entry.

### Sample CLI output

```
==============================================
  TODAY'S SCHEDULE  —  Arthur
==============================================

  Raw task order for Buddy (as added):
    [no pref]  Bath Time
    [no pref]  Feeding
    [08:00]  Morning Walk
    [08:15]  Vet Check

  Same-pet conflict warnings:
    Conflict: Morning Walk (08:00, 30 min) overlaps Vet Check (08:15, 20 min)

  After sort_by_time():
    [08:00]  Morning Walk
    [08:15]  Vet Check
    [no pref]  Feeding
    [no pref]  Bath Time

  Incomplete tasks for Buddy (completed=False):
    - Bath Time
    - Feeding
    - Morning Walk
    - Vet Check

  Recurring task rescheduled: 'Feeding' due 2026-07-02

  Incomplete tasks after completing Feeding:
    - Bath Time
    - Morning Walk
    - Vet Check
    - Feeding  (due 2026-07-02)

==============================================
  FULL DAILY PLAN
==============================================

  Buddy  (Dog)
  -----------------------------------------------
  08:00   Morning Walk            30 min  [HIGH]
  08:15   Vet Check               20 min  [HIGH]
  no pref Feeding                 10 min  [HIGH]
  no pref Bath Time               25 min  [MEDIUM]
  -----------------------------------------------
  Time used: 85 / 90 min  |  0 task(s) skipped
  Schedule generated at: 08:00

  Luna  (Cat)
  -----------------------------------------------
  08:10   Grooming                20 min  [MEDIUM]
  -----------------------------------------------
  Time used: 20 / 30 min  |  1 task(s) skipped

  Checking for scheduling conflicts...
  ! Conflict: Buddy/Morning Walk overlaps Buddy/Vet Check (08:15--08:30)

  Recurring tasks across all pets:
    Buddy: Feeding (daily)
    Luna: Playtime (weekly)

==============================================
```
