import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

def display_dfs(dfs):
	for name, df in dfs.items():
		print(name.replace("_", " ").title()+":")
		print(df.iloc[:10, [0, 1, -3, -2, -1]])

# Load the datasets into a dictionary of DataFrames
dfs = {}
for file in os.listdir('hans_rosling'):
	name = file.split('.')[0]
	dfs[name] = pd.read_csv('hans_rosling/' + file)


# DO NOT RUN! Code to reformat initial life_expectancy.csv

# dfs['life_expectancy'] = dfs['life_expectancy'].pivot_table(
#     index=['Entity', 'Code'], 
#     columns='Year', 
#     values='Life expectancy (years)'
# ).reset_index()


# dfs['life_expectancy'] = dfs['life_expectancy'].rename(columns={
#     'Entity': 'Country Name', 
#     'Code': 'Country Code'
# })

# dfs['life_expectancy'].columns.name = None
# dfs['life_expectancy'].columns = [str(col) if isinstance(col, int) else col for col in dfs['life_expectancy'].columns]

# dfs['life_expectancy'].drop(columns=dfs['life_expectancy'].loc[:, '1543':'1959'].columns)

# dfs['life_expectancy'].to_csv('hans_rosling/life_expectancy.csv', index=False)

years = [str(year) for year in range(1990, 2019)]
merged_rows = []

# Get the intersection of Country Names and Country Codes
intersection_df = pd.merge(pd.merge(dfs['life_expectancy'], dfs['gdp_per_capita'], on=['Country Name', 'Country Code']), dfs['world_population'], on=['Country Name', 'Country Code'])

# Process the intersection DataFrame
for index, row in intersection_df.iterrows():
    country_name = row['Country Name']
    country_code = row['Country Code']
    
    for year in years:
        # Initialize data for each year
        year_data = {
            'Country Name': country_name,
            'Country Code': country_code,
            'Year': year,
            'Life Expectancy': np.nan,
            'GDP': np.nan,
            'Population': np.nan
        }
        
        # Collect values for life expectancy, GDP, and population
        for key in dfs.keys():
            values = dfs[key].loc[dfs[key]['Country Name'] == country_name, year].values
            
            if len(values) > 0:
                if key == 'life_expectancy':
                    year_data['Life Expectancy'] = values[0]
                elif key == 'gdp_per_capita':
                    year_data['GDP'] = values[0]
                elif key == 'world_population':
                    year_data['Population'] = values[0]
            else:
                print(key, country_name, year)
        
        # Add the country data for the year to the merged_df rows
        merged_rows.append(year_data)

# Convert the merged_df list to a DataFrame
merged_df = pd.DataFrame(merged_rows)

# Set a MultiIndex based on 'Country Name' and 'Year'
merged_df.set_index(['Country Name', 'Country Code', 'Year'], inplace=True)

merged_df = merged_df.dropna()

# Create the scatterplot

# Create the figure and axis
fig, ax = plt.subplots(figsize=(10, 6))
plt.subplots_adjust(left=0.1, bottom=0.25)

# Slider axis and creation
ax_slider = plt.axes([0.1, 0.1, 0.8, 0.05], facecolor='lightgoldenrodyellow')
slider = Slider(ax_slider, 'Year', valmin=1990, valmax=2018, valinit=1990, valstep=1)

# Function to update the scatter plot based on the selected year
def update_plot(val):
    year = str(int(val))  # Get the year from the slider and format it as a string
    df_year = merged_df.xs(year, level='Year')  # Filter the DataFrame for the selected year

    # Filter out rows with NaN or infinite values
    df_year = df_year.replace([np.inf, -np.inf], np.nan).dropna(subset=['GDP', 'Life Expectancy', 'Population'])
    
    # Update scatter plot data
    scat.set_offsets(np.c_[df_year['GDP'], df_year['Life Expectancy']])
    scat.set_sizes(df_year['Population'] / 1e6)

    # Remove previous labels and add new ones
    for txt in texts:
        txt.remove()  # Remove old text labels
    texts.clear()  # Clear the list
    
    # Add new labels for the updated data
    for i in range(len(df_year)):
        txt = ax.text(df_year['GDP'].iloc[i], df_year['Life Expectancy'].iloc[i], df_year.index.get_level_values('Country Name')[i], fontsize=8)
        texts.append(txt)

    fig.canvas.draw_idle()  # Redraw the plot with the new data

# Initial data for the first year (e.g., 1990)
year = '2006'
df_year = merged_df.xs(year, level='Year')

# Filter out rows with NaN or infinite values
df_year = df_year.replace([np.inf, -np.inf], np.nan).dropna(subset=['GDP', 'Life Expectancy', 'Population'])

# Scatter plot with initial data
scat = ax.scatter(
    df_year['GDP'], df_year['Life Expectancy'],
    s=df_year['Population'] / 1e6, alpha=0.6, edgecolors="w", linewidth=0.5
)

# Labels for each point
texts = []
for i in range(len(df_year)):
    txt = ax.text(df_year['GDP'].iloc[i], df_year['Life Expectancy'].iloc[i], df_year.index.get_level_values('Country Name')[i], fontsize=8)
    texts.append(txt)

# Attach the update function to the slider
slider.on_changed(update_plot)

# Labels and title
ax.set_xlabel('GDP per Capita')
ax.set_ylabel('Life Expectancy (years)')
ax.set_title('Life Expectancy vs GDP Over Time')
ax.grid(True)

# Initial display
plt.show()
