from run_FI import increase_concatenate_files_with_same_number
from run_FIGAP import run

rate = 0.5

folder_path_origin = "./results/re_Traffic_GAP_2Pistes"

folder_path_actual_opt = "./results/intermediateFile/t_a_total/re_optimization_actual_3_" + str(rate) + "/"
folder_path_target_opt = "./results/intermediateFile/t_a_total/re_optimization_target_3_" + str(rate) + "/"

seuil = 0

for seed in range(3, 5):
    folder_path_increase = "./results/intermediateFile/t_a_total/re_increase_3_" + str(rate) + "_seed" + str(seed) + "/"
    output_path_concatenate = "./results/intermediateFile/t_a_total/re_concatenated_3_" + str(rate) + "_seed" + str(
        seed) + "/"

    folder_path = "./results/intermediateFile/t_a_total/re_concatenated_3_" + str(rate) + "_seed" + str(seed) + "\\"
    out_path = "./results/t_a_total/re_Traffic_Augmente_GAP_2Pistes_3_" + str(rate) + "_seed" + str(seed) + "\\"

    increase_concatenate_files_with_same_number(folder_path_target_opt, folder_path_actual_opt, folder_path_increase,
                                                output_path_concatenate, rate, seed)

    run(folder_path, out_path, seuil, "MANEX")
