import { describe, it, expect, afterEach } from 'vitest';
import dayjs from 'dayjs';
import {
  aggregateInventory,
  expiryStatus,
  EXPIRY_WARN_DAYS,
  type ExpiryStatus,
} from './inventory';
import type { Inventory } from '@/types';

// 构造库存记录的辅助函数，减少测试样板
function makeInventory(overrides: Partial<Inventory> & { medicine_id: number }): Inventory {
  return {
    id: null,
    batch_no: 'B1',
    quantity: 100,
    unit: 'g',
    price: 0.5,
    min_stock: 50,
    medicine_name: '甘草',
    category: '补益药',
    ...overrides,
  };
}

// ============ expiryStatus ============

describe('expiryStatus', () => {
  // 锁定"今天"避免跨日测试失败：mock dayjs 的起点
  const realNow = Date.now;

  afterEach(() => {
    Date.now = realNow;
  });

  function setToday(dateStr: string): void {
    const ms = dayjs(dateStr).valueOf();
    Date.now = () => ms;
  }

  it('无日期返回 none', () => {
    expect(expiryStatus(undefined)).toBe<ExpiryStatus>('none');
    expect(expiryStatus(null)).toBe<ExpiryStatus>('none');
    expect(expiryStatus('')).toBe<ExpiryStatus>('none');
  });

  it('无效日期返回 none', () => {
    expect(expiryStatus('not-a-date')).toBe<ExpiryStatus>('none');
    expect(expiryStatus('abcd-ef-gh')).toBe<ExpiryStatus>('none');
  });

  it('今天之前的日期返回 expired', () => {
    setToday('2026-07-25');
    expect(expiryStatus('2026-07-24')).toBe<ExpiryStatus>('expired');
    expect(expiryStatus('2025-12-31')).toBe<ExpiryStatus>('expired');
  });

  it('今天当天返回 near（边界：还未过期但已在预警窗口内）', () => {
    setToday('2026-07-25');
    // 今天到期：startOf('day') 之前判断为 expired？今天等于今天，不 before，进入 near 分支
    expect(expiryStatus('2026-07-25')).toBe<ExpiryStatus>('near');
  });

  it('预警窗口内的未来日期返回 near', () => {
    setToday('2026-07-25');
    // 窗口边界：EXPIRY_WARN_DAYS - 1 天后仍在窗口内（isBefore 严格小于）
    const nearEdge = dayjs('2026-07-25')
      .add(EXPIRY_WARN_DAYS - 1, 'day')
      .format('YYYY-MM-DD');
    expect(expiryStatus(nearEdge)).toBe<ExpiryStatus>('near');
    // 窗口内一天后
    expect(expiryStatus('2026-07-26')).toBe<ExpiryStatus>('near');
  });

  it('预警窗口外的远期日期返回 ok', () => {
    setToday('2026-07-25');
    const ok = dayjs('2026-07-25')
      .add(EXPIRY_WARN_DAYS + 1, 'day')
      .format('YYYY-MM-DD');
    expect(expiryStatus(ok)).toBe<ExpiryStatus>('ok');
    expect(expiryStatus('2027-12-31')).toBe<ExpiryStatus>('ok');
  });
});

// ============ aggregateInventory ============

describe('aggregateInventory', () => {
  it('空列表返回空 Map', () => {
    const map = aggregateInventory([]);
    expect(map.size).toBe(0);
  });

  it('单条记录直接进 Map', () => {
    const list = [makeInventory({ medicine_id: 1, quantity: 100 })];
    const map = aggregateInventory(list);
    expect(map.size).toBe(1);
    expect(map.get(1)?.totalQty).toBe(100);
    expect(map.get(1)?.minStock).toBe(50);
    expect(map.get(1)?.name).toBe('甘草');
    expect(map.get(1)?.price).toBe(0.5);
    expect(map.get(1)?.unit).toBe('g');
  });

  it('同药材多批次聚合 totalQty 为各批次之和', () => {
    const list = [
      makeInventory({ medicine_id: 1, batch_no: 'B1', quantity: 30 }),
      makeInventory({ medicine_id: 1, batch_no: 'B2', quantity: 50 }),
      makeInventory({ medicine_id: 1, batch_no: 'B3', quantity: 20 }),
    ];
    const map = aggregateInventory(list);
    expect(map.size).toBe(1);
    expect(map.get(1)?.totalQty).toBe(100);
  });

  it('多批次 minStock 取所有批次的最小值（最严格预警阈值）', () => {
    const list = [
      makeInventory({ medicine_id: 1, min_stock: 80 }),
      makeInventory({ medicine_id: 1, min_stock: 30 }),
      makeInventory({ medicine_id: 1, min_stock: 100 }),
    ];
    const map = aggregateInventory(list);
    expect(map.get(1)?.minStock).toBe(30);
  });

  it('首批次 price/unit 用于聚合结果（开方取默认价格口径）', () => {
    const list = [
      makeInventory({ medicine_id: 1, batch_no: 'B1', price: 0.5, unit: 'g' }),
      makeInventory({ medicine_id: 1, batch_no: 'B2', price: 0.8, unit: 'kg' }),
    ];
    const map = aggregateInventory(list);
    expect(map.get(1)?.price).toBe(0.5);
    expect(map.get(1)?.unit).toBe('g');
  });

  it('不同药材各自独立聚合', () => {
    const list = [
      makeInventory({ medicine_id: 1, medicine_name: '甘草', quantity: 100 }),
      makeInventory({ medicine_id: 2, medicine_name: '黄芪', quantity: 50 }),
      makeInventory({ medicine_id: 1, medicine_name: '甘草', quantity: 20 }),
    ];
    const map = aggregateInventory(list);
    expect(map.size).toBe(2);
    expect(map.get(1)?.totalQty).toBe(120);
    expect(map.get(1)?.name).toBe('甘草');
    expect(map.get(2)?.totalQty).toBe(50);
    expect(map.get(2)?.name).toBe('黄芪');
  });

  it('medicine_name 缺失时回退为空字符串，不抛异常', () => {
    const list = [
      makeInventory({ medicine_id: 1, medicine_name: undefined }),
    ];
    const map = aggregateInventory(list);
    expect(map.get(1)?.name).toBe('');
  });

  it('category 缺失时回退为空字符串', () => {
    const list = [
      makeInventory({ medicine_id: 1, category: undefined }),
    ];
    const map = aggregateInventory(list);
    expect(map.get(1)?.category).toBe('');
  });
});
