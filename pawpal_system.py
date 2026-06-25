from dataclasses import dataclass, field
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


@dataclass
class Task:
    title: str
    duration: int
    priority: Priority
    completed: bool = False

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

    def get_tasks(self) -> list:
        """Return the list of tasks assigned to this pet."""
        return self.tasks


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
            for entry in self.slots:
                task = entry["task"]
                slot = entry["time_slot"]
                tag = priority_tag.get(task.priority, "      ")
                print(f"  {slot}   {task.title:<22} {task.duration:>3} min  {tag}")
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
        feasible_tasks = self.filter_feasible()
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
