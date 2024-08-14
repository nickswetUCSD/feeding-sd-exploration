# FEEDING SAN DIEGO EXPLORATION
## ABOUT
This repo will contain tools for exploring data from "Feeding San Diego", a non-governmental organization fighting food insecurity across San Diego. I hope these tools can help identify patterns in volunteer demographics, time of participation, absenteeism, and more, so that resources may be better spent in community outreach and decision-making.

## REPO ANATOMY
**data**: folder that contains raw, anonymized volunteer data (.csv) for the 2023 and 2024 years. 
**out**: folder that contains cleaned, interactive diagrams (.html) that summarize our data.
**explore**: script (.py) that takes a .csv file from *data* as input, and outputs multiple diagrams to the *out* folder.
**explorefuncs**: library (.py) that contains many functions that *explore* imports.

## HOW TO USE
The file to use is **explore.py**. 
1) Clone the repo.
2) Insert your data-to-analyze (.csv) into the *data* folder.
3) Run "python explore.py {data.csv} {out_folder}" in the terminal, where:
  - {data.csv} is replaced by the name of the .csv file you wish to create diagrams for. Example: "data/FY23.csv".
  - {out_folder} is the name of the (already created) folder your .html diagrams will be cast into. Example: "out/2023".
4) Wait a few moments.
5) Access your .html diagrams in the *out* folder.

## TO BE IMPLEMENTED
- Faster geojson import, to speed up creation of Plot 4/4 and other potential choropleth plots.
- Small .txt "summary" files that give a concise numerical description of data.
- More plots that are more useful. 



