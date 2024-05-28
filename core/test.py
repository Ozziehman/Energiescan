import pandas as pd
index = 0
while True:
    data = pd.read_csv('core/static/data/2022_15min_data.csv')

    new_index = index + 1
    index = new_index
    print(data.iloc[new_index]['PV Productie (W)'])