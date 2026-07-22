"""Voice Service (Business Layer) - dummy Speech-to-Text.

Per ARCHITECTURE.md section 7(iii), Voice Service is a named Business
Layer component responsible for processing voice interactions. This is a
placeholder implementation only - no real Speech-to-Text model is
integrated here. It exists purely so a real implementation (e.g. backed
by Whisper, per ARCHITECTURE.md's Technology Stack) can be swapped in
later without touching InterviewService or the API layer.
"""

import logging

logger = logging.getLogger(__name__)


class VoiceService:
    """Converts a submitted audio reference into text.

    `audio_file` is treated as an opaque reference string (e.g. a
    filename), matching API_CONTRACT.md's literal request shape - this
    service does not receive or process raw audio bytes.
    """

    def transcribe(self, audio_file: str) -> str:
        """Return a dummy transcription for the given audio reference."""
        logger.info("Dummy transcription requested for audio_file=%s", audio_file)
        return (
            f"[Dummy transcription placeholder for audio file '{audio_file}']. "
            "This will be replaced by a real Speech-to-Text integration."
        )
