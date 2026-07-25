// 应用版本号单一来源（SSOT）
//
// 所有需要版本号的地方（MainLayout、Settings、更新检查等）都从此处导入，
// 不允许在业务代码中再硬编码版本字面量。package.json 是唯一事实源。
//
// 同步规则：
// - 修改版本号只改 package.json
// - 运行 `npm run version:sync` 把版本号同步到 Cargo.toml / install.bat / distrib/install.bat
// - tauri.conf.json 已移除 version 字段，Tauri 2 会自动回退到 Cargo.toml 的版本

import pkg from '../../package.json';

/** 当前应用版本号（派生自 package.json） */
export const APP_VERSION: string = pkg.version;
