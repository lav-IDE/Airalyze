'''
import pandas as pd

input_excel_file = 'data_raw/2025cpcb_mandir_marg.xlsx'  
output_csv_file = 'data_raw/2025_mandir_marg.csv'

df = pd.read_excel(input_excel_file, skiprows=10)

print("Preview of extracted data:")
print(df.head())

df.to_csv(output_csv_file, index=False)

print(f"\nSuccessfully converted! File saved as: {output_csv_file}")
'''

import pandas as pd


csv_2025 = 'data_raw/2025_mandir_marg.csv'  
csv_2026 = 'data_raw/2026_mandir_marg.csv' 
output_file = 'mandir_marg_cpcb.csv'

df_2025 = pd.read_csv(csv_2025)
df_2026 = pd.read_csv(csv_2026)

combined_df = pd.concat([df_2025, df_2026], ignore_index=True)

combined_df.to_csv(output_file, index=False)

print(f"Successfully combined the files! Saved as: {output_file}")
