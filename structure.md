Based on the detailed Software Requirements Specification (SRS) for CodeGenie and the capabilities of the Google Agent Development Kit (ADK), here is a comprehensive architectural plan to build a robust, scalable, and highly optimized system.

### 1. High-Level Architecture Diagram

The architecture is designed as a hierarchical multi-agent system, orchestrated by a central Coordinator. This design promotes modularity, specialization, and parallel execution.

**Textual Diagram:**

```
[User via Chat/Voice UI] <--> [CodeGenieCoordinator (LlmAgent)]
    |
    +-- Manages Main Workflow -> [ProjectLifecycle (SequentialAgent)]
    |   |
    |   +-- 1. [SRSCreationAgent (LoopAgent)] -> Writes to/reads from [SRS_Artifact.md/json]
    |   |      - Sub-agent: [SRSWriter (LlmAgent)]
    |   |
    |   +-- 2. [DirectoryStructureAgent (LlmAgent)] -> Uses [ExecutorAgent] as Tool -> Writes to [ProjectTree_Artifact.md]
    |   |
    |   +-- 3. [DividerAgent (LlmAgent)] -> Reads [SRS_Artifact.json] -> Creates dependency graph
    |   |
    |   +-- 4. [ParallelCodeGeneration (ParallelAgent)]
    |   |      |
    |   |      +-- [CodeGeneratorAgent_1 (LlmAgent)] -> Uses [VersionControlAgent] as Tool -> Writes to [Code_Artifacts]
    |   |      +-- [CodeGeneratorAgent_2 (LlmAgent)] -> Uses [VersionControlAgent] as Tool -> Writes to [Code_Artifacts]
    |   |      +-- ... (Dynamically scaled)
    |   |
    |   +-- 5. [TestingAgent (LlmAgent)] -> Uses [ExecutorAgent] as Tool -> Reads [Code_Artifacts] -> Writes [TestResults_Artifact.md]
    |   |
    |   +-- 6. [DocumentationAgent (LlmAgent)] -> Reads all Artifacts -> Writes [Documentation_Artifacts]
    |
    +-- Manages Cross-Cutting Agents (available as Tools to all other agents)
        |
        +-- [ExecutorAgent (BaseAgent)] -> Tool: execute_secure_command()
        +-- [VersionControlAgent (BaseAgent)] -> Tool: git_diff(), git_commit()
        +-- [UserInputsAgent (LlmAgent)] -> Tool: request_sensitive_input()
        +-- [ErrorHandlingAgent (LlmAgent)] -> Tool: analyze_error_log()
        +-- [UpdaterAgent (LlmAgent)] -> Tool: apply_code_update()
    |
    +-- Manages Asynchronous Feedback
        |
        +-- [Universal Event Queue] <-- All agents send events via Callbacks
        |
        +-- [VoiceAgent_1 (BaseAgent)] -> Reads from Queue -> Speech Synthesis
        +-- [VoiceAgent_2 (BaseAgent)] -> Reads from Queue -> Speech Synthesis
```

### 2. Agent Design & Responsibilities

Each agent is designed to leverage specific ADK primitives for optimal performance.

**`CodeGenieCoordinator`**

* **Type**: `LlmAgent`
* **Responsibilities**: The main entry point. It interprets the user's initial high-level request and delegates tasks to the `ProjectLifecycle` sequence or other specialized agents like the `UpdaterAgent`. It uses LLM-Driven Delegation (`transfer_to_agent`) to route complex user requests (e.g., "update the database schema" -> `UpdaterAgent`).
* **ADK Features**: `sub_agents`, `LLM-Driven Delegation`, `Tool` (uses `UpdaterAgent`, `UserInputsAgent` as tools).
* **Error Handling**: Catches escalations from sub-agents and communicates failures to the user.

**`ProjectLifecycle`**

* **Type**: `SequentialAgent`
* **Responsibilities**: Orchestrates the end-to-end software development flow in a predictable order.
* **ADK Features**: Manages the sequence of `SRSCreationAgent`, `DirectoryStructureAgent`, etc. It passes context via `Shared Session State`.

**`SRSCreationAgent`**

* **Type**: `LoopAgent`
* **Responsibilities**: Iteratively refines the SRS based on user feedback, as specified in SRS 3.1.1.
* **ADK Features**: `LoopAgent` is perfect for the "generate -> get feedback -> refine" cycle.
  * `sub_agents`: Contains an `LlmAgent` to write the SRS.
  * **State**: Uses `session.state['srs_content']` to hold the SRS between iterations.
  * **Artifacts**: Uses `context.save_artifact()` to save the final `srs.md` and `srs.json`.

**`DirectoryStructureAgent`**

* **Type**: `LlmAgent`
* **Responsibilities**: Designs the project directory structure and uses the `ExecutorAgent` to create it (SRS 3.1.2).
* **ADK Features**:
  * **Tool Use**: Invokes the `ExecutorAgent`'s `execute_secure_command` tool.
  * **Artifacts**: Saves the proposed structure to a markdown artifact for user approval.

**`ParallelCodeGeneration`**

* **Type**: `ParallelAgent`
* **Responsibilities**: Manages the concurrent execution of multiple `CodeGeneratorAgent` instances (SRS 1.2).
* **ADK Features**: Executes sub-agents in parallel, significantly reducing generation time for independent modules.

**`CodeGeneratorAgent`**

* **Type**: `LlmAgent`
* **Responsibilities**: Generates code for a specific module based on the SRS and dependency graph (SRS 3.1.3).
* **ADK Features**:
  * **Tool Use**: Calls the `VersionControlAgent` tool to commit generated code.
  * **Artifacts**: `context.save_artifact()` to write the generated code to files.
  * **Callbacks**: `after_tool_callback` is used to send the explanation of the generated code to the `Universal Event Queue` for the `VoiceAgent`.

**`ExecutorAgent`**

* **Type**: Custom `BaseAgent` (not an LLM).
* **Responsibilities**: Acts as the sole, secure gateway for executing OS commands (CRUD operations, running tests, etc.) as per SRS 3.1.4.
* **ADK Features**:
  * **Tool**: Exposed as a `FunctionTool` named `execute_secure_command`.
  * **Security**: The tool's implementation contains a strict whitelist of allowed commands (e.g., `mkdir`, `touch`, `python -m unittest`). It sanitizes all inputs to prevent command injection.
  * **Context**: Uses `ToolContext` to log every command execution for auditing.

**`VoiceAgent` (Pair)**

* **Type**: Custom `BaseAgent` (not an LLM).
* **Responsibilities**: Provides asynchronous voice feedback by reading messages from a shared queue (SRS 3.1.7).
* **ADK Features**:
  * This agent runs in a separate process.
  * It reads from a `PriorityQueue` populated by callbacks from all other agents. High-priority items (errors) are processed immediately.
  * It uses a speech synthesis library (`pyttsx3` or a cloud-based TTS) to generate audio. The two agents can alternate reading from the queue to create a more dynamic, podcast-like feel.

**`UpdaterAgent`**

* **Type**: `LlmAgent`
* **Responsibilities**: Identifies required changes and modifies code based on new requirements, presenting a diff for approval (SRS 3.1.5).
* **ADK Features**:
  * **Tool Use**: Leverages the `VersionControlAgent` to calculate diffs and the `ExecutorAgent` to apply changes.
  * **Artifacts**: Loads code from artifacts to analyze it.

### 3. ADK Feature Inventory & Integration Strategy

A survey of ADK features shows how deeply they can be integrated into `CodeGenie`:

* **`Toolsets`**: The `ExecutorAgent` and `VersionControlAgent` can be grouped into a `SystemTools` toolset. An `ApiInteraction` toolset could be created to manage tools for interacting with external APIs (e.g., Google Search). This organizes tools and allows for dynamic availability based on context.
* **`Memory`**: `search_memory` can be used by the `UpdaterAgent` to retrieve context from past development sessions or decisions when trying to understand a new change request. This enhances its ability to make context-aware modifications.
* **`Callbacks`**: This is the key to the voice feedback system. Every agent will be configured with an `after_agent_callback` and `after_tool_callback`. These callbacks will not modify the flow (`return None`) but will post messages (e.g., "Starting code generation for module X," "Execution failed: ...") to the `Universal Event Queue` with a priority level.
* **`State Prefixes (`user:`, `app:`)`**: User-specific API keys collected by the `UserInputsAgent` should be stored with the `user:` prefix (e.g., `user:github_api_key`) to be available across sessions for that user. Application-wide settings, like coding style rules, can use the `app:` prefix.
* **`Long Running Function Tools`**: If a build or testing process takes a long time, the `ExecutorAgent`'s `execute_secure_command` tool can be implemented as a long-running tool, allowing the system to continue processing other tasks or provide updates without blocking.

### 4. Dataflows & State Management

* **SRS and Project State**: The definitive SRS (JSON) and human-readable version (.md) will be stored as versioned **Artifacts**. This ensures that every agent has access to the canonical project requirements. Similarly, generated code, documentation, and test results are stored as artifacts.
* **Inter-Agent Communication**:
  * **`session.state`**: Used for passing small, ephemeral data between steps in the `SequentialAgent`. For example, the `DividerAgent` places the dependency graph into `session.state['dependency_graph']` for the `ParallelCodeGeneration` agent to read.
  * **Tool Calls**: Used for direct, synchronous command-like interactions (e.g., `DirectoryStructureAgent` calling `ExecutorAgent`).
* **Shared Knowledge Schema**:
  * `srs.json`: A well-defined JSON schema for the SRS is critical for machine readability by the `DividerAgent` and `CodeGeneratorAgents`.
  * `user_preferences.json`: A user-scoped artifact (`user:preferences.json`) can store preferences like coding language, style guides, or voice verbosity levels.

### 5. Security, Access Control & Compliance

* **ExecutorAgent as a Bastion Host**: The `ExecutorAgent` is the single point of failure and control. No other agent can execute OS commands directly. Its internal whitelist of commands is the primary defense mechanism, fulfilling SRS 3.2.1.
* **Sensitive Data Handling**: The `UserInputsAgent` will use `ToolContext.request_credential` to handle sensitive inputs like API keys. The ADK's authentication flow will manage the secure capture, and the keys will be stored encrypted in the session state with a `user:` prefix.
* **Agent/Tool Permissions**: While ADK doesn't have a built-in RBAC for tools, the architecture itself provides role separation. For example, only agents that are explicitly given the `ExecutorAgent`'s tool in their configuration can use it. The `CodeGenieCoordinator` can be programmed not to delegate execution privileges to certain sub-agents.

### 6. Scalability & Deployment

* **Deployment Strategy**: A container-based deployment using Kubernetes is recommended for scalability. Each agent, or logical group of agents (like the two `VoiceAgent`s), can run in its own pod.
* **Auto-Scaling**: The `ParallelCodeGeneration` agent is a prime candidate for auto-scaling. The number of `CodeGeneratorAgent` replicas can be scaled horizontally based on the number of independent modules identified by the `DividerAgent`. Kubernetes Horizontal Pod Autoscaler can be used to manage this.
* **Observability**:
  * **Logging**: All agents will use a structured logger. Callbacks will be used to log every agent entry/exit and tool call.
  * **Tracing**: The `invocation_id` provided by the ADK context objects should be propagated as a trace ID across all logs and agent interactions, allowing for a complete trace of a user request through the entire system.
  * **Monitoring**: A central dashboard (e.g., Grafana) can monitor the `Universal Event Queue` size, agent error rates, and the execution time of different pipeline stages.

### 7. Future UI Extension (VS Code-like UI)

The ADK is well-suited to power a rich, interactive front-end.

* **Real-time Streaming**: The left panel displaying the SRS and directory structure can be updated in real-time. The back-end can stream `Event` objects as they are generated. A front-end WebSocket listener would receive these events and dynamically update the DOM to reflect changes to artifacts (`srs.md`, directory structure).
* **Exposing Tools to UI**: The front end could have buttons or command palettes that directly invoke specific agent tools. For example, a "Run Tests" button would trigger a call to the `TestingAgent`. This is achieved by creating API endpoints that route requests to the `runner.run()` method, targeting the specific tool-equipped agent.
* **Context Switching**: The chat interface (right panel) would be the primary interaction point with the `CodeGenieCoordinator`. The UI could send the entire chat history with each request, which the ADK can place into the agent's memory or context, enabling stateful conversations.
* **Voice Control**: Voice commands received in the UI would be transcribed to text and sent to the `CodeGenieCoordinator`, just like typed prompts. The audio feedback from the `VoiceAgent`s would be streamed back to the browser and played using the Web Audio API. ADK's `run_live()` method is ideal for these streaming interactions.
