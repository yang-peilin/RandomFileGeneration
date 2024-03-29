import os
import random

def generate_folders(root_path, folder_path_list, folder_number_min, folder_number_max, N, folder_map,
                     folder_leaf_map, index):

    if not os.path.exists(root_path):
        # 如果路径不存在，则创建新的文件夹
        os.makedirs(root_path)

    # 从第一层开始生成文件夹
    current_layer = 1
    folder_path_list.append(root_path)

    while folder_path_list:
        curr_len = len(folder_path_list)

        if current_layer > N:
            break

        for _ in range(0, curr_len):
            # 当前的文件夹路径
            current_folder_path = folder_path_list.pop(0)
            # 当前的文件夹路径中要生成多少个子文件夹
            n = int(random.uniform(folder_number_min, folder_number_max))

            for j in range(1, n + 1):
                # 确定要生成的文件夹的编号
                new_folder_id = str(current_layer) + "_" + str(j)
                # 确定要生成的文件夹的名称
                new_folder_name = "folder_" + new_folder_id
                # 确定要生成的文件夹的路径
                new_folder_path = os.path.join(current_folder_path, new_folder_name)
                # 如果文件夹存在，则先删除
                if os.path.exists(new_folder_path):
                    shutil.rmtree(new_folder_path)
                # 创建文件夹
                os.makedirs(new_folder_path)
                # 将该文件夹的路径放入folder_path_list中
                folder_path_list.append(new_folder_path)
                # 将这个文件夹的信息记录到map中
                folder_map[index] = new_folder_path
                # 如果该文件夹已经到了最底层，那么还要加入另一个map中
                if current_layer == N:
                    folder_leaf_map[index] = new_folder_path
                index += 1

        current_layer += 1
