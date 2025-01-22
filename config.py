# mode = 'low_prod'  # total production = 0.9 total consumption
mode = 'mid_prod'  # total production = total consumption
# mode = 'high_prod'  # total production = 1.1 total consumption

consumption_mode = 'base'

# Time setting
n_day = 366  # number of days to simulate
n_day_figure = 7  # number of days to plot
n_hour = n_day * 24
horizon = 24

# Battery
use_battery = True  # whether to use battery
n_battery = 2  # number of batteries
single_capacity = 13.5  # kWh
capacity = n_battery * single_capacity  # kWh
c_rate = 0.5
min_battery_level = 0.2
efficiency = 0.95

ampacity = 12  # kW

tariff = 1  # Grid feed-in tariff
