# import plot
import os
import GenernateSolution
import reallocation


part = 3
delta = 5
seuil = 0
regulation = 3
quarter = 100

if __name__ == "__main__":
    # Specify the folder path
    folder_path = "../data/error-in-data"
    # folder_path = '../results/intermediateFile/Traffic_ConcatenatedFiles_GAP_2Pistes'

    # Iterate through the files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):  # Check if the file ends with .csv
            filename = os.path.join(folder_path, filename)

            # Generate initial solution
            genernate_solution, pattern, obj = GenernateSolution.generante_solution(
                filename, regulation, seuil, quarter, part, delta
            )

            # Reallocate through iteration
            re_solution = reallocation.reallocation(
                filename, seuil, part, delta, genernate_solution, regulation, pattern
            )
