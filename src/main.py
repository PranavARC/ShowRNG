"""
Main entry point for ShowRNG.
"""

import argparse
import sys
from pathlib import Path

from replay_parser import extract_player_names, extract_turns
from event_finder import find_events
from rng_calculator import calculate_luck_percentiles

def main():
    """Executes the main logic of the ShowRNG application."""
    replay_html = read_replay_html()

    player_names = extract_player_names(replay_html)
    turns = extract_turns(replay_html)

    events = find_events(turns)
    percentiles = calculate_luck_percentiles(events)

    print(f"Player 1 aka {player_names[1]}'s luck percentile: {percentiles[1]}")
    print(f"Player 2 aka {player_names[2]}'s luck percentile: {percentiles[2]}")


def read_replay_html() -> str:
    """Parses the CLI arguments for the file path of the Showdown HTML replay file and reads it into a string."""
    parser = argparse.ArgumentParser(
        description = (
            "This application analyzes Pokémon Showdown .html replay files, and calculates each player's RNG percentile, "
            "where a percentile of 50.0 represents a player of average luck."
        )
    )
    parser.add_argument("path", type=str, help="Path to the Pokémon Showdown .html replay file.")

    args = parser.parse_args()
    replay_path = Path(args.path)

    if replay_path.suffix.lower() != ".html":
        print(f"Error: The provided file '{args.path}' does not have a .html extension.", file=sys.stderr)
        sys.exit(1)
    if not replay_path.is_file():
        print(f"Error: The file '{args.path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    with open(replay_path, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    main()
