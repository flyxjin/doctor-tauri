// 通用 CRUD Mutation Hook：统一处理成功消息、错误提示、缓存失效
//
// 用法：
//   const { create, update, remove } = useCrudMutations<Medicine>({
//     queryKey: ['medicines'],
//     invalidateKeys: [['dashboard'], ['inventory']],
//     createFn: createMedicine,
//     updateFn: updateMedicine,
//     deleteFn: deleteMedicine,
//     messages: { created: '药材已添加', updated: '药材已更新', deleted: '药材已删除' },
//     onClose: () => setModalOpen(false),
//   });

import { useMutation, useQueryClient, type QueryKey } from '@tanstack/react-query';
import { App } from 'antd';

interface CrudOptions<T> {
  /** 主缓存键（创建/更新/删除后均失效） */
  queryKey: QueryKey;
  /** 额外需要失效的缓存键列表 */
  invalidateKeys?: QueryKey[];
  /** 创建函数 */
  createFn?: (item: T) => Promise<unknown>;
  /** 更新函数 */
  updateFn?: (item: T) => Promise<unknown>;
  /** 删除函数（参数为 id 或整个对象） */
  deleteFn?: (id: number) => Promise<unknown>;
  /** 操作成功消息 */
  messages?: {
    created?: string;
    updated?: string;
    deleted?: string;
  };
  /** 成功后回调（如关闭弹窗） */
  onClose?: () => void;
}

/**
 * 通用 CRUD mutations，封装消息提示与缓存失效。
 * 返回 create/update/remove 三个 mutation，直接在页面中使用。
 */
export function useCrudMutations<T extends { id?: number | null }>(
  options: CrudOptions<T>,
) {
  const queryClient = useQueryClient();
  const { message } = App.useApp();

  const invalidateAll = () => {
    queryClient.invalidateQueries({ queryKey: options.queryKey });
    for (const key of options.invalidateKeys ?? []) {
      queryClient.invalidateQueries({ queryKey: key });
    }
  };

  const create = useMutation({
    mutationFn: (item: T) => {
      if (!options.createFn) throw new Error('createFn 未配置');
      return options.createFn(item);
    },
    onSuccess: () => {
      if (options.messages?.created) message.success(options.messages.created);
      invalidateAll();
      options.onClose?.();
    },
    onError: (e: unknown) => message.error(String(e)),
  });

  const update = useMutation({
    mutationFn: (item: T) => {
      if (!options.updateFn) throw new Error('updateFn 未配置');
      return options.updateFn(item);
    },
    onSuccess: () => {
      if (options.messages?.updated) message.success(options.messages.updated);
      invalidateAll();
      options.onClose?.();
    },
    onError: (e: unknown) => message.error(String(e)),
  });

  const remove = useMutation({
    mutationFn: (id: number) => {
      if (!options.deleteFn) throw new Error('deleteFn 未配置');
      return options.deleteFn(id);
    },
    onSuccess: () => {
      if (options.messages?.deleted) message.success(options.messages.deleted);
      invalidateAll();
    },
    onError: (e: unknown) => message.error(String(e)),
  });

  return { create, update, remove };
}
