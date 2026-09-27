import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';

/** 主题模式：浅色（默认东方本草宣纸风）/ 深色 */
export type ThemeMode = 'light' | 'dark';

/** localStorage 持久化键 */
const STORAGE_KEY = 'tcm-theme-mode';

interface ThemeContextValue {
  /** 当前主题模式 */
  mode: ThemeMode;
  /** 在深浅主题之间切换 */
  toggle: () => void;
}

const ThemeContext = createContext<ThemeContextValue>({
  mode: 'light',
  toggle: () => {},
});

/** 读取持久化的主题；无效值回退浅色 */
function readInitialMode(): ThemeMode {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === 'dark' || saved === 'light') return saved;
  } catch {
    // localStorage 不可用时静默回退
  }
  return 'light';
}

/**
 * 主题 Provider：
 * - 维护当前模式并持久化到 localStorage（重启后保持）
 * - 同步 `document.documentElement.dataset.theme`，
 *   供 global.css 中 `:root[data-theme='dark']` 的 CSS 变量覆盖生效
 */
export function ThemeProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<ThemeMode>(readInitialMode);

  useEffect(() => {
    document.documentElement.dataset.theme = mode;
    try {
      localStorage.setItem(STORAGE_KEY, mode);
    } catch {
      // 忽略持久化失败（仅本次会话生效）
    }
  }, [mode]);

  const toggle = useCallback(() => {
    setMode((prev) => (prev === 'light' ? 'dark' : 'light'));
  }, []);

  const value = useMemo(() => ({ mode, toggle }), [mode, toggle]);

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

/** 读取当前主题模式与切换函数 */
export function useThemeMode(): ThemeContextValue {
  return useContext(ThemeContext);
}
