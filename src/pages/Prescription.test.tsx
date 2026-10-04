// @vitest-environment jsdom
// 开处方页关键商业流程测试：保存时患者外键关联 + 库存预校验拦截
import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, cleanup } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import { App as AntdApp } from 'antd';
import PrescriptionPage from '@/pages/Prescription';
import * as api from '@/api/tauri';
import type { Inventory, Medicine, Patient } from '@/types';

vi.mock('@/api/tauri', () => ({
  listPatients: vi.fn(),
  listMedicines: vi.fn(),
  listInventory: vi.fn(),
  checkCompatibility: vi.fn(async () => []),
  createPrescription: vi.fn(),
  generatePrescriptionHtml: vi.fn(),
  listPrescriptions: vi.fn(async () => []),
  saveMyTemplate: vi.fn(async () => 1),
  listMyTemplates: vi.fn(async () => []),
}));

const patients: Patient[] = [
  { id: 1, name: '张三', gender: '男', age: 40 },
  { id: 2, name: '李四', gender: '女', age: 30 },
];

const medicines = [
  { id: 10, name: '甘草', category: '补虚药', nature: '平', taste: '甘', dosage: null },
] as unknown as Medicine[];

const inventoryRows = [
  {
    id: 1,
    medicine_id: 10,
    batch_no: 'B001',
    quantity: 100,
    unit: 'g',
    price: 0.5,
    min_stock: 10,
  },
] as unknown as Inventory[];

function mockApi() {
  vi.mocked(api.listPatients).mockResolvedValue(patients);
  vi.mocked(api.listMedicines).mockResolvedValue(medicines);
  vi.mocked(api.listInventory).mockResolvedValue(inventoryRows);
  vi.mocked(api.createPrescription).mockResolvedValue(101);
}

function renderPage() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={client}>
      <AntdApp>
        <MemoryRouter>
          <PrescriptionPage />
        </MemoryRouter>
      </AntdApp>
    </QueryClientProvider>,
  );
}

async function preparePage() {
  const user = userEvent.setup();
  renderPage();
  // 药材库加载完成后左侧检索面板出现药材条目
  expect(await screen.findByText('甘草')).toBeInTheDocument();
  // 点击药材条目加入处方（数量取默认 10g）；名称列 td 内有样式包裹层，放宽为包含匹配
  await user.click(screen.getByText('甘草'));
  await screen.findByText((_, el) => el?.tagName === 'TD' && !!el.textContent?.includes('甘草'));
  return user;
}

async function saveAndAssert() {
  await userEvent.click(screen.getByRole('button', { name: /保存处方/ }));
  await waitFor(() => expect(api.createPrescription).toHaveBeenCalledTimes(1));
  return vi.mocked(api.createPrescription).mock.calls[0][0];
}

beforeEach(() => {
  vi.clearAllMocks();
  mockApi();
});

// vitest 未开启 globals 时 RTL 不自动清理，需显式执行避免跨用例 DOM 残留
afterEach(() => cleanup());

describe('开处方页 · 保存流程', () => {
  it('患者姓名唯一匹配档案时，保存的处方携带 patient_id 外键关联', async () => {
    const user = await preparePage();
    // antd AutoComplete 的 placeholder 是 span 而非 input 属性，按 label 关联取输入框
    const nameInput = screen.getByLabelText(/患者姓名/);
    await user.type(nameInput, '张三');

    const payload = await saveAndAssert();
    expect(payload.patient_id).toBe(1);
    expect(payload.patient_name).toBe('张三');
    expect(payload.items).toHaveLength(1);
    expect(payload.items[0].medicine_id).toBe(10);
    expect(payload.items[0].quantity).toBe(10);
  });

  it('重名患者不建立 patient_id 关联（保持仅姓名关联）', async () => {
    vi.mocked(api.listPatients).mockResolvedValue([
      { id: 1, name: '张三' },
      { id: 3, name: '张三' },
    ]);
    const user = await preparePage();
    const nameInput = screen.getByLabelText(/患者姓名/);
    await user.type(nameInput, '张三');

    const payload = await saveAndAssert();
    expect(payload.patient_id).toBeNull();
  });

  it('库存不足时拦截提交，不调用 createPrescription', async () => {
    vi.mocked(api.listInventory).mockResolvedValue([
      { ...inventoryRows[0], quantity: 5 },
    ] as unknown as Inventory[]);
    const user = await preparePage();
    const nameInput = screen.getByLabelText(/患者姓名/);
    await user.type(nameInput, '张三');

    await user.click(screen.getByRole('button', { name: /保存处方/ }));
    // 库存预校验失败提示（跨批次总库存 5g < 默认用量 10g）
    expect(await screen.findByText(/库存不足/)).toBeInTheDocument();
    await waitFor(() => expect(screen.queryByText(/库存不足/)).toBeInTheDocument());
    expect(api.createPrescription).not.toHaveBeenCalled();
  });
});
