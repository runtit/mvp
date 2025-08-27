import re
import pandas as pd
from typing import Optional


def _parse_month_to_yyyymm(value, base_year=2024, base_month=1) -> Optional[int]:
    """将多种月份格式统一解析为 YYYYMM 整数，解析失败返回 pd.NA"""
    if pd.isna(value):
        return pd.NA

    s = str(value).strip()
    if not s:
        return pd.NA

    # 尝试自动解析日期
    try:
        dt = pd.to_datetime(s, errors="raise")
        return dt.year * 100 + dt.month
    except:
        pass

    # 提取纯数字：202408、20240801、8、2025、"1/2024"
    nums = re.findall(r"\d+", s)
    if not nums:
        return pd.NA

    if len(nums) == 1:
        num = int(nums[0])

        # 8位日期格式：YYYYMMDD (19000101-21001231)
        if 19000101 <= num <= 21001231:
            y = num // 10000
            m = (num // 100) % 100
            # 验证月份有效性
            if 1 <= m <= 12:
                return y * 100 + m
            else:
                return pd.NA  # 修复：无效月份直接返回 NA

        # 6位格式：YYYYMM (190001-210012)
        elif 190001 <= num <= 210012:
            y, m = divmod(num, 100)
            if 1 <= m <= 12:
                return y * 100 + m
            else:
                return pd.NA  # 修复：无效月份直接返回 NA

        # 4位年份：使用默认月份
        elif 1900 <= num <= 2100:
            return num * 100 + base_month

        # 1-2位月份：使用默认年份
        elif 1 <= num <= 12:
            return base_year * 100 + num

    # 多个数字的情况
    elif len(nums) >= 2:
        y1, y2 = int(nums[0]), int(nums[1])

        # 年-月 格式
        if 1900 <= y1 <= 2100 and 1 <= y2 <= 12:
            return y1 * 100 + y2

        # 月-年 格式
        elif 1 <= y1 <= 12 and 1900 <= y2 <= 2100:
            return y2 * 100 + y1

    return pd.NA


# 测试代码
test_values = [
    "2025-08", "2025/08", "2025-08-01", "2025/08/01", "07/01/2025",
    "202508", 20250801, 2025, 8, "8", "08/2025", "2025/8", "8/25", "Q1 2025",
    "第13月", "13/2025", "abcdefg", None, "", "202513", 20259999
]

# 执行测试并展示结果
df_test = pd.DataFrame({"Original": test_values})
df_test["Parsed_YYYYMM"] = df_test["Original"].apply(_parse_month_to_yyyymm)
df_test["Valid"] = df_test["Parsed_YYYYMM"].notna()

print("=== 测试结果 ===")
print(df_test)

# 验证一些关键案例
print("\n=== 关键案例验证 ===")
critical_cases = [
    ("202513", "应该返回 pd.NA (13月无效)"),
    ("20259999", "应该返回 pd.NA (99月无效)"),
    ("8/25", "应该解析为 2025年8月"),
    ("13/2025", "应该返回 pd.NA (13月无效)"),
]

for case, expected in critical_cases:
    result = _parse_month_to_yyyymm(case)
    print(f"{case:10} -> {result:>8} ({expected})")

# 额外的边界测试
print("\n=== 边界测试 ===")
boundary_tests = [
    190001,  # 最小有效 YYYYMM
    210012,  # 最大有效 YYYYMM
    190013,  # 无效月份
    209999,  # 无效月份
    19000101,  # 最小有效 YYYYMMDD
    21001231,  # 最大有效 YYYYMMDD
    20240229,  # 闰年2月29日
    20240230,  # 无效日期（2月30日）
]

for test in boundary_tests:
    result = _parse_month_to_yyyymm(test)
    print(f"{test:10} -> {result}")


# 性能优化版本（如果需要处理大量数据）
def _parse_month_to_yyyymm_optimized(value, base_year=2024, base_month=1) -> Optional[int]:
    """优化版本：减少异常处理，提高性能"""
    if pd.isna(value):
        return pd.NA

    s = str(value).strip()
    if not s:
        return pd.NA

    # 先尝试直接数值转换（最常见情况）
    if s.isdigit():
        num = int(s)

        # 8位日期格式
        if 19000101 <= num <= 21001231:
            y = num // 10000
            m = (num // 100) % 100
            return y * 100 + m if 1 <= m <= 12 else pd.NA

        # 6位 YYYYMM
        elif 190001 <= num <= 210012:
            y, m = divmod(num, 100)
            return y * 100 + m if 1 <= m <= 12 else pd.NA

        # 4位年份
        elif 1900 <= num <= 2100:
            return num * 100 + base_month

        # 1-2位月份
        elif 1 <= num <= 12:
            return base_year * 100 + num

        return pd.NA

    # 尝试日期解析（字符串格式）
    try:
        dt = pd.to_datetime(s, errors="raise")
        return dt.year * 100 + dt.month
    except:
        pass

    # 正则提取数字（最复杂情况）
    nums = re.findall(r"\d+", s)
    if len(nums) >= 2:
        y1, y2 = int(nums[0]), int(nums[1])
        if 1900 <= y1 <= 2100 and 1 <= y2 <= 12:
            return y1 * 100 + y2
        elif 1 <= y1 <= 12 and 1900 <= y2 <= 2100:
            return y2 * 100 + y1

    return pd.NA