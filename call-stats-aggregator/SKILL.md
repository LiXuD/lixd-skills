---
name: call-stats-aggregator
agent_created: true
description: Aggregate answered-call statistics from monthly report workbooks across multiple months or a custom date range. Reads the 《接听电话详情》 sheet of the standard monthly attachment workbook, sums call categories, computes totals and percentages, and emits a summary Excel plus a short Markdown report. Use when the user asks for call counts/percentages over a period such as「3月26日至6月25日」or across several monthly files.
---

# 月度接听电话统计汇总

## Overview

汇总多月《附件1 月报统计数据记录表》中「接听电话详情」Sheet 的每日电话分类数据：
按指定日期区间过滤、逐类求和、计算占比，输出「分类汇总 + 月度明细」两页 Excel（含饼图）与一段 Markdown 摘要。

## When to use

- 需要跨多月统计电话量、类别分布或占比
- 需要某个自定义区间的电话合计（如「3月26日至6月25日」这类跨月区间）
- 用户给出若干 `附件1《YY年M月报统计数据记录表》.xlsx` 文件并要求汇总

## Workflow

1. 确定源文件与目标区间。用户给了文件就用给定路径；否则按
   `<MR_ROOT>/月报/<YY>年<M>月/附件1《YY年M月报统计数据记录表》.xlsx` 约定推断
   （`MR_ROOT` 为环境变量，未设则用当前目录）。
2. 逐个文件读取名为 `接听电话详情` 的 Sheet。
3. 解析首列中文日期（`X月Y号`），结合文件所属年月还原成真实日期。
4. 按闭区间过滤行。
5. 对日期列以外的所有数值列求和，缺失值按 0 处理。
6. 计算总数与各类占比。
7. 需要时按 `YYYY-MM` 输出月度分组小计。
8. 写汇总 Excel，两个 Sheet：
   - `分类汇总`：类别、数量、占比 + 饼图
   - `月度明细`：各月分类小计与月度总计
9. 另出一份简短 Markdown 摘要便于快速阅读。

## Important conventions

- 月度工作簿命名：`附件1《YY年M月报统计数据记录表》.xlsx`，位于 `月报/<YY>年<M>月/`
- 目标 Sheet 固定为 `接听电话详情`
- 首列是中文日期字符串（`X月Y号`）
- 其余列均为电话类别，标准 11 类：
  柜员强制签退、终端变更、数据查询业务、人为操作失误、设备故障异常、系统异常故障、
  银行业务问题、机房环境、服务器设备问题、网络设备问题、基础设施问题
- 若某文件出现新增/改名类别，**动态纳入**，不要硬编码丢弃

## Reusable script

```bash
# 按约定目录自动发现文件
python3 scripts/aggregate_calls.py --start "2026-03-26" --end "2026-06-25" \
    --output /path/to/output.xlsx

# 或显式指定文件
python3 scripts/aggregate_calls.py \
    --files mar.xlsx apr.xlsx may.xlsx jun.xlsx \
    --start "2026-03-26" --end "2026-06-25" --output /path/to/output.xlsx
```

依赖：`pandas`、`openpyxl`。

## Output format

- Excel：两个 Sheet（分类汇总含占比与饼图、月度明细）
- Markdown：总数、类别、数量、占比的简洁表格
