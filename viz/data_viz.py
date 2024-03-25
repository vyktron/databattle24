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

        # Do the opposite, count the number of appearances of each solution
        # Create a dictionary to count the number of appearances of each solution
        solution_count = {}
        for l in df['solutions']:
            if isinstance(l, float):
                continue
            else:
                for i in l:
                    if i in solution_count:
                        solution_count[i] += 1
                    else:
                        solution_count[i] = 1
        
        # Create an histogram to show the number of sectors that have a certain number of appearances
        histogram = [0 for i in range(max(solution_count.values())+1)]
        for i in solution_count.values():
            histogram[i] += 1
        
        plt.bar(range(1, len(histogram)), histogram[1:])
        plt.xlabel('Number of appearances')
        plt.ylabel('Number of solutions')
        plt.title('Histogram of number of sectors per solution')
        plt.savefig(self.img_folder + 'solution_sector_hist.png')
        plt.show()

        # Get the root sector (first row = index 1)
        root_sector = df['sous_secteurs'][1]

        # For each root sector, recursively get the number of solutions by adding the number of solutions of its children
        def get_solution_count(sector):
            if sector in df['sous_secteurs']:
                return sum([get_solution_count(i) for i in df[df['sous_secteurs'] == sector]['solutions'].values[0]])
            else:
                return len(df[df['sous_secteurs'] == sector]['solutions'].values[0])
        
        for i in root_sector:
            print(i, get_solution_count(i))

        print('Root sector:', root_sector)


# Usage
if __name__ == "__main__":
    data_viz = DataVisualizer('viz/img/')
    data_viz.sector_solution_viz()