"""
Calculator to process identified luck events and
determine the luck percentiles for both players
"""

import pandas as pd
import numpy as np
from scipy.stats import norm

from event import Event

# Constant default percentiles of 50.0 for each player, aka average
DEFAULT_PERCENTILES = {1: 50.0, 2: 50.0}

def calculate_luck_percentiles(events: tuple[Event], relative=False) -> dict[int, float]:
    """Calculates the luck percentiles for both players based on the provided event list."""
    if not events:
        return DEFAULT_PERCENTILES.copy()

    player_stats = pd.DataFrame(events).groupby('player').apply(lambda g: pd.Series({
        'luck_delta': (g['success'] - g['chance']).sum(),   # luck_delta = the difference between actual and expected luck
        'variance': (g['chance'] * (1 - g['chance'])).sum()
    }))

    results = {}
    for p_id in (1, 2):
        # Since we default to considering individual luck, take the player's total variance and luck_delta
        variance = player_stats.loc[p_id, 'variance']
        luck_delta = player_stats.loc[p_id, 'luck_delta']

        # If we consider relative luck, aka that bad events to the opponent count as good events to the player:
        # - The new variance would sum up that of every event that occurred
        # - The new luck delta would be the player's minus everyone else's since opponent's luck = player's negative luck
        if relative:
            variance = player_stats['variance'].sum()
            luck_delta = net_value = 2 * player_stats.loc[p_id, 'luck_delta'] - player_stats['luck_delta'].sum()

        # Handle players with zero variance
        if variance <= 0:
            results[p_id] = DEFAULT_PERCENTILES[1]
            continue

        # Calculate the z-score to find how far this net luck is from the average
        std_dev = np.sqrt(variance)
        z_score = luck_delta / std_dev

        # Use a cumulative distribution function to represent the probability
        # that a random player would be less luckier than this player
        results[p_id] = round(norm.cdf(z_score) * 100, 2)

    return results
