---
name: monthly-report-formalizer
description: 把已成稿的《数据机房值班月报》Word 草稿改写为正式、规范的汇报文本（不新增/不删减工作内容，只做体例与表述规范化）。适用于甲方反馈「月报太随意、不正式」的场景。触发词：月报不正式、月报太随意、月报规范化、月报改写、正式化月报。
agent_created: true
version: 1.0
---

# 月报正式化改写 Skill

对已写好的《数据机房值班月报》做**体例与表述规范化**，使其达到可提交甲方的正式度。

**铁律：只改写法，不改事实。** 不新增工作内容、不删减已写内容、不编造数据、
不添加「改进措施/建议/下一步计划」（避免给自己派活）。

## 一、正式化检查清单（逐条核）

### 体例 / 排版
1. **半角标点清零**：中文语句中不得出现半角 `,` `:` `;` `(` `)` `!` `?`
   （千分位 `,` 与时间 `HH:MM` 中的 `:` 除外）。这是最伤正式感的一项。
2. **日期体例统一**：`2026年07月01号` → `2026年7月1日`（去零填充、`号`改`日`）；
   区间用 `（2026年7月1日—2026年7月31日）`。
3. **数字分级**：`20747167笔` → `20,747,167笔`，表格数字同步加千分位。
4. **章节编号成体系**：一级用 `一、二、三…`，二级用 `（一）（二）…`，编号必须连续（易漏 `（二）`）。
5. **标题与目录一致**：目录若是 TOC 域，条目文字是**缓存值**，改标题后需按 F9 / 右键「更新域」刷新；
   也可直接改写域缓存文字（见技术要点）。
6. **章节标题不得带零填充月份歧义**：`08 月排班计划` → `下月排班计划`（该章讲的是下月排班）。
7. **附件章节必须有清单**：正文引用了「附件1/2/3《…》」，末尾「附件」章下必须逐条列出。

### 表格
8. 全表**表头底纹 + 加粗**统一（模板用 `B5C6EA`）。
9. 全表**字号统一**（正文 11pt 宋体，不出现 9pt 例外）。
10. **必须有「合计」行**（排班统计表合计 = 白班/中班/夜班各当月天数、总工作天数 = 天数 × 3）。
11. 表头首列标注计量单位，如 `统计内容（单位：笔）`。
12. 栏目名去口语冗余：`交易笔数总数` → `交易总笔数`；`交易笔数日平均数` → `日均交易笔数`。

### 表述
13. **巡检事件结构化**：`发现项一/发现项二` → `异常事件一/异常事件二`；
    子项固定为 `发现时间 / 情况描述 / 处置措施`（不用「问题详情」「问题解决方案」）。
14. **去掉指示代词与口语**：`发现此情况后立即上报` → `发现后立即上报`；`周六日` → `周六、周日`。
15. **数据完整且自洽**：总体段与分类段口径必须一致（总体句列的类别数 = 分类段的类别数）。
16. **百分比精确到两位**并合计 100.00%。
17. **列表按时间/数量排序**：请假人次须按日期升序，不按原稿顺序。
18. **链接前的引导语**：`详细记录见: [附件1]` → `明细详见：[附件1]`（全角冒号）。
19. **专有名词纠错**：机房配电柜为 **UPS**（常误写 `USP`）；`#ATS柜` 保留原样。

## 一点五、封面 / 页眉 / 页脚规范

- **标题必须带主体名**：正式月报标题形如 **`XX银行数据机房值班月报`**（不是「数据机房值班月报」）。
  改标题时**同步改目录首条**（目录是 TOC 域，缓存文字要一并对齐）。
- **页眉**：居中一行 `XX银行数据机房值班月报（2026年7月）`（`doc_insert_header`，
  `horizontal_align="center"`，一次处理 section 0）。
- **页脚**：居中页码（`doc_set_page_number`，`position="center"`，`format="decimal"`，
  `scope="whole_doc"`）。它和 `doc_insert_footer` **互斥**，不要连用。
- 页眉页脚原来可能**完全不存在**（无 `word/header*.xml` / `word/footer*.xml`），需新建。

## 一点六、⚠️ 致命坑：内嵌附件会被编辑器另存时丢弃

原稿末尾「附件」章下的空段落，可能是**嵌在正文里的 OLE Excel 对象**
（`<w:object>` + `o:OLEObject ProgID="Excel.Sheet.12" DrawAspect="Icon"`，各配一张图标 `word/media/imageN.png`）。

**`editor_sdk` 另存时会丢掉 `word/embeddings/*.bin` 与 `word/media/*.png`，并把正文里的 `r:id` 清空**
→ 附件不可再打开，且留下悬空引用（Word 报错）。
`doc_resolve_document_structure` / `doc_get_images` 都**看不出来**（它们只当普通空段落处理）。

**因此每次用编辑器另存后，必须手工把嵌入附件补回**（只读原稿、不动原稿）：

1. 用 `zipfile` 把 `word/embeddings/oleObject*.bin`、`word/media/image*.png` 从原稿复制进修订版包；
2. `[Content_Types].xml` 补 `<Default Extension="bin" ContentType="application/vnd.openxmlformats-officedocument.oleObject"/>`
   与 `<Default Extension="png" ContentType="image/png"/>`；
3. `word/_rels/document.xml.rels` 追加关系（**避开已被 header/footer 占用的 rId**）；
4. 正文里每个 `<w:object>` 块各有两处 `r:id=""`（先 `v:imagedata`、后 `o:OLEObject`），按「图标→OLE」顺序填回新 rId；
5. 重写 zip 时把 `[Content_Types].xml` 放在首个条目。

**验证**：所有 XML 良构 + `document.xml` 引用的每个 `r:id` 都能在 rels 找到 + 每个 rel Target 部件存在
+ `zipfile.testzip()` 为 None。

> 判断方法：`zipfile.ZipFile(原稿).namelist()` 里出现 `word/embeddings/` 就说明有内嵌附件，
> 务必按上面流程补回，否则交付物是残缺的。

## 二点五、观感升级：整套重排（HTML→DOCX 流水线）

当甲方嫌「不好看/不够正式」而不只是文字随意时，可走「生成 HTML 版式再转 docx」的流水线。

**关键决策**：整套重排会**丢掉**原 docx 的 TOC 域、内部书签超链接、页眉页脚、以及**全部内嵌 OLE 附件**。
动手前先跟用户确认要「保留结构精修」还是「整套重排」——重排必须配一套补回动作。

### 流水线要点
1. **Stage 0**：建 `output/<request_id>/{stage2,stage3,working,trace}`，确定 `output_docx_path`，写 `pipeline-state.yaml`。
2. **genre 判定**：值班月报 → `business-report` → 主题 `business-modern`，design-token 静态查表。
3. **doc-typeset**：按业务报告 HTML 骨架 + 提示词硬约束生成 HTML。
4. **html-review**：跑评审脚本，退出码 1 = 不通过；按 `actionable_feedback` 做**一次**定向修正后直接输出
   （不循环、不复检）。
5. **Stage 3**：`html_to_docx convert <html> -o <docx> --page-size A4 --margin-* 2.5/2.0`
   （边距对齐 business 主题的 layout token）。
6. **收尾必修**：按「一点六」把内嵌 OLE 附件 zip 手术补回；页眉页脚可由 HTML 的
   `@page { @top-center / @bottom-center }` 直接产出。

### 坑与规避
- **`format-extract` 在部分分发里不可用**：`dist/cli.cjs` 缺失 → 报「本地 docx2html CLI 不存在」。
  这是**分发缺陷不是网络问题**，不要试图联网修复。降级为把文档内容自己整理成 `created_content` 传下去，
  并在 yaml 记 `fallback: true / fallback_reason: content_extract_failed`。
- **html-review 的高频不通过项**：
  - `[BR-01]` 执行摘要区的 class **必须是 `.executive-summary`**；
  - `[SI-02]` **每一张 `<table>` 都要有 `<thead>`+`<tbody>`**（连 KV 型两列表也要）；
  - `[TQ-03]` `<h2>` 后不能紧跟 `<h3>`，中间要有一句章节导语。
- **转换器不支持 flex / grid / `::before` 生成内容**：多列 KPI 直接用普通 `<table>`（thead/tbody）最稳。
- **继承会断**：`text-align` / `font-size` / `color` / `font-family` 不会从父容器下发到子块——
  封面每个 `<p>` / `<h1>` 都要自己写 `text-align: center`。
- **禁装饰性短横线**：封面不要放 `<hr>`，转 docx 会变满版横线。

### 重排链路的隐藏坑（HTML→DOCX 转换层）

- **裸标签选择器不生效**：`p { }` / `h2 { }` 这类**元素选择器被完全忽略**（出参 `<w:pPr/>` 为空）。
  所有样式必须落在 **class 或内联 `style`** 上。
- **⚠️ class 的 `font-family` 在 `h1/h2/h3` 上失效**：表格 th/td、`<p>`、内联 style 都正常，唯独标题段落拿到正文宋体。
  → **对策（必做）**：转换后在 `document.xml` 里把 `<w:pStyle w:val="Heading[123]"/>` 段落内所有
  `<w:rFonts>` 强制改为 `黑体`（正式中文文档 = 黑体标题 + 宋体正文）。
- **表格单元格会被插入 CJK↔拉丁 分隔空格**（`1 天`、`2026 年 7 月 1 日`），正文段落却不会 → 体例不一致。
  这些空格是**独立的 `<w:t> </w:t>` run**，正则对原始 XML 匹配不到（空格前一字符是 `>`）。
  必须在**文本层面**处理：取出全部 `<w:t>` 内容按序，对「整段就是一个空格」的元素看其前后**可见字符**，
  一边 CJK 一边拉丁才置空。
- **TOC 域 begin 的注入位置**：定位**第一个目录条目段落**，`<w:p>` 后若有 `<w:pPr>` 就插在 pPr 之后，
  否则直接插在 `<w:p>` 之后，再用 `<w:fldChar w:fldCharType="end"/>` 收尾。
  校验：`begin` 之前不得出现任何目录条目文字。
- **converter 会把 `bookmarkStart` 插在 `<w:pPr>` 之前**，违反 OOXML 顺序（`pPr` 必须为首个子元素），
  转换后用正则 `(<w:p[^>]*>)((?:<w:bookmarkStart[^>]*/>)+)(<w:pPr>.*?</w:pPr>)` → `\1\3\2` 重排。
- **`<w:t>` 前缀正则会误吞 `<w:tabs>` / `<w:tcMar>`**：一律用 `ElementTree` 解析；
  非要用正则就写 `<w:t(?:\s[^>]*)?>`。
- **表格边框必须显式声明**：`.x { border: 1px solid var(--color-border) }`（class 里可写 `var()`），
  漏写则产出**完全无边框**。`:last-child` / `:nth-child` 伪类**不生效**，加粗「合计」行要另加 class。
- **不要用 `<caption>`**：改用表格上方一个 `<p class="tbl-cap">表N …</p>`。
- **交付前必须核对目标文件未被并发改写**：实测同目录的「-优化版」「-正式版」曾被另一进程先后替换。
  交付前用 `md5 -q` + `stat -f "%N %z bytes mtime=%Sm"` 比对；发现被抢占立即换**独立文件名**。
  取证方法：逐部件搜 `报告日期` / `pStyle w:val="2"` / 旧 `_Toc` 锚点 / `wpsCustomData`。

### 无 LibreOffice 时的交付验收清单（必跑）

1. `zipfile.testzip()` 为 `None`；`namelist()` 含 `word/embeddings/`、`word/media/`、`header1.xml`、`footer1.xml`。
2. 全部 `.xml` / `.rels` 经 `ElementTree.fromstring` 良构。
3. `document.xml` 引用的每个 `r:id` 都能在 `document.xml.rels` 找到；每个 rel `Target` 部件真实存在。
4. `<w:object>` 数 = 原稿附件数；`fldCharType="begin"` 与 `"end"` 各 1（TOC）；
   `settings.xml` 有 `<w:updateFields w:val="true"/>`。
5. `<w:pPr>` 顺序违规计数为 0。
6. `python-docx` 能 `Document(path)` 打开，节数 = 2（封面 + 正文）。
7. 原稿 `md5` + `mtime` 与本轮开始时一致。

## 三、执行流程（本地 Office 编辑通道）

1. `open_file` 打开文档，`doc_resolve_document_structure` 通读结构
2. 逐段对照检查清单，列出 `(begin, end, 新文本)`
3. **严格从文档后部往前替换**（自下而上），这样先取得的坐标不会因前面的长度变化而漂移
4. 表格改动用 `doc_set_table_cells` / `doc_insert_table_row`（`table_id` 定位，不随编辑漂移）；
   追加合计行用 `doc_insert_table_row row=<末行> insert_below=true`
5. **另存为新文件**（如 `…（规范修订版）.docx`），保留原稿供对比
6. 改动后用 `doc_resolve_document_structure` 复读全文 + `doc_find ":"` / `","` 复查半角标点

## 三、技术要点（踩过的坑）

- **`doc_replace_text` 不能跨越域占位符**，否则报
  `would break a field structure by removing only one of its paired placeholders`。
  含超链接/域的段落（「…详见：[附件N]」）**只能替换链接之前的纯文本**，且结束位置要落在域起始占位符之前
  （逐个试 end=文本末、+1、+2，取第一个成功）。
- 域指令（`HYPERLINK \l "_附件" `）**占用坐标但不显示**，因此「见」与「附件」之间的半角空格属于域指令，
  **不必也不可删**；只有域外的 `:` 需要改成 `：`。
- `doc_set_table_cells` 的 `text_format` 字号字段名是 **`font_size`**，不是 `font_size_pt`（写错会静默不生效）。
- 改标题文字会让 **TOC 域缓存**变旧；可直接 `doc_replace_text` 命中目录条目中的纯文本区间同改
  （`doc_find "六、"` + related_text 含 `PAGEREF` 即为目录条目）。
- 空段落可能承载 `bookmarkStart/_GoBack` 等占位符，**不要删除**，否则会打断指向 `_附件` 书签的内部超链接。
- `doc_to_image`（渲染预览）依赖外网上传，受限网络下会超时；本地无 LibreOffice 时**跳过视觉校验**，
  靠结构与文本复读校验。
- **别做「自动注入 file_id」的封装**：统一往每次调用塞 `file_id`，调 `open_file` 时会**同时**传
  `file_path` 和不相关的 `file_id`，把别的文档加载进本该属于另一路径的实例、污染文档池。
- **只写新文件**：本场景要求「不得改动原有文档」。全部编辑在新副本上做，收尾用 `md5` + `mtime`
  复核原稿未被触碰。
