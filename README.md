# Energiescan

get larger csv from OSF and put in `core/static/data`
- Household Power Consumption: https://osf.io/swqfg
- Household Power Consumption Processed: https://osf.io/v56nm
- Household Power Consumption Datetime Processed: https://osf.io/q4ebs
- Household Power Consumption processed 15min: https://osf.io/xpgk4
- 2022 15min data: https://osf.io/n6r8a
- 2022 15min data with GHI: https://osf.io/a4kz3
- Solar simulation data: https://osf.io/xwbp4


# Om het programma goed te draaien gebruik aub de volgende kernel setup binnen anaconda (https://www.anaconda.com/)

`conda create --name tensorflowgpu python==3.10`

`conda activate tensorflowgpu`

`conda install -c conda-forge cudatoolkit=11.2 cudnn=8.1.0`

`pip install tensorflow==2.10`
