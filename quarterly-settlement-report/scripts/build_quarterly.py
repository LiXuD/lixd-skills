#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
季度结算报告生成器（XX银行科技运维服务项目人员外包合同）

用法：
    python3 build_quarterly.py --quarter 2026Q3            # 生成指定季度
    python3 build_quarterly.py --all                       # 生成 data/quarters.json 中全部季度
    python3 build_quarterly.py --quarter 2026Q3 --out /tmp # 输出到指定目录（试跑）
    python3 build_quarterly.py --quarter 2026Q3 --dry-run  # 只打印取数，不写文件

★ 统计口径：一律按「报告周期」（26 日界，如 6/26–9/25）逐日统计，
  数据源自各月附件1《XX月报统计数据记录表》的逐日明细（不是月报合计数）。
  附件仍挂整月月报（甲方要求每月都收到），但报告内的数据只算周期内那几天，
  因此**季度数 ≠ 各月月报合计数**，这是既定口径（用户 2026-10-20 明确）。

口径细则：
  · 值机天数 = 周期自然天数
  · 班次 = 各月排班班次 × 该月落在周期内的天数 ÷ 该月总天数（同月内每日班次数恒定，折算精确）
  · 巡检次数 = 班次数（每班次 1 次交接班巡检）
  · 交易/电话 = 附件1 逐日明细求和；电话分类占比 = 单项 / 周期电话总数
  · 预警起数 = 各月月报「预警N」条目中，发生时间落在周期内的
  · 批处理耗时 = 周期内逐日耗时的算术平均
  · 一律不体现处罚/罚款
"""
import argparse
import calendar
import copy
import json
import os
import re
import sys
from datetime import date
from statistics import mean

import docx

# 项目根目录：优先取环境变量 MR_ROOT，其次取当前工作目录
ROOT = os.environ.get("MR_ROOT") or os.getcwd()
MB_ROOT = os.path.join(ROOT, "月报")
QS_ROOT = os.path.join(ROOT, "季度结算")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(HERE), "data")
ASSETS = os.path.join(os.path.dirname(HERE), "assets")

sys.path.insert(0, HERE)
from period_data import period_sum, period_alerts  # noqa: E402

# 模版查找顺序：环境变量 QS_TEMPLATE → skill 自带 assets 快照
TEMPLATE_CANDIDATES = [
    os.environ.get("QS_TEMPLATE") or "",
    os.path.join(ASSETS, "季度结算模版.docx"),
]

# 模版段落索引（2026-10-20 用户调整后版本，共 54 段）
IDX = dict(
    p_period=3, p_staff=4, p_core=6, p_task=7, p_doc=8,
    p_leave=12, p_extra=16, p_report=18, p_conclusion=27,
    attach_title=48, attach_first=49, attach_last=52,
)

CAT_ORDER = ["柜员强制签退", "银行业务问题", "数据查询业务", "终端变更", "人为操作失误",
             "设备故障异常", "系统异常故障", "网络设备问题", "基础设施问题",
             "机房环境", "服务器设备问题"]
CAT_LABEL = {
    "柜员强制签退": "柜员强制签退需求", "银行业务问题": "银行业务问题",
    "数据查询业务": "数据查询业务问题", "终端变更": "终端变更需求",
    "人为操作失误": "人为操作失误问题", "设备故障异常": "设备故障异常问题",
    "系统异常故障": "系统异常故障问题", "网络设备问题": "网络设备问题",
    "基础设施问题": "基础设施问题", "机房环境": "机房环境问题",
    "服务器设备问题": "服务器设备问题",
}
CAT_MERGE = {"支行设备故障": "设备故障异常"}

FIXED_STAFF = ("人员配置方面，本项目运维保障团队共配置 9 人，其中 8 名专职值守人员划分为 4 个班组，"
               "采用四班三倒模式实现机房 7×24 小时不间断值守；另设 1 名项目经理，统筹项目管理并承担机动补位职责，"
               "应对人员临时异常情况，保障值守工作连续稳定。本周期内机房未发生重大运行中断事件，"
               "各项保障工作均符合甲方标准要求。")
STARTUP_TAIL = ("本周期为项目启动阶段，2025 年 9 月 26 日首名运维人员入场启动值机工作，至 10 月 20 日完成合同约定的 "
                "9 人团队组建；人员到位前通过 “在岗人员轮换 + 项目经理顶岗支援” 的方式，确保机房值守无空缺，"
                "业务保障不中断。")


def n(x):
    return f"{x:,}"


# ---------------------------------------------------------------- 月报辅助
def month_path(y, m):
    folder = os.path.join(MB_ROOT, f"{str(y)[2:]}年{m}月")
    tag = f"{str(y)[2:]}年{m}月"
    if not os.path.isdir(folder):
        raise FileNotFoundError(f"月报目录不存在：{folder}")
    for f in sorted(os.listdir(folder)):
        if f.endswith("-V2.docx") and tag in f:
            return os.path.join(folder, f)
    raise FileNotFoundError(f"{folder} 下找不到含「{tag}」的 *-V2.docx")


def parse_month(path):
    """读月报：班次数与请假句（其余数据一律走附件1 逐日）"""
    d = docx.Document(path)
    t = "\n".join(p.text for p in d.paragraphs).replace(" ", "")
    m2 = re.search(r"本月值机[^。]*?(\d+)天[、，](?:共计)?(\d+)个班次", t)
    if not m2:
        raise ValueError(f"无法解析值机班次：{path}")
    leave = ""
    for p in d.paragraphs:
        if "个班次。" in p.text and "请假" in p.text:
            seg = p.text.split("个班次。", 1)[1]
            leave = seg.split("；其余值机人员")[0].strip().rstrip("。；")
            break
    return dict(days=int(m2.group(1)), shifts=int(m2.group(2)), leave=leave)


def months_between(start, end):
    y, m = start.year, start.month
    out = []
    while (y, m) <= (end.year, end.month):
        out.append((y, m))
        m += 1
        if m > 12:
            m, y = 1, y + 1
    return out


def overlap_days(start, end, y, m):
    dim = calendar.monthrange(y, m)[1]
    a = max(start, date(y, m, 1))
    b = min(end, date(y, m, dim))
    return max(0, (b - a).days + 1)


# ---------------------------------------------------------------- 周期汇总
def aggregate(q):
    start = date(*map(int, q["period_start"].split("-")))
    end = date(*map(int, q["period_end"].split("-")))
    s = period_sum(start, end)

    shifts = 0.0
    for y, m in months_between(start, end):
        rep = parse_month(month_path(y, m))
        dim = calendar.monthrange(y, m)[1]
        # 分母用「该月月报实际覆盖天数」：25年9月 只覆盖 9/26-9/30 共 5 天
        base = rep["days"] or dim
        shifts += rep["shifts"] * overlap_days(start, end, y, m) / base
    s["shifts"] = round(shifts)
    s["inspect"] = s["shifts"]                      # 每班次 1 次交接班巡检
    s["calls_total"] = s["call_total"]
    s["branch_avg"] = round(mean(s["branch"])) if s["branch"] else 0
    s["main_avg"] = round(mean(s["main"])) if s["main"] else 0
    s["branch_range"] = (round(min(s["branch"])), round(max(s["branch"]))) if s["branch"] else (0, 0)
    s["main_range"] = (round(min(s["main"])), round(max(s["main"]))) if s["main"] else (0, 0)

    alerts = period_alerts(start, end)
    s["warn"] = len(alerts)
    s["alert_titles"] = [t for _, t in alerts]
    s["start"], s["end"] = start, end
    return s


def cats_text(s):
    parts = []
    for k in CAT_ORDER:
        v = s["calls"].get(k, 0)
        if v:
            parts.append(f"{CAT_LABEL[k]} {n(v)} 个（{v / s['calls_total'] * 100:.2f}%）")
    return "、".join(parts)


# ---------------------------------------------------------------- 写入工具
def set_para(p, text):
    runs = p.runs
    if not runs:
        p.add_run(text)
        return
    runs[0].text = text
    for r in runs[1:]:
        r._element.getparent().remove(r._element)


def set_cell(cell, text):
    ps = cell.paragraphs
    set_para(ps[0], text)
    for p in ps[1:]:
        p._element.getparent().remove(p._element)


def loc_template():
    for p in TEMPLATE_CANDIDATES:
        if os.path.exists(p):
            return p
    raise FileNotFoundError("找不到季度结算模版，请检查 assets/季度结算模版-2026Q3.docx")


# ---------------------------------------------------------------- 生成
def build(q, out_dir=None, dry=False):
    s = aggregate(q)
    nar = q.get("narratives", {}) or {}
    months = [tuple(int(x) for x in m.split("-")) for m in q["months"]]

    warn_list = nar.get("warn_list") or (
        "、".join(s["alert_titles"]) + "等事件" if s["alert_titles"] else "无")
    batch_note = nar.get("batch_note") or (
        f"村镇银行日终批量平均耗时 {s['branch_avg']} 分钟，XX银行日终批量平均耗时 {s['main_avg']} 分钟")
    sys_note = nar.get("sys_note") or (
        "本周期内XX银行、村镇银行核心系统运行总体平稳，系统类异常均已随巡检预警闭环处置，未发生核心系统中断。")

    raw_leave = []
    for y, m in months_between(s["start"], s["end"]):
        lv = parse_month(month_path(y, m))["leave"]
        if lv and "无请假" not in lv:
            raw_leave.append(re.sub(r"[，；]?(请假期间|当天由|请假当天由).*$", "", lv))
    leave = nar.get("leave") or (("本周期内" + "；".join(raw_leave) +
                                 "；请假期间由项目经理顶岗补位，全程保障机房值守无空缺、运行不间断。")
                                if raw_leave else
                                "本周期内无请假记录，全体值机人员均严格遵守考勤要求按时到岗。")
    note = [k for k, v in (("请假段", nar.get("leave")), ("预警清单", nar.get("warn_list")),
                           ("批量耗时说明", nar.get("batch_note")), ("系统级预警", nar.get("sys_note"))) if not v]

    y1, m1, d1 = q["period_start"].split("-")
    y2, m2, d2 = q["period_end"].split("-")
    period_dot = f"{y1}年{m1}月{d1}日-{y2}年{m2}月{d2}日"
    period_cn = f"{y1} 年 {m1} 月 {d1} 日 - {y2} 年 {m2} 月 {d2} 日"
    span = f"{m1}-{m2}"
    delivery = "、".join(f"{int(x.split('-')[1])} 月" for x in q["months"])
    delivery2 = [x.split("-")[1] for x in q["months"]]
    attach = [(x.split("-")[0], x.split("-")[1]) for x in q["months"]]

    if dry:
        print(f"\n=== {q['id']}  {q['period_start']} ~ {q['period_end']}  ({s['days']} 天，附件 {len(attach)} 份月报)")
        print(f"    值机 {s['days']} 天 / {s['shifts']} 班次 | 巡检 {s['inspect']} 次 | 预警 {s['warn']} 起")
        print(f"    交易 {n(s['tot'])} (核{n(s['core'])}+付{n(s['pay'])}+网{n(s['wl'])}+银{n(s['yl'])})")
        print(f"    电话 {n(s['calls_total'])}：{cats_text(s)}")
        print(f"    批量均值 村镇 {s['branch_avg']} 分钟（{s['branch_range'][0]}-{s['branch_range'][1]}）"
              f" XX银行 {s['main_avg']} 分钟（{s['main_range'][0]}-{s['main_range'][1]}）")
        print(f"    预警：{'、'.join(s['alert_titles'])}")
        print(f"    请假：{leave}")
        if note:
            print(f"    ⚠ 自动草稿：{'、'.join(note)}")
        return None, s, note

    doc = docx.Document(loc_template())
    ps = doc.paragraphs

    cover = doc.tables[0]
    assert cover.rows[1].cells[0].text.strip().startswith("报告周期"), "模版封面结构已变，请复核"
    set_cell(cover.rows[1].cells[1], period_dot)

    set_para(ps[IDX["p_period"]],
             f"本次项目工作总结周期（{period_cn}），项目团队严格按照《XX银行股份有限公司科技运维服务项目人员外包合同》"
             f"及工作说明书要求，完成XX银行数据机房全周期科技运行保障工作。核心满足 “7*24 小时值守在岗”"
             f"“突发问题即时响应”“业务流程规范执行” 三大核心需求，期间机房无重大运行中断事件，各项保障工作符合甲方标准。"
             f"本周期累计值机 {s['days']} 天、{s['shifts']} 个班次，监测核心、支付、网联、银联四大系统交易合计 "
             f"{n(s['tot'])} 笔，接听并记录业务来电 {n(s['calls_total'])} 通，处置机房巡检预警 {s['warn']} 起。")
    set_para(ps[IDX["p_staff"]], FIXED_STAFF + (STARTUP_TAIL if nar.get("startup") else ""))
    set_para(ps[IDX["p_core"]],
             f"核心保障进度：全程保障XX银行数据机房 7*24 小时连续运行，无任何因人员值守缺失、响应延迟导致的进度偏差，"
             f"{span} 月机房整体运行稳定性达 100%。")
    set_para(ps[IDX["p_task"]],
             "关键任务进度：系统交易监测、日常巡检、日终批处理监测等关键任务均按计划完成。" + (nar.get("new_task") or ""))
    set_para(ps[IDX["p_doc"]],
             f"文档交付进度：提前一周完成下月值班表编制和按月度完成 {delivery}值班月报编制，无文档延迟交付情况。")
    set_para(ps[IDX["p_leave"]], leave)

    tb = doc.tables[1]
    set_cell(tb.rows[1].cells[2],
             f"共接听电话 {n(s['calls_total'])} 个，其中{cats_text(s)}；接听电话平均响应时长＜2 分钟，问题解决率 100%。")
    set_cell(tb.rows[2].cells[2],
             f"本周期累计巡检 {s['inspect']} 次，处置预警信息 {s['warn']} 起，包括：{warn_list}，均已闭环解决，无遗留风险。")
    set_cell(tb.rows[3].cells[2],
             f"本周期批处理监测、日终切换、数据库备份全部做到详细记录，监测记录 100% 覆盖；{batch_note}。"
             f"每日批处理详细时间可查阅各月附件 1《报统计数据记录表》。")
    set_cell(tb.rows[4].cells[2], sys_note)

    set_para(ps[IDX["p_extra"]], nar.get("extra") or
             "协助甲方完成机房外来人员接待登记、年度资产盘点等工作，协作响应率 100%。")
    report_items = "".join(f"《XX银行数据机房 {m} 月值班月报》" for m in delivery2)
    set_para(ps[IDX["p_report"]],
             f"报表编制：本周期按甲方要求编制{report_items}各 1 份，报表涵盖人员变动、人员考勤、交易监测、"
             f"巡检事件、批量处理、数据安全等核心内容；附件为各月整月月度报告，本报告所列数据按报告周期"
             f"（{y1} 年 {m1} 月 {d1} 日—{y2} 年 {m2} 月 {d2} 日）统计。")

    concl = ps[IDX["p_conclusion"]]
    old = concl.text
    set_para(concl, old.replace(old[old.index("（") + 1: old.index("）")], q["qlabel"]))

    p_first, p_last = IDX["attach_first"], IDX["attach_last"]
    have = p_last - p_first + 1
    if len(attach) < have:
        for i in range(p_first + len(attach), p_last + 1):
            el = ps[i]._element
            el.getparent().remove(el)
        ps = doc.paragraphs
    elif len(attach) > have:
        for _ in range(len(attach) - have):
            src = ps[p_last]._element
            src.addnext(copy.deepcopy(src))
            ps = doc.paragraphs
    for i, (y, m) in enumerate(attach):
        set_para(ps[p_first + i], f"《{y} 年 {m} 月XX银行数据机房值班月报》")

    folder = os.path.join(out_dir, q["folder"]) if out_dir else os.path.join(QS_ROOT, q["folder"])
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, q["out"])
    doc.save(path)
    return path, s, note


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quarter")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--config", default=os.path.join(DATA_DIR, "quarters.json"))
    a = ap.parse_args()

    cfg = json.load(open(a.config, encoding="utf-8"))
    quarters = cfg["quarters"]
    if not a.all:
        quarters = [q for q in quarters if q["id"] == a.quarter]
        if not quarters:
            sys.exit(f"quarters.json 中没有 id={a.quarter} 的季度")

    for q in quarters:
        r = build(q, out_dir=a.out, dry=a.dry_run)
        if a.dry_run:
            continue
        path, s, note = r
        print(f"OK  {path}")
        print(f"    {s['days']}天/{s['shifts']}班次 | 交易 {n(s['tot'])} | 电话 {n(s['calls_total'])} "
              f"| 预警 {s['warn']} | 巡检 {s['inspect']}")
        if note:
            print(f"    ⚠ 自动草稿，请人工润色后写入 data/quarters.json：{'、'.join(note)}")


if __name__ == "__main__":
    main()
