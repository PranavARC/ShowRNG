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

def calculate_luck_percentiles(events: tuple[Event]) -> dict[int, float]:
    """Calculates the luck percentiles for both players based on the provided event list."""
    if not events:
        return DEFAULT_PERCENTILES.copy()

    # Load a DataFrame with the relevant event details
    df = pd.DataFrame([{
        'player': event.player,
        'chance': event.chance,
        'success': event.success
    } for event in events])

    # For each event:
    df['luck_delta'] = df['success'] - df['chance'] # Calculate the difference between actual and expected luck
    df['variance'] = df['chance'] * (1 - df['chance']) # Calculate the degree of how much the outcome can vary

    # Sum up the variance of all the events, and if there was none, assign each player average luck
    total_variance = df['variance'].sum()
    if total_variance <= 0:
        return DEFAULT_PERCENTILES.copy()

    # Sum up the luck deltas for both players, and compute how much luckier Player 1 was than Player 2
    p1_delta = df[df['player'] == 1]['luck_delta'].sum()
    p2_delta = df[df['player'] == 2]['luck_delta'].sum()
    net_luck = p1_delta - p2_delta

    # Calculate the z-score to find how far this net luck is from the average
    std_dev = np.sqrt(total_variance)
    z_score = net_luck / std_dev

    # Use a cumulative distribution function to represent the probability that a random player would be less luckier than Player 1
    # P2 would be 100 - P1, since we're considering luck to be relative (aka a good event for Player 1 is a bad one for Player 2)
    luck_percentile = norm.cdf(z_score) * 100
    return {1: round(luck_percentile, 2), 2: round(100 - luck_percentile, 2)}
