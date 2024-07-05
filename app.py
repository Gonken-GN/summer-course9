import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from flask import Flask, render_template, jsonify

year = 2020

data_dir = 'data'
file_path = os.path.join(data_dir, 'data_2020.xlsx')

if not os.path.exists(file_path):
    raise FileNotFoundError(f'File {file_path} not found.')

try:
    data = pd.read_excel(file_path, header=1)
except Exception as e:
    raise Exception(f'Error reading file: {str(e)}')

# Preprocess the data
data.rename(columns={
    'Tahun': 'Year',
    'Provinsi': 'Province',
    'Kabupaten/Kota': 'City',
    'Timbulan Sampah Harian(ton)': 'Daily Waste (tons)',
    'Timbulan Sampah Tahunan(ton)': 'Annual Waste (tons)'
}, inplace=True)

province_to_analyze = ['DKI Jakarta', 'Jawa Barat']
# data = data[data['Province'].isin(province_to_analyze)]
# Analysis

# 1. Total annual waste generation in each province in 2020
annual_waste = data.groupby(['Province', 'Year'])['Annual Waste (tons)'].sum().reset_index()

# (Since we only have one year, this is the same as total annual waste for that year)
average_annual_waste = annual_waste.groupby('Province')['Annual Waste (tons)'].mean().reset_index()

# 3. Province with the most and least annual waste generation in 2020
most_waste = annual_waste.loc[annual_waste['Annual Waste (tons)'].idxmax()].reset_index(drop=True)
least_waste = annual_waste.loc[annual_waste['Annual Waste (tons)'].idxmin()].reset_index(drop=True)

def categorize_province(row):
    if row['Annual Waste (tons)'] <= 100000:
        return 'GREEN'
    if row['Annual Waste (tons)'] <= 700000:
        return 'Orange'
    else:
        return 'RED'
    

average_annual_waste['Category'] = average_annual_waste.apply(categorize_province, axis=1)
# 5. Graph of the total annual amount of waste in each province from year to year
plt.figure(figsize=(14, 7))
sns.lineplot(data=annual_waste, x='Year', y='Annual Waste (tons)', hue='Province', marker='o')
plt.title('Total Annual Amount of Waste in Each Province from Year to Year')
plt.xlabel('Year')
plt.ylabel('Waste (tons)')
plt.legend(title='Province')
plt.grid(True)
plt.savefig('static/annual_waste_trend.png')

# 6. Categorized visualization of average annual waste generation
plt.figure(figsize=(14, 7))
sns.countplot(data=average_annual_waste, x='Category', palette={'GREEN': 'green', 'Orange': 'orange', 'RED': 'red'})
plt.title('Categorization of Average Annual Waste Generation in Each Province for All Years', fontsize=16, fontweight='bold')
plt.xlabel('Category', fontsize=14)
plt.ylabel('Number of Provinces', fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.savefig('static/average_annual_waste_category.png')



app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data/annual_waste')
def get_annual_waste():
    return jsonify(annual_waste.to_dict(orient='records'))

@app.route('/data/average_annual_waste')
def get_average_annual_waste():
    return jsonify(average_annual_waste.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)