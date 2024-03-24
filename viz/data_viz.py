import pandas as pd
import matplotlib.pyplot as plt

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.extractor import Extractor

class DataVisualizer:
    def __init__(self, img_folder):
        self.img_folder = img_folder
        self.extractor = Extractor()

    def sector_solution_viz(self):
        
        df = self.extractor.extract_sector_solution(self.extractor.extract_solution_rex(), False)

        # Get the column "solution"
        sector_solution = df['solutions']
        # Count NaN values
        nan_count = sector_solution.isnull().sum()    
        # Add a column "count" to count the number of solutions (this is a list of solution)
        # and take care of NaN values
        sector_solution = sector_solution.dropna().apply(lambda x: len(x) if x is not None else 0)

        # Create a histogram to details the number of sectors with a certain number of solutions
        histogram = [0 * i for i in range(max(sector_solution)+1)] ; histogram[0] = nan_count
        for i in sector_solution:
            histogram[i] += 1

        # Aggregate the number by class of number of solutions
        histogram = [sum(histogram[i:i+5]) for i in range(0, len(histogram), 5)]
        
        plt.bar(range(3, 5*len(histogram), 5), histogram, width=4)
        plt.xlabel('Number of solutions')
        plt.ylabel('Number of sectors')
        plt.title('Histogram of number of solutions per sector')
        plt.savefig(self.img_folder + 'sector_solution_hist.png')
        plt.show()

# Usage
if __name__ == "__main__":
    data_viz = DataVisualizer('viz/img/')
    data_viz.sector_solution_viz()