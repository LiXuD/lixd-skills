---
name: workload-record-parser
description: |
  值班工作量记录 Word 文档解析技能。
  读取按月累积的「值班工作量记录YYYYMM.docx」，按月份提取每日接听电话分类数据，
  输出每日明细表格（可填入附件1「接听电话详情」Sheet），并自动汇总各类问题总数与占比。
  触发词：解析工作量记录 / 提取X月电话数据 / 从工作量记录提取X月数据
agent_created: true
---

# 值班工作量记录解析

## 适用场景

把每月累积的「值班工作量记录.docx」中指定月份的电话数据提出来，输出可直接填入附件1
Excel「接听电话详情」Sheet 的每日明细表，并生成月报「接听电话解答问题情况」段落文字。

---

## 文档结构（已验证）

工作量记录 Word 的结构非常规律：

- **段落**：每条记录以 `YYYYMMDD`（如 `20261001`）的段落作为日期标题
- **表格**：紧跟日期段落之后，是一个 7 行 × 4 列的问题类型统计表
- 表头行：`问题类型 | 工作次数 | 问题类型 | 工作次数`
- 表格记录 11 种问题类型（左右各一列）

**问题类型字段映射（Word → 附件1 列名）：**

| Word 中的问题类型 | 附件1 列名 |
|---|---|
| 柜员强制签退 | 柜员强制签退 |
| 终端变更 | 终端变更 |
| 数据查询业务问题 | 数据查询业务 |
| 人为操作问题 | 人为操作失误 |
| 设备故障异常问题 | 设备故障异常 |
| 系统异常故障问题 | 系统异常故障 |
| 银行业务问题 | 银行业务问题 |
| 机房环境问题 | 机房环境 |
| 服务器设备问题 | 服务器设备问题 |
| 网络设备问题 | 网络设备问题 |
| 基础设施问题 | 基础设施问题 |

**注意**：工作次数单元格可能带备注，如 `1（切svn）`，需只取前面的数字。

---

## 执行步骤

### Step 1：确认参数

- 确认要提取的月份（对应 `YYYYMM` 前缀）
- 确认文件路径。默认位置：`<项目根>/月报/<YY>年<M>月/值班工作量记录<YYMM>.docx`
  （项目根由环境变量 `MR_ROOT` 指定；该文档是累积记录，也可能仍在**上月**目录里）

### Step 2：解析文档

```python
from docx import Document
import re

FIELD_MAP = {
    '柜员强制签退': '柜员强制签退',
    '终端变更': '终端变更',
    '数据查询业务问题': '数据查询业务',
    '人为操作问题': '人为操作失误',
    '设备故障异常问题': '设备故障异常',
    '系统异常故障问题': '系统异常故障',
    '银行业务问题': '银行业务问题',
    '机房环境问题': '机房环境',
    '服务器设备问题': '服务器设备问题',
    '网络设备问题': '网络设备问题',
    '基础设施问题': '基础设施问题',
}


def parse_workload_by_month(docx_path, year_month_prefix):
    """提取指定月份（如 '202610'）的每日电话数据。返回 (rows, cols)"""
    doc = Document(docx_path)
    COLS = list(dict.fromkeys(FIELD_MAP.values()))

    # 找出所有「纯 8 位数字」的日期段落
    date_entries = [(i, p.text.strip()) for i, p in enumerate(doc.paragraphs)
                    if re.match(r'^\d{8}$', p.text.strip())]

    results = []
    for table_idx, (_, date_str) in enumerate(date_entries):
        if not date_str.startswith(year_month_prefix):
            continue
        if table_idx >= len(doc.tables):
            break

        table = doc.tables[table_idx]
        row = {'日期': f"{int(date_str[4:6])}月{int(date_str[6:8])}号"}
        row.update({c: '' for c in COLS})

        for tr in table.rows[1:]:           # 跳过表头
            cells = [c.text.strip() for c in tr.cells]
            if len(cells) < 4:
                continue
            for key_idx, val_idx in [(0, 1), (2, 3)]:
                if cells[key_idx] in FIELD_MAP:
                    m = re.match(r'^(\d+)', cells[val_idx])   # 忽略备注文字
                    if m:
                        row[FIELD_MAP[cells[key_idx]]] = int(m.group(1))
        results.append(row)

    return results, COLS
```

### Step 3：输出结果

1. 每日明细 Markdown 表格（日期 + 11 类）
2. 各类问题汇总行（合计）
3. 各类问题总数及占比（按占比降序）
4. **写入附件1.xlsx 的 Sheet3「接听电话详情」**
   ```bash
   python3 <skill>/../monthly-report-generator/scripts/generate_attachment1.py <月份> <年份> <batch_json> <phone_json>
   ```
   每日一行，空值留空（与 Excel 使用习惯一致）

### Step 4：生成月报电话摘要文字

```
本月共接听电话XXX个，其中柜员强制签退需求XXX个、终端变更需求XXX个、
数据查询业务问题XXX个、银行业务问题XXX个[、其他类型若>0则列出]。
经分析目前问题发生较多的时间段主要为周一至周五的工作时间，周六、周日接听电话数较少。
```

只列数量 > 0 的类型，按数量从大到小排列。

---

## 注意事项

1. **数字解析健壮性**：工作次数有时带备注（`1（切svn）`、`2（含协助）`），只取开头数字
2. **空值处理**：空单元格视为 0，写入时保持空白
3. **字段顺序**：附件1 列顺序固定（见映射表），脚本输出需与之一致
4. **缺日检查**：每月务必核对解析结果是否覆盖当月所有天，**缺日要显式提示用户**（累积文档偶尔漏记整天），
   不要静默跳过
5. **与附件1校验**：若附件1已有数据，逐行对比确认无错位

---

## 依赖

- `python-docx`
- 若脚本同时要写 xlsx，还需 `openpyxl`
