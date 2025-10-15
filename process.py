# %%
import pandas as pd
import os
import requests
import json

def download_file_if_not_exists(url, fname=None, jsonkey=None):
    if fname is None:
        fname = os.path.basename(url)
    if not os.path.isfile(fname):
        session = requests.Session()
        if jsonkey is None:
            with session.get(url, stream=True) as stream:
                stream.raise_for_status()
                with open(fname, 'wb') as f:
                    for chunk in stream.iter_content(chunk_size=8192):
                        f.write(chunk)
        else:
            resp = session.get(url)
            resp.raise_for_status()
            print(resp.json())
            with open(fname, 'w') as f:
                json.dump(resp.json().get(jsonkey), f)

# Calculate ratio of metrics compared to first period for each council
def compare_to_start_date(df, metrics, group_by, names, filename):
    for i in range(len(metrics)):
        first_period = df.sort_values('Date').groupby(group_by)[metrics[i]].transform('first')
        df[names[i]] = (df[metrics[i]] / first_period) - 1
    df = pd.melt(
        df[['Date', group_by] + names], 
        id_vars=[group_by, 'Date'], 
        var_name='Metric', 
        value_name='Value'
    ).pivot(
        index=['Date', 'Metric'], 
        columns=group_by, 
        values='Value'
    )
    df.to_csv(filename, index=True)
    return df

# %%
dom = pd.read_csv('data/domestic-property-vacancy-rates-by-district-council.csv')
nondom = pd.read_csv('data/non-domestic-property-vacancy-rates-by-district-council.csv')
all = pd.read_csv('data/property-vacancy-rates-by-district-council.csv')
# Convert dates to usable format
dom['Date'] = pd.to_datetime(dom['Date'].str.replace(r'(\d)(st|nd|rd|th)', r'\1', regex=True), format='%d %B %Y')
nondom['Date'] = pd.to_datetime(nondom['Date'].str.replace(r'(\d)(st|nd|rd|th)', r'\1', regex=True), format='%d %B %Y')
all['Date'] = pd.to_datetime(all['Date'].str.replace(r'(\d)(st|nd|rd|th)', r'\1', regex=True), format='%d %B %Y')
# Combine the three datasets into one
full = pd.merge(dom, nondom, on=['Date', 'District Council'], how='outer')
full = pd.merge(full, all, on=['Date', 'District Council'], how='outer')
# Output a combined CSV
full.to_csv('data/property-vacancy-rates-by-district-council-combined.csv', index=False)

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
compare_to_start_date(full, ['Number of Non-Domestic Properties'], 'District Council', ['Non-Domestic Properties Ratio'], 'data/property-vacancy-rates-by-district-council-non-domestic-ratio.csv')
compare_to_start_date(full, ['Number of Vacant Non-Domestic Properties'], 'District Council', ['Non-Domestic Vacant Properties Ratio'], 'data/property-vacancy-rates-by-district-council-non-domestic-vacant-ratio.csv')

# %%
download_file_if_not_exists('https://www.communities-ni.gov.uk/sites/default/files/2025-08/tcd-non-domestic-property-nav-planning-applications-vacancy-rates-floor-space.xlsx', 'data/tcd-non-domestic-property-nav-planning-applications-vacancy-rates-floor-space.xlsx')
# Convert the Excel to a dataframe with multi-index columns
tcd = pd.read_excel('data/tcd-non-domestic-property-nav-planning-applications-vacancy-rates-floor-space.xlsx', sheet_name='Non-Dom Vacancy Rates ', header=list(range(5,8)))
tcd.columns = tcd.columns.droplevel(1)
# Discard all-NA columns
tcd = tcd.dropna(axis=1, how='all')
# Fix incorrect year in column multiindex
tcd.columns = tcd.columns.set_levels([x.replace('20173', '2017') for x in tcd.columns.levels[0]], level=0)
# Clean up inferred column name
tcd.columns = tcd.columns.set_levels([x.replace('Unnamed: 1_level_0', '') for x in tcd.columns.levels[0]], level=0)
# Collapse multi-index columns into single level with format "firstlevel - secondlevel"
tcd.columns = [f"{col[1]} - {col[0]}" if col[0] != '' else col[1] for col in tcd.columns]
# Adjust to long format
tcd_long = pd.wide_to_long(tcd, stubnames=['No. of Properties', 'No. of Vacant Properties', '% of Vacant Properties'], i=['TOWN CENTRE'], j='Date', sep=' - ', suffix='.*').reset_index()
# Use a proper date format
tcd_long['Date'] = pd.to_datetime(tcd_long['Date'], format='%d %B %Y')
# Calculate number of non-vacant properties
tcd_long['No. of Non-Vacant Properties'] = tcd_long['No. of Properties'] - tcd_long['No. of Vacant Properties']
# %% Multiply % by 100 for display purposes
tcd_long['% of Vacant Properties'] = tcd_long['% of Vacant Properties'] * 100

# %% Output to CSV
tcd_long.to_csv('data/tcd-non-domestic-property-vacancy-rates.csv')

# %%
tcd_raw = pd.melt(tcd_long, id_vars=['TOWN CENTRE', 'Date'], var_name='Metric', value_name='Value').pivot(index=['Date', 'Metric'], columns='TOWN CENTRE', values='Value')
tcd_raw.to_csv('data/tcd-non-domestic-property-vacancy-rates-wide.csv')

# %%
tcd_ratios = compare_to_start_date(tcd_long, ['No. of Properties','No. of Vacant Properties','No. of Non-Vacant Properties'], 'TOWN CENTRE', ['Change in Total', 'Change in Vacant', 'Change in Non-Vacant'], 'data/tcd-non-domestic-properties-ratios.csv').reset_index()

# %%
most_recent = tcd_ratios[tcd_ratios['Date'] == tcd_ratios['Date'].max()]
most_recent.drop(columns='Date').set_index('Metric').transpose().to_csv('data/tcd-non-domestic-properties-ratios-latest.csv')
# %%
