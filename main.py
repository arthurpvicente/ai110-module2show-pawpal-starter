from pawpal_system import Owner, Pet, Task, Priority, Scheduler, detect_conflicts

owner = Owner(name="Arthur")

buddy = Pet(name="Buddy", species="Dog")
luna  = Pet(name="Luna",  species="Cat")

# Tasks added deliberately OUT OF TIME ORDER to demonstrate sort_by_time()
buddy.add_task(Task("Bath Time",    25, Priority.MEDIUM))
buddy.add_task(Task("Feeding",      10, Priority.HIGH,  recurrence="daily"))
buddy.add_task(Task("Morning Walk", 30, Priority.HIGH,  preferred_start="08:00"))
# Vet Check starts at 08:15 — overlaps Morning Walk (08:00–08:30) to trigger same-pet conflict detection
buddy.add_task(Task("Vet Check",    20, Priority.HIGH,  preferred_start="08:15"))

luna.add_task(Task("Playtime",  15, Priority.LOW,    recurrence="weekly"))
luna.add_task(Task("Grooming",  20, Priority.MEDIUM, preferred_start="08:10"))

owner.add_pet(buddy)
owner.add_pet(luna)

width = 46
print("=" * width)
print(f"  TODAY'S SCHEDULE  —  {owner.name}")
print("=" * width)

# --- Sorting demo ---
print("\n  Raw task order for Buddy (as added):")
for t in buddy.get_tasks():
    start = t.preferred_start if t.preferred_start else "no pref"
    print(f"    [{start}]  {t.title}")

scheduler_buddy = Scheduler(pet=buddy, available_time=90)

# Same-pet conflict check (preferred_start overlaps)
same_pet_warnings = scheduler_buddy.check_conflicts()
if same_pet_warnings:
    print("\n  Same-pet conflict warnings:")
    for w in same_pet_warnings:
        print(f"    {w}")

print("\n  After sort_by_time():")
for t in scheduler_buddy.sort_by_time():
    start = t.preferred_start if t.preferred_start else "no pref"
    print(f"    [{start}]  {t.title}")

# --- Filtering demo ---
print("\n  Incomplete tasks for Buddy (completed=False):")
for t in buddy.get_tasks(completed=False):
    print(f"    - {t.title}")

# Use scheduler.mark_task_complete() so recurring logic fires
feeding_task = next(t for t in buddy.get_tasks() if t.title == "Feeding")
next_feeding = scheduler_buddy.mark_task_complete(feeding_task)
if next_feeding:
    print(f"\n  Recurring task rescheduled: '{next_feeding.title}' due {next_feeding.due_date}")

print("\n  Incomplete tasks after completing Feeding:")
for t in buddy.get_tasks(completed=False):
    due = f"  (due {t.due_date})" if t.due_date else ""
    print(f"    - {t.title}{due}")

# --- Full schedule ---
print("\n" + "=" * width)
print("  FULL DAILY PLAN")
print("=" * width)

budgets = {"Buddy": 90, "Luna": 30}
plans = []
for pet in owner.get_pets():
    scheduler = Scheduler(pet=pet, available_time=budgets[pet.name])
    plan = scheduler.generate()
    plans.append(plan)
    plan.display()
    print(f"  {plan.summary()}")

# Conflict detection
print("\n  Checking for scheduling conflicts...")
conflicts = detect_conflicts(plans)
if conflicts:
    for c in conflicts:
        print(
            f"  ! Conflict: {c['pet_a']}/{c['task_a']} overlaps "
            f"{c['pet_b']}/{c['task_b']} "
            f"({c['overlap_start']}--{c['overlap_end']})"
        )
else:
    print("  No conflicts detected.")

# Recurring tasks
print("\n  Recurring tasks across all pets:")
for pet in owner.get_pets():
    for t in pet.get_recurring_tasks():
        print(f"    {pet.name}: {t.title} ({t.recurrence})")

print("\n" + "=" * width)
