#!/usr/bin/env node
// 软件著作权登记 · 源代码鉴别材料生成器
//
// 依据中国版权保护中心的鉴别材料要求：
// - 源程序：前、后各连续 30 页（共 60 页）；整段程序不足 60 页时全部提交
// - 每页不少于 50 行（本脚本固定 50 行/页）
// - 页眉标注软件名称 + 版本号，页码连续
//
// 用法：
//   node scripts/copyright-package.mjs              # 生成到 copyright-output/
//   node scripts/copyright-package.mjs --open       # 生成后用浏览器打开（可直接打印为 PDF）
//
// 输出：
//   copyright-output/source-listing.html   打印就绪的鉴别材料（浏览器打开 → 打印 → 另存 PDF）
//   copyright-output/line-count.txt        各文件行数明细 + 总行数（申请表"源程序量"栏填写依据）
//
// 说明：申请表"开发的软件程序量"按总行数（含空行注释）填写即可；本脚本同时给出
//       非空非注释口径，按需取用。

import { readFileSync, writeFileSync, mkdirSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { execSync } from 'node:child_process';

const ROOT = join(import.meta.dirname, '..');
const OUT_DIR = join(ROOT, 'copyright-output');
const OPEN = process.argv.includes('--open');

const SOFTWARE_NAME = '中药材销售管理系统';
const VERSION = JSON.parse(readFileSync(join(ROOT, 'package.json'), 'utf8')).version;
const LINES_PER_PAGE = 50;
const PAGES_HEAD = 30;
const PAGES_TAIL = 30;

// 源文件清单：git 跟踪的文件按扩展名过滤，保证与仓库实际内容一致；
// 排除锁文件/生成物。顺序：后端核心 → 前端入口 → 页面/组件 → 数据/样式 → SQL
const ORDER_HINTS = [
  'src-tauri/src/main.rs',
  'src-tauri/src/lib.rs',
  'src-tauri/src/db.rs',
  'src-tauri/src/commands.rs',
  'src-tauri/src/updater.rs',
  'src-tauri/src/models.rs',
  'src-tauri/src/compatibility.rs',
  'src/main.tsx',
  'src/App.tsx',
];
const EXT_WHITELIST = ['.rs', '.ts', '.tsx', '.sql', '.css'];
const EXCLUDE = [
  'package-lock.json',
  'src/vite-env.d.ts',
];

function trackedFiles() {
  const out = execSync('git ls-files', { cwd: ROOT, encoding: 'utf8' })
    .split('\n')
    .map((s) => s.trim())
    .filter(Boolean);
  // 只保留源代码扩展名；锁文件/配置 JSON/类型声明不进鉴别材料
  return out.filter(
    (f) =>
      !EXCLUDE.includes(f) &&
      !f.endsWith('.json') &&
      EXT_WHITELIST.some((ext) => f.endsWith(ext)),
  );
}

function orderFiles(files) {
  const rest = files.filter((f) => !ORDER_HINTS.includes(f));
  rest.sort((a, b) => {
    const rank = (f) => (f.startsWith('src-tauri/') ? 0 : f.startsWith('src/') ? 1 : 2);
    return rank(a) - rank(b) || a.localeCompare(b);
  });
  const head = ORDER_HINTS.filter((h) => files.includes(h));
  return [...head, ...rest];
}

// ==================== 主流程 ====================

const all = orderFiles(trackedFiles());
const report = [];
const blocks = []; // { file, lines: string[] }

let total = 0;
for (const f of all) {
  const content = readFileSync(join(ROOT, f), 'utf8');
  const lines = content.split('\n');
  // 去掉文件末尾多余的纯空行（保留一个）
  while (lines.length > 1 && lines[lines.length - 1].trim() === '') lines.pop();
  const nonEmpty = lines.filter((l) => l.trim() && !/^\s*(\/\/|#)/.test(l)).length;
  report.push({ file: f, total: lines.length, code: nonEmpty });
  total += lines.length;
  blocks.push({ file: f, lines });
}

// 拼接为连续源程序流：每段之间以文件头注释行分隔
const stream = [];
for (const b of blocks) {
  stream.push(`// ============ 文件: ${b.file} ============`);
  stream.push(...b.lines);
  stream.push('');
}

const totalPages = Math.ceil(stream.length / LINES_PER_PAGE);
const keepHead = totalPages <= PAGES_HEAD + PAGES_TAIL ? totalPages : PAGES_HEAD;
const keepTail = totalPages <= PAGES_HEAD + PAGES_TAIL ? 0 : PAGES_TAIL;

// 选页：不足 60 页全部提交；否则前 30 页 + 后 30 页
const pageIndices = [];
for (let p = 0; p < keepHead; p++) pageIndices.push(p);
if (keepTail > 0) {
  for (let p = totalPages - keepTail; p < totalPages; p++) pageIndices.push(p);
}

const escape = (s) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

const pagesHtml = pageIndices
  .map((pageNo, seq) => {
    const start = pageNo * LINES_PER_PAGE;
    const slice = stream.slice(start, start + LINES_PER_PAGE);
    while (slice.length < LINES_PER_PAGE) slice.push('');
    const body = slice
      .map((l) => `<span class="ln">${escape(l) || ' '}</span>`)
      .join('\n');
    return `
<section class="page">
  <header>${SOFTWARE_NAME} V${VERSION}&emsp;&emsp;第 ${seq + 1} 页 / 共 ${pageIndices.length} 页</header>
  <pre>${body}</pre>
</section>`;
  })
  .join('\n');

const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>${SOFTWARE_NAME} V${VERSION} 源程序鉴别材料</title>
<style>
  /* A4 纵向，每 section 一页；浏览器打印时勾选"背景图形" */
  @page { size: A4 portrait; margin: 18mm 16mm 16mm 16mm; }
  * { box-sizing: border-box; }
  body { margin: 0; font-family: "SimSun", "宋体", monospace; color: #000; }
  .page { page-break-after: always; }
  .page:last-child { page-break-after: auto; }
  header {
    font-size: 10.5pt; border-bottom: 1px solid #000;
    padding-bottom: 2mm; margin-bottom: 3mm; font-family: "SimHei", "黑体", sans-serif;
  }
  pre {
    margin: 0; padding: 0; white-space: pre-wrap; word-break: break-all;
    font-size: 9pt; line-height: 1.28; font-family: "SimSun", "宋体", monospace;
  }
  .ln { display: block; min-height: 1.28em; }
  @media print { .page { height: auto; } }
</style>
</head>
<body>
${pagesHtml}
</body>
</html>`;

mkdirSync(OUT_DIR, { recursive: true });
const htmlPath = join(OUT_DIR, 'source-listing.html');
writeFileSync(htmlPath, html, 'utf8');

// 行数明细
const totalCode = report.reduce((s, r) => s + r.code, 0);
const byLang = {};
for (const r of report) {
  const ext = r.file.slice(r.file.lastIndexOf('.'));
  byLang[ext] = byLang[ext] || { total: 0, code: 0, files: 0 };
  byLang[ext].total += r.total;
  byLang[ext].code += r.code;
  byLang[ext].files += 1;
}
const reportLines = [
  `${SOFTWARE_NAME} V${VERSION} 源程序量统计（申请表"开发的软件程序量"栏参考）`,
  `生成时间：${new Date().toLocaleString('zh-CN')}`,
  '',
  `总行数（含空行与注释，登记常用口径）：${total} 行`,
  `代码行数（非空、非注释行）：${totalCode} 行`,
  `源文件数：${report.length} 个`,
  '',
  '按语言汇总：',
  ...Object.entries(byLang).map(
    ([ext, v]) => `  ${ext.padEnd(5)} 文件 ${String(v.files).padStart(3)} 个 | 总行 ${String(v.total).padStart(6)} | 代码行 ${String(v.code).padStart(6)}`,
  ),
  '',
  `鉴别材料：源程序共 ${totalPages} 页（50 行/页），本次提交前 ${keepHead} 页${keepTail ? ` + 后 ${keepTail} 页（共 ${pageIndices.length} 页）` : '（全部）'}`,
  '',
  '按文件明细：',
  ...report.map((r) => `  ${String(r.total).padStart(6)} 行  ${r.file}`),
];
const reportPath = join(OUT_DIR, 'line-count.txt');
writeFileSync(reportPath, reportLines.join('\n'), 'utf8');

console.log(`[copyright] ${SOFTWARE_NAME} V${VERSION}`);
console.log(`[copyright] 源程序总行数: ${total}（代码行 ${totalCode}），文件 ${report.length} 个`);
console.log(`[copyright] 鉴别材料: ${totalPages} 页 -> 提交 ${pageIndices.length} 页（前 ${keepHead} + 后 ${keepTail}）`);
console.log(`[copyright] 已生成: ${htmlPath}`);
console.log(`[copyright] 已生成: ${reportPath}`);
console.log('[copyright] 打开 HTML → 浏览器打印 → 另存为 PDF（勾选背景图形）即为提交用 PDF');

if (OPEN) {
  const { platform } = process;
  const cmd = platform === 'win32' ? `start "" "${htmlPath}"` : platform === 'darwin' ? `open "${htmlPath}"` : `xdg-open "${htmlPath}"`;
  execSync(cmd, { shell: platform === 'win32' ? 'cmd.exe' : undefined });
}
