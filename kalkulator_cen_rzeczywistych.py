from datetime import datetime, time, timedelta, date
import csv

start_date = datetime(2024, 12, 1, 14, 0, 0)
end_date = datetime(2024, 12, 31, 23, 0, 0)
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

grid_max_power = 10500
grid_charging = 5000
battery_capacity = 30000
battery_charge = 30000
battery_minimum = 3000
game_over = False
visible_prices_gross = []


with open('em_data_C_sorted.csv', mode='r') as pobor_mocy_plik:
    with open('PL_CENY_RYN_03_2024.csv', mode='r') as ceny_rynkowe_plik:
        pobor_mocy_csv = csv.DictReader(pobor_mocy_plik)
        ceny_rynkowe_csv = csv.DictReader(ceny_rynkowe_plik)

        last_datetime = datetime(2024, 2, 1, 0, 0, 0)
        start_count_datetime = start_date
        pobor_mocy_liczona_godzina = 0
        interval = timedelta(hours=1)
        interval_correction = timedelta(minutes=10)
        current_hour_cost = 0.0
        ceny_rynkowe_list = list(ceny_rynkowe_csv)
        ceny_rynkowe_counter = 0

        for pobor_mocy_line in pobor_mocy_csv:
            line_datetime = datetime.strptime(pobor_mocy_line["date"], '%Y-%m-%d %H:%M')
            if line_datetime < start_date:
                continue
            if line_datetime > end_date:
                break
            total_use += float(pobor_mocy_line["power"])
            if start_count_datetime + interval < line_datetime and pobor_mocy_liczona_godzina != 0.0:
                current_hour_cost = float(ceny_rynkowe_list[0]["cost"])
                ceny_rynkowe_counter += 1
                if (line_datetime.weekday() == 5 or line_datetime.weekday() == 6 or line_datetime.date() in dni_wolne or night_start_time < start_count_datetime.time() or start_count_datetime.time() < night_end_time or night_start_time_day < start_count_datetime.time() < night_end_time_day):
                    cost_night += float(pobor_mocy_liczona_godzina) * cena_noc
                    total_use_night += float(pobor_mocy_liczona_godzina)
                    cost_alternative += float(pobor_mocy_liczona_godzina) * (current_hour_cost + transmisja_noc)
                else:
                    cost_day += float(pobor_mocy_liczona_godzina) * cena_dzien
                    total_use_day += float(pobor_mocy_liczona_godzina)
                    cost_alternative += float(pobor_mocy_liczona_godzina) * (current_hour_cost + transmisja_dzien)
                if (night_start_time_G12R < start_count_datetime.time() or start_count_datetime.time() < night_end_time_G12R or night_start_time_day_G12R < start_count_datetime.time() < night_end_time_day_G12R):
                    cost_night_G12R += float(pobor_mocy_liczona_godzina) * cena_noc_G12R
                    total_use_night_G12R += float(pobor_mocy_liczona_godzina)
                else:
                    cost_day_G12R += float(pobor_mocy_liczona_godzina) * cena_dzien_G12R
                    total_use_day_G12R += float(pobor_mocy_liczona_godzina)
                start_count_datetime = line_datetime - interval_correction
                total_use1 += pobor_mocy_liczona_godzina
                pobor_mocy_liczona_godzina = float(pobor_mocy_line["power"])
            else:
                pobor_mocy_liczona_godzina += float(pobor_mocy_line["power"])

cost_day /= 1000
cost_night /= 1000
cost_day_G12R /= 1000
cost_night_G12R /= 1000
cost_alternative /= 1000000
cost_alternative *= 1.23
total_use /= 1000
total_use1 /= 1000
total_use_day /= 1000
total_use_night /= 1000
total_cost_g11 = total_use * cena_g11

print(f"koszt dzien: {cost_day}")
print(f"koszt noc: {cost_night}")
print(f"koszt dzien G12R: {cost_day_G12R}")
print(f"koszt noc G12R: {cost_night_G12R}")
print(f"koszt calosc normalnie: {cost_day + cost_night}")
print(f"koszt calosc po staremu: {total_use_day * (0.5038 + 0.2823) * 1.23 + total_use_night * (0.3278 + 0.0595) * 1.23}")
print(f"wzrost kosztu: {(cost_day + cost_night) / (total_use_day * (0.5038 + 0.2823) * 1.23 + total_use_night * (0.3278 + 0.0595) * 1.23)}")
print(f"koszt calosc G12R: {cost_day_G12R + cost_night_G12R}")
print(f"koszt G11: {total_cost_g11}")
print(f"koszt diff normal vs G11: {total_cost_g11 - cost_night - cost_day}")
print(f"koszt diff normal vs G12R: {cost_night + cost_day - cost_night_G12R - cost_day_G12R}")
print(f"koszt alternatywny: {cost_alternative}")
print(f"calkowite zuzycie: {total_use} kWh")
print(f"calkowite zuzycie zliczane godzinami: {total_use1} kWh")
print(f"calkowite zuzycie dzien: {total_use_day} kWh")
print(f"calkowite zuzycie noc: {total_use_night} kWh")




