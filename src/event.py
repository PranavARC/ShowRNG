"""
Models for representing Pokémon Showdown RNG events.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Literal


class EventType(Enum):
    ATTACK = "attack"
    CRITICAL = "critical"
    SECONDARY = "secondary"
    IMMOBILIZE = "immobilize"
    MULTI_HIT = "multi-hit"
    MULTI_BLOCK = "multi-block"


@dataclass(frozen=True)
class Event:
    """Represents a specific RNG event that occurred during a turn."""
    event_type: EventType
    turn_num: int

    # The player who triggered the event by:
    # attempting an attack (ATTACK, CRITICAL, SECONDARY, MULTI_HIT)
    # attempting to move under a immobilizing status condition (IMMOBILIZE)
    # attempting to block a move consecutively (MULTI_BLOCK)
    player: Literal[1, 2]

    chance: float
    success: Literal[0, 1]  # Used integers instead of booleans to assist in calculations

    def __post_init__(self):
        """Validates event turn numbering and base chance range after instantiation."""
        if self.turn_num <= 0:
            raise ValueError("turn number must be 1 or more.")
        if not 0.0 < self.chance < 1.0:
            raise ValueError("base_chance must be between 0.0 and 1.0 (non-inclusive).")

    def __str__(self):
        """Returns a string representation of the RNG event including its type and result."""
        return (
            f"event_type: {self.event_type.value}\n"
            f"turn_num: {self.turn_num}\n"
            f"player: {self.player}\n"
            f"chance: {self.chance}\n"
            f"success: {self.success == 1}"
        )
