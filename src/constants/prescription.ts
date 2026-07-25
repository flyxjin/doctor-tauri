// 跨页面处方复制契约
//
// 抽取自原 pages/History.tsx 的导出常量，消除 hooks/useCopyToPrescription.ts
// 对表现层页面的逆向依赖（DIP 违反）。History / Prescription / useCopyToPrescription
// 三方都从此处导入，依赖方向归位为：表现层 → 常量模块 ← 应用层。

/** sessionStorage key：用于 History → Prescription 跨页面传递待复制的处方 */
export const PRESCRIPTION_COPY_KEY = 'prescription_copy_data';
