// 库存相关工具函数：聚合、效期判断
//
// 抽取自 Inventory.tsx 与 Prescription.tsx 中重复的 inline 实现，
// 统一"一药多批"聚合口径与效期状态判断逻辑。

import dayjs from 'dayjs';
import type { Inventory } from '@/types';

/** 距效期多少天开始标黄预警 */
export const EXPIRY_WARN_DAYS = 30;

export type ExpiryStatus = 'expired' | 'near' | 'ok' | 'none';

/**
 * 判断批次效期状态：
 * - expired：已过期
 * - near：近效期（EXPIRY_WARN_DAYS 天内到期）
 * - ok：正常
 * - none：无期或日期无效
 */
export function expiryStatus(dateStr?: string | null): ExpiryStatus {
  if (!dateStr) return 'none';
  const d = dayjs(dateStr);
  if (!d.isValid()) return 'none';
  const today = dayjs().startOf('day');
  if (d.isBefore(today)) return 'expired';
  if (d.isBefore(today.add(EXPIRY_WARN_DAYS, 'day'))) return 'near';
  return 'ok';
}

/** 按药材聚合的汇总信息 */
export interface MedicineSummary {
  /** 跨批次总库存量 */
  totalQty: number;
  /** 跨批次最低库存预警阈值（取所有批次的最小值） */
  minStock: number;
  /** 药材名 */
  name: string;
  /** 分类 */
  category: string;
  /** 首批次单价（用于开方时取默认价格） */
  price: number;
  /** 首批次单位 */
  unit: string;
}

/**
 * 将库存列表（按批次行）按药材 ID 聚合为一药一条汇总。
 *
 * - totalQty：所有批次数量之和
 * - minStock：所有批次的最低值（最严格的预警阈值）
 * - price/unit：首批次（inventory 顺序）的值，用于开方时取默认价格
 */
export function aggregateInventory(list: Inventory[]): Map<number, MedicineSummary> {
  const map = new Map<number, MedicineSummary>();
  for (const i of list) {
    const cur = map.get(i.medicine_id);
    if (cur) {
      cur.totalQty += i.quantity;
      cur.minStock = Math.min(cur.minStock, i.min_stock);
    } else {
      map.set(i.medicine_id, {
        totalQty: i.quantity,
        minStock: i.min_stock,
        name: i.medicine_name ?? '',
        category: i.category ?? '',
        price: i.price,
        unit: i.unit,
      });
    }
  }
  return map;
}
