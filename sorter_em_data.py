from datetime import datetime, timedelta
import csv

import pandas as pd


def sort():
    for phase in {"A", "B", "C"}:
        file_name = f"2024_em_data_{phase}"
        file_extention = ".csv"
        file_to_be_sorted = f"{file_name}{file_extention}"
        file_sorted = f"{file_name}_sorted{file_extention}"
        path = "shelly_odczyty/"

        with open(f'{path}{file_to_be_sorted}', mode='r') as pobor_mocy_plik:
            lines = pobor_mocy_plik.readlines()

        lines[0] = "time,power,b\n"

        with open(f'{path}{file_to_be_sorted}', mode='w') as pobor_mocy_plik:
            pobor_mocy_plik.writelines(lines)

        with open(f'{path}{file_to_be_sorted}', mode='r') as pobor_mocy_plik:
            pobor_mocy_csv = csv.DictReader(pobor_mocy_plik)
            data = [row for row in pobor_mocy_csv]

        date_format = '%Y-%m-%d %H:%M'

        for row in data:
            row['date'] = datetime.strptime(row['date'], date_format)

        data.sort(key=lambda x: x['date'])

        with open(f'{path}{file_sorted}', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
            writer.writeheader()
            for row in data:
                row['date'] = row['date'].strftime(date_format)
                writer.writerow(row)


def combine():
    df1 = pd.read_csv("shelly_odczyty/2024_em_data_A_sorted.csv")
    df2 = pd.read_csv("shelly_odczyty/2024_em_data_B_sorted.csv")
    df3 = pd.read_csv("shelly_odczyty/2024_em_data_C_sorted.csv")

    combined_df = (
        pd.concat([df1, df2, df3])
        .fillna(0)
        .groupby('time', as_index=False)
        .sum()
    )

    combined_df.to_csv("shelly_odczyty/2024_em_data_combined_sorted.csv", index=False)


# sort()
combine()

