import pandas as pd
import numpy as np

# Load the data
file_path = "Data/output_data_with_time.csv"  # Replace with your file path
data = pd.read_csv(file_path)

# Check for the structure of your data
print(data.head())

# Assume columns are ['T', 'FHR', 'UC'] and we want to fix FHR
if 'FHR' not in data.columns:
    raise ValueError("FHR column not found in the data.")

# Replace zero or missing FHR values with NaN for interpolation
data['FHR'] = data['FHR'].replace(0, np.nan)

# Interpolate missing values (linear interpolation)
data['FHR'] = data['FHR'].interpolate(method='spline', order=3)

# Save the fixed data back to a file
output_file_path = "Data/spline interpolated data.csv"  # Replace with desired output file path
data.to_csv(output_file_path, index=False)

print(f"Interpolated data saved to {output_file_path}")