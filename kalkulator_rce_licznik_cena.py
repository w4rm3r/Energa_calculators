import pandas as pd

# Load the CSV files
price_df = pd.read_csv('ceny_rce/2024_12_RCE_grudzien.txt', parse_dates=['time'])
amount_df = pd.read_csv('shelly_odczyty/2024_em_data_combined_sorted.csv', parse_dates=['time'])

# Resample the price data to hourly intervals by averaging prices within each hour
# (Alternatively, you can use interpolation if needed)
price_df.set_index('time', inplace=True)
price_resampled = price_df.resample('H').mean()  # Resample to hourly and take the mean price
amount_df.set_index('time', inplace=True)
amount_resampled = amount_df.resample('H').sum()

# Merge the resampled price data with the amount data on the time column
merged_df = pd.merge(amount_resampled, price_resampled, on='time', how='inner')

# Calculate the cost (price * amount)
markup_net = 0.0878
merged_df['cost'] = (merged_df['price'] / 1000 + markup_net) * merged_df['power'] / 1000 * 1.23
total_cost = merged_df['cost'].sum()
total_kwh = merged_df['power'].sum()

# Save the result to a new CSV file
merged_df.to_csv('cost_output_per_hour.txt', index=False)

print("Cost calculation complete. Results saved to 'cost_output_per_hour.csv'.")
print(f"total kWh {total_kwh/1000}")
print(f"total cost {total_cost}")
przesyl_G12R_noc_net = 0.0870
cena_noc_G12R = 0.4731 + przesyl_G12R_noc_net * 1.23
print(f"total cost G12R {total_kwh / 1000 * cena_noc_G12R}")