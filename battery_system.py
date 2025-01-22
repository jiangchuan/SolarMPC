class BatterySystem:
    def __init__(self, capacity, max_charge_rate, max_discharge_rate, min_battery_level=0.2, efficiency=0.95):
        self.capacity = capacity  # kWh
        self.safe_level = capacity * min_battery_level  # kWh
        self.max_charge_rate = max_charge_rate  # kW
        self.max_discharge_rate = max_discharge_rate  # kW
        self.efficiency = efficiency  # Battery round-trip efficiency
        self.soc = 0.5 * capacity  # Initialize at 50% capacity
