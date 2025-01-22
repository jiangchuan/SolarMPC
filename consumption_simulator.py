# Data source: https://catalog.data.gov/dataset/commercial-and-residential-hourly-load-profiles-for-all-tmy3-locations-in-the-united-state-bbc75
import numpy as np
import pandas as pd


class ConsumptionSimulator:
    def __init__(self, mode='base'):
        self.base_load = 0.3  # Base load (always-on appliances)
        self.mode = mode
        df = self.pre_process(mode=self.mode)
        df[['date', 'time']] = df['Date/Time'].str.split('  ', n=1, expand=True)
        df[['month', 'day']] = df['date'].str.split('/', expand=True)
        df[['hour', 'minute', 'second']] = df['time'].str.split(':', expand=True)
        df['mdh'] = df.apply(lambda r: (int(r['month']), int(r['day']), int(r['hour']) - 1), axis=1)
        self.mdh_consumption = dict(zip(df['mdh'], df['consumption']))

    def pre_process(self, mode='base'):
        df = pd.read_csv(f'data/input/consumption_SD_Montgomery_{mode}.csv')
        vals = ['Electricity:Facility [kW](Hourly)', 'Heating:Electricity [kW](Hourly)',
                'Cooling:Electricity [kW](Hourly)', 'HVACFan:Fans:Electricity [kW](Hourly)',
                'General:InteriorLights:Electricity [kW](Hourly)', 'General:ExteriorLights:Electricity [kW](Hourly)',
                'Appl:InteriorEquipment:Electricity [kW](Hourly)', 'Misc:InteriorEquipment:Electricity [kW](Hourly)']
        cols = ['Date/Time'] + vals
        df = df[cols]
        df['consumption'] = df[vals].sum(axis=1)
        print(f"Average daily consumption for {mode}: {np.sum(df['consumption']) / 365:.1f}")
        return df[['Date/Time', 'consumption']]

    def simulate(self, month: int, day: int, hour: int) -> float:
        """Simulate home energy consumption based on time of day"""

        if (month, day, hour) in self.mdh_consumption:
            return self.mdh_consumption[(month, day, hour)]

        if month == 2 and day == 29:
            return self.simulate(month, day - 1, hour)

        # Morning peak (7-9 AM): breakfast, getting ready
        if 7 <= hour <= 9:
            return self.base_load + 1.5

        # Evening peak (17-22): dinner, TV, lights, etc.
        elif 17 <= hour <= 22:
            return self.base_load + 2.0

        # Mid-day (10-16): moderate usage
        elif 10 <= hour <= 16:
            return self.base_load + 0.8

        # Night time (23-6): low usage
        else:
            return self.base_load + 0.2
