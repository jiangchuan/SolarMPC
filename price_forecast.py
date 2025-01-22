# Buy price data source: https://www.sdge.com/residential/pricing-plans/about-our-pricing-plans/whenmatters
from datetime import date


class PriceForecast:
    def __init__(self):
        self.buy_prices_weekdays = {'Super Off-Peak': 0.376, 'Off-Peak': 0.394, 'On-Peak': 0.456}
        self.buy_prices_weekends = {'Super Off-Peak': 0.481, 'Off-Peak': 0.499, 'On-Peak': 0.561}

        # Sell prices (24 hours x 12 months) from SCE 2024 Average Export Compensation
        self.sell_prices = [
            #  Jan    Feb    Mar    Apr    May    Jun    Jul    Aug    Sep    Oct    Nov    Dec      Hour
            [0.057, 0.053, 0.054, 0.046, 0.058, 0.055, 0.057, 0.057, 0.056, 0.055, 0.050, 0.056],  # 00:00
            [0.057, 0.053, 0.054, 0.036, 0.051, 0.051, 0.053, 0.055, 0.052, 0.050, 0.049, 0.056],  # 01:00
            [0.058, 0.052, 0.055, 0.034, 0.048, 0.051, 0.052, 0.054, 0.051, 0.050, 0.048, 0.056],  # 02:00
            [0.057, 0.052, 0.053, 0.034, 0.045, 0.051, 0.051, 0.054, 0.051, 0.049, 0.048, 0.056],  # 03:00
            [0.056, 0.052, 0.053, 0.035, 0.047, 0.052, 0.051, 0.053, 0.050, 0.049, 0.048, 0.056],  # 04:00
            [0.056, 0.053, 0.054, 0.037, 0.051, 0.052, 0.051, 0.054, 0.050, 0.049, 0.049, 0.057],  # 05:00
            [0.061, 0.059, 0.057, 0.038, 0.051, 0.053, 0.053, 0.054, 0.053, 0.050, 0.052, 0.058],  # 06:00
            [0.064, 0.060, 0.055, 0.031, 0.029, 0.049, 0.051, 0.055, 0.053, 0.053, 0.049, 0.061],  # 07:00
            [0.063, 0.047, 0.040, 0.013, 0.023, 0.047, 0.052, 0.059, 0.050, 0.049, 0.050, 0.061],  # 08:00
            [0.060, 0.045, 0.034, 0.011, 0.023, 0.050, 0.055, 0.063, 0.052, 0.050, 0.051, 0.062],  # 09:00
            [0.059, 0.043, 0.032, 0.010, 0.022, 0.051, 0.055, 0.063, 0.053, 0.050, 0.050, 0.060],  # 10:00
            [0.058, 0.042, 0.032, 0.010, 0.022, 0.051, 0.055, 0.062, 0.053, 0.051, 0.051, 0.058],  # 11:00
            [0.056, 0.040, 0.030, 0.011, 0.021, 0.051, 0.055, 0.062, 0.054, 0.051, 0.051, 0.058],  # 12:00
            [0.056, 0.041, 0.028, 0.010, 0.020, 0.053, 0.065, 0.076, 0.060, 0.056, 0.053, 0.057],  # 13:00
            [0.056, 0.043, 0.028, 0.009, 0.019, 0.069, 0.076, 0.111, 0.070, 0.057, 0.055, 0.057],  # 14:00
            [0.057, 0.046, 0.029, 0.005, 0.017, 0.080, 0.096, 0.139, 0.077, 0.069, 0.060, 0.059],  # 15:00
            [0.066, 0.063, 0.033, 0.006, 0.018, 0.096, 0.113, 0.148, 0.083, 0.079, 0.063, 0.062],  # 16:00
            [0.070, 0.071, 0.055, 0.015, 0.032, 0.097, 0.131, 0.243, 0.097, 0.095, 0.062, 0.067],  # 17:00
            [0.072, 0.070, 0.070, 0.049, 0.064, 0.092, 0.118, 0.397, 3.240, 0.076, 0.062, 0.069],  # 18:00
            [0.073, 0.070, 0.072, 0.048, 0.060, 0.081, 0.331, 0.985, 3.640, 0.062, 0.063, 0.070],  # 19:00
            [0.072, 0.071, 0.070, 0.048, 0.062, 0.076, 0.155, 0.356, 0.189, 0.061, 0.062, 0.068],  # 20:00
            [0.070, 0.069, 0.069, 0.048, 0.060, 0.072, 0.076, 0.464, 0.071, 0.062, 0.060, 0.063],  # 21:00
            [0.063, 0.062, 0.064, 0.043, 0.058, 0.069, 0.072, 0.357, 0.064, 0.058, 0.054, 0.059],  # 22:00
            [0.058, 0.057, 0.058, 0.044, 0.059, 0.062, 0.060, 0.061, 0.056, 0.053, 0.052, 0.058],  # 23:00
        ]

    def _get_buy_price_weekdays(self, hour: int) -> float:
        if hour < 6:
            return self.buy_prices_weekdays['Super Off-Peak']
        if hour < 10:
            return self.buy_prices_weekdays['Off-Peak']
        if hour < 14:
            return self.buy_prices_weekdays['Super Off-Peak']
        if hour < 16:
            return self.buy_prices_weekdays['Off-Peak']
        if hour < 21:
            return self.buy_prices_weekdays['On-Peak']
        return self.buy_prices_weekdays['Off-Peak']

    def _get_buy_price_weekends(self, hour: int) -> float:
        if hour < 14:
            return self.buy_prices_weekends['Super Off-Peak']
        if hour < 16:
            return self.buy_prices_weekends['Off-Peak']
        if hour < 21:
            return self.buy_prices_weekends['On-Peak']
        return self.buy_prices_weekends['Off-Peak']

    def get_daily_prices(self, month: int) -> list[float]:
        """Get prices for a specific month (1-12)"""
        return [hour_prices[month - 1] for hour_prices in self.sell_prices]

    def get_buy_price(self, year: int, month: int, day: int, hour: int) -> float:
        current_date = date(year, month, day)
        weekday = current_date.weekday()  # 0 = Monday, 6 = Sunday
        if weekday < 5:  # Weekday
            return self._get_buy_price_weekdays(hour)
        else:  # Weekend
            return self._get_buy_price_weekends(hour)

    def get_sell_price(self, month: int, hour: int) -> float:
        """Get price for specific hour (0-23) and month (1-12)"""
        return self.sell_prices[hour][month - 1]
