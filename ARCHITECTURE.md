# AI Interview Coach

## 1. Project Vision

AI Interview Coach is an enterprise-ready interview platform designed to help candidates prepare for technical and behavioral interviews through AI-driven conversations.

The platform supports both test and voice interactions, evaluates candidate responses, provides follow-up questions, and delivers
recommendations.

The architecture is modular, scalable, and provider-agnostic, allowing integration with multiple Large Language Models (LLMs),
Speech-to-Text engines, Text-to-Speech providers, AI Gateways, and Knowledge Graphs in future releases.

The long-term vision is to evolve from a mock interview assistant into an AI-assisted interview platform that can support candidate preparation, technical screening, recruiter workflows, and expert interview evaluation. 


## 2. Problem Statement

Many organixations face challenges in preparing candidates and conducting consistent technical interviews. Interview prepation often depends on the availability and experience of senior engineers, creating unnecessary dependencies and making the process difficult to scale.

Candidates preparing for client interviews usually rely on informal knowledge sharing, personal notes, or one-to-one guidance from
experienced team members. As a result, interview preparion is inconsistnet, knowledge is not retained, and valuable expertise remains distributed across individuals instead of being captured in a reusable platform. 

Similarly, technical screening interviews require significant interviewer effort, while candidates often receive little or no structured feedback after the inteview. This makes it difficult for candidates to improve and increases the workload on experienced interviewers.

This project aims to address these challenges by building an AI-assisted interview platform that focuses on three key objecttives. 

### i. Interview Preparation
    
    - Help candidates practice role-specific technical interviews independently through AI-guided conversations and personalized feedback

### ii. AI-assisted Technical Screening

    - Support interviewers by conducting structured first-round technical assessments and generating evaluation reports for human review.

### iii. Knowledge Enablement

    - Capture interview knowledge, best practicesm and role-specific learning path into a reusable and scalable platform, reducing dependency on individual experts and improving knowledge sharing across teams.


## 3. Goals

The primary goals of this project are:

### Functional Goals

    - Provide an AI-powered interview preparation platform.
    - Support both text-based and voice-based interview interactions.
    - Evaluate candidate responses using Large Language Models (LLMs).
    - Generate structured feedback, scores, and improvement recommendations.
    - Support configurable interview flows based on roles, skills, and experience levels.
    - Maintain a modular architecture for future scalablity. 

### Technical Goals

    - Follow clean architecture and separation of concerns.
    - Keep the frontend and backend loosely coupled.
    - Introduce an AI Gateway layer for future multi-model support.
    - Support configurable LLM providers without changing business logic.
    - Design the system to support future integration with Knowledge Graphs and enterprise knowledge bases. 


## 4. Non-Goals

The first version of the platform will not include:

    - User authentication and authorization.
    - Database presistence.
    - Multi-user support.
    - Production deployment.
    - Recruiter dashboard.
    - Knowledge Graph integration.
    - Enterprise client integration.

## 5. HLD 

Please check the diagram - AI-interview-Coach.png

## 6. Technology Stack

The following technologies have been selected to build the AI Interview Coach platform. The architecture is modular, scalable, and
provide-agnostic, allowing individual components to evolve independently. 

| Layer | Technology | Purpose |
|-------| -----------|---------|
| Frontend | Streamlit | Provies the web-based user interface for interview interactions. |
| Backend | FastAPI | Exposes REST APIs and manages application requests. |
| Programing Language | Python | Primary Programming Language for the application |
| AI Gateway | Custom Python Module | Routes requests to AI providers and abstracts provider-specific implementations |
| Primary LLM | Google Gemeini | Generate interview questions, evaluates responses, and provides feedback. |
| Alternative LLMs | OpenAI, Ollama | Supports future multi-model integration |
| Speech-To-Text | Whisper | Converts voice responses into text |
| Text-to-Speech | Piper / Coqui | Converts AI responses into speech |
| Knowledge Layer | File-based Repository(JSON/Markdown) | Stoores prompts and interview questions for the MVP |
| Knowledge Graph (Future) | Neo4j | Represents relationships between roles, skills, and interview topics |


## 7. Component Responsibilities

### i. Presentation Layer

#### Component: 

    - Streamlit Web Application

#### Responsibilities:
    
    - Provides the user interface for interview sessions.
    - Allows users to select interview roles
    - Accepts text and voice inputs.
    - Displays interview questions, scores, and feedback.
    - Communications with the backend through REST APIs.


### ii. API Layer

#### Component: 

    - FastAPI Backend

#### Responsibilities:

    - Exposes RESTful APIs.
    - Receives and validates client requests.
    - Routes requests to the Business Layer.
    - Returns responses to the frontend.

### iii. Business Layer

#### Component: 

    - Interview Service
    - Voice Service
    - Evaluation Service
    - Session Service

#### Responsibilities:

    - Controls the interview workflow.
    - Manages interview sessions.
    - Processess voice interactions.
    - Evaluates candidate responses.
    - Generates interview feedback.
    - Sends AI requests through the AI Gateway. 


### iv. AI Gateway

#### Component: 

    - Model Router
    - Provider Adapter

#### Responsibilities:

    - Selects the appropriate AI provider.
    - Abstracts provider-specific implementations.
    - Standardizes request and response formats.
    - Enables support for multiple LLM Providers.


### v. AI Providers

#### Component:

    - Google Gemini
    - OpenAI
    - Ollama

#### Responsibilities:

    - Generates interview questions.
    - Evaluates canddiate responses.
    - Produces AI-generated feedback.


### vi. Knowledge Layer

#### Component:

    - Prompt Repository
    - Interview Question Repository

#### Responsibilities:

    - Stores reusable prompts.
    - Stores role-specific interview questions.
    - Supports future knowledge Graph integration.


## 8. Interview Workflow

The AI Interview Coach supports multiple interview scenarios, including interview prepartion, AI-assisted technical screening, and future enterprise recruitment workflows. 

### Step 1: Interview Configuration

The interview session can be initiated in one of the following ways:

- Select a predefined interview role (e.g. AI Solution Architect, AI Consultant, Cloud Architect)
- Upload a Job Description to generate a customized interview.
- Receive a predefined interview configuration from an organization or recruiter. (** Future Enhancement ** )

### Step 2: Interview Preparation

The platform prepares the interview by:

- Identifying the required skills and responsibilities.
- Determining the interview objectives
- Generating role-specific or JD-specific interview questions.

### Step 3: Interaction Mode Selection

The user selects the preferred interview mode:

- Text
- Voice 
- Text + Voice

### Step 4: Interview Initialization

The frontend sends the interview request to the backend.

The Business Layer creates a new interview session and requests the first interview questions through the AI Gateway.

### Step 5: Interview Execution

The AI provider generates the interview question,

The question is presented to the candidate. 

The candidate submits an answer using text or voice.

If voice mode is selected, the Voice Service converts speech into text before evaluation.

### Step 6: AI Evaluation

The candidate's response is evaluated through the AI Gateway.

The AI provider generates:

- Candidate score
- Strengths
- Areas for improvements
- Ideal answer of the questions
- Next interview question

### Step 7: Continuous Interview

Step 5 and Step 6 are repeated until the interview is completed.

### Step 8: Interview Summary

At the end of the interview, the platform generates a comprehensive interview report containing:

- Overall score
- Performance summary
- Strengths
- Ares for improvement
- Final recommendations


## 9. API Design

The AI Interview Coach exposes RESTful APIs to support interview initialization, candidate interaction, and interview completion.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/interviews/configuration` | POST   | Creates a new interview configuration based on the selected role or uploaded Job Description (JD), preferred interaction mode (Text/Voice), and returns an interview session ID. |
| `/interviews/{interviewId}/start` |  POST | Starts the interview session and returns the first interview question. |
| `/interviews/{interviewId}` | GET | Retrieves the current interview session details and progress. |
| `/interviews/{interviewId}/answer/text` | POST | Accepts a text response, evaluates the answer, and returns the score, feedback, and next interview question. |
| `/interviews/{interviewId}/answer/voice` | POST | Accepts a voice response, converts speech to text, evaluates the answer, and returns the score, feedback, and next interview question. |
| `/interviews/{interviewId}/complete` | POST | Completes the interview session and generates the final interview report. |

## 10. AI Gateway Design

The AI Gateway acts as the abstraction layer between the Business Layer and AI providers. Instead of directly integrating with a specific LLM, all AI requests pass through the AI Gateway. 

The design provides flexibility, maintainability, and provider independence.

### Components

#### Model Router

The Model Router determines which AI procider should handle a request based on the configured routing strategy. 

#### Provider Adapter

The Provider Adapter translates provider-specific request and response formats into a standarized internal format. 

### Responsibilities

- Decouple business logic from AI providers
- Support multiple LLM providers.
- Standardize request and response formats
- Enable future model routing strategies.
- Simplify provider replacement without affectinf the Business Layer.

### Supported Providers

- Google Gemini (Primary)
- OpenAI
- Ollama

### Future Enhancements

- Dynamic model routing
- Cost-aware routing
- Performance-based routing
- Fallback provider support
- AI usage monitoring

## 11. Future Roadmap

The current architecture is designed to support future enhancements while keeping the core components modular and extensible.

### Phase 2

- Recruiter Portal for interview configuration and candidate management.
- Candidate authentication and authorization.
- Persistent storage for interview sessions and evaluation history.
- Configurable interview templates for different job roles.

### Phase 3

- Knowledge Grapg integration for domain-specific interview generation.
- Retrieval-Augmented Generation (RAG) for contextual question generation.
- AI Agent-based interview orchestration.
- Dynamic model routing through the AI Gateway.

### Phase 4

- Multi-round interview workflows.
- Adaptive interview generation based on candidate performance.
- Analytics and reporting dashboard
- Enterprise integration with ATS, HRMS, and Calendar systems.
- AI governance, monitoring, and observability.