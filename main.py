import os
import numpy as np
import pandas as pd
from price_forecast import PriceForecast
from solar_simulator import SolarProductionSimulator
from consumption_simulator import ConsumptionSimulator
from battery_system import BatterySystem
from smart_grid_mpc import SmartGridMPC
from config import mode, capacity, c_rate, min_battery_level, efficiency, ampacity, n_hour, horizon, use_battery

np.random.seed(1)

# Run simulation and analyze results
delta_hour = 24
charge_rate = capacity * c_rate
battery = BatterySystem(
    capacity=capacity,  # kWh
    max_charge_rate=charge_rate,  # kW
    max_discharge_rate=charge_rate,  # kW
    min_battery_level=min_battery_level,
    efficiency=efficiency
)

mpc_controller = SmartGridMPC(battery, ampacity=ampacity, horizon=horizon)

# Generate sample data
n_hour_pad = n_hour + horizon
times = pd.date_range('2024-01-01', periods=n_hour_pad, freq='h')
# times = pd.date_range('2024-09-01', periods=n_hour_pad, freq='h')

buy_prices = np.zeros(times.shape)
sell_prices = np.zeros(times.shape)
solar_production = np.zeros(times.shape)
consumption = np.zeros(times.shape)
price_forecast = PriceForecast()
solar_simulator = SolarProductionSimulator()
consumption_simulator = ConsumptionSimulator()
for i, t in enumerate(times):
    buy_prices[i] = price_forecast.get_buy_price(t.year, t.month, t.day, t.hour)
    sell_prices[i] = price_forecast.get_sell_price(t.month, t.hour)
    solar_production[i] = solar_simulator.simulate(t.month, t.day, t.hour)
    consumption[i] = consumption_simulator.simulate(t.month, t.day, t.hour)

adjust = 16176.58 / 13983.73
if mode == 'low_prod':
    adjust *= 0.9
elif mode == 'high_prod':
    adjust *= 1.1
solar_production *= adjust

# Initialize results DataFrame
results = pd.DataFrame({
    'time': times[:n_hour],
    'buy_price': buy_prices[:n_hour],
    'sell_price': sell_prices[:n_hour],
    'solar_production': solar_production[:n_hour],
    'consumption': consumption[:n_hour],
    'battery_action': np.nan,
    'grid_action': np.nan,
    'battery_soc': np.nan,
    'buying_cost': np.nan,
    'selling_revenue': np.nan
})

# Simulate system operation
for t in range(0, n_hour, delta_hour):
    if t % 24 == 0:
        print(f'MPC for day {t // 24 + 1}, {times[t]}')
    # Get predictions for the next horizon
    buy_price_pred = buy_prices[t:t + horizon]
    sell_price_pred = sell_prices[t:t + horizon]
    production_pred = solar_production[t:t + horizon]
    consumption_pred = consumption[t:t + horizon]

    # Pad predictions if needed
    input_length = len(buy_price_pred)
    if input_length < horizon:
        print(f'Pad: input_length < horizon: {input_length} < {horizon}')
        # Repeat the last value to fill the horizon
        pad_width = (0, horizon - input_length)
        buy_price_pred = np.pad(buy_price_pred, pad_width, 'edge')
        sell_price_pred = np.pad(sell_price_pred, pad_width, 'edge')
        production_pred = np.pad(production_pred, pad_width, 'edge')
        consumption_pred = np.pad(consumption_pred, pad_width, 'edge')

    # Get optimal actions
    battery_action, grid_action = mpc_controller.optimize(
        buy_price_pred,
        sell_price_pred,
        production_pred,
        consumption_pred
    )

    # Store the next delta_hour of actions (or remaining hours if less than delta_hour)
    steps_to_store = min(delta_hour, n_hour - t)
    for i in range(steps_to_store):
        ti = t + i

        # Store actions and states
        results.loc[ti, 'battery_action'] = battery_action[i]
        results.loc[ti, 'grid_action'] = grid_action[i]
        results.loc[ti, 'battery_soc'] = battery.soc

        # Calculate costs and revenues
        if grid_action[i] > 0:  # Buy
            results.loc[ti, 'buying_cost'] = grid_action[i] * buy_prices[ti]
            results.loc[ti, 'selling_revenue'] = 0
        else:  # Sell
            results.loc[ti, 'buying_cost'] = 0
            results.loc[ti, 'selling_revenue'] = -grid_action[i] * sell_prices[ti]

        # Update battery state
        if battery_action[i] > 0:  # Charging
            battery.soc += battery_action[i] * battery.efficiency
        else:  # Discharging
            battery.soc += battery_action[i] / battery.efficiency

        battery.soc = np.clip(battery.soc, 0, battery.capacity)

# Print summary statistics
print("\nSimulation Summary:")
print(f"Total Hours: {results.shape[0]}, Delta Hours: {delta_hour}")
print(f"Valid Results: {results['battery_action'].notna().sum()} hours")

# Calculate profits
results['income'] = results['selling_revenue'] - results['buying_cost']
results['cum_income'] = results['income'].cumsum()

results['consumption_cost'] = results['consumption'] * results['buy_price']
results['cum_consumption_cost'] = results['consumption_cost'].cumsum()
results['cum_solar_earn'] = results['cum_consumption_cost'] + results['cum_income']


def make_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir, exist_ok=True)


dir = f'data/output/{mode}'
make_dir(dir)
results.to_csv(f'{dir}/{mode}_{capacity if use_battery else 0}.csv', encoding='utf-8', index=False)

# Validity Check
arr = results[['solar_production', 'consumption', 'battery_action', 'grid_action', 'battery_soc']].values
for i in range(arr.shape[0]):
    p = arr[i, 0]
    c = arr[i, 1]
    charge = arr[i, 2]
    buy = arr[i, 3]
    soc1 = arr[i, 4]
    # print(f'balance check: {abs((c + charge) - (p + buy)) < 1e-6}')
    if not abs((c + charge) - (p + buy)) < 1e-6:
        print('balance check False')
    if i < arr.shape[0] - 1:
        soc = arr[i + 1, 4]
        if charge > 0:
            # print(f'charge check: {abs(soc - soc1 - charge * battery.efficiency) < 1e-6}')
            if not abs(soc - soc1 - charge * battery.efficiency) < 1e-6:
                print('charge check False')
        else:
            # print(f'charge check: {abs(soc - soc1 - charge / battery.efficiency) < 1e-6}')
            if not abs(soc - soc1 - charge / battery.efficiency) < 1e-6:
                print('charge check False')
