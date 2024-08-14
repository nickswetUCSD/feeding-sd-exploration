# explore.py
#
# A script that takes in a Feeding San Diego .csv file (containing one year's worth of data) 
# and outputs a series of .html diagrams that aid in exploration of the data.
#
# Usage: python explore.py data.csv out_folder
# After running, out_folder will contain several .html diagrams and (TODO) a .txt file summarizing the .csv data.

import sys
from explorefuncs import *


if __name__ == '__main__':
    if len(sys.argv[1:]) != 2:
        raise ValueError(f'2 arguments required but {len(sys.argv[1:])} provided.')
    file_path = sys.argv[1]
    out_dir = sys.argv[2]
    
    # Step 1: Import .csv file.
    data = read_file(file_path)
    
    # Step 2: Clean and filter .csv file; creates new time columns, changes dtypes, drops rows with missing vals for 'Start Date', 'Start Time', 'Opportunity Zip'; drops unnecessary columns.
    cleaned = clean_data(data)
    
    # Step 3: Generate .html files, and individually ship them to out_folder
    hoursPlot(cleaned, out_dir)
    weektimeHeatmap(cleaned, out_dir)
    participationYear(cleaned, out_dir)
    locationPlot(cleaned, out_dir)
    
    
    
    