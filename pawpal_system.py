from dataclasses import dataclass, field


@dataclass
class Owner:
    name: str
    pets: list = field(default_factory=list)

    def add_pet(self, pet) -> None:
        pass

    def get_pets(self) -> list:
        pass


@dataclass
class Task:
    title: str
    duration: int
    priority: str

    def priority_rank(self) -> int:
        pass

    def is_feasible(self, available_time: int) -> bool:
        pass


@dataclass
class Pet:
    name: str
    species: str
    tasks: list = field(default_factory=list)

    def add_task(self, task) -> None:
        pass

    def get_tasks(self) -> list:
        pass


@dataclass
class DailyPlan:
    scheduled_tasks: list
    time_slots: list
    explanation: str

    def display(self) -> None:
        pass

    def summary(self) -> str:
        pass


class Scheduler:
    def __init__(self, tasks: list, available_time: int):
        self.tasks: list = tasks
        self.available_time: int = available_time

    def sort_by_priority(self) -> list:
        pass

    def filter_feasible(self) -> list:
        pass

    def generate(self) -> DailyPlan:
        pass
