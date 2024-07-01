# Energiescan

Grote datasets zijn opgeslagen in een OSF library, download alle bestanden en plaats ze in de volgende folder: `core/static/data`
- Household Power Consumption: https://osf.io/swqfg
- Household Power Consumption Processed: https://osf.io/v56nm
- Household Power Consumption Datetime Processed: https://osf.io/q4ebs
- Household Power Consumption processed 15min: https://osf.io/xpgk4
- 2022 15min data: https://osf.io/n6r8a
- 2022 15min data with GHI: https://osf.io/a4kz3
- Solar simulation data: https://osf.io/xwbp4

# Om het programma zo goed mogelijk te draaien, gebruik een anaconda kernel: (https://www.anaconda.com/)

`conda create --name tensorflowgpu python==3.10.6`

`conda activate tensorflowgpu`

`conda install -c conda-forge cudatoolkit=11.2 cudnn=8.1.0`

`pip install tensorflow==2.10`

Als er geen GPU gebruikt hoeft te worden kan het ook op een python versie op het systeem zelf worden gedraaid, raadpleeg dan simpelweg het volgende kopje (Installeren vna libraries)

# Installeren van libraries
gebruik command:
`pip install -r requirements.txt`

Zorg dat alle versies van python libraries correct zijn anders zal er een error ontstaan in het laden van de modellen, het is namelijk cruciaal dat tensorflow 2.10.0 wordt gebruikt met correcte library versies. De applicatie is getest om te werken op python versie `3.10.xx` de specifiek gebruiktes versies zijn `3.10.14` en `3.10.6`.

# Draaien van programma
Zodra alle libraries goed zijn geinstalleerd kan het programma gedraaid worden door `flask run` te typen in in de terminal en op de link te klikken die verschijnt.

# Visualisatie
Op de website zijn 4 grafieken, voor beide datasets zijn er twee grafieken de eerste is de inputdata en de tweede is de voorspelling.
Per dataset kan er in een dropdown gekozen worden tussen GRU, LSTM en Ensemble. LSTM overschat gemiddeld, GRU onderschat, en ensemble is het gemiddelde tussen de twee.

# Contributors
- [Axel Frederiks](https://github.com/ProgrammerGhostPrK)
- [Oscar Theelen](https://github.com/Ozziehman)
- [Menno Rompelberg](https://github.com/MasterDisaster7)
- [Jonah Siemers](https://github.com/Doomayy)

