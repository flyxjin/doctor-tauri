#!/usr/bin/env node
// 版本号同步脚本：以 package.json 为单一来源（SSOT），同步到其他需要版本号的文件
//
// 用法：
//   node scripts/sync-version.mjs
//   或通过 npm script:  npm run version:sync
//
// 同步目标：
//   1. src-tauri/Cargo.toml        —— Rust crate version（CARGO_PKG_VERSION 编译期注入）
//   2. install.bat                  —— NSIS 安装脚本 APP_VERSION 变量
//   3. distrib/install.bat          —— 分发目录的安装脚本
//
// 注意：tauri.conf.json 已移除 version 字段，Tauri 2 会自动回退到 Cargo.toml 版本号。
// CHANGELOG.md 由人工维护（含日期与变更说明），不在自动同步范围内。

import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, '..');

const pkg = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
const version = pkg.version;

if (!version || !/^\d+\.\d+\.\d+/.test(version)) {
  console.error(`[sync-version] package.json 版本号无效: ${version}`);
  process.exit(1);
}

console.log(`[sync-version] SSOT 版本号: ${version}`);

// 1. Cargo.toml
const cargoPath = join(root, 'src-tauri', 'Cargo.toml');
const cargoSrc = readFileSync(cargoPath, 'utf8');
const cargoOut = cargoSrc.replace(
  /^version\s*=\s*".*"/m,
  `version = "${version}"`,
);
if (cargoSrc === cargoOut) {
  console.log('[sync-version] Cargo.toml: 已是最新');
} else {
  writeFileSync(cargoPath, cargoOut, 'utf8');
  console.log(`[sync-version] Cargo.toml: 已同步到 ${version}`);
}

// 2 & 3. install.bat (根目录 + distrib/)
for (const rel of ['install.bat', 'distrib/install.bat']) {
  const batPath = join(root, rel);
  let batSrc;
  try {
    batSrc = readFileSync(batPath, 'utf8');
  } catch {
    console.warn(`[sync-version] 跳过不存在的文件: ${rel}`);
    continue;
  }
  // 替换 set "APP_VERSION=x.y.z"
  let batOut = batSrc.replace(
    /set\s+"APP_VERSION=\d+\.\d+\.\d+[^"]*"/,
    `set "APP_VERSION=${version}"`,
  );
  // 替换 Set-ItemProperty -Name 'DisplayVersion' -Value 'x.y.z'
  batOut = batOut.replace(
    /Set-ItemProperty\s+-Name\s+'DisplayVersion'\s+-Value\s+'[^']+'/g,
    `Set-ItemProperty -Name 'DisplayVersion' -Value '${version}'`,
  );
  if (batSrc === batOut) {
    console.log(`[sync-version] ${rel}: 已是最新`);
  } else {
    writeFileSync(batPath, batOut, 'utf8');
    console.log(`[sync-version] ${rel}: 已同步到 ${version}`);
  }
}

console.log('[sync-version] 完成。CHANGELOG.md 与 tauri.conf.json 请人工维护。');
