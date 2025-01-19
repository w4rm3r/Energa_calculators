from datetime import datetime, time, timedelta, date
import csv
import pandas as pd
import math

start_date = datetime(2024, 8, 1, 14, 0, 0)
end_date = datetime(2024, 8, 30, 13, 0, 0)
dni_wolne = [date(2024, 4, 1), date(2024, 5, 1), date(2024, 5, 3)]
przesyl_G12R_dzien_net = 0.359
przesyl_G12R_noc_net = 0.0870
cena_dzien = 0.6212 + 0.4707 * 1.23
cena_noc = 0.6159 + 0.1017 * 1.23
cena_dzien_G12R = 0.6212 + przesyl_G12R_dzien_net * 1.23
cena_noc_G12R = 0.4731 + przesyl_G12R_noc_net * 1.23
cena_g11 = 0.6212 + 0.4267 * 1.23
transmisja_noc = przesyl_G12R_noc_net * 1.23 * 1000
transmisja_dzien = przesyl_G12R_dzien_net * 1.23 * 1000
markup_net = 0.0878
cost_night = 0.0
cost_day = 0.0
cost_night_G12R = 0.0
cost_day_G12R = 0.0
cost_alternative = 0.0
cost_dynamic = 0.0
night_start_time = time(21, 50)
night_start_time_G12R = time(21, 50)
night_end_time = time(6, 0)
night_end_time_G12R = time(7, 0)
night_start_time_day = time(12, 50)
night_end_time_day = time(15, 00)
night_start_time_day_G12R = time(12, 50)
night_end_time_day_G12R = time(16, 00)
total_use = 0.0
total_use1 = 0.0
total_use_day = 0.0
total_use_night = 0.0
total_use_day_G12R = 0.0
total_use_night_G12R = 0.0
total_discharge_energy = 0.0
total_discharge_earnings = 0.0

grid_max_power = 10500.0
battery_grid_charging = 7000.0
battery_capacity = 30000.0
battery_charge = 30000.0
battery_minimum = 3000.0
battery_max_power = 10000.0
battery_to_grid = 3700.0
projected_sell_energy = 0.0
charge_in_next_hours = 12
days_below_G12R_prices = 0
game_over = False
visible_prices_gross = []
visible_prices_RCE = []
buy_decisions = [False] * 34
current_time = start_date
time_index = 0
price_update_time = time(hour=14, minute=0, second=0)


def create_decision_list(reevaluate=False):
    global visible_prices_gross
    global buy_decisions
    global cena_noc_G12R
    global battery_capacity
    global battery_charge
    global battery_grid_charging
    global time_index
    global charge_in_next_hours
    global days_below_G12R_prices

    if not reevaluate:
        hour_counter = 0
        for i in visible_prices_gross[10:]:
            if i < cena_noc_G12R * 1000:
                hour_counter += 1
            if hour_counter > 6:
                days_below_G12R_prices += 1
                break
        buy_decisions = [False] * 34
        sorted_visible_prices = sorted(visible_prices_gross)
        charge_cycles_needed = math.ceil((battery_capacity - battery_charge - count_sell_in_future()) / battery_grid_charging)
        sorted_visible_prices_to_use = sorted_visible_prices[:charge_cycles_needed]
        for price, index in zip(visible_prices_gross, range(len(buy_decisions))):
            if price in sorted_visible_prices_to_use:
                buy_decisions[index] = True

    if reevaluate:
        charge_in_next_hours = math.ceil((battery_charge / battery_capacity) * 17)
        if battery_charge < 10000:
            charge_in_next_hours = 5
        if battery_charge < 5000:
            charge_in_next_hours = 2
        print(f"battery charge in {charge_in_next_hours}")
        sorted_visible_prices = sorted(visible_prices_gross[time_index:time_index+charge_in_next_hours])
        charge_cycles_needed = math.ceil(
            (battery_capacity - battery_charge - count_sell_in_future() * battery_to_grid) / battery_grid_charging / 2)
        sorted_visible_prices_to_use = sorted_visible_prices[:charge_cycles_needed]
        for price, index in zip(visible_prices_gross, range(len(sorted_visible_prices))):
            if price in sorted_visible_prices_to_use:
                buy_decisions[index + time_index] = True
        print(f"Decision updated matrix {buy_decisions}")


def decide_charge():
    return True


def decide_discharge():
    return True


def decide_sell_now(current_price):
    if current_price > 1000:
        return True
    else:
        return False


def count_sell_in_future():
    global visible_prices_RCE
    global projected_sell_energy
    global battery_to_grid
    result = 0
    for price in visible_prices_RCE:
        if price > 900:
            projected_sell_energy += battery_to_grid
            result += battery_to_grid
    return result


def sell(price):
    global total_discharge_energy
    global total_discharge_earnings
    global battery_charge
    global battery_to_grid
    global game_over
    global battery_minimum
    total_discharge_energy += battery_to_grid / 1000
    total_discharge_earnings += price / 1000 * battery_to_grid / 1000
    battery_charge -= battery_to_grid
    if battery_charge < battery_minimum:
        game_over = True
        total_discharge_energy -= battery_minimum / 1000 - battery_charge / 1000
        total_discharge_earnings -= price / 1000 * (battery_minimum - battery_charge) / 1000
        battery_charge = battery_minimum


def discharge(energy, price):
    global battery_charge
    global battery_to_grid
    global game_over
    global battery_minimum
    global cost_dynamic
    global cena_noc_G12R
    if price < cena_noc_G12R * 1000 - 250:
        use_grid(price, energy, False)
        return
    battery_charge -= energy
    if battery_charge < battery_minimum:
        game_over = True
        cost_dynamic += price / 1000 * (battery_minimum - battery_charge) / 1000 * 1.23
        battery_charge = battery_minimum


def use_grid(price, energy, charge=True):
    global cost_dynamic
    global battery_charge
    global battery_grid_charging
    cost_dynamic += price / 1000 * energy / 1000 * 1.23
    if charge:
        battery_charge += battery_grid_charging
        cost_dynamic += price / 1000 * battery_grid_charging / 1000 * 1.23
        if battery_charge > battery_capacity:
            cost_dynamic -= (battery_charge - battery_capacity) / 1000 * price / 1000 * 1.23
            battery_charge = battery_capacity


def update_prices(ceny_rynkowe):
    global current_time
    global visible_prices_gross
    global projected_sell_energy
    global visible_prices_RCE
    projected_sell_energy = 0
    matching_row = ceny_rynkowe[ceny_rynkowe.index == current_time]
    start_index = matching_row.index[0]
    visible_prices_gross = ceny_rynkowe['price'][start_index:start_index + pd.Timedelta(hours=33)].tolist()
    visible_prices_RCE = visible_prices_gross.copy()
    visible_prices_gross[0] = (visible_prices_gross[0] + markup_net + przesyl_G12R_noc_net) * 1.23
    visible_prices_gross[1] = (visible_prices_gross[1] + markup_net + przesyl_G12R_noc_net) * 1.23
    for i in range(2, 7):
        visible_prices_gross[i] = (visible_prices_gross[i] + markup_net + przesyl_G12R_dzien_net) * 1.23
    for i in range(7, 16):
        visible_prices_gross[i] = (visible_prices_gross[i] + markup_net + przesyl_G12R_noc_net) * 1.23
    for i in range(16, 22):
        visible_prices_gross[i] = (visible_prices_gross[i] + markup_net + przesyl_G12R_dzien_net) * 1.23
    for i in range(22, 25):
        visible_prices_gross[i] = (visible_prices_gross[i] + markup_net + przesyl_G12R_noc_net) * 1.23
    for i in range(25, 31):
        visible_prices_gross[i] = (visible_prices_gross[i] + markup_net + przesyl_G12R_dzien_net) * 1.23
    visible_prices_gross[31] = (visible_prices_gross[31] + markup_net + przesyl_G12R_noc_net) * 1.23
    visible_prices_gross[32] = (visible_prices_gross[32] + markup_net + przesyl_G12R_noc_net) * 1.23


def simulate():
    global total_use
    global current_time
    global visible_prices_gross
    global time_index
    global buy_decisions
    global game_over
    global battery_charge
    global total_discharge_energy
    global total_discharge_earnings
    global days_below_G12R_prices
    pobor_mocy_csv = pd.read_csv('shelly_odczyty/2024_em_data_combined_sorted.csv', parse_dates=['time'])
    ceny_rynkowe_csv = pd.read_csv('ceny_rce/2024_08_RCE_sierpien.txt', parse_dates=['time'])
    pobor_mocy_csv.set_index('time', inplace=True)
    ceny_rynkowe_csv.set_index('time', inplace=True)
    pobor_mocy_csv = pobor_mocy_csv.resample('H').sum()
    ceny_rynkowe_csv = ceny_rynkowe_csv.resample('H').mean()
    for index, row in pobor_mocy_csv.iterrows():
        line_datetime = index.to_pydatetime()
        current_time = line_datetime
        if line_datetime < start_date:
            continue
        if line_datetime > end_date:
            break
        total_use += float(row["power"])
        if time_index == 0 or time_index == 24:
            time_index = 0
            update_prices(ceny_rynkowe_csv)
            create_decision_list()
            print(f"Current prices {visible_prices_gross}")
            print(f"Decision matrix {buy_decisions}")
        # aa = visible_prices_RCE[time_index]
        # aaa = datetime(2024, 12, 4, 16, 0, 0)
        # if line_datetime == aaa:
        #     asd = 1
        # if aa > 1000.0:
        #     asd = 2
        # if battery_charge < battery_capacity / 2:
        #     create_decision_list(True)
        if decide_sell_now(visible_prices_RCE[time_index]):
            sell(visible_prices_RCE[time_index])
        elif buy_decisions[time_index]:
            use_grid(visible_prices_gross[time_index], float(row["power"]))
        else:
            discharge(float(row["power"]), visible_prices_gross[time_index])
        time_index += 1

        print(f"Current Time: {current_time}")

        print(f"Battery charge {battery_charge}")
        print(f"Total use: {total_use/1000} kWh")
        print(f"Dynamic cost: {cost_dynamic} PLN")
        print(f"G12R cost: {total_use/1000 * cena_noc_G12R}")
        print(f"Total discharged energy: {total_discharge_energy}")
        print(f"Total discharged ernings: {total_discharge_earnings}")
        print(f"Days with low prices: {days_below_G12R_prices}")
        print(f"Game over: {game_over}")






simulate()











