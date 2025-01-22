import numpy as np
import pandas as pd
from config import mode, use_battery, capacity, n_day_figure
import matplotlib.pyplot as plt

if not use_battery:
    capacity = 0
results = pd.read_csv(f'data/output/{mode}/{mode}_{capacity}.csv')
results = results.head(24 * n_day_figure)
results['time'] = pd.to_datetime(results['time'])
total_production = results['solar_production'].sum()
total_consumption = results['consumption'].sum()

print(f"\nFinancial Summary:")
print(f"Battery Capacity: {capacity} kWh")
print(f"Total Production: {results['solar_production'].sum():.2f}")
print(f"Total Consumption: {results['consumption'].sum():.2f}")
print(f"Need to buy = ${(total_consumption - total_production) * results['buy_price'].max():.2f}")
print(f"Total Buying Cost: ${results['buying_cost'].sum():.2f}")
print(f"Total Selling Revenue: ${results['selling_revenue'].sum():.2f}")
print(f"Net Income: ${results['income'].sum():.2f}")
print(f"Solar Earn: ${results['cum_solar_earn'].iloc[-1]:.2f}")
print(f"Average Hourly Income: ${results['income'].mean():.3f}")


def get_daily_mean(arr):
    n = len(arr)
    marr = np.zeros(n)
    for i in range(0, n, 24):
        marr[i:i + 24] = np.mean(arr[i:i + 24])
    return marr


# Visualize results including profit
default_blue = '#1f77b4'
dark_orange = '#cc5500'
fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(6, 1, figsize=(28.4, 16))

# Plot prices
ax1.plot(results['time'], results['buy_price'], label='Buy Price')
ax1.plot(results['time'], results['sell_price'], label='Sell Price')
ax1.set_ylabel('Price ($/kWh)')
ax1.legend(loc='upper left')

# Plot power flows
ax2.plot(results['time'], results['solar_production'], label='Solar Production', color='green')
ax2.plot(results['time'], results['consumption'], label='Consumption', color='orange')
ax2.plot(results['time'], get_daily_mean(results['solar_production'].values), label='Avg Solar Production',
         color='darkgreen',
         linewidth=2)
ax2.plot(results['time'], get_daily_mean(results['consumption'].values), label='Avg Consumption', color=dark_orange,
         linewidth=2)
ax2.fill_between(results['time'], results['solar_production'], 0, color='yellow', alpha=0.2)
ax2.fill_between(results['time'], results['consumption'], 0, color='red', alpha=0.2)
ax2.set_ylabel('Power (kW)')
ax2.legend(loc='upper left')

# Plot actions
ax3.plot(results['time'], results['battery_action'], label='Battery Charge (+) / Discharge (-)')
ax3.plot(results['time'], results['grid_action'], label='Purchase (+) / Sell (-) from the grid')
ax3.set_ylabel('Power (kW)')
ax3.axhline(y=0, color='k', linestyle='-', alpha=0.2)
ax3.legend(loc='upper left')

# Plot battery SOC
if capacity == 0:
    ax4.plot(results['time'], np.zeros(len(results['time'])), label='Battery SOC')
else:
    ax4.plot(results['time'], results['battery_soc'], label='Battery SOC')
ax4.set_ylabel('State of Charge (kWh)')
ax4.legend(loc='upper left')

# Plot income
ax5.plot(results['time'], results['income'], label='Surplus and Shortfall to Grid', color=default_blue)
ax5.fill_between(results['time'], results['income'], 0, where=(results['income'] >= 0), color='green', alpha=0.3)
ax5.fill_between(results['time'], results['income'], 0, where=(results['income'] <= 0), color='red', alpha=0.3)
ax5.set_ylabel('$')
ax5.axhline(y=0, color='k', linestyle='-', alpha=0.2)
ax5.legend(loc='upper left')

# Plot cumulative earn, cost, and income
ax6.plot(results['time'], results['cum_solar_earn'], color='green')
ax6.plot(results['time'], results['cum_consumption_cost'], color='orange')
label = 'Cumulative Solar + Battery Value' if use_battery else 'Cumulative Solar Value'
ax6.fill_between(results['time'], results['cum_solar_earn'], 0, color='green', alpha=0.2, label=label)
ax6.fill_between(results['time'], results['cum_consumption_cost'], 0, color='red', alpha=0.2,
                 label='Cumulative Consumption')
ax6.set_ylabel('$')
ax6.axhline(y=0, color='k', linestyle='-', alpha=0.2)
ax6.legend(loc='upper left')

plt.tight_layout()
plt.show()
plt.savefig(f'figure/{mode}_{capacity}.png')
