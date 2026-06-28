"""Setup entry point (Gmail OAuth now; full onboarding in Epic 10)."""

# Implements FR-001

import logging

from app.services import gmail

logger = logging.getLogger(__name__)


def main() -> None:
    gmail.authorize()
    logger.info("Gmail authorized successfully.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

