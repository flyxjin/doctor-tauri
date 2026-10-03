// @vitest-environment jsdom
// 库存管理页关键商业流程测试：盘点调整提交参数正确
import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, cleanup } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { App as AntdApp } from 'antd';
import InventoryPage from '@/pages/Inventory';
import * as api from '@/api/tauri';
import type { Inventory } from '@/types';

vi.mock('@/api/tauri', () => ({
  listInventory: vi.fn(),
  listExpiringBatches: vi.fn(async () => []),
  listInventoryHistory: vi.fn(async () => []),
  updateStock: vi.fn(),
  adjustStock: vi.fn(async () => undefined),
}));

const inventoryRows = [
  {
    id: 1,
    medicine_id: 10,
    medicine_name: '甘草',
    category: '补虚药',
    batch_no: 'B001',
    quantity: 100,
    unit: 'g',
    price: 0.5,
    min_stock: 10,
  },
] as unknown as Inventory[];

function renderPage() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={client}>
      <AntdApp>
        <InventoryPage />
      </AntdApp>
    </QueryClientProvider>,
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(api.listInventory).mockResolvedValue(inventoryRows);
});

// vitest 未开启 globals 时 RTL 不自动清理，需显式执行避免跨用例 DOM 残留
afterEach(() => cleanup());

describe('库存管理页 · 盘点调整流程', () => {
  it('盘点弹窗提交时以正确的批次 id 与目标数量调用 adjustStock', async () => {
    const user = userEvent.setup();
    renderPage();
    // 表格按药材聚合展示
    expect(await screen.findByText('甘草')).toBeInTheDocument();

    // 行内「库存调整（盘点）」按钮（ToolOutlined 图标，仅 Tooltip 无文字）
    const adjustBtn = screen
      .getAllByRole('button')
      .find((b) => b.querySelector('.anticon-tool'));
    expect(adjustBtn).toBeTruthy();
    await user.click(adjustBtn!);

    // 盘点弹窗出现，目标库存量默认回填当前库存 100
    expect(await screen.findByText('甘草 - 库存调整')).toBeInTheDocument();
    const targetInput = screen.getByLabelText(/目标库存量/);
    expect(targetInput).toHaveValue('100');

    // 调整为目标 88，填写操作人
    await user.clear(targetInput);
    await user.type(targetInput, '88');
    await user.type(screen.getByPlaceholderText('操作人姓名'), '王药师');
    await user.click(screen.getByRole('button', { name: '确认调整' }));

    await waitFor(() => expect(api.adjustStock).toHaveBeenCalledTimes(1));
    expect(vi.mocked(api.adjustStock).mock.calls[0][0]).toBe(1);
    expect(vi.mocked(api.adjustStock).mock.calls[0][1]).toBe(88);
    expect(vi.mocked(api.adjustStock).mock.calls[0][2]).toBe('王药师');
  });

  it('正常渲染库存数据并显示批次号', async () => {
    renderPage();
    expect(await screen.findByText('甘草')).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText('B001')).toBeInTheDocument());
  });
});
