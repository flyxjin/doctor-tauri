// 复制处方到处方页的通用 Hook
//
// 抽取自 History.tsx 与 Patients.tsx 中完全重复的 handleCopyToPrescription。
// 统一 payload 结构、sessionStorage 写入、跳转和消息提示。

import { useNavigate } from 'react-router-dom';
import { App } from 'antd';
import type { PrescriptionWithItems } from '@/types';
import { PRESCRIPTION_COPY_KEY } from '@/pages/History';

/**
 * 复制处方到处方页。
 *
 * 设计要点：
 * - 沿用原方价格（复诊常沿用原价，医生可在处方页手动调整）
 * - 不复制 created_at（新处方用当前时间）
 * - 不复制 id/prescription_id/batch_id（新处方为新行）
 *
 * @param onClose 可选的关闭回调（如关闭 Drawer/详情面板）
 */
export function useCopyToPrescription(onClose?: () => void) {
  const navigate = useNavigate();
  const { message } = App.useApp();

  const copyToPrescription = (record: PrescriptionWithItems) => {
    const payload = {
      patient_name: record.patient_name,
      patient_age: record.patient_age ?? null,
      patient_gender: record.patient_gender,
      diagnosis: record.diagnosis,
      created_by: record.created_by,
      items: record.items.map((i) => ({
        medicine_id: i.medicine_id,
        medicine_name: i.medicine_name,
        quantity: i.quantity,
        unit: i.unit,
        price: i.price,
        amount: Number((i.quantity * i.price).toFixed(2)),
      })),
    };
    sessionStorage.setItem(PRESCRIPTION_COPY_KEY, JSON.stringify(payload));
    onClose?.();
    navigate('/prescription');
    message.success(`已加载处方 #${record.id} 的 ${record.items.length} 味药材，请核对后保存`);
  };

  return { copyToPrescription };
}
