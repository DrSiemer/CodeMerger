import logging
from src.api_parts.starter_api_session import StarterApiSession
from src.api_parts.starter_api_prompts import StarterApiPrompts
from src.api_parts.starter_api_parsing import StarterApiParsing
from src.api_parts.starter_api_scaffold import StarterApiScaffold

log = logging.getLogger("CodeMerger")

class StarterApi(
    StarterApiSession,
    StarterApiPrompts,
    StarterApiParsing,
    StarterApiScaffold
):
    """API methods concerning the comprehensive Project Starter feature pipeline."""

    def test(self):
        """A simple test method to verify the Vue -> Python bridge is working."""
        log.info("API test method called from Vue frontend.")
        return "Hello from Python API! The bridge is working perfectly."