import pandas as pd

# Load the CSV files
price_df = pd.read_csv('RCE_pazdziernik.txt', parse_dates=['time'])
amount_df = pd.read_csv('output.txt', parse_dates=['time'])

# Resample the price data to hourly intervals by averaging prices within each hour
# (Alternatively, you can use interpolation if needed)
price_df.set_index('time', inplace=True)
price_resampled = price_df.resample('H').mean()  # Resample to hourly and take the mean price

# Merge the resampled price data with the amount data on the time column
merged_df = pd.merge(amount_df, price_resampled, on='time', how='inner')

# Calculate the cost (price * amount)
merged_df['cost'] = merged_df['price'] * merged_df['amount'] / 1000
total_cost = merged_df['cost'].sum()
total_kwh = merged_df['amount'].sum()

# Save the result to a new CSV file
merged_df.to_csv('cost_output_per_hour.txt', index=False)

print("Cost calculation complete. Results saved to 'cost_output_per_hour.csv'.")
print(f"total kWh {total_kwh}")
print(f"total cost {total_cost}")