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

        # Delete the first element of the list (it is the root sector)
        root_sector = root_sector[1:]

        # For each roots sector, recursively count the number of solutions by adding the number of solutions of its children
        def count_solutions(sector):
            # take care of non existing values
            if sector not in df.index:
                return []
            # Get the solutions of the sector
            solutions = df['solutions'][sector]
            solutions = solutions if not isinstance(solutions, float) else []
            # Get the children of the sector
            children = df['sous_secteurs'][sector]
            # If children is NaN, return number of solutions of the sector
            if isinstance(children, float):
                children = None
            if children is not None:
                for i in children:
                    solutions += count_solutions(i)
            
            return list(set(solutions))
        
        # Get the solutions of the root sector
        root_solutions = [count_solutions(i) for i in root_sector]

        # Create a dictionary to count the number of appearances of each solution
        solution_count = {}
        for l in root_solutions:
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
        plt.savefig(self.img_folder + 'root_solution_sector_hist.png')
        plt.show()

    def solution_rex(self):

        df2 = self.extractor.extract_solution_rex(False)

        # Get the indeces where first index is the solution and the second is the numrex
        solution_rex = df2.index

        # Delete rows when solution is equal to 1
        solution_rex = solution_rex[solution_rex.get_level_values(0) != 1]

        # Count the number of numrex for each solution and store it in a dictionary
        solution_count = {}
        for i in solution_rex:
            if i[0] in solution_count:
                solution_count[i[0]] += 1
            else:
                solution_count[i[0]] = 1

        # Create a histogram to show the number of numrex for each solution
        histogram = [0 for i in range(max(solution_count.values())+1)]
        for i in solution_count.values():
            histogram[i] += 1

        mean = sum([i*j for i, j in enumerate(histogram)]) / sum(histogram)

        # Agregate to have classes width of 5
        histogram = [sum(histogram[i:i+5]) for i in range(0, len(histogram), 5)]
        
        plt.axvline(mean, color='r', linestyle='dashed', linewidth=1)
        plt.bar(range(3, 5*len(histogram), 5), histogram, width=4)
        plt.xlabel('Number of numrex')
        plt.ylabel('Number of solutions')
        plt.title('Histogram of number of numrex per solution')
        plt.savefig(self.img_folder + 'solution_rex_hist.png')
        plt.show()

# Usage
if __name__ == "__main__":
    data_viz = DataVisualizer('viz/img/')
    data_viz.sector_solution_viz()
    data_viz.solution_rex()