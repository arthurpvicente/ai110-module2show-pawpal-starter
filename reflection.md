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

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
