// 纯 SVG 折线图组件（零依赖）
//
// 设计目标：
// - 不引入 recharts/echarts 等重型库，保持 Tauri 应用包体积小巧
// - 支持双 Y 轴（左：销售额，右：处方数）
// - 自适应容器宽度
// - 主题色与全局 CSS 变量对齐
//
// 用法：
//   <TrendChart data={data} xKey="date" lines={[{key:'total_amount', name:'销售额', color:'#C8472C'}]} />

import { useMemo } from 'react';

export interface LineConfig {
  /** 数据字段名 */
  key: string;
  /** 图例名称 */
  name: string;
  /** 线条颜色 */
  color: string;
  /** 是否填充面积（默认 true） */
  area?: boolean;
}

export interface TrendChartProps<T> {
  data: T[];
  /** X 轴字段名 */
  xKey: keyof T & string;
  /** 折线配置列表 */
  lines: LineConfig[];
  /** 容器高度，默认 280 */
  height?: number;
}

/** 将值线性映射到像素坐标 */
function scale(value: number, domain: [number, number], range: [number, number]) {
  const [dMin, dMax] = domain;
  const [rMin, rMax] = range;
  if (dMax === dMin) return (rMin + rMax) / 2;
  return rMin + ((value - dMin) / (dMax - dMin)) * (rMax - rMin);
}

/** 格式化 Y 轴刻度 */
function formatTick(v: number, isCurrency: boolean) {
  if (isCurrency) {
    if (v >= 10000) return `¥${(v / 10000).toFixed(1)}万`;
    return `¥${v.toFixed(0)}`;
  }
  return String(Math.round(v));
}

export default function TrendChart<T extends object>({
  data,
  xKey,
  lines,
  height = 280,
}: TrendChartProps<T>) {
  const padding = { top: 16, right: 16, bottom: 32, left: 56 };
  const width = 720;
  const innerW = width - padding.left - padding.right;
  const innerH = height - padding.top - padding.bottom;

  // 计算每条线的定义域
  const config = useMemo(() => {
    return lines.map((line) => {
      const values = data.map((d) => Number((d as Record<string, unknown>)[line.key] ?? 0));
      const max = values.length > 0 ? Math.max(...values) : 0;
      // 上取整到合适刻度
      const niceMax = max <= 0 ? 1 : niceCeil(max);
      return {
        ...line,
        domain: [0, niceMax] as [number, number],
        isCurrency: line.key.includes('amount'),
      };
    });
  }, [data, lines]);

  if (data.length === 0) {
    return (
      <div
        style={{
          height,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--text-muted)',
          fontSize: 13,
        }}
      >
        暂无数据
      </div>
    );
  }

  // X 轴刻度：数据点 <= 10 个全显示，否则隔几个显示
  const xStep = data.length > 1 ? innerW / (data.length - 1) : 0;
  const xTickInterval = Math.ceil(data.length / 8);

  return (
    <div style={{ width: '100%', overflowX: 'auto' }}>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        style={{ width: '100%', minWidth: 600, height: 'auto' }}
      >
        {/* Y 轴网格线与刻度（基于第一条线） */}
        {config[0] && (
          <>
            {Array.from({ length: 5 }, (_, i) => {
              const ratio = i / 4;
              const value = config[0].domain[0] + ratio * (config[0].domain[1] - config[0].domain[0]);
              const y = padding.top + innerH - ratio * innerH;
              return (
                <g key={`grid-${i}`}>
                  <line
                    x1={padding.left}
                    y1={y}
                    x2={padding.left + innerW}
                    y2={y}
                    strokeDasharray="3 3"
                    style={{ stroke: 'var(--border-color)' }}
                  />
                  <text
                    x={padding.left - 8}
                    y={y + 4}
                    textAnchor="end"
                    fontSize={11}
                    style={{ fill: 'var(--text-muted)' }}
                  >
                    {formatTick(value, config[0].isCurrency)}
                  </text>
                </g>
              );
            })}
          </>
        )}

        {/* X 轴刻度 */}
        {data.map((d, i) => {
          if (i % xTickInterval !== 0 && i !== data.length - 1) return null;
          const x = padding.left + i * xStep;
          const label = String((d as Record<string, unknown>)[xKey] ?? '').slice(5); // YYYY-MM-DD -> MM-DD
          return (
            <text
              key={`x-${i}`}
              x={x}
              y={padding.top + innerH + 18}
              textAnchor="middle"
              fontSize={11}
              style={{ fill: 'var(--text-muted)' }}
            >
              {label}
            </text>
          );
        })}

        {/* 折线与面积 */}
        {config.map((line, lineIdx) => {
          const points = data.map((d, i) => {
            const v = Number((d as Record<string, unknown>)[line.key] ?? 0);
            const x = padding.left + i * xStep;
            const y = padding.top + innerH - scale(v, line.domain, [0, innerH]);
            return { x, y, v };
          });

          const pathD = points
            .map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`)
            .join(' ');

          const areaD =
            `${pathD} L ${points[points.length - 1].x.toFixed(1)} ${(padding.top + innerH).toFixed(1)}` +
            ` L ${points[0].x.toFixed(1)} ${(padding.top + innerH).toFixed(1)} Z`;

          return (
            <g key={`line-${lineIdx}`}>
              {line.area !== false && (
                <path d={areaD} opacity={0.08} style={{ fill: line.color }} />
              )}
              <path
                d={pathD}
                fill="none"
                strokeWidth={2}
                strokeLinejoin="round"
                strokeLinecap="round"
                style={{ stroke: line.color }}
              />
              {points.map((p, i) => (
                <circle
                  key={`pt-${lineIdx}-${i}`}
                  cx={p.x}
                  cy={p.y}
                  r={3}
                  strokeWidth={1.5}
                  style={{ fill: 'var(--bg-elevated)', stroke: line.color }}
                >
                  <title>{`${line.name}: ${formatTick(p.v, line.isCurrency)}`}</title>
                </circle>
              ))}
            </g>
          );
        })}

        {/* 图例 */}
        {config.map((line, i) => (
          <g key={`legend-${i}`}>
            <rect
              x={padding.left + i * 120}
              y={4}
              width={12}
              height={3}
              rx={1.5}
              style={{ fill: line.color }}
            />
            <text
              x={padding.left + i * 120 + 16}
              y={9}
              fontSize={11}
              style={{ fill: 'var(--text-secondary)' }}
            >
              {line.name}
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
}

/** 将最大值上取整到合适的刻度（1, 2, 5, 10, 20, 50, 100...） */
function niceCeil(max: number): number {
  if (max <= 0) return 1;
  const exp = Math.floor(Math.log10(max));
  const base = Math.pow(10, exp);
  const ratio = max / base;
  let nice: number;
  if (ratio <= 1) nice = 1;
  else if (ratio <= 2) nice = 2;
  else if (ratio <= 5) nice = 5;
  else nice = 10;
  return nice * base;
}
