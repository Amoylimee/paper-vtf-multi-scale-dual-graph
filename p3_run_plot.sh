#!/bin/bash
# 批量测试不同分位数截断方案

echo "========================================="
echo "Testing different percentile clipping schemes"
echo "========================================="
echo ""

# 创建输出目录
mkdir -p output/p3_plot

# 定义要测试的分位数组合 (vmin, vmax)
# 格式: "vmin vmax 描述"
test_cases=(
    "0 85 VeryConservative-85th"
    # "0 90 Conservative-90th"
    # "0 92 Standard-92nd"
    # "0 95 Standard-95th"
    # "0 97 Aggressive-97th"
    # "0 99 VeryAggressive-99th"
    # "5 90 Trimmed-5to90"
    # "5 95 Trimmed-5to95"
    # "5 99 Trimmed-5to99"
    # "10 90 Trimmed-10to90"
    # "10 95 Trimmed-10to95"
    # "10 99 Trimmed-10to99"
)

echo "Will test ${#test_cases[@]} configurations:"
for case in "${test_cases[@]}"; do
    read -r vmin vmax desc <<< "$case"
    echo "  - ${desc}: vmin=${vmin}%, vmax=${vmax}%"
done
echo ""

# 运行每个测试
counter=1
total=${#test_cases[@]}

for case in "${test_cases[@]}"; do
    read -r vmin vmax desc <<< "$case"
    
    echo "[$counter/$total] Running: ${desc} (vmin=${vmin}%, vmax=${vmax}%)"
    echo "----------------------------------------"
    
    # 设置环境变量并运行脚本
    VMIN_PERCENTILE=$vmin VMAX_PERCENTILE=$vmax python p3_plot_research_area.py
    
    if [ $? -eq 0 ]; then
        echo "✓ Success: output/p3_plot/study_area_map_${vmin}_${vmax}.png"
    else
        echo "✗ Failed: ${desc}"
    fi
    
    echo ""
    counter=$((counter + 1))
done

echo "========================================="
echo "All tests completed!"
echo "Results saved in: output/p3_plot/"
echo ""
echo "Generated files:"
ls -lh output/p3_plot/study_area_map_*.png 2>/dev/null || echo "No files generated"
echo "========================================="
