import numpy as np
from scipy.optimize import minimize
from config import use_battery


class SmartGridMPC:
    def __init__(self, battery, ampacity, horizon=24):
        self.battery = battery
        self.ampacity = ampacity
        self.horizon = horizon

    def decode_actions(self, x):
        """Decode the optimization vector into battery and grid actions."""
        battery_actions = x[:self.horizon]  # charge (+), discharge (-)
        grid_actions = x[self.horizon:]  # buy (+), sell (-)
        return battery_actions, grid_actions

    def objective_function(self, x, buy_prices, sell_prices, solar_production, consumption):
        """
        Calculate the negative profit over the prediction horizon.
        We use negative profit because scipy.minimize minimizes the objective.

        Profit = Revenue from selling - Cost of buying
        """
        battery_actions, grid_actions = self.decode_actions(x)

        total_profit = 0
        soc = self.battery.soc

        for t in range(self.horizon):
            # Calculate profit from grid actions
            if grid_actions[t] > 0:  # Buying (cost)
                total_profit -= grid_actions[t] * buy_prices[t]
            else:  # Selling (revenue)
                total_profit -= grid_actions[t] * sell_prices[t]

            # Update battery state
            if battery_actions[t] > 0:  # Charging
                soc += battery_actions[t] * self.battery.efficiency
            else:  # Discharging
                soc += battery_actions[t] / self.battery.efficiency

        return -total_profit  # Return negative profit for minimization

    def constraints(self, x, solar_production, consumption):
        """Generate constraints for the optimization problem."""
        constraints = []

        for t in range(self.horizon):
            # SOC minimum constraint: SOC ≥ safe_level
            constraints.append({
                'type': 'ineq',
                'fun': lambda x, t=t: self._calculate_soc_at_time(x, t + 1) - self.battery.safe_level
            })

            # SOC maximum constraint: SOC ≤ capacity
            constraints.append({
                'type': 'ineq',
                'fun': lambda x, t=t: self.battery.capacity - self._calculate_soc_at_time(x, t + 1)
            })

            # Power balance constraint: consumption = solar_production - battery_charge + grid_buy
            constraints.append({
                'type': 'eq',
                'fun': lambda x, t=t: consumption[t] - (solar_production[t] - x[t] + x[t + self.horizon])
            })

        return constraints

    def _calculate_soc_at_time(self, x, t):
        """Helper function to calculate SOC at any time t based on actions x"""
        battery_actions = x[:self.horizon]
        soc = self.battery.soc

        for i in range(t):
            if battery_actions[i] > 0:  # Charging
                soc += battery_actions[i] * self.battery.efficiency
            else:  # Discharging
                soc += battery_actions[i] / self.battery.efficiency

        return soc

    def optimize(self, buy_prices, sell_prices, solar_production, consumption):
        """
        Optimize battery and grid actions over the prediction horizon.

        Returns:
            Tuple of (battery_actions, grid_actions)
        """
        # Initial guess: no battery action and grid meets net demandbound
        x0 = np.zeros(2 * self.horizon)  # [battery_actions, grid_actions]

        # Set initial grid actions to meet net demand
        x0[self.horizon:] = consumption - solar_production

        # Bounds for actions
        if use_battery:
            battery_action_bounds = [(-self.battery.max_discharge_rate, self.battery.max_charge_rate) for _ in
                                     range(self.horizon)]
        else:
            battery_action_bounds = [(0, 0) for _ in range(self.horizon)]

        # Grid bounds - assume we can buy/sell up to the maximum consumption
        max_buy_grid_power = min(self.ampacity, np.mean(consumption) + self.battery.max_charge_rate)  # buy
        max_sell_grid_power = min(self.ampacity, np.mean(solar_production) + self.battery.max_discharge_rate)  # sell
        # max_buy_grid_power = min(self.ampacity, self.battery.max_charge_rate)  # buy
        # max_sell_grid_power = min(self.ampacity, self.battery.max_discharge_rate)  # sell
        grid_action_bounds = [(-max_sell_grid_power, max_buy_grid_power) for _ in range(self.horizon)]

        bounds = battery_action_bounds + grid_action_bounds

        # Optimize
        result = minimize(
            fun=self.objective_function,
            x0=x0,
            args=(buy_prices, sell_prices, solar_production, consumption),
            bounds=bounds,
            constraints=self.constraints(x0, solar_production, consumption),
            method='SLSQP',
            options={'maxiter': 500}
        )

        if not result.success:
            print(f"Optimization failed: {result.message}")

        return self.decode_actions(result.x)
