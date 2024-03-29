import os

# 生成一个[min,max]有上下限符合正态分布的随机数
def generate_normal_random_number(mean, standard_deviation, lower_limit, upper_limit):
    mean = float(mean)
    standard_deviation = float(standard_deviation)
    lower_limit = float(lower_limit)
    upper_limit = float(upper_limit)
    # 生成符合正态分布的随机数
    random_number = np.random.normal(mean, standard_deviation)
    # 限制随机数范围在下限和上限之间
    random_number = max(lower_limit, min(random_number, upper_limit))
    return int(random_number)



# 输入字节数，输出可读的容量大小
def byte2string(total_size):
    temp_size = int(total_size)
    suffixes = ['B', 'KB', 'MB', 'GB']  # 添加更大的单位
    index = 0
    while temp_size >= 1024 and index < len(suffixes) - 1:
        temp_size /= 1024
        index += 1
    if temp_size.is_integer():  # 如果结果是整数，则将其转换为整数形式
        temp_size = int(temp_size)
    return f"{temp_size:.2f}{suffixes[index]}"  # 保留两位小数并添加相应的单位


def string2byte(size_str):
    size_str = size_str.lower().replace(" ", "")
    # 定义单位和对应的字节数
    size_units = {
        "b": 1,
        "kb": 1024,
        "mb": 1024 ** 2,
        "gb": 1024 ** 3,
    }
    # 尝试从字符串中提取数字和单位
    try:
        num_str = ''
        unit_str = ''
        for char in size_str:
            if char.isalpha():
                unit_str += char
            elif char.isdigit() or char == '.':
                num_str += char
            else:
                raise ValueError("Invalid character in size string")

        if not num_str or not unit_str:
            raise ValueError("Invalid size string format")

        num = float(num_str)
        unit = size_units.get(unit_str)
        if unit is None:
            raise KeyError("Unknown unit")

        return int(num * unit)
    except (ValueError, KeyError) as e:
        # 如果解析失败，返回 None
        return None


# 计算指定文件夹中的文件数量
def count_files_in_folder(folder_path):
    file_count = 0
    for _, _, files in os.walk(folder_path):
        file_count += len(files)
    return file_count


# 计算指定路径下所有文件的大小 include_folders=True表示包括文件夹，如果为False表示不包括文件夹
def calculate_total_size(path, include_folders=True):
    total_size = 0
    # 列出指定路径下的所有文件和文件夹
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        # 如果是文件，则获取文件大小并累加
        if os.path.isfile(item_path):
            total_size += os.path.getsize(item_path)
        # 如果 include_folders 为 True，且是文件夹，则递归计算其大小
        elif include_folders and os.path.isdir(item_path):
            total_size += calculate_total_size(item_path, include_folders=True)
    return total_size

