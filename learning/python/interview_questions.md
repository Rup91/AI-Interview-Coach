# Python & Backend Architecture — Interview Preparation

Grounded entirely in the AI Interview Coach backend we've built so far:
the FastAPI foundation, the Configure Interview API, and the Start
Interview API. Every question below maps to a real decision made in this
codebase, not a generic textbook definition — the goal is that you can
answer "why did you do X" about your own project, which is what a senior
interview actually probes for.

**How to use this:** read a question, try to answer it out loud or in
writing *before* reading the answer, using our actual code as your
evidence. Then check yourself against the answer and the file it points
to. This file will grow as we add more features (Submit Answer, AI
Gateway, Gemini integration, etc.) — treat it as a living document.

---

## Part 1 — Python Language Fundamentals

### Q1. `SessionStatus` is defined as `class SessionStatus(str, Enum)`. Why inherit from both, and what would break if it only inherited from `Enum`?

**Answer:** Inheriting from `str` as well as `Enum` makes each member *also* a genuine string — `SessionStatus.CONFIGURED == "Configured"` is `True`, and `json.dumps`/Pydantic serialization emits the plain string `"Configured"` rather than something like `<SessionStatus.CONFIGURED: 'Configured'>`. If it only inherited from `Enum`, FastAPI/Pydantic would still handle serialization correctly (Pydantic knows how to serialize enums), but comparisons against plain strings elsewhere in the code, and any place that does simple string formatting (`f"...{status}..."`), would behave less predictably, and libraries that don't know about `Enum` (plain `json.dumps`, log formatters) would need `.value` everywhere instead of just working.

*Where:* `backend/app/business/models.py`

### Q2. We used `@dataclass` for `InterviewSession` but Pydantic `BaseModel` for API schemas (`InterviewConfigureRequest`, etc.). Why two different tools for what looks like the same job?

**Answer:** They solve different problems. Pydantic's job is **parsing and validating untrusted external input** (JSON from an HTTP client) into a trusted shape — it's the boundary between the outside world and our code. `@dataclass` is for **internal, already-trusted data** — it's lighter weight, has zero validation overhead, and critically, using it keeps the Business Layer free of a Pydantic/FastAPI dependency (see Q13). If `InterviewSession` were a Pydantic model, the business layer would be importing an API-framework-adjacent library, which is exactly the coupling we deliberately avoided.

*Where:* `backend/app/business/models.py` (dataclass) vs `backend/app/schemas/interview.py` (Pydantic).

### Q3. Explain `created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))`. Why not just `created_at: datetime = datetime.now(timezone.utc)`?

**Answer:** Default argument values (including dataclass field defaults) are evaluated **once**, at class-definition time — not each time an instance is created. `created_at = datetime.now(timezone.utc)` as a bare default would compute a single timestamp when the module is imported, and *every* `InterviewSession` ever created would share that exact same timestamp. `default_factory` instead stores a callable, which the dataclass machinery invokes fresh for every new instance. This is the same trap as Python's classic `def f(x, items=[])` mutable-default-argument bug, generalized.

### Q4. Why `datetime.now(timezone.utc)` instead of `datetime.utcnow()`?

**Answer:** `datetime.utcnow()` returns a **naive** datetime (no `tzinfo` attached) that happens to hold UTC values — nothing about the object itself says "this is UTC," so it's easy to accidentally mix it with local-time naive datetimes and get silently wrong arithmetic. `datetime.now(timezone.utc)` returns an **aware** datetime that carries its UTC offset explicitly. It's the officially recommended approach in modern Python (`utcnow()` is actually deprecated as of Python 3.12).

### Q5. What does the bare `*` do in `def configure_interview(self, *, role: str, interaction_mode: InteractionMode, ...)`?

**Answer:** Everything after a bare `*` in a function signature must be passed **as a keyword argument** — positional calls are rejected. With five-plus parameters of similar types (several strings, several enums), positional calls become a silent-bug factory: swap two arguments of the same type and Python won't complain, it'll just misassign data. Forcing keywords makes every call self-documenting and removes an entire class of argument-order bugs, at zero runtime cost.

*Where:* `backend/app/business/interview_service.py`

### Q6. What is `functools.lru_cache` doing on `get_settings()`, `get_session_store()`, etc., and why does that give us a singleton?

**Answer:** `lru_cache` memoizes a function's return value keyed by its arguments. Our provider functions take **no arguments**, so there's only ever one possible cache key — meaning the underlying object (e.g. the one `InMemorySessionStore` instance) is constructed exactly once per process and every subsequent call returns the *same* object. That's a singleton, implemented without a singleton class, a module-level global, or a metaclass — just a decorator, which is simpler to reason about and to override in tests (`lru_cache`d functions can have their cache cleared or be monkeypatched cleanly via FastAPI's `app.dependency_overrides`).

*Where:* `backend/app/api/dependencies.py`, `backend/app/core/config.py`

### Q7. Why does `InMemorySessionStore` need a `threading.Lock` at all — doesn't Python's GIL already make dict operations safe?

**Answer:** The GIL guarantees that a *single bytecode instruction* is atomic — a single `dict[key] = value` or `dict.get(key)` won't corrupt the dict's internal C structure. But it says nothing about **sequences of operations**. `transition_status()` does *check* the current status, *then* writes a new one — that's two operations, and the GIL can switch threads between any two Python bytecode instructions (FastAPI runs sync `def` routes in a thread pool, so this is a real, not theoretical, concern here). Without the lock, two threads could both pass the "is it Configured?" check before either writes "In Progress," and both would proceed to start the same interview. See Q19 for the deeper walkthrough — we deliberately tested this exact scenario with two parallel requests.

*Where:* `backend/app/business/session_store.py`

### Q8. What's the difference between `raise HTTPException(...) from exc` and just `raise HTTPException(...)`?

**Answer:** `raise ... from exc` sets `__cause__` on the new exception, explicitly recording "this exception was caused by that one." Python's default traceback then prints both exceptions with `"The above exception was the direct cause of the following exception"`, instead of the more ambiguous "during handling of the above exception, another exception occurred" you'd get from a bare `raise` inside an `except` block (or, worse, losing the connection entirely with a fully new `raise SomeError()`). For debugging in production logs, this is the difference between seeing the real root cause (a `InterviewNotFoundError`) and only ever seeing the generic `HTTPException(404)` that replaced it.

*Where:* `backend/app/api/routes/interviews.py`

### Q9. What is `Generic[DataT]` doing in `class SuccessResponse(BaseModel, Generic[DataT])`?

**Answer:** It makes `SuccessResponse` a **generic container** — `SuccessResponse[InterviewConfigureData]` and `SuccessResponse[StartInterviewData]` are both valid, type-checked specializations of the same envelope class, each knowing its `data` field's exact shape. Without generics we'd either lose type safety (`data: dict` / `data: Any`) or hand-write a near-duplicate response class per endpoint (`ConfigureInterviewResponse`, `StartInterviewResponse`, ...) purely to pin down the `data` type — `Generic` lets one class serve every endpoint while `mypy`/Pydantic still catch a mismatched `data` payload at the type-checking or validation level.

*Where:* `backend/app/schemas/common.py`

---

## Part 2 — FastAPI & API Design

### Q10. Walk through, step by step, what happens between a client calling `POST /interviews/configure` and a response being sent.

**Answer:**
1. Uvicorn receives the raw HTTP request and hands it to Starlette's ASGI app.
2. It passes through the registered exception-handling middleware (a safety net, not yet doing anything).
3. The router matches `/interviews/configure` to `configure_interview()`.
4. FastAPI parses the JSON body against `InterviewConfigureRequest` — if it fails validation, a `RequestValidationError` is raised right here, before our function body ever runs.
5. `Depends(get_interview_service)` resolves — since it's `lru_cache`d, this returns the same shared `InterviewService` instance every time rather than constructing one per request.
6. Our function body runs: calls `service.configure_interview(...)`.
7. The returned domain object is wrapped in `SuccessResponse[InterviewConfigureData]` and returned.
8. FastAPI serializes it using the schema's aliasing rules (snake_case → camelCase) and sends the JSON response with the declared `status_code=201`.

### Q11. FastAPI's default response for a validation failure is `422`. We override it to `400`. Why, and how?

**Answer:** API_CONTRACT.md — our own documented contract — specifies `400` for "Invalid request." FastAPI's built-in behavior doesn't know or care about our contract; it raises `RequestValidationError` internally and has a *default* handler registered for it that returns `422`. We register our **own** handler for the same exception type via `@app.exception_handler(RequestValidationError)`, which FastAPI lets you override — the last handler registered for a given exception type wins. Our handler builds the same `{success, message, errors}` envelope every other error path uses, and returns it with `400`. This was actually caught by testing, not designed up front — worth remembering as a general lesson: **framework defaults and your API contract are not the same document**, and you have to verify each error path individually rather than assume the framework already matches your spec.

*Where:* `backend/app/main.py`

### Q12. Our other exception handler is registered on `starlette.exceptions.HTTPException`, not `fastapi.HTTPException`. Why does that distinction matter?

**Answer:** `fastapi.HTTPException` is a *subclass* of `starlette.exceptions.HTTPException`. Code we write ourselves (`raise HTTPException(404, ...)` in our routes) raises the FastAPI subclass. But **Starlette's own router** — for something we never explicitly coded, like a request to a URL that doesn't exist — raises the **base** Starlette class directly. If we'd registered our handler only on the FastAPI subclass, an unmatched route would skip our handler entirely and fall through to Starlette's default, leaking the raw `{"detail": "Not Found"}` shape instead of our contract's `{success, message, errors}` envelope. We actually reproduced this exact bug while testing the health endpoint, before this project's interview APIs even existed, and fixed it by registering on the base class instead — registering on a parent class in Starlette's handler lookup covers all its subclasses too.

*Where:* `backend/app/main.py`

### Q13. Why did we choose plain `def` route handlers instead of `async def`?

**Answer:** `async def` only pays off when the function body actually `await`s something — a real async I/O operation (an async DB driver, an async HTTP client call). Our current handlers only do in-memory dict lookups and, soon, a call to an in-memory `QuestionRepository` — no I/O, nothing to await. If we wrote `async def` here, we'd get *no* benefit and one real risk: any accidentally-blocking call inside an `async def` (e.g. a synchronous library call) would freeze the *entire event loop*, blocking every other concurrent request, not just this one. A plain `def` route is automatically run by FastAPI in a worker thread pool, which is exactly the right execution model for synchronous, CPU-light, I/O-light code like ours. When we eventually add a real async AI provider call (Gemini's async client, for instance), *that* handler should become `async def`.

### Q14. Explain the camelCase/snake_case aliasing setup (`CamelCaseModel`, `alias_generator=to_camel`, `populate_by_name=True`).

**Answer:** API_CONTRACT.md's JSON uses camelCase (`jobDescription`, `interactionMode`) — standard for JSON APIs. Python's own style convention (PEP 8) is snake_case. Rather than pick one and violate the other, `alias_generator=to_camel` tells Pydantic to automatically derive a camelCase **alias** for every field from its snake_case name, used when parsing/serializing JSON. `populate_by_name=True` additionally allows constructing the model using the *Python* name too (`InterviewConfigureData(interview_id=..., status=...)` in our own code), not just the alias — without it, we'd be forced to write `InterviewConfigureData(**{"interviewID": ..., "status": ...})` everywhere internally, which is exactly the ugliness we're avoiding.

*Where:* `backend/app/schemas/common.py`

### Q15. `interviewID` is aliased explicitly with `Field(alias="interviewID")` instead of relying on the generator. Why?

**Answer:** The generic `to_camel` conversion of `interview_id` produces `interviewId` (lowercase `d`) — standard camelCase. But API_CONTRACT.md's actual documented response uses `interviewID` (capital `ID`), an inconsistency baked into the contract itself (the contract's own path parameter is `{interviewId}`, lowercase, while its response *body* field is capitalized). Since we were told to follow the contract exactly, we can't "fix" this inconsistency — we have to reproduce it. An explicit `Field(alias=...)` on that one field overrides the generator's default for just that field, without disturbing every other field's normal camelCase conversion.

*Where:* `backend/app/schemas/interview.py`

---

## Part 3 — Software Architecture & Design Patterns

### Q16. Describe the layered architecture (API → Business → Knowledge) we've built, and the dependency rule between the layers.

**Answer:** Three layers so far: the **API Layer** (`app/api/`) parses HTTP, validates shape, and translates domain exceptions into status codes; the **Business Layer** (`app/business/`) holds the actual interview lifecycle rules (`InterviewService`, `InterviewSession`, the status state machine); the **Knowledge Layer** (`app/knowledge/`) is a file-based lookup for content (interview questions), decoupled from how that content is used. The dependency rule is one-directional: **API depends on Business, Business depends on Knowledge — never the reverse.** Concretely: `app/business/interview_service.py` never imports anything from `app/api/` or `app/schemas/`; if you found such an import, that would be a layering violation, because it means the thing meant to be reusable/testable in isolation now silently requires a web framework to even import.

### Q17. Where exactly is Dependency Inversion applied, and what's the concrete payoff?

**Answer:** `InterviewService` doesn't construct its own `InMemorySessionStore`, `SequentialIdGenerator`, or `QuestionRepository` — it receives them as constructor parameters (`session_store`, `id_generator`, `question_repository`). The *wiring* — deciding which concrete class actually gets used — lives entirely in `app/api/dependencies.py`. The payoff isn't hypothetical: when we eventually replace `InMemorySessionStore` with a real database-backed store, `interview_service.py` doesn't change **at all** — only `dependencies.py`'s one function body changes, because `InterviewService` only ever depended on "something with a `save`/`get`/`transition_status` interface," not on "specifically an in-memory dict."

*Where:* `backend/app/api/dependencies.py`, `backend/app/business/interview_service.py`

### Q18. `InterviewSession` has zero FastAPI/Pydantic imports. Why is that a deliberate design goal, not an accident?

**Answer:** It means the entire business rule set — "an interview can't be started twice," "the question count is backend-controlled," the status state machine — can be exercised and unit-tested with plain Python objects, no test client, no running server, no HTTP layer at all. It also proves the business logic doesn't secretly *depend* on how it's exposed — if we added a CLI tool or a batch job that needed to configure interviews without going through HTTP, the business layer would already support that, because it was never coupled to FastAPI in the first place. This is the same reasoning CLAUDE.md states directly: "Business logic must remain independent of AI providers" — we generalized that principle one layer further, to independence from the web framework too.

### Q19. Why do the domain exceptions (`InterviewNotFoundError`, `InterviewAlreadyStartedError`) live in the Business Layer, but get translated to HTTP codes in the API Layer?

**Answer:** The business layer's job is to express *what went wrong* in domain terms — "this interview doesn't exist," "this interview is not in a state that allows this operation." Those concepts exist independent of HTTP. The *decision* that "not found" means status code 404 and "wrong state" means 409 is an HTTP/REST convention, not a business rule — a different transport (a CLI, a message queue consumer) would need a different mapping. Keeping the `try/except HTTPException` translation in `app/api/routes/interviews.py`, not inside `interview_service.py`, means the business layer stays reusable across transports and the mapping logic lives exactly once, in the layer whose whole job is "translate to HTTP."

*Where:* `backend/app/business/exceptions.py`, `backend/app/api/routes/interviews.py`

### Q20. The API schema's `InteractionMode`/`ExperienceLevel` enums are the *same* enum objects as the business layer's, imported rather than redefined — but we deliberately kept `SuccessResponse`/`ErrorResponse` and `InterviewSession` as two separate model types even though they overlap in fields like `status`. What's the actual rule here, and isn't reusing the enum a layering violation per Q16?

**Answer:** This is a nuanced one, and a good senior-level question to be asked back. The rule isn't "layers must never share *any* type" — it's "layers must not share types that would leak a framework dependency in the wrong direction." A plain `enum.Enum` is pure standard library; importing it into a Pydantic schema doesn't drag Pydantic into the business layer, because the import direction is schema → business, which is already the allowed direction (API depends on Business). Duplicating those enums would just be two vocabularies for one concept with no decoupling benefit, which is a real anti-pattern (violates "avoid unnecessary abstractions"). By contrast, `InterviewSession` (a dataclass, internal, may carry fields — like `current_question` — the API should never expose) and `InterviewConfigureData`/`StartInterviewData` (Pydantic, external, deliberately expose *fewer* fields than the domain model has) are different *shapes for different audiences* — collapsing them into one class would either leak internal state to the API response or force internal code to carry Pydantic validation overhead it doesn't need. The test to apply: "would sharing this type either leak internal data outward, or pull a framework dependency the wrong direction?" If yes, keep them separate. If it's genuinely the same concept with no such risk, share it.

### Q21. What is the Repository pattern, and how does `InMemorySessionStore` implement it?

**Answer:** The Repository pattern hides *how* data is stored behind a small interface expressing *what* operations are needed (`save`, `get`, `exists`, `transition_status`), so calling code depends on that interface, never on storage mechanics (a dict, a SQL table, a Redis hash). `InMemorySessionStore` is one implementation of that shape; nothing in `InterviewService` knows or cares that it's backed by a Python `dict` rather than Postgres. This is what makes the "swap in a real database later" claim in Q17 actually true rather than aspirational — the interface, not the implementation, is the contract the rest of the code relies on.

---

## Part 4 — Concurrency & Correctness

### Q22. What's a race condition, concretely, in the context of Start Interview?

**Answer:** Two nearly-simultaneous requests to start the *same* interview (a double-click, a client retry after a slow response it assumed failed). If "check the status is Configured" and "write the new status" were two separate operations, both requests could read "Configured" before either had written "In Progress" — both would then proceed to treat themselves as the legitimate first starter, both would generate a first question, and (worse, in a future step) both might increment counters or fire side effects meant to happen exactly once per interview.

### Q23. Why must the check and the write happen inside the *same* lock acquisition in `transition_status()`? What would go wrong with two separate locked calls — one to check, one to write?

**Answer:** This is the classic **TOCTOU bug** (time-of-check to time-of-use). If `is_configured(id)` and `set_status(id, IN_PROGRESS)` were two separate methods, each individually thread-safe, a second thread could acquire the lock and run *between* the first thread's check and its write — the first thread's decision ("it was Configured when I checked") would be stale by the time it acts on it. The fix is to make "check + write" a single atomic unit of work — one lock acquisition, one critical section — so no other thread can observe or modify state in between. That's exactly what `transition_status()` does: get, compare, and set all happen while holding `self._lock`, so the winner of the race is fully decided before the lock is released.

*Where:* `backend/app/business/session_store.py`

### Q24. How did we actually verify this works, rather than just trust the code?

**Answer:** We fired two `curl` requests at the *same* interview ID in the background simultaneously (`curl ... & curl ... & wait`) against a freshly configured (never-started) interview, and confirmed the real output: exactly one request got `200` with a generated question, the other got `409` reporting the interview was already `In Progress`. That's a genuine concurrency test, not a code-reading exercise — and it's a good habit to describe in an interview: "I don't just reason about thread safety, I reproduce the race with real concurrent requests and check the actual outcome."

---

## Part 5 — REST API Design & HTTP Semantics

### Q25. Why does Configure Interview return `201` but Start Interview returns `200`?

**Answer:** `201 Created` is the correct code specifically when a request **creates a new resource** — Configure Interview creates a brand-new interview session with a new ID. Start Interview modifies an *existing* resource's state (status, current question) without creating a new one, so `200 OK` is correct. This is a small but real signal of REST fluency: picking status codes based on what actually happened to the resource, not defaulting to `200` everywhere.

### Q26. Why `409 Conflict` — not `400 Bad Request` — when trying to start an interview that isn't `Configured`?

**Answer:** `400` means "the request itself is malformed or invalid" (bad JSON, wrong types, a value outside allowed bounds) — a problem with what the *client sent*. `409` means "the request is well-formed, but conflicts with the current state of the resource on the server" — the interview ID is valid, the request is empty as expected, but *this particular resource, right now,* can't accept this operation. That's precisely our situation: nothing is wrong with the request; the interview's current status just doesn't allow it.

### Q27. Is our Start Interview endpoint idempotent? Why does that matter?

**Answer:** No, and deliberately so. An idempotent operation produces the same *end state* no matter how many times it's repeated (e.g. `PUT /resource/5` with the same body twice leaves the resource identical either way). Calling Start Interview twice does **not** leave the same end state — the first call transitions `Configured → In Progress` and succeeds; the second call, hitting a resource that's no longer `Configured`, correctly fails with `409`. That's the right behavior for this specific action (starting is a one-time transition, not a "set this value" operation), but it's worth being able to say explicitly which HTTP verbs and endpoints in a system are and aren't idempotent — it directly affects whether a client is safe to blindly retry a request after a timeout.

### Q28. Why should error responses never include a raw stack trace to the client (per CLAUDE.md's Error Handling rule), and how did we enforce that?

**Answer:** Two reasons: security (a stack trace can leak file paths, internal package names, sometimes even fragments of data, to anyone probing the API) and stability of the contract (clients shouldn't be coupled to Python's internal exception representation, which can change on any refactor). We enforced it with a catch-all `@app.exception_handler(Exception)` in `main.py` that logs the full exception server-side (`logger.exception(...)`, which *does* capture the traceback, but only to our own logs) and returns a generic `"An unexpected error occurred"` message with `500` to the client — the two audiences (developer debugging via logs, and the client consuming the API) get different levels of detail, on purpose.

---

## Part 6 — Testing Mindset

### Q29. How would you unit test `InterviewService.start_interview` without running FastAPI or a real HTTP server at all?

**Answer:** Because the business layer has no FastAPI/Pydantic dependency (Q18), you can construct an `InterviewService` directly in a plain test function: instantiate a real `InMemorySessionStore`, a real `SequentialIdGenerator`, a real (or a small fake) `QuestionRepository`, wire them into `InterviewService(...)` by hand, call `configure_interview(...)` then `start_interview(...)`, and assert on the returned `InterviewSession`'s fields (`status == SessionStatus.IN_PROGRESS`, `current_question is not None`) and on the exceptions raised for the not-found/wrong-state cases. No `TestClient`, no running server — pure Python object construction and assertions, which is both faster and a stronger signal that the *business rule* is correct, independent of how it's exposed over HTTP.

### Q30. How would you turn our manual "fire two curl requests in parallel" concurrency check into an automated test?

**Answer:** Using Python's `threading` or `concurrent.futures.ThreadPoolExecutor`, spin up two threads that both call `interview_service.start_interview(same_id)` at (as close to) the same instant as possible, collect both results/exceptions, and assert that exactly one call succeeded and the other raised `InterviewAlreadyStartedError` — never "both succeeded" and never "both failed." Because `InMemorySessionStore`'s lock is real, this is a legitimate, deterministic-enough test of the exact race we manually verified with `curl`, and it would catch a regression (e.g. someone "simplifying" `transition_status` back into two separate locked calls) automatically in CI, without needing a live server.

---

## Quick-Fire Round

Short-answer versions of the above, useful for a fast self-check before an interview:

1. Why `str, Enum` and not just `Enum`? — *So members compare equal to plain strings and serialize as plain strings.*
2. Why dataclass for domain models, Pydantic for API schemas? — *Validation of untrusted input vs. lightweight internal data; keeps business layer framework-free.*
3. Why `default_factory` over a bare default for `datetime.now()`? — *Bare defaults evaluate once at class definition time, not per instance.*
4. Why `lru_cache` on dependency providers? — *Zero-argument function → one cache entry → same object every call → singleton.*
5. Why a `Lock` despite the GIL? — *GIL protects single operations, not multi-step check-then-write sequences (TOCTOU).*
6. Why override 422 with 400? — *Our contract specifies 400; FastAPI's framework default doesn't know our contract.*
7. Why register on `StarletteHTTPException`, not `fastapi.HTTPException`? — *Framework-raised errors (like 404 on an unmatched route) use the Starlette base class directly.*
8. Why sync `def`, not `async def`, for our routes? — *No actual I/O to await yet; FastAPI threadpools sync handlers automatically.*
9. Why 201 vs 200? — *201 = a new resource was created; 200 = an existing resource was read/modified.*
10. Why 409, not 400, for "already started"? — *400 = malformed request; 409 = valid request conflicting with current resource state.*
11. Why is `InterviewSession` framework-free? — *So business rules are testable and reusable without HTTP/Pydantic at all.*
12. Why do domain exceptions get translated to HTTP codes in the API layer, not the business layer? — *HTTP status codes are a transport-layer decision; the business layer should stay meaningful outside HTTP too.*
