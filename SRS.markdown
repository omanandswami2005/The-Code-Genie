# Software Requirements Specification (SRS)

**For CodeGenie: Automated Software Development System**

**Version 1.1**

**Prepared by:** Omanand Swami

**Date:** June 26, 2025

---

## 1. Introduction

### 1.1 Purpose

This document outlines the requirements for **CodeGenie**, an automated software development system designed to create software projects or any project based on user requirements. The system uses a chat interface to interact with users, automating the process of requirement gathering, code generation, execution, and maintenance, with real-time voice feedback for enhanced user interaction.

### 1.2 Scope

CodeGenie will:

- Generate and refine a Software Requirements Specification (SRS) iteratively based on user input.
- Design and implement a project directory structure.
- Generate code in parallel for independent modules.
- Execute code securely using OS commands.
- Update code based on new requirements.
- Collect sensitive user inputs (e.g., API keys) securely.
- Provide voice feedback on progress, code explanations, and agent activities.
- Include testing, documentation, error handling, and version control features.

### 1.3 Definitions, Acronyms, and Abbreviations

- **SRS**: Software Requirements Specification
- **ADK**: Agent Development Kit (Google ADK assumed)
- **JSON**: JavaScript Object Notation
- **Markdown (.md)**: Lightweight markup language for human-readable documents
- **CRUD**: Create, Read, Update, Delete
- **CodeGenie**: The name of the automated software development system

### 1.4 References

- Google ADK Documentation (for agent communication and tool integration)

### 1.5 Overview

This document includes an overall description, specific functional and non-functional requirements, system architecture, user interface details, implementation notes, testing, deployment, and maintenance plans.

---

## 2. Overall Description

### 2.1 Product Perspective

CodeGenie is a standalone tool to automate software development, enabling rapid project creation for developers, project managers, or non-technical users with basic project knowledge. It leverages a chat interface and voice feedback to enhance usability and provide real-time updates.

### 2.2 Product Functions

- **SRS Creation**: Generate and refine an SRS based on user input.
- **Directory Structure Design**: Create and implement a project directory structure.
- **Code Generation**: Produce code in parallel with explanations.
- **Code Execution**: Run generated code securely.
- **Code Updates**: Modify code based on new requirements.
- **User Input Collection**: Securely gather specific inputs.
- **Voice Feedback**: Provide asynchronous updates, code explanations, and feedback from all agents via a processing queue.
- **Testing**: Generate and run unit tests.
- **Documentation**: Auto-generate project documentation.
- **Error Handling**: Monitor and address execution errors.
- **Version Control**: Manage project versions.

### 2.3 User Characteristics

Users are expected to understand basic project requirements and interact via a chat interface. No advanced technical expertise is required, though familiarity with software development is beneficial. Users can leverage voice feedback for intuitive interaction.

### 2.4 Constraints

- Security must be ensured for OS command execution and sensitive data handling.
- The system must be portable across operating systems (Linux, Windows, macOS).
- Voice feedback must not degrade system performance or overwhelm users.

### 2.5 assumptions and Dependencies

- Assumes availability of Python and related libraries on the user's system.
- Depends on Google ADK for agent communication and tool integration.
- Assumes a speech synthesis system is available for voice feedback.

---

## 3. Specific Requirements

### 3.1 Functional Requirements

#### 3.1.1 SRS Creation

- The system shall provide a chat interface for users to specify project requirements.
- The SRS Creation Agent shall generate an initial SRS in JSON format for machine processing.
- The system shall render the JSON SRS into a human-readable markdown (.md) document for display.
- Users shall review and provide feedback via the chat interface.
- The SRS Creation Agent shall refine the SRS iteratively based on user feedback.

#### 3.1.2 Directory Structure Design

- The Directory Structure Agent shall design a full project directory structure based on the SRS.
- The structure shall be presented in markdown for user approval.
- Upon approval, the system shall implement the structure using platform-agnostic libraries (e.g., Python’s `os` or `pathlib`).
- All directory creation commands shall be validated to prevent security risks (e.g., unauthorized file deletion).
- The Voice Agent shall provide audio updates on directory structure creation progress and completion.

#### 3.1.3 Code Generation

- The Divider Agent shall analyze the SRS and directory structure to build a dependency graph.
- It shall split the work into independent modules for parallel processing.
- Multiple Code Generator Agents shall produce code for each module concurrently.
- Code shall adhere to standardized conventions (e.g., naming, formatting) defined in a shared configuration.
- Explanations of the generated code shall be sent to the Voice Agent for real-time audio narration, detailing code purpose and structure.

#### 3.1.4 Code Execution

- The Executor Agent shall execute the generated code using OS commands.
- The system shall maintain a whitelist of allowed commands and sanitize inputs for security.
- All executed commands shall be logged for auditing and debugging.
- The Voice Agent shall provide audio feedback on execution progress, success, or errors.

#### 3.1.5 Code Updating

- The Updater Agent shall modify code based on new user requirements.
- Changes shall be tracked using a lightweight version control system (e.g., Git-like diffs).
- Proposed updates shall be presented as diffs in the markdown document for user approval before merging.
- The Voice Agent shall narrate proposed changes and their impact before user approval.

#### 3.1.6 User Input Collection

- The User Inputs Agent shall collect specific inputs (e.g., API keys, database URLs) THROUGH the chat interface.
- All inputs shall be encrypted to ensure security.
- The Voice Agent shall confirm successful input collection or request clarification if inputs are invalid.

#### 3.1.7 Voice Feedback

- The Voice Agent shall provide asynchronous updates and code explanations from all agents (SRS Creation, Directory Structure, Code Generator, Executor, Updater, User Inputs, Testing, Documentation, Error Handling, Version Control).
- Updates shall use a priority queue:
  - High-priority messages (e.g., errors, critical updates) are spoken immediately.
  - Low-priority messages (e.g., progress updates, detailed code explanations) are batched or summarized.
- Users shall toggle verbosity (e.g., "silent mode," "summary mode," or "detailed explanations") via the chat interface.
- The Voice Agent shall narrate code snippets and explain their functionality during generation or updates.

#### 3.1.8 Testing

- The Testing Agent shall generate unit tests for the code.
- Tests shall be executed via the Executor Agent, with results reported to the user.
- The Voice Agent shall provide audio summaries of test results, highlighting passed or failed tests.

#### 3.1.9 Documentation

- The Documentation Agent shall auto-generate documentation (e.g., README, API docs) based on the SRS and code.
- The Voice Agent shall provide audio summaries of generated documentation.

#### 3.1.10 Error Handling

- The Error Handling Agent shall monitor execution logs for errors.
- Upon detecting an error, it shall suggest fixes (e.g., "Missing import: add `import os`") or alert the user via the chat interface.
- The Voice Agent shall narrate error details and proposed fixes in real-time.

#### 3.1.11 Version Control

- The Version Control Agent shall manage versions of the code and SRS, supporting change tracking and rollback.
- The Voice Agent shall provide audio updates on version changes or rollback events.

### 3.2 Non-Functional Requirements

#### 3.2.1 Security

- All OS commands shall be validated and sanitized to prevent vulnerabilities.
- Sensitive user inputs (e.g., API keys) shall be encrypted during collection and storage.

#### 3.2.2 Portability

- The system shall use platform-agnostic libraries to ensure compatibility across Linux, Windows, and macOS.

#### 3.2.3 Usability

- The chat interface shall be intuitive, with a dynamically updated markdown document for easy review.
- Voice feedback shall be clear, concise, and adjustable to user preferences.

#### 3.2.4 Performance

- Code generation and execution shall be optimized for efficiency using parallel processing.
- Voice feedback shall not significantly impact system responsiveness, even during intensive tasks.

#### 3.2.5 Reliability

- The system shall handle errors gracefully, providing actionable feedback.
- Unit tests shall ensure code meets specified requirements.

---

## 4. System Architecture

CodeGenie comprises multiple agents (SRS Creation, Directory Structure, Divider, Code Generator, Executor, Updater, User Inputs, Voice, Testing, Documentation, Error Handling, Version Control) interacting via Google ADK protocols. Agents share data (e.g., JSON SRS, dependency graphs) and integrate with external tools (e.g., AI models for code generation, Google search, and crawling) as needed. The Voice Agent processes a queue of feedback from all agents to provide real-time audio updates.

---

## 5. User Interface

The interface features:

- **Left Panel**: A dynamic markdown document displaying the SRS and directory structure.
- **Right Panel**: A ChatGPT-like chat window for user interaction, feedback, and command input.
- **Voice Feedback (UI 2)**: Real-time audio narration of agent activities, including:
  - Code explanations during generation or updates.
  - Progress updates on directory creation, execution, and testing.
  - Error reports and suggested fixes.
  - Summaries of documentation and version control actions.
- Users can toggle voice feedback verbosity (silent, summary, or detailed) via the chat interface.

---

## 6. Implementation Details

### 6.1 Technologies Used

- **Python**: Core scripting language.
- **JSON**: Machine-readable data format for SRS and internal processing.
- **Markdown**: Human-readable document format.
- **Google ADK**: Agent communication and tool integration.
- **Speech Synthesis Library**: For Voice Agent audio feedback (e.g., `pyttsx3` or similar).

### 6.2 Agent Communication

Agents communicate via message queues or direct calls, leveraging ADK protocols for seamless data sharing (e.g., Divider Agent sends context to Code Generator Agents). The Voice Agent receives feedback from all agents via a priority queue for processing and narration.

---

## 7. Testing and Validation

### 7.1 Unit Testing

- The Testing Agent shall generate and run unit tests for each code module.
- The Voice Agent shall narrate test results, highlighting critical outcomes.

### 7.2 Integration Testing

- Validate interactions between agents (e.g., SRS Creation to Directory Structure, Voice Agent feedback integration).

### 7.3 User Acceptance Testing

- Conduct testing with real users to ensure the system meets usability and functionality needs, including voice feedback clarity.

---

## 8. Deployment

CodeGenie shall be deployed on the user’s machine, requiring installation of Python, necessary libraries, Google ADK dependencies, and a speech synthesis library.

---

## 9. Maintenance and Support

- Regular updates shall address bugs and improve features, including voice feedback enhancements.
- User-reported issues shall be handled via a support channel.

---

## 10. Appendices

- **Example SRS**: Sample JSON and markdown SRS.
- **Directory Structure**: Example project layout in markdown.
- **Agent Specifications**: Detailed roles and interactions, including Voice Agent queue management.