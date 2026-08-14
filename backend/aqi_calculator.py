"""
AQI calculator using India's National Ambient Air Quality Standards (NAAQs).
"""
from config import AQI_BREAKPOINTS, AQI_CATEGORIES


def _sub_index(pollutant, concentration):
    """
    Calculate sub-index for a single pollutant.
    Returns None if concentration is None or out of range.
    """
    if concentration is None:
        return None

    breakpoints = AQI_BREAKPOINTS.get(pollutant)
    if not breakpoints:
        return None

    for bp_lo, bp_hi, aqi_lo, aqi_hi in breakpoints:
        if bp_lo <= concentration <= bp_hi:
            aqi = ((aqi_hi - aqi_lo) / (bp_hi - bp_lo)) * (concentration - bp_lo) + aqi_lo
            return round(aqi)

    return None  # Out of range


def calculate_aqi(pollutant_values):
    """
    Calculate overall AQI from a dict of pollutant concentrations.

    pollutant_values: {'pm25': 65.3, 'pm10': 120.0, 'no2': None, ...}
    Returns: (aqi_value, aqi_category, dominant_pollutant) or (None, None, None)
    """
    sub_indices = {}
    for pollutant, conc in pollutant_values.items():
        if conc is not None:
            si = _sub_index(pollutant, conc)
            if si is not None:
                sub_indices[pollutant] = si

    if not sub_indices:
        return None, None, None

    # AQI is the maximum sub-index
    dominant = max(sub_indices, key=sub_indices.get)
    aqi = sub_indices[dominant]

    # Find category
    category = 'Unknown'
    for lo, hi, cat, _color in AQI_CATEGORIES:
        if lo <= aqi <= hi:
            category = cat
            break
    else:
        if aqi > 500:
            category = 'Severe'

    return aqi, category, dominant


def get_aqi_category(aqi):
    """Get category and colour for an AQI value."""
    if aqi is None:
        return None, None
    for lo, hi, cat, color in AQI_CATEGORIES:
        if lo <= aqi <= hi:
            return cat, color
    if aqi > 500:
        return 'Severe', '#7e0023'
    return None, None
