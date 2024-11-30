import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from dotenv import load_dotenv
load_dotenv()


SITES = ["466970572", ""]


class GAFetch:
    def __init__(self):
        self.data = None
        self.ga_service_account = os.getenv("GA_SERVICE_ACCOUNT")
        if not self.ga_service_account:
            raise ValueError("GA_SERVICE_ACCOUNT is not set in .env file")

    async def fetch(self):
        self.data = "GA data"

        return {"id": "ga-232342", "data": self.data}

    def get_data(self):
        return self.data    
    
    def sample_run_report(self, property_id):
        if not property_id:
            raise ValueError("property_id is required")
        
        """Runs a simple report on a Google Analytics 4 property."""  
        # assumes GOOGLE_APPLICATION_CREDENTIALS environment variable.
        client = BetaAnalyticsDataClient()

        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="city")],
            metrics=[Metric(name="activeUsers")],
            date_ranges=[DateRange(start_date="2024-08-01", end_date="today")],
        )
        response = client.run_report(request)

        print("Report result:")
        for row in response.rows:
            print(row.dimension_values[0].value, row.metric_values[0].value)



import asyncio

if __name__ == '__main__':
    async def main():
        print("GA FETCH - START")
        ga_fetch = GAFetch()
        result = await ga_fetch.fetch()
        print(result)
        
        site_id = SITES[0]
        print(f"Loading data for site_id {site_id}")

        ga_fetch.sample_run_report(site_id)

        print("GA FETCH - END")

    asyncio.run(main())