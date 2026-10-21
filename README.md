# lixd-skills

Personal agent skills. Each top-level directory is one self-contained skill
(`SKILL.md` + optional `scripts/`, `templates/`, `assets/`, `agents/`).

## Skills

### Datacenter duty-report pipeline (银行/金融数据中心驻场运维)

Five skills that form one end-to-end pipeline for a monthly duty-report workflow:
screenshot recognition → attachment workbooks → Word report → quarterly settlement.

| Skill | What it does |
|---|---|
| `bank-log-recognition` | Reads duty-log screenshots, extracts batch/job-cut/backup timings, validates anomalies, emits Markdown + machine-readable JSON |
| `workload-record-parser` | Parses the cumulative workload Word record into per-day call statistics |
| `monthly-report-generator` | Builds 附件1 workbook (3 sheets) + 附件2 shift roster, then renders the 5-chapter V2 monthly report from data JSON |
| `monthly-report-formalizer` | Rewrites an existing draft into formal submission style (wording/typography only, never facts) |
| `quarterly-settlement-report` | Aggregates monthly reports + daily attachment data into a period-based quarterly settlement report |

Supporting skill:

| Skill | What it does |
|---|---|
| `call-stats-aggregator` | Sums call categories across monthly workbooks for any date range, outputs Excel + Markdown |

Pipeline shape:

```
duty-log screenshots ──► bank-log-recognition ──┐
workload Word record ──► workload-record-parser ─┼──► 附件1.xlsx (3 sheets) ──┐
transaction export  ────────────────────────────┘                              ├──► monthly report (V2)
previous month roster ──► generate_schedule.py ──► 附件2.xlsx ─────────────────┘
                                                              │
                                              monthly reports + 附件1 ──► quarterly settlement report
```

### Other skills

`database-evolution-safety`, `evidence-first-project-audit`, `knowledge-base-curator`,
`real-browser-business-acceptance`, `runtime-e2e-acceptance`, `service-boundary-guardian`,
`vertical-slice-delivery`.

## Conventions for the duty-report skills

These skills are sanitized: no customer bank name, no vendor name, no personal names,
no internal host/IP, no real business figures. Placeholders are used instead:

| Placeholder | Meaning |
|---|---|
| `XX银行` | the client bank (primary institution) |
| `村镇银行` | a generic category — the secondary / village-bank institution |
| `值班员A1`、`值班员B1` … | duty staff placeholders (in `GROUPS`) |
| `项目经理` | on-site project manager (weekday/holiday shift row) |
| `XX科技有限公司` | the service provider |
| `主行 / 村镇行` | the two institution blocks in the backup sheet |

All example values in `v2_report_schema.json`, `data/quarters.json` and the bundled
`.docx` templates are **fictional**. Replace them with your own data.

### Environment variables

| Variable | Used by | Default |
|---|---|---|
| `MR_ROOT` | all duty-report scripts | current working directory |
| `MR_TEMPLATE` | `render_v2_report.py` | `monthly-report-generator/templates/月报V2模板.docx` |
| `QS_TEMPLATE` | `build_quarterly.py` | `quarterly-settlement-report/assets/季度结算模版.docx` |

Expected layout under `MR_ROOT`:

```
<MR_ROOT>/
  月报/
    26年10月/                    # <YY>年<M>月
      主行图片/  村镇图片/        # duty-log screenshots
      值班工作量记录2610.docx
      附件1《26年10月报统计数据记录表》.xlsx
      附件2《26年11月排班表》.xlsx
      XX银行数据机房-26年10月值班月报-V2.docx
  季度结算/
    2026年6-7-8-9/
```

### Python dependencies

`python-docx`, `openpyxl`, `lxml`, `pandas` (call-stats only), `chinesecalendar` (optional —
`generate_schedule.py` falls back to Mon–Fri if the holiday calendar is unavailable).

## License

MIT — see `LICENSE`.
