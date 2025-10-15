# %%
import pandas as pd

# %%
dom = pd.read_csv('data/domestic-property-vacancy-rates-by-district-council.csv')
nondom = pd.read_csv('data/non-domestic-property-vacancy-rates-by-district-council.csv')
all = pd.read_csv('data/property-vacancy-rates-by-district-council.csv')

# %% Convert dates to usable format
dom['Date'] = pd.to_datetime(dom['Date'].str.replace(r'(\d)(st|nd|rd|th)', r'\1', regex=True), format='%d %B %Y')
nondom['Date'] = pd.to_datetime(nondom['Date'].str.replace(r'(\d)(st|nd|rd|th)', r'\1', regex=True), format='%d %B %Y')
all['Date'] = pd.to_datetime(all['Date'].str.replace(r'(\d)(st|nd|rd|th)', r'\1', regex=True), format='%d %B %Y')

# %% Combine the three datasets into one
full = pd.merge(dom, nondom, on=['Date', 'District Council'], how='outer')
full = pd.merge(full, all, on=['Date', 'District Council'], how='outer')

# %% Output a combined CSV
full.to_csv('data/property-vacancy-rates-by-district-council-combined.csv', index=False)

# %%
# %%
full.pivot(
    index='Date', 
    columns='District Council', 
    values='Non-Domestic Vacancy Rate %'
).to_csv('data/property-vacancy-rates-by-district-council-non-domestic.csv', index=True)
# %%
full.pivot(
    index='Date', 
    columns='District Council', 
    values='Number of Non-Domestic Properties'
).to_csv('data/property-vacancy-rates-by-district-council-non-domestic-properties.csv', index=True)

# %%
# Calculate ratio of non-domestic properties compared to first period for each council
first_period = full.sort_values('Date').groupby('District Council')['Number of Non-Domestic Properties'].transform('first')
full['Non-Domestic Properties Ratio'] = (full['Number of Non-Domestic Properties'] / first_period) - 1

# Output the ratios to CSV
full.pivot(
    index='Date',
    columns='District Council', 
    values='Non-Domestic Properties Ratio'
).to_csv('data/property-vacancy-rates-by-district-council-non-domestic-ratio.csv', index=True)

# %%
# Calculate ratio of non-domestic properties compared to first period for each council
first_period = full.sort_values('Date').groupby('District Council')['Number of Vacant Non-Domestic Properties'].transform('first')
full['Non-Domestic Vacant Properties Ratio'] = (full['Number of Vacant Non-Domestic Properties'] / first_period) - 1

# Output the ratios to CSV
full.pivot(
    index='Date',
    columns='District Council', 
    values='Non-Domestic Vacant Properties Ratio'
).to_csv('data/property-vacancy-rates-by-district-council-non-domestic-vacant-ratio.csv', index=True)

# %%
