"""
AirQ Pollution Intelligence Module
Generates human-readable summaries and trend analysis deterministically.
"""

def generate_intelligence_summary(reading, historical_readings=None, alerts=None):
    """
    Generate a concise, deterministic summary of current pollution conditions.
    Does NOT use LLMs, relies strictly on logic and rules.
    """
    if not reading:
        return "Insufficient data to generate an intelligence summary."

    city = reading.get('city', 'Unknown City')
    aqi = reading.get('aqi')
    category = reading.get('aqi_category', 'Unknown')
    dominant = reading.get('dominant_pollutant')
    
    if aqi is None:
        return f"Current air quality data for {city} is incomplete. Cannot determine overall condition."

    # 1. Base statement
    summary = f"Air quality in {city} is currently {category.upper()} (AQI {aqi}). "

    # 2. Dominant pollutant context
    if dominant:
        dominant_val = reading.get('pollutants', {}).get(dominant, {}).get('value')
        unit = reading.get('pollutants', {}).get(dominant, {}).get('unit', '')
        summary += f"The primary pollutant is {dominant.upper()} at {dominant_val}{unit}. "
        
        if category in ['Poor', 'Very Poor', 'Severe']:
            summary += f"High levels of {dominant.upper()} can cause respiratory issues. "

    # 3. Trend analysis
    trend = "stable"
    if historical_readings and len(historical_readings) >= 6:
        # Compare last 3 hours vs previous 3 hours
        recent = [r['value'] for r in historical_readings[-3:] if r.get('value') is not None]
        previous = [r['value'] for r in historical_readings[-6:-3] if r.get('value') is not None]
        
        if len(recent) > 0 and len(previous) > 0:
            avg_recent = sum(recent) / len(recent)
            avg_prev = sum(previous) / len(previous)
            
            diff = avg_recent - avg_prev
            if diff > 10:
                trend = "worsening"
            elif diff < -10:
                trend = "improving"
                
        summary += f"Over the past few hours, conditions have been {trend}. "

    # 4. Alerts context
    if alerts:
        severe_alerts = [a for a in alerts if a.get('severity') == 'SEVERE']
        if severe_alerts:
            summary += "CRITICAL WARNING: Severe thresholds have been breached. Limit outdoor exposure."
        elif len(alerts) > 0:
            summary += f"There are {len(alerts)} active alerts for this location."
    
    # 5. Data source warning
    if reading.get('data_type') == 'SIMULATED':
        summary += " (Note: This analysis is based on SIMULATED IoT data.)"
    elif reading.get('data_type') == 'FALLBACK':
        summary += " (Note: This analysis is based on static FALLBACK data due to API unavailability.)"

    return summary

def get_trend_direction(historical_readings):
    """
    Determine simple trend direction from historical values.
    Returns: 'improving', 'worsening', or 'stable'
    """
    if not historical_readings or len(historical_readings) < 6:
        return 'unknown'
        
    recent = [r['value'] for r in historical_readings[-3:] if r.get('value') is not None]
    previous = [r['value'] for r in historical_readings[-6:-3] if r.get('value') is not None]
    
    if len(recent) == 0 or len(previous) == 0:
        return 'unknown'
        
    avg_recent = sum(recent) / len(recent)
    avg_prev = sum(previous) / len(previous)
    
    # Lower is better (improving)
    diff = avg_recent - avg_prev
    if diff > 5:
        return 'worsening'
    elif diff < -5:
        return 'improving'
    return 'stable'
