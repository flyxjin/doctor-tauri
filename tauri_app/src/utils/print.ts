// 通过隐藏 iframe 调用 webview 的打印 API 打印 HTML 字符串
//
// 兼容 Tauri 2.x WebView：iframe 的 srcdoc 可在 webview 中正常加载并触发 print。
// 比 window.open 更稳定（部分 webview 屏蔽 window.open 行为）。

/** 把 HTML 字符串塞进隐藏 iframe 并触发打印 */
export function printHtmlInIframe(html: string): Promise<void> {
  return new Promise((resolve, reject) => {
    try {
      const iframe = document.createElement('iframe');
      iframe.style.position = 'fixed';
      iframe.style.right = '0';
      iframe.style.bottom = '0';
      iframe.style.width = '0';
      iframe.style.height = '0';
      iframe.style.border = '0';
      iframe.style.visibility = 'hidden';

      const cleanup = () => {
        if (iframe.parentNode) iframe.parentNode.removeChild(iframe);
      };

      iframe.onload = () => {
        try {
          const win = iframe.contentWindow;
          if (!win) {
            cleanup();
            reject(new Error('无法获取打印窗口'));
            return;
          }
          win.focus();
          // 给浏览器一点时间渲染再触发 print
          setTimeout(() => {
            try {
              win.print();
            } catch (err) {
              cleanup();
              reject(err);
              return;
            }
            // 等待打印对话框关闭后清理 iframe
            setTimeout(cleanup, 1000);
            resolve();
          }, 250);
        } catch (err) {
          cleanup();
          reject(err);
        }
      };

      iframe.onerror = (err) => {
        cleanup();
        reject(err);
      };

      // srcdoc 比 document.write 更稳定
      iframe.srcdoc = html;
      document.body.appendChild(iframe);
    } catch (err) {
      reject(err);
    }
  });
}
