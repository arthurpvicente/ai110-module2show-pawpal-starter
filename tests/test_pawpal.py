from pawpal_system import Task, Pet, Priority, Scheduler, Owner


def test_mark_complete_changes_status():
    task = Task(title="Walk", duration=20, priority=Priority.HIGH)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_count():
    pet = Pet(name="Buddy", species="Dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task(title="Feeding", duration=10, priority=Priority.MEDIUM))
    assert len(pet.get_tasks()) == 1


# --- Scheduler.sort_by_priority ---

def test_sort_by_priority_happy_path():
    pet = Pet(name="Max", species="Dog")
    low = Task(title="Play", duration=10, priority=Priority.LOW)
    high = Task(title="Walk", duration=20, priority=Priority.HIGH)
    med = Task(title="Feed", duration=15, priority=Priority.MEDIUM)
    pet.add_task(low)
    pet.add_task(high)
    pet.add_task(med)
    scheduler = Scheduler(pet, available_time=60)
    sorted_tasks = scheduler.sort_by_priority()
    assert sorted_tasks[0].priority == Priority.HIGH
    assert sorted_tasks[1].priority == Priority.MEDIUM
    assert sorted_tasks[2].priority == Priority.LOW


# --- Scheduler.filter_feasible ---

def test_filter_feasible_respects_time_budget():
    pet = Pet(name="Luna", species="Cat")
    pet.add_task(Task(title="High", duration=30, priority=Priority.HIGH))
    pet.add_task(Task(title="Med", duration=30, priority=Priority.MEDIUM))
    pet.add_task(Task(title="Low", duration=30, priority=Priority.LOW))
    scheduler = Scheduler(pet, available_time=40)
    feasible = scheduler.filter_feasible()
    total = sum(t.duration for t in feasible)
    assert total <= 40

def test_filter_feasible_zero_time_returns_empty():
    pet = Pet(name="Luna", species="Cat")
    pet.add_task(Task(title="Walk", duration=10, priority=Priority.HIGH))
    scheduler = Scheduler(pet, available_time=0)
    assert scheduler.filter_feasible() == []


# --- Scheduler.check_conflicts ---

def test_check_conflicts_detects_same_start_time():
    pet = Pet(name="Bella", species="Dog")
    pet.add_task(Task(title="Walk", duration=20, priority=Priority.HIGH, preferred_start="08:00"))
    pet.add_task(Task(title="Feed", duration=15, priority=Priority.MEDIUM, preferred_start="08:00"))
    scheduler = Scheduler(pet, available_time=60)
    conflicts = scheduler.check_conflicts()
    assert len(conflicts) > 0

def test_check_conflicts_no_conflict_with_one_task():
    pet = Pet(name="Bella", species="Dog")
    pet.add_task(Task(title="Walk", duration=20, priority=Priority.HIGH, preferred_start="08:00"))
    scheduler = Scheduler(pet, available_time=60)
    assert scheduler.check_conflicts() == []


# --- Scheduler.mark_task_complete recurring ---

def test_mark_task_complete_recurring_creates_new_task():
    pet = Pet(name="Rex", species="Dog")
    task = Task(title="Daily Walk", duration=30, priority=Priority.HIGH, recurrence="daily")
    pet.add_task(task)
    scheduler = Scheduler(pet, available_time=60)
    new_task = scheduler.mark_task_complete(task)
    assert task.completed is True
    assert new_task is not None
    assert new_task.completed is False

def test_mark_task_complete_non_recurring_returns_none():
    pet = Pet(name="Rex", species="Dog")
    task = Task(title="One-time Bath", duration=20, priority=Priority.MEDIUM)
    pet.add_task(task)
    scheduler = Scheduler(pet, available_time=60)
    result = scheduler.mark_task_complete(task)
    assert task.completed is True
    assert result is None


# --- Owner.get_tasks filtering ---

def test_owner_get_tasks_aggregates_across_pets():
    owner = Owner(name="Alice")
    pet1 = Pet(name="Buddy", species="Dog")
    pet2 = Pet(name="Whiskers", species="Cat")
    pet1.add_task(Task(title="Walk", duration=20, priority=Priority.HIGH))
    pet2.add_task(Task(title="Feed", duration=10, priority=Priority.LOW))
    owner.add_pet(pet1)
    owner.add_pet(pet2)
    assert len(owner.get_tasks()) == 2

def test_owner_get_tasks_filters_completed():
    owner = Owner(name="Alice")
    pet = Pet(name="Buddy", species="Dog")
    done = Task(title="Walk", duration=20, priority=Priority.HIGH)
    done.mark_complete()
    pending = Task(title="Feed", duration=10, priority=Priority.LOW)
    pet.add_task(done)
    pet.add_task(pending)
    owner.add_pet(pet)
    assert len(owner.get_tasks(completed=False)) == 1
    assert owner.get_tasks(completed=False)[0]["task"].title == "Feed"

def test_owner_get_tasks_no_pets_returns_empty():
    owner = Owner(name="Alice")
    assert owner.get_tasks() == []
