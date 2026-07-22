"""Question Generation Service (Knowledge Layer) - dummy follow-up questions.

Generates interview questions 2 and onward during Submit Answer.
Deliberately independent of app.knowledge.question_repository.
QuestionRepository, which remains exclusively responsible for Start
Interview's first question - the two are different concerns (a static
per-role/level lookup vs. a per-question-number follow-up), and keeping
them separate avoids touching Start Interview's existing, tested code.

This holds a small set of generic, clearly-placeholder templates rather
than a hand-authored bank of role-specific questions for every question
number - a real question bank of that depth isn't the point of this
placeholder, since it will be replaced wholesale by AI-generated
questions once the AI Gateway exists.
"""

import logging

from app.business.models import ExperienceLevel

logger = logging.getLogger(__name__)

_FOLLOW_UP_TEMPLATES = [
    "Can you share an example from your experience as a {role} where you had to make a difficult technical trade-off?",
    "How do you stay current with new developments relevant to a {role} role, and how have you applied something new recently?",
    "Describe a time you had to communicate a complex technical idea to a non-technical stakeholder.",
    "What's a mistake you made in a past project, and what did you learn from it?",
    "How do you approach mentoring or supporting less experienced colleagues on your team?",
    "Looking ahead, what do you see as the biggest challenge facing someone in a {role} role over the next few years?",
]


class QuestionGenerationService:
    """Generates the next dummy interview question given the session's context."""

    def generate_next_question(
        self,
        *,
        role: str,
        experience_level: ExperienceLevel,
        question_number: int,
    ) -> str:
        """Return a placeholder follow-up question for `question_number` (>= 2).

        `experience_level` is accepted (and logged) even though the dummy
        templates don't vary by it yet, so the method signature already
        matches what a real AI-backed generator will need.
        """
        template_index = (question_number - 2) % len(_FOLLOW_UP_TEMPLATES)
        question = _FOLLOW_UP_TEMPLATES[template_index].format(role=role)
        logger.info(
            "Dummy next question generated: question_number=%s experience_level=%s",
            question_number,
            experience_level.value,
        )
        return question
