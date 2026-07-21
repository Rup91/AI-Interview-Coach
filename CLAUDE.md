# AI Interview Coach

## Project Overview

This project follows an Architecture First development approach. Code implementation must always respect the architecture and API contract. If any ambiguity exists, ask for clarification instead of making architectural decisions.

AI Interview Coach is an enterprise-inspired AI-powered interview platform that helps candidates prepare for technical interviews through AI-generated questions, answer evaluation, and personalized feedback.

The application supports both text-based and voice-based interview experiences and is designed using a modular, layered architecture.

The project follows an **Architecture First** development approach.


## Source of Truth

Always use the following documents as the primary source of truth.

1. ARCHITECTURE.md
2. API_CONTRACT.md

Do not deviate from these documents unless explicitly instructed.


## Development Principles

- Write clean, readable, and maintainable code.
- Keep components loosely coupled.
- Prefer composition over duplication.
- Follow SOLID principles whenever applicable.
- Keep functions small and focused.
- Avoid unnecessary abstractions.
- Do not introduce new frameworks without approval.

## Project Structure

backend/
frontend/
docs/
shared/

Do not change the project structure unless requested.


## Backend Guidelines

Framework:
- FastAPI

Responsibilities:
- Expose REST APIs.
- Validate requests.
- Manage interview sessions.
- Route business requests.
- Handle errors consistently.

The API implementation must strictly follow API_CONTRACT.md.

## Frontend Guidelines

Framework:
- Streamlit

Responsibilities:
- Collect interview configuration.
- Display interview questions.
- Capture text or voice responses.
- Display AI feedback and scores.
- Display interview summary.

Frontend should not contain business logic.


## Business Layer

Responsibilities:

- Interview configuration
- Interview lifecycle
- Question generation
- Answer evaluation
- Session management
- Report generation

Business logic must remain independent of AI providers.


## AI Gateway

The AI Gateway is responsible for:

- Routing AI requests
- Calling AI providers
- Standardizing request/response formats
- Provider abstraction

Never call AI providers directly from business services.


## AI Providers

Primary Provider:
- Google Gemini

Future Providers:
- OpenAI
- Ollama

All provider integrations must go through the AI Gateway.


## Session Management

Each interview session must have a unique Interview ID.

Session lifecycle:

Configured
↓

In Progress
↓

Completed


## Error Handling

Always return consistent API responses.

Example:

{
    "success": false,
    "message": "...",
    "errors": []
}

Never expose stack traces to the client.

## Coding Standards

- Use meaningful names.
- Avoid hardcoded values.
- Prefer configuration files.
- Add docstrings where appropriate.
- Keep files modular.
- Avoid large classes.
- Avoid long methods.


## Logging

Use structured logging.

Log:

- Interview creation
- Interview start
- AI requests
- AI responses
- Errors
- Interview completion

Never log sensitive information.

## Configuration

Keep configurable values outside the source code.

Examples:

- API Keys
- Model names
- Temperature
- Maximum tokens
- Prompt locations

## Prompt Management

Do not hardcode prompts inside Python files.

Store prompts in dedicated files under the prompts/ directory.

## Future Compatibility

The implementation should remain compatible with future support for:

- Knowledge Graph
- RAG
- AI Agents
- Multiple LLM providers
- Recruiter Portal
- Authentication
- Persistent Database

Avoid implementation decisions that make these future enhancements difficult.

## Development Rules

Before implementing any feature:

1. Review ARCHITECTURE.md.
2. Review API_CONTRACT.md.
3. Implement only the requested functionality.
4. Keep changes localized.
5. Avoid unnecessary refactoring.

Never modify the architecture without explicit approval.

## Code Generation Rules

When generating code:

- Produce production-quality code.
- Follow Python best practices.
- Explain important design decisions.
- Keep modules independent.
- Prefer reusable components.
- Keep APIs RESTful.
- Validate inputs.
- Handle exceptions gracefully.

Do not generate placeholder implementations unless explicitly requested.

## Definition of Done

A task is considered complete only if:

- Code compiles successfully.
- APIs follow API_CONTRACT.md.
- Architecture remains unchanged.
- Error handling is implemented.
- Logging is added where appropriate.
- Code is modular and maintainable.
