import os
import xlrd

# Folder path containing .xls files
folder_path = "./odczyty"  # Replace with your folder path

# Open the output file in write mode
with open("output.txt", "w") as output_file:
    # Iterate through each file in the folder
    for filename in os.listdir(folder_path):
        # Check if the file is an .xls file
        if filename.endswith(".xls"):
            # Construct the full file path
            file_path = os.path.join(folder_path, filename)

            # Open the .xls file
            workbook = xlrd.open_workbook(file_path)
            sheet = workbook.sheet_by_index(0)  # Open the first sheet (index 0)

            # Iterate through each row of the sheet
            index = 0
            for row_idx in range(sheet.nrows):
                if index == 0:
                    index += 1
                    continue
                # Read column A (index 0) and column E (index 4)
                col_a_value = sheet.cell_value(row_idx, 0)
                col_e_value = sheet.cell_value(row_idx, 4)

                # Write the values to the output file, separated by a comma
                output_file.write(f"{col_a_value},{col_e_value}\n")

print("Data from all .xls files has been written to output.txt successfully.")