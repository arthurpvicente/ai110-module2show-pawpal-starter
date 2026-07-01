# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
The system is built around three core actions a user performs:

1. **Enter owner and pet info** — the user provides their name, their pet's name, and the pet's species. This grounds every plan in a specific owner–pet pair and maps to `Owner` and `Pet` classes that hold basic identity and preference data.

2. **Add and manage tasks** — the user creates care tasks by specifying a title, a duration in minutes, and a priority level (low, medium, or high). Tasks are the raw input to the scheduler and map to a `Task` class that holds at minimum those three attributes.

3. **Generate a daily schedule** — the user triggers the scheduler, which orders tasks by priority and available time and returns a time-slotted plan with reasoning. This maps to a `DailyPlan` class whose main responsibility is choosing, ordering, and annotating tasks for the day.

**b. Design changes**

After an AI-assisted review of the skeleton, four changes were made:

1. **`Priority` enum instead of a plain string** — `Task.priority` was originally a free-form `str`. Any typo or casing difference (`"High"` vs `"high"`) would silently produce wrong rankings. Replacing it with a `Priority(Enum)` with `LOW`, `MEDIUM`, and `HIGH` members means invalid values are caught at construction time, not buried in `priority_rank()` logic.

2. **`Pet.owner` back-reference** — the original design only linked `Owner → Pet`, with no way to navigate the other direction. Adding an optional `owner` field to `Pet` (with `repr=False` to prevent infinite loops) completes the relationship so a `Pet` always knows who it belongs to.

3. **`Scheduler` takes a `Pet` instead of a raw task list** — the original `Scheduler(tasks, available_time)` relied on the caller to pass the correct task list for the right pet, with no enforced connection. Changing it to `Scheduler(pet, available_time)` makes the source of tasks explicit and ties the scheduler to a specific pet.

4. **`DailyPlan` merged two parallel lists into one** — `scheduled_tasks` and `time_slots` were separate lists that had to stay the same length and order. If either was modified independently, behavior would be undefined. Replacing them with a single `slots` list — where each entry is a `{"task": Task, "time_slot": str}` dict — keeps every task paired with its slot by construction.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler balances four constraints: **priority level** (HIGH/MEDIUM/LOW enum), **available_time** budget (total minutes in the day), **preferred_start** anchor times (HH:MM wall-clock), and **task duration** (minutes). Priority was chosen as the primary ordering constraint because pet care has clear urgency tiers — feeding and medication outrank grooming regardless of the day's schedule. Available time acts as a hard budget cap enforced during `filter_feasible()`, preventing the plan from overcommitting the owner. Preferred start times operate as soft anchors: `sort_by_time()` schedules anchored tasks first (in wall-clock order), then fills remaining time with unanchored tasks sorted by priority. Duration is the unit of consumption against the budget, so it naturally determines feasibility without needing a separate constraint layer.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
**High-priority tasks always go first:**
The scheduler always picks the most important tasks first. If those fill up the day, lower-priority tasks get skipped entirely — even if a different combination would fit more tasks into the same time window. This is a reasonable choice for pet care because feeding and walking a dog are more important than a bath, and the goal is to always get the critical tasks done, not to maximize the number of tasks completed.

**Preferred start times are a suggestion, not a guarantee:**
If you tell the scheduler "start Grooming at 08:10," it will try to place it there, but if an earlier task runs over, Grooming just slides later to fill the gap. The scheduler never leaves empty time waiting for a preferred start. This makes the schedule compact and simple to generate, but it means preferred times are treated as hints rather than hard appointments.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

AI was most useful in three phases: **design critique**, **edge-case discovery**, and **implementation scaffolding**. During design, I described the initial UML and asked "What invariants could break with this design?" — that prompt surfaced the `Priority` enum refactor (free-form strings would silently mis-rank tasks), the `Pet.owner` back-reference (navigation only worked one direction), and collapsing the parallel `scheduled_tasks`/`time_slots` lists into a single `slots` list (two lists with implicit ordering are a maintenance hazard). During implementation, asking "What edge cases should conflict detection handle?" pushed the design toward the two-layer architecture: `check_conflicts()` catches same-pet overlaps before generation, and `detect_conflicts()` catches cross-pet overlaps after. Open-ended diagnostic questions ("What could go wrong here?") consistently produced more useful output than narrow implementation requests ("Write the sort function").

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

When building `DailyPlan`, the AI suggested introducing a dedicated `TimeSlot` dataclass to wrap each scheduled entry — giving it fields like `start`, `end`, and `task` instead of using a plain `{"task": ..., "time_slot": ...}` dict. I evaluated the suggestion by asking a single question: does this class have any methods, or is it pure data storage? The answer was "none" — the class would only hold two fields with no behavior. Adding a class purely for structure would have meant importing and constructing it everywhere without gaining any invariants or logic. I kept the dict, which kept the code flat and consistent with the rest of the dataclass-based model. The check I now apply to any AI structural suggestion: if a proposed class has no methods, it is almost always better as a dict or named tuple.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

The test suite covers five behavioral areas: **priority ordering** (HIGH tasks sort before MEDIUM and LOW), **greedy feasibility filtering** (tasks that exceed the remaining time budget are skipped), **same-pet conflict detection** via `check_conflicts()` (overlapping preferred_start windows on the same pet trigger a warning), **preferred_start anchor scheduling** (anchored tasks are placed first in wall-clock order, not by priority), and **recurring task rescheduling** (calling `mark_task_complete()` on a daily task advances its due_date by one day; weekly by seven). These areas matter because the scheduler's output depends entirely on ordering and time arithmetic — unit tests on data model fields would not catch a bug in `filter_feasible()` that silently drops a HIGH-priority task when the budget is tight.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am confident the scheduler handles all tested happy-path scenarios correctly. My confidence drops on boundary conditions that the current test suite does not cover. The edge cases I would add next: (1) `available_time = 0` — the scheduler should return an empty plan without crashing; (2) a task whose duration exactly equals the remaining budget — the boundary math in `filter_feasible()` needs to include, not exclude, that task; (3) two tasks with identical `preferred_start` times on the same pet — `sort_by_time()` has an undefined ordering for ties; (4) an owner with two pets whose schedules overlap but the owner is available to handle both — `detect_conflicts()` should not flag parallel tasks that require no owner travel. These cases matter most because they sit at the edges of the greedy algorithm's assumptions.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The two-layer conflict detection architecture is the part I am most satisfied with. Splitting it into `check_conflicts()` (same-pet, pre-generation warnings) and `detect_conflicts()` (cross-pet, post-generation validation) keeps each function's scope narrow and testable independently. The separation also reflects a real domain distinction: same-pet conflicts are scheduling input errors that should stop generation early, while cross-pet conflicts are emergent from the full schedule and can only be detected after all plans are built. That the architecture maps cleanly onto the domain logic — not just onto code organization — is what makes it feel right.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would replace `filter_feasible()`'s greedy priority algorithm with a bounded knapsack optimizer. The current algorithm fills the schedule top-priority-first, which means a single long HIGH-priority task can block three shorter MEDIUM tasks that would collectively deliver more care. A knapsack approach maximizes total scheduled duration while preserving a priority weight, so the schedule fits more tasks without abandoning the importance ordering. The tradeoff is implementation complexity and slightly less predictable output, but for a real pet care planner the difference between "fed and walked" and "fed, walked, groomed, and medicated" matters significantly to the owner.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The most important thing I learned is that AI is most valuable as a **design critic, not a design author**. Left unchecked, AI suggestions optimize for completeness and generality — adding classes, layers, and abstractions that would be appropriate in a large system but add friction in a focused one. My job as lead architect was to filter those suggestions through domain knowledge: does pet care scheduling actually need a `TimeSlot` class? No. Does it need two-layer conflict detection? Yes, because the domain has two genuinely distinct conflict types. Using separate sessions for design, implementation, and testing enforced that filter naturally — each session started from a clean context that I controlled, so AI could not carry forward assumptions from a previous phase that I had already rejected. The discipline of owning the architecture and treating AI output as a proposal to evaluate — not a solution to accept — is what kept the system coherent.
