# API Contract

## 1. Overview

This document defines the REST API contract for the AI Interview Coach platform.

The APIs enable interview configuration, interview execution, candidate interaction, AI-powered evaluation, and interview completion.

The API contract serves as the agreement between the frontend application and backend services, ensuring consistent request and response formats throughout the application.


## 2. Design Principles

The APIs are designed following RESTful principles and enterprise application best practices.

### Design Goals

- Resources-oriented API design
- Stateless Communication
- JSON-based request and response payloads
- Consistent response structure
- Clear HTTP status codes
- Extensible endpoint design
- Separation between interview configuration and interview execution.

## 3. Common Request Headers

| Header | Value |
|--------|-------|
| Content-Type | application/json |
| Accept | applicaiton/json |

> Authentication headers will be introduced in a future release.

## 4. Common Response Structure

Successful responses follow a standardized structure.

```json
{
    "success": true,
    "message": "Interview started successfully",
    "data": {}
}
```

where:

- success -> Indicates whether the request was processed successfully. 
- message -> Provides a human-readable response.
- data -> contains the endpoint-specific payload.

## 5. Error Response Structure

All API errors follow a consistent format.

``` json
{
    "success": false,
    "message": "Interview session not found",
    "errors": []
}
```
The errors - collection may contain one or more validation or processing errors.

## 6. API Endpoints

### i. Configure Interview

Creates a new interview configuration and initializes an interview session.

#### Endpoint

```
POST /interviews/configure

```
#### Description

This API configures an interview based on the selected role or uploaded Job Description (JD), preferred interaction mode, and interview settings.

A unique interview session is created and returned. The interview DOES NOT start automatically.

#### Request Body

```json
{
    "role": "AI Solution Architect",
    "jobDescription": "<optional JD text>",
    "interactionMode": "voice",
    "experienceLevel": "Senior"
}
```

> The number of interview questions is a backend-controlled business
> decision (minimum 6, up to a maximum of 12, based on candidate
> performance) and is intentionally not a client-supplied field.
#### Response

```json
{
    "success": true,
    "message": "Interview configured successfully",
    "data": {
        "interviewID": "INT-10001",
        "status": "Configured"
    }
}
```

#### Possible Status Codes

| Code | Description |
|------| ------------|
| 201 | Interview configuration created |
| 400 | Invalid request |
| 500 | Internal server error |

### ii. Start Interview

Starts a configured interview session and returns the first interview question.

#### Endpoint

```
POST /interviews/{interviewId}/start

```

#### Description

Starts the interview session and generates the first interview question using the configured interview settings.

#### Request Body

```json
{}
```
#### Response

```json
{
    "success": true,
    "message": "Interview started successfully",
    "data": {
        "questionNumber": 1,
        "question": "Explain the difference between RAG and Fine-tuning."
    }
}
```

#### Possible Status Codes

| Code | Description |
|------| ------------|
| 200 | Interview started |
| 404 | Interview not found |
| 409 | Interview already started |
| 500 | Internal server error |


### iii. Get Interview Session

Retrieves the current interview session details and progress.

#### Endpoint

```
GET /interviews/{interviewId}

```

#### Description

Returns the current interview status, progress, interaction mode, and interview configuration.

#### Response (interview in progress)

```json
{
    "success": true,
    "message": "Interview session retrieved successfully",
    "data": {
        "interviewID": "INT-10001",
        "status": "In Progress",
        "interactionMode": "voice",
        "currentQuestion": {
            "questionNumber": 4,
            "question": "Explain the role of embeddings in a RAG pipeline"
        },
        "questionsAnswered": 3,
        "averageScore": 6.33
    }
}
```

#### Response (not yet started / completed)

```json
{
    "success": true,
    "message": "Interview session retrieved successfully",
    "data": {
        "interviewID": "INT-10001",
        "status": "Configured",
        "interactionMode": "voice",
        "currentQuestion": null,
        "questionsAnswered": 0,
        "averageScore": null
    }
}
```

> The number of questions is a backend-controlled business decision (see
> section 6(i)) - this response deliberately does not include a total
> question count or a progress percentage, since interview length is
> adaptive. `currentQuestion` is `null` when the interview has not yet
> been started ("Configured") or has already finished ("Completed").
> `averageScore` (0-10, matching each answer's individual `score`) is
> `null` until at least one answer has been evaluated. This endpoint
> does not return the final interview report (recommendation, summary,
> aggregated strengths) - that is only produced when the interview
> completes via Submit Answer, or by a future Complete Interview
> endpoint.

#### Possible Status Codes


| Code | Description |
|------| ------------|
| 200 | Interview session retrieved successfully |
| 404 | Interview session not found |
| 500 | Internal server error |


### iv. Submit Text Answer

Submits a text response, evaluates the answer, and returns feedback with the next interview question.

#### Endpoint

```
POST /interviews/{interviewId}/answer/text

```

#### Description

Evaluates the candidate's text response using the AI Gateway and returns the evaluation result along with the next interview question.

#### Request Body

```json
{
    "answer": "RAG combines retrieval with generation by providing external knowledge to the LLM before generating the response."
}
```

#### Response (interview continues)

```json
{
    "success": true,
    "message": "Answer evaluated successfully",
    "data": {
        "score": 8,
        "strengths": [
            "Good conceptual understanding"
        ],
        "improvementAreas": [
            "include practical use cases"
        ],
        "feedback": "Your explanation is technically correct but could be more detailed.",
        "idealAnswer": "A strong answer would explain the core concept, walk through the reasoning, and connect it to a concrete example.",
        "nextQuestion": {
            "questionNumber": 2,
            "question": "Explain the role of embeddings in a RAG pipeline"
        },
        "interviewResult": null
    }
}
```

#### Response (interview completes)

```json
{
    "success": true,
    "message": "Answer evaluated successfully",
    "data": {
        "score": 7,
        "strengths": [
            "Good conceptual understanding"
        ],
        "improvementAreas": [
            "include practical use cases"
        ],
        "feedback": "Your explanation is technically correct but could be more detailed.",
        "idealAnswer": "A strong answer would explain the core concept, walk through the reasoning, and connect it to a concrete example.",
        "nextQuestion": null,
        "interviewResult": {
            "overallScore": 74,
            "strengths": [
                "Good conceptual understanding"
            ],
            "improvementAreas": [
                "include practical use cases"
            ],
            "recommendation": "Recommended for further evaluation",
            "summary": "The candidate completed 6 questions with an overall score of 74%. Recommendation: Recommended for further evaluation."
        }
    }
}
```

> The number of questions is a backend-controlled business decision (see
> section 6(i)). Every response includes the evaluation of the answer
> just submitted, plus exactly one of `nextQuestion` (interview
> continues) or `interviewResult` (interview has just completed) - never
> both, never neither.

#### Possible Status Codes

| Code | Description |
|------| ------------|
| 200 | Answer evaluated successfully |
| 400 | Invalid request |
| 404 | Interview session not found |
| 409 | Interview session exists but is not currently "In Progress" |
| 500 | Internal server error |


### v. Submit Voice Answer

Submits a voice response, converts speech to text, evaluates the answer, and returns feedback with the next interview question.

#### Endpoint

```
POST /interviews/{interviewId}/answer/voice

```

#### Description

Processes the uploaded audio, converts it to text, evaluates the response using the AI Gateway, and returns the evaluation result with the next interview question.

#### Request Body

```json
{
    "audioFile": "candidate-answer.wav"
}
```

#### Response (interview continues)

```json
{
    "success": true,
    "message": "Answer evaluated successfully",
    "data": {
        "transcription": "RAG combines retrieval with generation...",
        "score": 8,
        "strengths": [
            "Clear explanation"
        ],
        "improvementAreas": [
            "Provide an implementation example"
        ],
        "feedback": "Well explained. Consider adding a real-world use case",
        "idealAnswer": "A strong answer would explain the core concept, walk through the reasoning, and connect it to a concrete example.",
        "nextQuestion": {
            "questionNumber": 2,
            "question": "Explain the role of embeddings in a RAG pipeline"
        },
        "interviewResult": null
    }
}
```

> Same rules as Submit Text Answer: exactly one of `nextQuestion` /
> `interviewResult` is present, never both, never neither. `audioFile` is
> a reference string identifying previously-uploaded audio (e.g. a
> filename) - this endpoint does not accept a raw file upload.

#### Possible Status Codes

| Code | Description |
|------| ------------|
| 200 | Answer evaluated successfully |
| 400 | Invalid request |
| 404 | Interview session not found |
| 409 | Interview session exists but is not currently "In Progress" |
| 500 | Internal server error |



### vi. Complete Interview

Completes the interview session and generates the final interview report.

#### Endpoint

```
POST /interviews/{interviewId}/complete

```
#### Description

Finalizes the interview and returns the overall evaluation summary.

#### Request Body

```json
{}
```

#### Response

```json
{
    "success": true,
    "message": "Interview completed successfully",
    "data": {
        "overallScore": 84,
        "strengths": [
            "Strong AI founamentals",
            "Good communication"
        ],
        "improvementAreas": [
            "System Design",
            "Enterprise Architecture"
        ],
        "recommendation": "Recommended for Techinical Round 2",
        "summary": "The candidate demonstrated strong conceptual knowledge with minor improvement areas."

    }
}
```
#### Possible Status Codes

| Code | Description |
|------| ------------|
| 200 | Interview completed successfully |
| 404 | Interview session not found  |
| 500 | Internal server error |


## 7. HTTTP Status COdes

| Status Code | Description |
|-------------| ------------|
| 200 | Request processed successfully |
| 201 | Resource created successfully  |
| 400 | Bad request |
| 401 | Unauthorized (Future) |
| 403 | Forbidden (Future) |
| 404 | Resource not found | 
| 409 | Conflict |
| 500 | Internal server error|


## 8. End-to-End API Flow

```
    configure Interview
           ↓
    
    Generate Interview Session
            ↓
    
    Start Interview
            ↓
    
    Receive First Question
            ↓
    
    Submit Answer (text/Voice)
            ↓
    
    AI Evaluation
            ↓
    
    Receive Next Question
            ↓
    
    Repeat Untill Completion
            ↓
    
    Complete Interview
            ↓

    Generate Final Report
            