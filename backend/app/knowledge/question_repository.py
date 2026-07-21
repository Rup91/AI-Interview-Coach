"""Interview Question Repository (Knowledge Layer).

File-based repository of interview questions, per ARCHITECTURE.md's
Knowledge Layer component and Technology Stack ("File-based Repository
(JSON/Markdown)"). This holds placeholder/dummy content only - no AI
provider is called from here or anywhere in this module.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Tuple

from app.business.models import ExperienceLevel

logger = logging.getLogger(__name__)

_DEFAULT_DATA_PATH = Path(__file__).resolve().parent / "data" / "first_questions.json"


class QuestionRepository:
    """Looks up a dummy first interview question by role and experience level.

    The data file path is resolved relative to this module's own location
    (not the process's working directory), since it is a bundled data
    asset shipped with the code - unlike .env, it must resolve the same
    way regardless of where the server process is launched from.
    """

    def __init__(self, data_path: Path = _DEFAULT_DATA_PATH) -> None:
        self._roles, self._default = self._load(data_path)

    @staticmethod
    def _load(data_path: Path) -> Tuple[Dict[str, Dict[str, str]], Dict[str, str]]:
        with data_path.open(encoding="utf-8") as file:
            raw = json.load(file)
        # Role keys are normalized to lowercase so lookups are case-insensitive,
        # since "role" is free text supplied by the client, not a fixed enum.
        roles = {role.strip().lower(): levels for role, levels in raw.get("roles", {}).items()}
        default = raw.get("default", {})
        return roles, default

    def get_first_question(self, role: str, experience_level: ExperienceLevel) -> str:
        """Return the dummy first question for the given role and experience level.

        Falls back to a generic, experience-level-appropriate question if
        the role isn't one of the predefined ones, so an unrecognized role
        string never results in a failure to produce a question.
        """
        level_map = self._roles.get(role.strip().lower(), self._default)
        question = level_map.get(experience_level.value) or self._default.get(experience_level.value)
        if question is None:
            raise ValueError(
                f"No dummy question configured for experience level '{experience_level.value}'"
            )
        return question
