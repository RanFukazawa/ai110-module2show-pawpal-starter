# PawPal+ Project Reflection

## 1. System Design

Core actions
1. Add and schedule a pet care task (feeding, walk, medication, etc.)
2. Set availability and preferences (work schedule, time constraints)
3. View today's generated care plan

Brainstorming
- Owner
  - Attributes: `name`, `work_schedule`, `available_hours`, `preferred_morning_start`, `preferred_evening_end`
  - Methods: `get_name()`, `set_availability()`, `get_availability()`

- Pet
  - Attributes: `name`, `species`, `gender`, `age`, `health_history`, `medical_needs`, `owner`, `tasks`
  - Methods: `get_name()`, `get_species()`, `get_age()`, `get_medical_needs()`, `add_task()`, `get_tasks()`

- Task
  - Attributes: `name`, `duration`, `priority`, `type`, `scheduled_time`, `is_completed`
  - Methods: `get_name()`, `get_duration()`, `get_priority()`, `get_type()`, `set_priority()`, `mark_complete()`

- Schedule
  - Attributes: `owner`, `pets`, `tasks`, `generated_plan`, `reasoning`
  - Methods: `generate_plan()`, `explain_reasoning()`, `display_plan()`

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
  
  My initial design included three classes: `Owner`, `Pet`, and `Task`. The `Owner` class was responsible for storing personal contact information such as name, phone number, and home address, with simple getter methods to retrieve each attribute. The `Pet` class held descriptive information about each pet including name, species, gender, age, health history, and medical needs, also with getter methods. The `Task` class represented a single care task with attributes for name, duration, priority, and type, again with basic getters.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
  
  Yes, the design changed in a few ways during the planning process.
  
  The most significant change was to the `Owner` class. The original design focused on contact details, but these turned out to be irrelevant to the core purpose of the app. Since PawPal+ is a scheduling tool, `Owner` needed to hold availability and preference data instead — attributes like `work_schedule`, `available_hours`, `preferred_morning_start`, and `preferred_evening_end`. This change was necessary because the `Schedule` class reads from `Owner` to generate the daily plan, so without this information the scheduling logic would have nothing to work with.
  
  The second change was adding a fourth class, `Schedule`, which was not in the original design. As the responsibilities of the app became clearer — particularly the requirement to generate a daily plan and explain its reasoning — it became apparent that this logic was substantial enough to deserve its own class rather than being placed inside `Owner` or `Pet`.
  
  Smaller additions were also made to `Pet` and `Task`: `Pet` gained an owner attribute and a tasks list to reflect real-world relationships between objects, and `Task` gained `scheduled_time` and `is_completed` to support time placement and progress tracking.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler currently considers three constraints: the owner's total available hours, task priority, and each task's scheduled time. Available hours sets the budget — tasks are fitted into the day until the time runs out. Priority determines the order tasks are considered, ensuring high-priority tasks like medication and feeding are scheduled before lower-priority ones like grooming or enrichment. Scheduled time is used after the plan is built to sort tasks chronologically, so the final output reflects the actual flow of the day.

The decision to weight priority most heavily was driven by pet health — a dog's medication matters more than a grooming session regardless of how much time is available, so priority felt like the most important constraint to enforce first.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff the scheduler makes is that it stores owner preferences — specifically `preferred_morning_start` and `preferred_evening_end` — but does not use them when generating the plan. The scheduler only checks whether a task fits within the owner's total available hours, not whether it falls within their preferred time window. This means a task scheduled at 06:00 would not be flagged even if the owner's morning start is 07:00.

This tradeoff is reasonable for a first version because enforcing a time window would require significantly more logic in `generate_plan()` — each task's `scheduled_time` would need to be validated against the owner's window, and tasks outside it would need to be either rejected or rescheduled. Collecting and storing the preferences now means that logic can be added later without changing the data model or the UI.

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
