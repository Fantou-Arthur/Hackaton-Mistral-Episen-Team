import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Metric, Dimension, RunReportRequest

USE_LIVE = os.getenv("USE_LIVE", "false").lower() == "true"
GA4_PROPERTY_ID = os.getenv("GA4_PROPERTY_ID")

async def sessions_report():
    """Retourne le nombre de sessions sur les 7 derniers jours (GA4)."""
    if not USE_LIVE:
        # --- Mock mode ---
        return "GA4 (mock) → 1243 sessions sur les 7 derniers jours."

    try:
        client = BetaAnalyticsDataClient()
        request = RunReportRequest(
            property=f"properties/{GA4_PROPERTY_ID}",
            dimensions=[Dimension(name="date")],
            metrics=[Metric(name="sessions")],
            date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
        )
        response = client.run_report(request)
        total_sessions = sum(int(row.metric_values[0].value) for row in response.rows)
        return f"GA4 → {total_sessions} sessions sur les 7 derniers jours."
    except Exception as e:
        return f"Erreur GA4 API: {e}"
