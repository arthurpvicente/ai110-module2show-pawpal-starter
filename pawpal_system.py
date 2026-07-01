from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from typing import Optional


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Owner:
    name: str
    pets: list = field(default_factory=list)

    def add_pet(self, pet) -> None:
        """Add a pet to this owner and set the pet's owner back-reference."""
        self.pets.append(pet)
        pet.owner = self

    def get_pets(self) -> list:
        """Return the list of pets belonging to this owner."""
        return self.pets

    def get_tasks(self, pet_name: str = None, completed: bool = None) -> list:
        """Return tasks across all pets, optionally filtered by pet name and/or completion status."""
        results = []
        for pet in self.pets:
            if pet_name and pet.name != pet_name:
                continue
            for task in pet.tasks:
                if completed is not None and task.completed != completed:
                    continue
                results.append({"pet": pet.name, "task": task})
        return results


@dataclass
class Task:
    title: str
    duration: int
    priority: Priority
    completed: bool = False
    preferred_start: Optional[str] = None  # "HH:MM" wall-clock anchor
    recurrence: Optional[str] = None       # "daily", "weekly", or None
    due_date: Optional[date] = None        # set automatically for recurring next occurrences

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def priority_rank(self) -> int:
        """Return a numeric rank for the task's priority (HIGH=3, MEDIUM=2, LOW=1)."""
        ranks = {Priority.HIGH: 3, Priority.MEDIUM: 2, Priority.LOW: 1}
        return ranks[self.priority]

    def is_feasible(self, available_time: int) -> bool:
        """Return True if this task's duration fits within the given available time."""
        return self.duration <= available_time


@dataclass
class Pet:
    name: str
    species: str
    tasks: list = field(default_factory=list)
    # repr=False prevents infinite loop when Owner also references this Pet
    owner: Optional["Owner"] = field(default=None, repr=False)

    def add_task(self, task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def get_tasks(self, completed: bool = None) -> list:
        """Return tasks, optionally filtered by completion status."""
        if completed is None:
            return self.tasks
        return [t for t in self.tasks if t.completed == completed]

    def get_recurring_tasks(self) -> list:
        """Return tasks that have a recurrence set."""
        return [t for t in self.tasks if t.recurrence is not None]


@dataclass
class DailyPlan:
    # Each entry: {"task": Task, "time_slot": str} — keeps task and slot paired
    slots: list
    explanation: str
    pet: Optional["Pet"] = None
    available_time: int = 0

    def display(self) -> None:
        """Print the formatted daily schedule with a time bar to the terminal."""
        pet_name = self.pet.name if self.pet else "Unknown Pet"
        species = f"({self.pet.species})" if self.pet else ""
        width = 44
        print(f"\n  {pet_name}  {species}")
        print("  " + "-" * width)
        if not self.slots:
            print("  No tasks scheduled.")
        else:
            priority_tag = {Priority.HIGH: "[HIGH]", Priority.MEDIUM: "[MED] ", Priority.LOW: "[LOW] "}
            recurrence_tag = {"daily": "[DAILY]", "weekly": "[WEEKLY]"}
            for entry in self.slots:
                task = entry["task"]
                slot = entry["time_slot"]
                tag = priority_tag.get(task.priority, "      ")
                rec = "  " + recurrence_tag[task.recurrence] if task.recurrence else ""
                due = f"  due {task.due_date}" if task.due_date else ""
                print(f"  {slot}   {task.title:<22} {task.duration:>3} min  {tag}{rec}{due}")
        print("  " + "-" * width)
        total_used = sum(entry["task"].duration for entry in self.slots)
        if self.available_time > 0:
            filled = round((total_used / self.available_time) * 20)
            bar = "#" * filled + "." * (20 - filled)
            skipped_count = len(self.pet.get_tasks()) - len(self.slots) if self.pet else 0
            skipped_note = f"  {skipped_count} task(s) skipped (not enough time)" if skipped_count else ""
            print(f"  Time: [{bar}]  {total_used} / {self.available_time} min{skipped_note}")

    def summary(self) -> str:
        """Return a one-line string summarizing the plan's task count, total time, and explanation."""
        pet_name = self.pet.name if self.pet else "Unknown Pet"
        total_time = sum(entry["task"].duration for entry in self.slots)
        task_count = len(self.slots)
        return (
            f"Plan for {pet_name}: {task_count} task(s) totaling {total_time} min. "
            f"{self.explanation}"
        )


class Scheduler:
    def __init__(self, pet: "Pet", available_time: int):
        self.pet: Pet = pet
        self.available_time: int = available_time

    def sort_by_priority(self) -> list:
        """Return the pet's tasks sorted from highest to lowest priority."""
        return sorted(self.pet.get_tasks(), key=lambda t: t.priority_rank(), reverse=True)

    def sort_by_time(self) -> list:
        """Return feasible tasks ordered for time-slot assignment.

        Tasks with a preferred_start are placed first, sorted earliest to latest.
        Tasks without a preferred_start follow, sorted by priority (highest first).
        Calls filter_feasible() internally so only schedulable tasks are returned.
        """
        tasks = self.filter_feasible()
        return sorted(tasks, key=lambda t: (
            (0, int(t.preferred_start.split(":")[0]) * 60 + int(t.preferred_start.split(":")[1]))
            if t.preferred_start else (1, -t.priority_rank())
        ))

    def check_conflicts(self) -> list:
        """Detect same-pet scheduling conflicts before a plan is generated.

        Compares every pair of non-completed tasks that have a preferred_start set.
        A conflict exists when the time window of one task (start + duration) overlaps
        the time window of another. Returns a list of human-readable warning strings —
        one per conflicting pair — so the caller can print warnings without crashing.
        Returns an empty list if no conflicts are found.
        """
        anchored = [t for t in self.pet.get_tasks() if t.preferred_start and not t.completed]
        warnings = []
        for i in range(len(anchored)):
            for j in range(i + 1, len(anchored)):
                a, b = anchored[i], anchored[j]
                a_h, a_m = map(int, a.preferred_start.split(":"))
                b_h, b_m = map(int, b.preferred_start.split(":"))
                a_start = a_h * 60 + a_m
                b_start = b_h * 60 + b_m
                a_end   = a_start + a.duration
                b_end   = b_start + b.duration
                overlap_start = max(a_start, b_start)
                overlap_end   = min(a_end,   b_end)
                if overlap_start < overlap_end:
                    fmt = lambda m: f"{m // 60:02d}:{m % 60:02d}"
                    warnings.append(
                        f"WARNING: '{a.title}' ({a.preferred_start}, {a.duration} min) overlaps "
                        f"'{b.title}' ({b.preferred_start}, {b.duration} min) "
                        f"for {self.pet.name} from {fmt(overlap_start)} to {fmt(overlap_end)}"
                    )
        return warnings

    def filter_feasible(self) -> list:
        """Return tasks that fit within available_time, selected greedily by priority."""
        # Track cumulative duration across selected tasks, not each task in isolation
        selected = []
        time_used = 0
        for task in self.sort_by_priority():
            if time_used + task.duration <= self.available_time:
                selected.append(task)
                time_used += task.duration
        return selected

    def generate(self) -> DailyPlan:
        """Build and return a DailyPlan with time slots assigned to all feasible tasks."""
        feasible_tasks = self.sort_by_time()

        slots = []
        current_hour = 8
        current_minute = 0
        for task in feasible_tasks:
            time_slot = f"{current_hour:02d}:{current_minute:02d}"
            slots.append({"task": task, "time_slot": time_slot})
            current_minute += task.duration
            current_hour += current_minute // 60
            current_minute = current_minute % 60

        total = sum(t.duration for t in feasible_tasks)
        skipped = len(self.pet.get_tasks()) - len(feasible_tasks)
        explanation = (
            f"Scheduled {len(feasible_tasks)} task(s) using {total} of {self.available_time} available minutes."
        )
        if skipped > 0:
            explanation += f" {skipped} task(s) skipped due to time constraints."

        return DailyPlan(slots=slots, explanation=explanation, pet=self.pet, available_time=self.available_time)

    def mark_task_complete(self, task: "Task") -> Optional["Task"]:
        """Mark a task complete and automatically reschedule it if it recurs.

        Always calls task.mark_complete() to flip the completed flag.
        If task.recurrence is 'daily', creates a copy due tomorrow (today + 1 day).
        If task.recurrence is 'weekly', creates a copy due in 7 days.
        The new copy is added to the pet's task list and returned so the caller can
        display or log it. Returns None for non-recurring tasks.
        Uses datetime.timedelta for date arithmetic — handles month/year rollovers
        automatically without manual day counting.
        """
        task.mark_complete()
        if task.recurrence == "daily":
            delta = timedelta(days=1)
        elif task.recurrence == "weekly":
            delta = timedelta(weeks=1)
        else:
            return None
        next_task = Task(
            title=task.title,
            duration=task.duration,
            priority=task.priority,
            preferred_start=task.preferred_start,
            recurrence=task.recurrence,
            due_date=date.today() + delta,
        )
        self.pet.add_task(next_task)
        return next_task


def detect_conflicts(plans: list) -> list:
    """Detect cross-pet scheduling conflicts across a set of generated daily plans.

    Takes a list of DailyPlan objects (one per pet) and compares the assigned
    time_slot windows of every task pair from *different* pets. A conflict exists
    when two tasks from different pets overlap in wall-clock time, meaning the owner
    would need to be in two places at once.

    Returns a list of dicts, one per conflicting pair, each containing:
        pet_a, task_a  — name of the first pet and its task title
        pet_b, task_b  — name of the second pet and its task title
        overlap_start  — "HH:MM" when the overlap begins
        overlap_end    — "HH:MM" when the overlap ends

    Returns an empty list if no conflicts are found. Does not raise exceptions.
    """
    def _to_minutes(time_slot: str) -> int:
        h, m = time_slot.split(":")
        return int(h) * 60 + int(m)

    # Build flat list of (pet_name, task, start_min, end_min)
    windows = []
    for plan in plans:
        pet_name = plan.pet.name if plan.pet else "Unknown"
        for entry in plan.slots:
            start = _to_minutes(entry["time_slot"])
            end = start + entry["task"].duration
            windows.append((pet_name, entry["task"], start, end))

    conflicts = []
    for i in range(len(windows)):
        for j in range(i + 1, len(windows)):
            pet_a, task_a, start_a, end_a = windows[i]
            pet_b, task_b, start_b, end_b = windows[j]
            if pet_a == pet_b:
                continue
            overlap_start = max(start_a, start_b)
            overlap_end = min(end_a, end_b)
            if overlap_start < overlap_end:
                conflicts.append({
                    "pet_a": pet_a, "task_a": task_a.title,
                    "pet_b": pet_b, "task_b": task_b.title,
                    "overlap_start": f"{overlap_start // 60:02d}:{overlap_start % 60:02d}",
                    "overlap_end":   f"{overlap_end   // 60:02d}:{overlap_end   % 60:02d}",
                })
    return conflicts
