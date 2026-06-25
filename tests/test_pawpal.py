from pawpal_system import Task, Pet, Priority


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
