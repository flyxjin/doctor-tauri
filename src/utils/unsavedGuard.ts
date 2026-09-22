// 开处方页未保存内容的跨组件脏标记
//
// MainLayout 的全局快捷键（Ctrl+1~9 切页）在跳转前读取此标记；
// 若存在未保存处方则弹确认，避免用户误触快捷键丢失已录入的处方内容。
// 仅用模块级布尔而非 Context：只需同步读写，无需触发渲染。

let unsaved = false;

/** 标记/清除未保存状态（开处方页在明细变化、保存成功、卸载时调用） */
export function setUnsavedChanges(value: boolean): void {
  unsaved = value;
}

/** 是否存在未保存内容 */
export function hasUnsavedChanges(): boolean {
  return unsaved;
}
