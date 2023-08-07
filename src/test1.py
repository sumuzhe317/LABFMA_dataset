import numpy as np

# 假设你的三维数组是 data，形状为 (167, 1944, 3)
# 创建一个例子数据来代替 data
data = np.random.randint(0, 10, size=(167, 1944, 3))

# 使用 np.unique 按最后一个维度的值进行归类计数
flattened_data = data.reshape(-1, 3)  # 将最后一个维度展平为二维数组
unique_values, counts = np.unique(flattened_data, axis=0, return_counts=True)

# 打印结果
for value, count in zip(unique_values, counts):
    print(f"值为 {value} 的元素出现了 {count} 次")
