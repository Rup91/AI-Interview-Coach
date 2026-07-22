"""Evaluation Service (Business Layer) - dummy answer evaluation.

Per ARCHITECTURE.md section 7(iii), Evaluation Service is a named
Business Layer component responsible for evaluating candidate responses
and generating feedback. This is a placeholder implementation only: the
underlying scoring signal is answer length (word count), since no LLM is
integrated yet. The generated text references multiple evaluation
facets (knowledge, clarity, communication, proactiveness, vision) so the
*shape* of the output already matches what a real AI Gateway-backed
evaluator will eventually produce - only the scoring mechanism itself is
a stand-in, and is expected to be replaced wholesale later.
"""

import logging

from app.business.models import EvaluationResult

logger = logging.getLogger(__name__)

_IDEAL_ANSWER_TEMPLATE = (
    "A strong answer would clearly explain the underlying concept, walk through "
    "the reasoning step by step, connect it to a concrete real-world example, and "
    "discuss relevant trade-offs."
)


class EvaluationService:
    """Produces a dummy score, feedback, and ideal answer for one submitted answer."""

    def evaluate(self, *, question: str, answer: str) -> EvaluationResult:
        """Evaluate `answer` against `question` using placeholder logic."""
        word_count = len(answer.split())

        if word_count == 0:
            score = 1
            feedback = "No answer was provided, so knowledge of the topic could not be demonstrated."
            strengths: list[str] = []
            improvement_areas = [
                "Attempt an answer, even a partial one, rather than leaving it blank",
                "Demonstrate basic knowledge of the topic",
                "Communicate your reasoning, even if incomplete",
            ]
        elif word_count < 10:
            score = 3
            feedback = "The answer is too brief to demonstrate clear understanding or communication."
            strengths = ["Attempted a direct response to the question"]
            improvement_areas = [
                "Expand on the reasoning behind your answer",
                "Demonstrate deeper knowledge of the topic",
                "Communicate the broader vision or impact of your approach",
            ]
        elif word_count < 30:
            score = 6
            feedback = "The answer shows a reasonable understanding of the topic with adequate explanation."
            strengths = [
                "Clear understanding of the core concept",
                "Communicates the idea in a structured way",
            ]
            improvement_areas = [
                "Add a concrete real-world example",
                "Discuss trade-offs or alternative approaches",
                "Show more proactive thinking about edge cases",
            ]
        else:
            score = 9
            feedback = "The answer is thorough, well-communicated, and demonstrates strong command of the topic."
            strengths = [
                "Deep knowledge of the topic",
                "Clear and structured communication",
                "Proactively addresses edge cases and trade-offs",
                "Demonstrates strategic vision beyond the immediate question",
            ]
            improvement_areas = ["Consider being more concise while retaining the depth of detail"]

        logger.info(
            "Dummy evaluation: word_count=%s score=%s",
            word_count,
            score,
        )

        return EvaluationResult(
            question=question,
            answer=answer,
            score=score,
            strengths=strengths,
            improvement_areas=improvement_areas,
            feedback=feedback,
            ideal_answer=_IDEAL_ANSWER_TEMPLATE,
        )
