"""
Parser to read through a Pokémon Showdown replay .html file and extract info like turns, player names, etc.
"""

import re

def extract_player_names(replay_html: str) -> dict[int, str]:
    """
    Extracts the names of Player 1 and Player 2 from the Showdown HTML file.
    """
    # Regex to look for "|player|p1|<Name>| or |player|p2|<Name>|
    p1_match = re.search(r"\|player\|p1\|([^|]+)", replay_html)
    p2_match = re.search(r"\|player\|p2\|([^|]+)", replay_html)

    names = {
        1: p1_match.group(1) if p1_match else "P1",
        2: p2_match.group(1) if p2_match else "P2"
    }
    return names

def extract_turns(replay_html: str) -> tuple[str]:
    """
    Extracts a list of turns from the pipe-delimited
    battle protocol log within the Showdown HTML file.
    """
    # Search for all script blocks and look through them
    pattern = re.compile(r"<script[^>]*>(.*?)</script>", re.IGNORECASE | re.DOTALL)
    battle_log = ""
    for match in pattern.finditer(replay_html):
        script_content = match.group(1)
        # If the script block contains this, it belongs to the battle protocol
        if "|player|p1|" in script_content:
            battle_log = script_content.strip()
            break
    if not battle_log:
        raise ValueError("No valid Showdown battle log found in replay file.")

    # 1. End the log right before "|win|" or "|tie|"
    end_idx = max(battle_log.find("\n|win|"), battle_log.find("\n|tie|"))
    if end_idx != -1:
        battle_log = battle_log[:end_idx]

    # 2. Find where the first turn starts
    t1_match = re.search(r"^\|turn\|1", battle_log, re.MULTILINE)
    if t1_match:
        start_idx = t1_match.start()
    if start_idx == -1:
        raise ValueError("Could not find '|turn|1' in the battle log.")
    battle_body = battle_log[start_idx:]

    # 3. Divide the log into a list of turns by splitting at a newline followed by the turn marker, keeping the turn marker itself
    raw_turns = re.split(r'\n(?=\|turn\|\d+\b)', battle_body)

    # 4. Process the turns by removing white space, getting rid of preceding pipe characters, and removing turn numbers and timestamps
    processed_turns = []
    for turn_string in raw_turns:
        turn_string = turn_string.strip()
        if not turn_string:
            continue

        processed_lines = []
        for line in turn_string.splitlines():
            # 1. Remove the preceding pipe character "|" (each line should have it)
            if line.startswith("|"):
                line = line[1:]

            # 2. Remove lines starting with "turn|<number>" or "t:|<timestamp>"
            if line.startswith(("turn|", "t:|")):
                continue

            processed_lines.append(line)

        processed_turn = "\n".join(processed_lines).strip()
        if processed_turn:
            processed_turns.append(processed_turn)

    return tuple(processed_turns)
