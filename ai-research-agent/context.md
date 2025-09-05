# Portia Agentic Framework: Context Overview

Portia is a Python framework for formalized planning and execution of agentic LLM workflows. It is designed to support robust, inspectable, and interactive agentic systems, with a focus on explicit plans, stepwise execution, and user clarifications.

## Core Concepts

### 1. **Plan**

- **Definition:**  
  A `Plan` is a formal, structured representation of how to solve a user query. It consists of a sequence of `Step` objects, each representing a discrete action (often a tool call) to be performed by an agent.
- **Key Fields:**
  - `id`: Unique identifier for the plan.
  - `plan_context`: Metadata about the plan, including the original query and available tools.
  - `steps`: Ordered list of `Step` objects, each with its own inputs, outputs, and associated tool.
  - `plan_inputs`: List of `PlanInput` objects, representing required external inputs (e.g., API keys, user parameters).
  - `structured_output_schema`: (Optional) Pydantic schema for the expected output.
- **Purpose:**  
  Encapsulates the entire workflow for a query, making it inspectable, reusable, and modifiable. Plans can be generated dynamically (via LLMs) or constructed programmatically.

### 2. **PlanRun**

- **Definition:**  
  A `PlanRun` is a concrete execution instance of a `Plan`. It tracks the current state, progress, and all intermediate/final outputs for a specific run.
- **Key Fields:**
  - `id`: Unique identifier for the run.
  - `plan_id`: Reference to the associated `Plan`.
  - `current_step_index`: Index of the step currently being executed.
  - `state`: Enum (`PlanRunState`) indicating status (e.g., NOT_STARTED, IN_PROGRESS, NEED_CLARIFICATION, COMPLETE, FAILED).
  - `outputs`: `PlanRunOutputs` object, storing step outputs, clarifications, and the final output.
  - `plan_run_inputs`: Mapping of input names to values for this run.
  - `end_user_id`: Identifier for the user this run is for.
- **Purpose:**  
  Provides a full, auditable record of a plan's execution, including all user interactions and clarifications. Enables pausing, resuming, and inspecting runs at any point.

### 3. **Clarification**

- **Definition:**  
  A `Clarification` is a formal request for additional information or action from the user, raised when the agent cannot proceed (e.g., missing argument, authentication required, ambiguous choice).
- **Types:**
  - `InputClarification`: Requests a value for a missing argument.
  - `ActionClarification`: Requests the user to perform an action (e.g., OAuth login), possibly requiring confirmation.
  - `MultipleChoiceClarification`: Asks the user to select from options.
  - `ValueConfirmationClarification`: Asks the user to confirm a value.
  - `UserVerificationClarification`: Requests explicit user approval before proceeding (e.g., for sensitive tool calls).
  - `CustomClarification`: Extensible for arbitrary user-defined needs.
- **Key Fields:**
  - `id`: Unique identifier.
  - `plan_run_id`: The run this clarification is for.
  - `category`: The type of clarification.
  - `user_guidance`: Message to display to the user.
  - `resolved`: Whether the clarification has been addressed.
  - `response`: The user's response (if any).
  - `step`: The step index this clarification is associated with.
  - `source`: Where the clarification originated (e.g., tool, agent).
- **Purpose:**  
  Enables interactive, robust execution by pausing the run and requesting user input whenever the agent cannot proceed autonomously.

---

## The Agentic Workflow

### 1. **Planning**

- The user issues a query.
- The `Portia` client (main entrypoint) uses a `PlanningAgent` (often LLM-backed) to generate a `Plan`:
  - The plan specifies the sequence of steps, required inputs, and tools to use.
  - Example plans and tool registries can be provided to guide planning.

### 2. **PlanRun Creation**

- A `PlanRun` is instantiated for the plan, with any required `plan_run_inputs` (e.g., user parameters, API keys).
- The run is persisted to storage (memory, disk, or cloud).

### 3. **Stepwise Execution**

- The run proceeds step by step:
  - For each step, the appropriate `ExecutionAgent` is invoked (e.g., `DefaultExecutionAgent`, `OneShotAgent`).
  - The agent prepares the tool call, gathers inputs (from previous outputs or plan inputs), and executes the tool.
  - Outputs are stored in the run's state.

### 4. **Clarification Handling**

- If a step cannot proceed (e.g., missing input, tool not ready, ambiguous choice), a `Clarification` is raised.
- The run transitions to `NEED_CLARIFICATION` state.
- A `ClarificationHandler` (e.g., CLI, web, custom) is invoked to present the clarification to the user and collect a response.
- Once resolved, the run resumes from the point of interruption.

### 5. **Hooks and Extensibility**

- The `ExecutionHooks` system allows custom logic at key points:
  - Before/after plan run, before/after each step, before/after tool calls, and for clarification handling.
  - Hooks can raise clarifications, modify arguments, log, or enforce policies (e.g., require user verification before sensitive actions).

### 6. **Completion and Output**

- The run continues until all steps are executed or a terminal state (COMPLETE/FAILED) is reached.
- The final output is available in the run's outputs.

---

## Additional Notes

- **Storage:**  
  Plans and runs are persisted via pluggable backends (memory, disk, cloud), enabling auditability and resumption.
- **Tool Registry:**  
  Tools are registered and described formally, enabling both LLMs and agents to reason about their capabilities and requirements.
- **ReadOnlyPlan/PlanRun:**  
  Read-only variants are passed to agents to prevent mutation and ensure reproducibility.
- **Execution Agents:**  
  Different agent types (default, one-shot, etc.) can be used for different execution strategies.
- **User Experience:**  
  Clarifications are surfaced to the user via handlers (CLI, web, etc.), and can be synchronous or asynchronous.

---

## Example Use Cases

- **Multi-step workflows:**  
  Fetch data, process it, and send a notification, with explicit steps and user clarifications for missing info.
- **Interactive tool use:**  
  Require user approval before sending emails or making purchases.
- **Robust automation:**  
  Pause and resume long-running or complex workflows, with full audit trails and user input where needed.

---

## References

- See the `portia/portia.py` file for the main orchestration logic.
- See `portia/plan.py` and `portia/plan_run.py` for the core data models.
- See `portia/clarification.py` for clarification types and handling.
- See `portia/execution_hooks.py` for extensibility points.
- See the latest PRs for recent changes to input handling, clarification, and execution hooks.

---

This context should provide a solid foundation for understanding and building on top of Portia's agentic planning and execution system. If you need more detail on any specific object or flow, let me know! 