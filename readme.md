# 海量小文件生成器

## 功能简介

适用于生成文件系统，在一个root路径下生成多级别的多个文件夹以及文件。

## 参数解释

* root_path：生成文件的文件夹路径
* N：文件夹的层级，一般为3或者4，输入一个int整数
* file_count_min：每一个文件夹包含的子文件夹数的最小值
* file_count_max：每一个文件夹包含的子文件夹数的最大值
* folder_size_max：文件要求的大小上限
* file_number_max：生成文件总数的上限
* file_size_min：生成文件大小的最小值
* file_size_max：生成文件大小的最大值
* file_size_mean：生成文件大小的平均值
* file_size_standard_deviation: 生成的单个文件大小的标准差
* generate_way：文件生成的约束方式，最多生成多少个文件或者生成文件占用的总大小为多大 [ byNumber / bySize ]
* generate_place：文件在所有的文件夹中生成还是只放置在叶子结点的文件夹 [ all / leaf ]
* file_size_distribution：文件大小的排布方式（每个文件大小一样还是符合正态分布）[ average / normal ]

```ini
[Settings]


; root_path：生成文件的文件夹路径
root_path = /Users/edy/Documents/ypl/randomFileGenerator/version2/root


; N：文件夹的层级，一般为3或者4，输入一个int整数
N = 3
; 举例，当N=3的时候，会创建出来三层深度
;【Root】
;	|
;	| --- Folder_1_1
;  	| 		| --- Folder_2_1
;  	|		|		| --- Folder_3_1
;  	|		|		| --- Folder_3_2
;  	|		| --- Folder_2_2
;   |
;   | --- Folder_1_2
;    		| --- Folder_2_1
;    	    |			| --- Folder_3_1
;					    |


; file_count_min：每一个文件夹包含的子文件夹数的最小值
; file_count_max：每一个文件夹包含的子文件夹数的最大值
; 这种情况就是最少包含1个子文件夹，最多包含5个子文件夹
file_count_min = 1
file_count_max = 5


; folder_size_max：文件要求的大小上限
; 例如，要求生成的文件大小为100mb，可以用这个参数进行约束
; 【可选参数】数字+KB/MB/GB/TBPB，如 200KB, 400MB, 大小写不敏感
folder_size_max = 100MB


; file_number_max：生成文件总数的上限
; 例如，现在这种情况就是要求生成500个文件
file_number_max = 500


; file_size_min：文件的大小要求（最大值、最小值、平均值、标准差）
; 【可选参数】数字+KB/MB/GB/TBPB，如 200KB, 400MB, 大小写不敏感
file_size_min = 500kb


; file_size_max：文件大小的上限，文件大小不可以超过该值
; 【可选参数】数字+KB/MB/GB/TBPB，如 200KB, 400MB, 大小写不敏感
file_size_max = 1000kb


; file_size_mean：生成文件大小的平均值，如果要求所有生成文件的大小一致，则文件大小为该值
; 如果要求生成的多个文件大小符合正态分布的规律，这个参数为正态分布的均值
; 【可选参数】：数字+KB/MB/GB/TBPB，如 200KB, 400MB, 大小写不敏感
file_size_mean = 1mb									


; file_size_standard_deviation：文件大小的标准差，如果要求生成文件的大小符合正态分布，会用到该参数
file_size_standard_deviation = 5000


; generate_way：按照数量生成还是按照文件总大小生成     
;【可选参数】：byNumber / bySize
;【参数解释】：byNumber：总共生成 "file_number_max" 个文件
;【参数解释】：bySize：生成的文件大小加起来不能超过 "folder_size_max" 的大小
generate_way = byNumber


; generate_place：文件在所有的文件夹中生成还是只放置在叶子结点的文件夹
;【可选参数】：all / leaf
;【参数解释】：all代表放置在所有文件夹内，leaf表示只能放置在叶子节点的文件夹内
;
;																【N = 2 一个实例】
;																【Root】根目录 
;															 /              \
;												Folder_1_1                Folder_1_2
;												/ 					    /			   \
;									Folder_2_1				      Folder_2_1	    	Folder_2_2
;
; 	   这种情况，Folder_2_1、Folder_2_1、Folder_2_2就是三个leaf（叶子节点）文件夹
generate_place = all


; file_size_distribution：文件大小的排布方式（每个文件大小一样还是符合正态分布）
;【可选参数】：normal / average
;【参数解释】：normal: 生成的所有文件的大小是一致的
;【参数解释】：average: 生成的文件大小要符合正态分布
file_size_distribution = average


```


## GUI_Thread

加入了并发，可以在生成过程中查看文件生成的进度


### 使用说明

* 在点击【确认】后程序会开始运行，之后可以在下面的进度条中看到文件生成的进度。在程序未运行时，操作进度的组件会被禁用；在程序生成过程中，上方的组件会被禁用


* 可以点击【暂停】、【继续】或者【终止】进行相应的操作。
