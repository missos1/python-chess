"""
Shared pytest configuration and fixtures.

Initialises a headless pygame session before any test modules are imported
so that piece constructors (which call pygame.image.load) can run without
a real display.
"""

import os
import pytest

# Must be set before pygame is imported by any module.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402  (imported after env-var setup on purpose)

pygame.init()
pygame.display.set_mode((800, 800))


# ---------------------------------------------------------------------------
# Session-level fixture – keeps the pygame subsystem alive for all tests.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def _pygame_session():
    yield
    pygame.quit()


# ---------------------------------------------------------------------------
# Board factories – used across multiple test modules.
# ---------------------------------------------------------------------------

@pytest.fixture
def board():
    """Return a freshly initialised Board in the standard starting position."""
    from data.classes.Board import Board
    return Board(800, 800)


@pytest.fixture
def empty_board():
    """Return a Board with all squares cleared of pieces."""
    from data.classes.Board import Board
    b = Board(800, 800)
    for sq in b.squares:
        sq.occupying_piece = None
    return b
