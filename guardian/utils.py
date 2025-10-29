"""
Shared utility functions for GuardianNav
Consolidates common operations to avoid code duplication
"""
from typing import Tuple
from math import radians, cos, sin, asin, sqrt
from functools import lru_cache


# Cache for frequently used calculations
@lru_cache(maxsize=1024)
def haversine(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Calculate the distance in meters between two GPS points using the Haversine formula.
    Results are cached for performance.
    
    Args:
        coord1: (latitude, longitude) of first point
        coord2: (latitude, longitude) of second point
        
    Returns:
        Distance in meters
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371000  # Earth radius in meters
    
    return c * r


def format_message_efficiently(*parts: str) -> str:
    """
    Efficiently concatenate message parts using join instead of += operations
    
    Args:
        *parts: Message parts to concatenate
        
    Returns:
        Concatenated message
    """
    return '\n'.join(filter(None, parts))
