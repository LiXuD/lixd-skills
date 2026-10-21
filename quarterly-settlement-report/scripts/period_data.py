#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按「报告周期」逐日取数：解析各月附件1《XX月报统计数据记录表》的逐日明细，
按起止日期过滤后汇总，供季度结算报告使用。

三张表：
  · 4大系统交易量详情  日期 | 核心 | 支付 | 网联 | 银联
  · 接听电话详情      日期 | 11 类问题
  · 数据库备份详情    日期 | 批量开始 | 批量结束 | 耗时 | …（村镇银行块 + 主行块）
"""
import os
import re
from datetime import date, timedelta

import openpyxl

# 月报根目录：优先取环境变量 MR_ROOT，其次取当前工作目录
ROOT = os.environ.get("MR_ROOT") or os.getcwd()
MB_ROOT = os.path.join(ROOT, "月报")

# 附件1 放在各月文件夹；25年9月的数据在 25年10月的「9-10月」表里
ATT1_OVERRIDE = {
    "2025-09": ("25年10月", "附件1《2025年9-10月报统计数据记录表》.xlsx"),
}

DATE_RE = re.compile(r"(\d{1,2})\s*月\s*(\d{1,2})\s*[号日]")


def att1_path(y, m):
    key = f"{y:04d}-{m:02d}"
    if key in ATT1_OVERRIDE:
        folder, name = ATT1_OVERRIDE[key]
        return os.path.join(MB_ROOT, folder, name)
    folder = os.path.join(MB_ROOT, f"{str(y)[2:]}年{m}月")
    if not os.path.isdir(folder):
        raise FileNotFoundError(folder)
    for f in sorted(os.listdir(folder)):
        if f.startswith("附件1") and f.endswith(".xlsx"):
            return os.path.join(folder, f)
    raise FileNotFoundError(f"{folder} 下没有 附件1*.xlsx")


def _cell_date(v, y, m):
    """把「9月26号」/datetime 转成 date，非日期行返回 None"""
    if v is None:
        return None
    if hasattr(v, "year") and hasattr(v, "month") and hasattr(v, "day"):
        return date(v.year, v.month, v.day)
    s = str(v)
    mm = DATE_RE.search(s)
    if not mm:
        return None
    mo, dd = int(mm.group(1)), int(mm.group(2))
    yy = y
    if mo == 12 and m == 1:      # 12 月的表里偶尔出现跨年
        yy = y - 1
    try:
        return date(yy, mo, dd)
    except ValueError:
        return None


def _num(v):
    if v is None or v == "":
        return 0
    if isinstance(v, (int, float)):
        return v
    s = str(v).replace(",", "").strip()
    try:
        return float(s)
    except ValueError:
        return 0


def load_month(y, m):
    """返回 {date: {...}}，以及该表的字段口径信息"""
    wb = openpyxl.load_workbook(att1_path(y, m), data_only=True)
    sh = {s.title: s for s in wb.worksheets}
    mk = lambda kw: next((s for t, s in sh.items() if kw in t), None)

    days = {}

    def slot(d):
        return days.setdefault(d, dict(core=0, pay=0, wl=0, yl=0, calls={}, branch_min=None, main_min=None))

    # --- 交易
    ws = mk("交易")
    hdr = [str(c.value).strip() if c.value else "" for c in ws[1]]
    idx = {}
    for i, h in enumerate(hdr):
        for kw, k in (("核心", "core"), ("支付", "pay"), ("网联", "wl"), ("银联", "yl")):
            if kw in h and k not in idx:
                idx[k] = i
    for row in ws.iter_rows(min_row=2, values_only=True):
        d = _cell_date(row[0], y, m)
        if not d:
            continue
        s = slot(d)
        for k, i in idx.items():
            s[k] += int(_num(row[i]))

    # --- 电话
    ws = mk("电话")
    hdr = [str(c.value).strip() if c.value else "" for c in ws[1]]
    for row in ws.iter_rows(min_row=2, values_only=True):
        d = _cell_date(row[0], y, m)
        if not d:
            continue
        s = slot(d)
        for i, h in enumerate(hdr):
            if i == 0 or not h:
                continue
            v = int(_num(row[i]))
            if v:
                s["calls"][h] = s["calls"].get(h, 0) + v

    # --- 备份（村镇 / 主行 两块）
    ws = mk("备份")
    cur = None
    for row in ws.iter_rows(min_row=1, values_only=True):
        a = str(row[0]).strip() if row[0] is not None else ""
        b = str(row[1]).strip() if len(row) > 1 and row[1] is not None else ""
        if a == "日期" or (not a and "银行" in b):
            if "村镇" in b:
                cur = "branch"
            elif "XX" in b:
                cur = "main"
            continue
        if a in ("平均时长", "") or not cur:
            continue
        d = _cell_date(row[0], y, m)
        if not d:
            continue
        dur = _num(row[3]) if len(row) > 3 else 0
        if dur:
            slot(d)["branch_min" if cur == "branch" else "main_min"] = dur
    return days


def period_days(start, end):
    """周期内所有日期（含首尾）"""
    out, d = [], start
    while d <= end:
        out.append(d)
        d += timedelta(days=1)
    return out


def period_sum(start, end):
    """按周期逐日汇总；跨月的天数从相邻月附件1 取"""
    days = {}
    y, m = start.year, start.month
    months = []
    while (y, m) <= (end.year, end.month):
        months.append((y, m))
        m += 1
        if m > 12:
            m, y = 1, y + 1
    for yy, mm in months:
        for d, v in load_month(yy, mm).items():
            if start <= d <= end:
                days[d] = v

    res = dict(
        days=len(period_days(start, end)),
        covered=len(days),
        core=sum(v["core"] for v in days.values()),
        pay=sum(v["pay"] for v in days.values()),
        wl=sum(v["wl"] for v in days.values()),
        yl=sum(v["yl"] for v in days.values()),
        calls={},
        branch=[v["branch_min"] for v in days.values() if v["branch_min"]],
        main=[v["main_min"] for v in days.values() if v["main_min"]],
        missing=[d for d in period_days(start, end) if d not in days],
    )
    for v in days.values():
        for k, n in v["calls"].items():
            res["calls"][k] = res["calls"].get(k, 0) + n
    res["tot"] = res["core"] + res["pay"] + res["wl"] + res["yl"]
    res["call_total"] = sum(res["calls"].values())
    return res


ALERT_DATE_RE = re.compile(r"发生时间[:：]\s*(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日")
ALERT_TITLE_RE = re.compile(r"^预警[一二三四五六七八九十]+[:：]\s*(.+)$")


def alerts_in(y, m):
    """从该月 V2 月报正文提取 [(date, 标题)]"""
    import docx
    from build_quarterly import month_path
    d = docx.Document(month_path(y, m))
    paras = [p.text.strip() for p in d.paragraphs]
    out = []
    for i, t in enumerate(paras):
        mt = ALERT_TITLE_RE.match(t)
        if not mt:
            continue
        when = None
        for j in range(i + 1, min(i + 5, len(paras))):
            md = ALERT_DATE_RE.search(paras[j])
            if md:
                try:
                    when = date(int(md.group(1)), int(md.group(2)), int(md.group(3)))
                except ValueError:
                    when = None
                break
        out.append((when, mt.group(1).strip()))
    return out


def period_alerts(start, end):
    """周期内预警事件（按发生时间过滤；跨月需覆盖相邻月份）"""
    y, m = start.year, start.month
    months = []
    while (y, m) <= (end.year, end.month):
        months.append((y, m))
        m += 1
        if m > 12:
            m, y = 1, y + 1
    res = []
    for yy, mm in months:
        for when, title in alerts_in(yy, mm):
            if when and start <= when <= end:
                res.append((when, title))
    res.sort(key=lambda x: x[0])
    return res
