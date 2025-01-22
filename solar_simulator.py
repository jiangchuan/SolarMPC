# Data source: https://pvwatts.nrel.gov/pvwatts.php
import numpy as np
import pandas as pd


class SolarProductionSimulator:
    def __init__(self, peak_production: float = 6.48):  # peak_production = 6.48 makes daily prod = 45 kWh
        self.peak_production = peak_production
        solar_data = pd.read_csv('data/input/solar_production_SD.csv')
        solar_data['mdh'] = solar_data.apply(lambda r: (r['Month'], r['Day'], r['Hour']), axis=1)
        self.mdh_prod = dict(zip(solar_data['mdh'], solar_data['AC System Output (W)'] / 1000))

    def simulate(self, month: int, day: int, hour: int) -> float:
        """
        Simulate solar production based on historical data for given day, month, and hour.
        
        Args:
            month: Month of the year (1-12)
            day: Day of the month (1-31)
            hour: Hour of the day (0-23)
            
        Returns:
            float: Solar production in kW
        """

        if (month, day, hour) in self.mdh_prod:
            base_production = self.mdh_prod[(month, day, hour)]
            return base_production

        if month == 2 and day == 29:
            return self.simulate(month, day - 1, hour)

        # Fall back to bell curve simulation if no date provided or data not found
        if 6 <= hour <= 18:
            hour_offset = hour - 12  # offset from noon
            # Bell curve formula
            production = self.peak_production * np.exp(-(hour_offset ** 2) / 16)
            return max(0, production)
        return 0.0
