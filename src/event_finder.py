"""
Finder to scan through turn data and identify RNG-based events like misses, crits, and secondary effects.
NOTE: Currently only identifies hits/misses, and without factoring in accuracy/evasion buffs/debuffs
"""

from event import Event, EventType
from poke_env.data import GenData


def find_events(processed_turns: tuple[str]) -> tuple[Event]:
    """Scans through turn data to identify RNG-based events within each turn."""
    moves = GenData.from_gen(9).moves # For now, we only support Gen 9 replays
    events = []

    # Turn number is the turn's index in processed_turns plus 1 (0-based indexing)
    for turn_num, turn in enumerate(processed_turns, start = 1):
        steps = turn.splitlines()

        for step_idx, step in enumerate(steps):
            fields = step.split("|")

            if fields[0] == "move": # Ex. fields: ["move", "p1a: Glimmora", "Stealth Rock", "p2a: Camerupt"]
                if len(fields) < 3:
                    continue
                move_user = fields[1]    # p<1/2>a: <Name of Pokémon who used the move>
                move_name = fields[2]    # <Move Name>

                # Find the player from the second character of the move_user string, which should be 1 or 2 ("p1a... or "p2a...")
                if not move_user.startswith(("p1", "p2")):
                    continue
                player = int(move_user[1])

                # Convert the move name into its move_id for lookup by removing special characters, spaces, and punctuation, and keeping it lowercase
                move_id = "".join(c for c in move_name if c.isalnum()).lower()
                move_data = moves.get(move_id)
                if move_data is None:
                    continue

                accuracy = move_data.get("accuracy")
                # Skip events where accuracy is non-numeric (either True or an irregular value), a hundred percent (100) or zero percent (0)
                # Note: If accuracy=100, the move can miss due to accuracy debuffs or evasion buffs, but if accuracy=True, the move will never miss
                if type(accuracy) not in (int, float) or accuracy in (0, 100):
                    continue
                base_chance = accuracy / 100.0

                # Check the next step to see if the move missed
                success = 1
                if step_idx + 1 < len(steps):
                    next_step = steps[step_idx + 1]
                    if next_step.startswith("-miss|"):
                        success = 0

                events.append(
                    Event(
                        EventType.ATTACK,
                        turn_num,
                        player,
                        base_chance,    # TODO: Factor in accuracy/evasion buffs/debuffs, go from base_chance to chance
                        success
                    )
                )

    return tuple(events)
