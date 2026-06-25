from pawpal_system import Owner, Pet, Task, Priority, Scheduler

owner = Owner(name="Arthur")

buddy = Pet(name="Buddy", species="Dog")
luna = Pet(name="Luna", species="Cat")

owner.add_pet(buddy)
owner.add_pet(luna)

buddy.add_task(Task(title="Morning Walk", duration=30, priority=Priority.HIGH))
buddy.add_task(Task(title="Feeding", duration=10, priority=Priority.HIGH))
buddy.add_task(Task(title="Bath Time", duration=25, priority=Priority.MEDIUM))

luna.add_task(Task(title="Grooming", duration=20, priority=Priority.MEDIUM))
luna.add_task(Task(title="Playtime", duration=15, priority=Priority.LOW))

width = 46
print("=" * width)
print(f"  TODAY'S SCHEDULE  —  {owner.name}")
print("=" * width)
for pet in owner.get_pets():
    scheduler = Scheduler(pet=pet, available_time=60)
    plan = scheduler.generate()
    plan.display()
print("\n" + "=" * width)
