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
    "experienceLevel" "Senior",
    "totalQuestions": 10
}
```
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

#### Response

```json
{
    "success": true,
    "message": "Interview session retrieved successfully",
    "data": {
        "interviewID": "INT-10001",
        "status": "In Progress",
        "interactionMode": "Voice",
        "currentQuestion": 4,
        "completedQuestions": 3,
        "totalQuestions": 10,
        "progressPercentage": 30
    }
}
```
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

#### Response

```json
{
    "success": true,
    "message" "Answer evaluated successfully",
    "data": {
        "score": 8,
        "strengths": [
            "Good conceptual understanding"
        ],
        "improvementAreas": [
            "include practical use cases"
        ],
        "feedback": "Your explanation is technically correct but could be more detailed.",
        "nextQuestion": {
            "questionNumber": 2,
            "question": "Explain the role of embeddings in a RAG pipeline"
        }
    }
}
```

#### Possible Status Codes

| Code | Description |
|------| ------------|
| 200 | Answer evaluated successfully |
| 400 | Invalid request |
| 409 | Interview session not found  |
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

#### Response

```json
{
    "success": true,
    "message" "Answer evaluated successfully",
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
        "nextQuestion": {
            "questionNumber": 2,
            "question": "Explain the role of embeddings in a RAG pipeline"
        }
    }
}
```

#### Possible Status Codes

| Code | Description |
|------| ------------|
| 200 | Answer evaluated successfully |
| 400 |  Invalid request |
| 404 | Interview session not found  |
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
           &darr;
    
    Generate Interview Session
            &darr;
    
    Start Interview
            &darr;
    
    Receive First Question
            &darr;
    
    Submit Answer (text/Voice)
            &darr;
    
    AI Evaluation
            &darr;
    
    Receive Next Question
            &darr;
    
    Repeat Untill Completion
            &darr;
    
    Complete Interview
            &darr;

    Generate Final Report
            