#!/usr/bin/env node
// 一键发布脚本：构建 → SHA256 侧车 → 推送 tag → 创建 Gitee Release 并上传产物
//
// 用法：
//   GITEE_TOKEN=xxx npm run release            # 完整发布
//   npm run release -- --dry-run               # 只打印计划，不做任何发布动作
//   npm run release -- --skip-build            # 跳过构建（产物已存在时）
//   npm run release -- --force                 # 允许版本不高于线上最新 Release（重发用）
//   npm run release -- --skip-build --dry-run  # 组合可用
//
// 前置条件：
//   1. Gitee 私人令牌（权限勾选 projects）：https://gitee.com/profile/personal_access_tokens
//      通过环境变量 GITEE_TOKEN 传入
//   2. 工作区干净、位于 master 分支
//   3. package.json 版本号必须大于 Gitee 线上最新 Release（防重复发布，--force 可绕过）
//
// 产物路径（与 Tauri 默认输出一致）：
//   src-tauri/target/x86_64-pc-windows-msvc/release/bundle/nsis/*_x64-setup.exe
//   src-tauri/target/x86_64-pc-windows-msvc/release/medicine-system.exe

import { execSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { basename, join } from 'node:path';

const REPO_ROOT = join(import.meta.dirname, '..');
const RELEASE_TARGET = 'x86_64-pc-windows-msvc';
const NSIS_DIR = `src-tauri/target/${RELEASE_TARGET}/release/bundle/nsis`;

// ==================== 参数 ====================

const args = new Set(process.argv.slice(2));
const DRY_RUN = args.has('--dry-run');
const SKIP_BUILD = args.has('--skip-build');
const FORCE = args.has('--force');
const TOKEN = process.env.GITEE_TOKEN || '';

const log = (...m) => console.log('[release]', ...m);
const die = (msg) => {
  console.error(`[release] ❌ ${msg}`);
  process.exit(1);
};

// ==================== 工具 ====================

function git(cmd) {
  return execSync(`git ${cmd}`, { cwd: REPO_ROOT, encoding: 'utf8' }).trim();
}

function run(cmd) {
  execSync(cmd, { cwd: REPO_ROOT, stdio: 'inherit' });
}

async function giteeApi(pathname, { method = 'GET', body } = {}) {
  const sep = pathname.includes('?') ? '&' : '?';
  const res = await fetch(`https://gitee.com/api/v5${pathname}${sep}access_token=${TOKEN}`, {
    method,
    body,
  });
  const text = await res.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    data = text;
  }
  if (!res.ok) {
    const detail = typeof data === 'object' ? JSON.stringify(data) : String(data).slice(0, 200);
    throw new Error(`Gitee API ${method} ${pathname} 失败（HTTP ${res.status}）：${detail}`);
  }
  return data;
}

/** 从 CHANGELOG 提取指定版本的发布说明（## [x.y.z] 起到下一个 ## 或分隔线止） */
function extractChangelogSection(changelog, version) {
  const lines = changelog.split('\n');
  const start = lines.findIndex((l) => l.startsWith(`## [${version}]`));
  if (start < 0) return '';
  const rest = lines.slice(start + 1);
  const end = rest.findIndex((l) => /^## \[|^---\s*$/.test(l));
  return [lines[start], ...(end < 0 ? rest : rest.slice(0, end))].join('\n').trim();
}

function sha256File(path) {
  const h = createHash('sha256');
  h.update(readFileSync(path));
  return h.digest('hex');
}

function writeSidecar(path) {
  const digest = sha256File(path);
  writeFileSync(`${path}.sha256`, `${digest}  ${basename(path)}\n`, 'utf8');
  return digest;
}

/** 语义化版本比较：a > b 返回 1，相等 0，小于 -1 */
function compareVersions(a, b) {
  const pa = a.replace(/^v/, '').split('.').map(Number);
  const pb = b.replace(/^v/, '').split('.').map(Number);
  const len = Math.max(pa.length, pb.length);
  for (let i = 0; i < len; i++) {
    const d = (pa[i] || 0) - (pb[i] || 0);
    if (d !== 0) return Math.sign(d);
  }
  return 0;
}

// ==================== 主流程 ====================

async function main() {
  const pkg = JSON.parse(readFileSync(join(REPO_ROOT, 'package.json'), 'utf8'));
  const version = pkg.version;
  const tag = `v${version}`;
  log(`目标版本：${tag}`);

  // ---- 1. 预检 ----
  const branch = git('rev-parse --abbrev-ref HEAD');
  if (branch !== 'master') die(`必须在 master 分支发布，当前在 ${branch}`);
  if (git('status --porcelain')) die('工作区存在未提交改动，请先提交（git status 查看）');
  log('预检通过：master 分支，工作区干净');

  if (!DRY_RUN && !TOKEN) {
    die('缺少 GITEE_TOKEN 环境变量（Gitee 私人令牌，权限勾选 projects）');
  }

  // ---- 2. 线上版本检查 ----
  let latest = { tag_name: '' };
  try {
    latest = await giteeApi('/repos/flyxjin/doctor-tauri/releases/latest');
  } catch {
    log('⚠️ 无法读取 Gitee 最新 Release（首个 Release？），跳过版本比较');
  }
  if (latest.tag_name && compareVersions(version, latest.tag_name) <= 0 && !FORCE) {
    die(`本地 ${tag} 不高于线上最新 ${latest.tag_name}；如需重发请加 --force`);
  }
  if (latest.tag_name) log(`线上最新 Release：${latest.tag_name}`);

  // ---- 3. 构建 ----
  const setupDir = join(REPO_ROOT, NSIS_DIR);
  const portable = join(REPO_ROOT, `src-tauri/target/${RELEASE_TARGET}/release/medicine-system.exe`);

  if (SKIP_BUILD) {
    log('跳过构建（--skip-build）');
  } else {
    log('开始构建（npm run tauri:build，约 3-5 分钟）...');
    if (DRY_RUN) {
      log('(dry-run) 跳过实际构建');
    } else {
      run('npm run tauri:build');
    }
  }
  if (!DRY_RUN && !SKIP_BUILD && !existsSync(setupDir)) die(`未找到 NSIS 产物目录：${NSIS_DIR}`);

  // ---- 4. 收集产物 + 生成 SHA256 侧车 ----
  const assets = [];
  if (existsSync(setupDir)) {
    // 只上传当前版本的安装包：bundle 目录会残留历史版本产物，误传会污染 Release
    const setups = readdirSync(setupDir).filter(
      (f) => f === `中药材销售管理系统_${version}_x64-setup.exe`,
    );
    for (const f of setups) {
      const p = join(setupDir, f);
      const digest = writeSidecar(p);
      assets.push(p, `${p}.sha256`);
      log(`NSIS 安装包：${f}（sha256 ${digest.slice(0, 16)}...）`);
    }
  } else if (SKIP_BUILD) {
    log('⚠️ 未找到 NSIS 安装包（--skip-build 模式下允许，确认产物已存在）');
  }
  if (existsSync(portable)) {
    const digest = writeSidecar(portable);
    assets.push(portable, `${portable}.sha256`);
    log(`便携 EXE：${basename(portable)}（sha256 ${digest.slice(0, 16)}...）`);
  } else {
    log('⚠️ 未找到便携 EXE，跳过上传');
  }

  if (DRY_RUN) {
    log('=== dry-run 结束：以上为发布计划，未执行任何发布动作 ===');
    return;
  }

  // ---- 5. 推送 tag（Gitee + GitHub 双推：Gitee 仓库镜像是定时同步，
  //      tag 只推 Gitee 会延迟到达 GitHub，导致 release.yml 不能及时触发）----
  const changelog = readFileSync(join(REPO_ROOT, 'CHANGELOG.md'), 'utf8');
  const notes = extractChangelogSection(changelog, version) || `Release ${tag}`;
  const existingTags = git('tag').split('\n');
  if (!existingTags.includes(tag)) {
    run(`git tag -a ${tag} -m ${JSON.stringify(notes)}`);
    log(`已创建标签 ${tag}`);
  } else {
    log(`标签 ${tag} 已存在，跳过创建`);
  }
  run(`git push origin ${tag}`);
  const hasGithubRemote = git('remote').split('\n').includes('github');
  if (hasGithubRemote) {
    try {
      run(`git push github ${tag}`);
      log('已推送 tag 到 github 远程（触发 release.yml 构建）');
    } catch {
      log(`⚠️ 推送 github 远程失败（仓库不存在或未登录？）。请手动执行：git push github ${tag}`);
    }
  } else {
    log('⚠️ 未配置 github 远程，跳过 CI 构建（release.yml 仅在 GitHub Actions 运行）');
  }

  // ---- 6. 创建 Gitee Release ----
  let release;
  try {
    release = await giteeApi('/repos/flyxjin/doctor-tauri/releases', {
      method: 'POST',
      // target_commitish 必填：Gitee API 缺失该字段返回 400（target_commitish is missing）
      body: new URLSearchParams({
        tag_name: tag,
        name: `中药材销售管理系统 ${tag}`,
        body: notes,
        target_commitish: 'master',
      }),
    });
    log(`已创建 Gitee Release #${release.id}：${tag}`);
  } catch (e) {
    // tag 或 Release 已存在时复用现有 Release
    log(`创建失败（${e.message.slice(0, 120)}...），尝试复用已有 Release`);
    const list = await giteeApi('/repos/flyxjin/doctor-tauri/releases?direction=desc&per_page=20');
    release = Array.isArray(list) ? list.find((r) => r.tag_name === tag) : undefined;
    if (!release) die(`无法创建或找到 ${tag} 的 Release，请到 Gitee 网页检查标签状态`);
    log(`复用已有 Release #${release.id}：${tag}`);
  }

  // ---- 7. 上传产物 ----
  for (const p of assets) {
    const form = new FormData();
    form.append('file', new Blob([readFileSync(p)]), basename(p));
    await giteeApi(`/repos/flyxjin/doctor-tauri/releases/${release.id}/attach_files`, {
      method: 'POST',
      body: form,
    });
    log(`已上传：${basename(p)}`);
  }

  log(`🎉 发布完成：https://gitee.com/flyxjin/doctor-tauri/releases/tag/${tag}`);
  log('客户端将自动检测到此版本（check_for_update 读 releases/latest）');
}

main().catch((e) => die(e.message));
