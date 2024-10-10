import requests
import json
import datetime

# Function to fetch JSON data from a URL and write specific values to a txt file
def fetch_json_and_write_specific_values(url, output_file):
    with open(output_file, 'w') as file:
        current_date = start_date
        file.write("time,price\n")
        while current_date <= end_date:
            data_collection = current_date.strftime("%Y-%m-%d")
            try:
                # Send a GET request to the provided URL
                response = requests.get(url+f"'{data_collection}'")

                # Raise an error if the request failed
                response.raise_for_status()

                # Parse the JSON content
                data = response.json()

                # Iterate over each item in the "value" list
                for item in data.get("value", []):
                    # Extract "udtczas" and "rce_pln" values
                    udtczas = item.get("udtczas", "")
                    udtczas_datetime = datetime.datetime.strptime(udtczas, '%Y-%m-%d %H:%M')
                    udtczas_datetime = udtczas_datetime - offset
                    udtczas = udtczas_datetime.strftime('%Y-%m-%d %H:%M')
                    rce_pln = item.get("rce_pln", "")

                    # Write the values separated by a comma to the file
                    file.write(f"{udtczas},{rce_pln}\n")

                print(f"Selected values have been written to {output_file}")

            except requests.exceptions.RequestException as e:
                print(f"Error fetching data from URL: {e}")
            except json.JSONDecodeError:
                print("Error decoding JSON response")

            current_date += delta



# Example usage
start_date = datetime.date(2024,10, 1)
end_date = datetime.date(2024,10, 11)
delta = datetime.timedelta(days=1)
offset = datetime.timedelta(minutes=15)
url = "https://api.raporty.pse.pl/api/rce-pln?$filter=business_date eq "  # Replace with your actual URL
output_file = 'RCE_pazdziernik.txt'  # Specify the output file
fetch_json_and_write_specific_values(url, output_file)
