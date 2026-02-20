import axios from 'axios';
import { ElMessage } from 'element-plus';

const api = axios.create({
  baseURL: 'http://localhost:3001/api',
  timeout: 10000
});

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config;
  },
  error => {
    ElMessage.error('网络请求失败，请检查网络连接');
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response;
  },
  error => {
    let errorMessage = '操作失败，请重试';
    
    if (error.response) {
      // 服务器返回错误状态码
      switch (error.response.status) {
        case 404:
          errorMessage = '请求的资源不存在';
          break;
        case 500:
          errorMessage = '服务器内部错误，请重新启动系统';
          break;
        case 400:
          errorMessage = '请求参数错误，请检查输入';
          break;
        default:
          errorMessage = `操作失败：${error.response.data.error || '未知错误'}`;
      }
    } else if (error.request) {
      // 请求已发出，但没有收到响应
      errorMessage = '无法连接到服务器，请检查系统是否已启动';
    } else {
      // 请求配置出错
      errorMessage = '操作失败，请重试';
    }
    
    ElMessage.error(errorMessage);
    return Promise.reject(error);
  }
);

// 中药材相关API
export const medicinesApi = {
  // 获取所有中药材
  getAll: () => api.get('/medicines'),
  // 根据ID获取中药材
  getById: (id) => api.get(`/medicines/${id}`),
  // 添加中药材
  add: (data) => api.post('/medicines', data),
  // 更新中药材
  update: (id, data) => api.put(`/medicines/${id}`, data),
  // 删除中药材
  delete: (id) => api.delete(`/medicines/${id}`)
};

// 处方相关API
export const prescriptionsApi = {
  // 获取所有处方
  getAll: () => api.get('/prescriptions'),
  // 根据ID获取处方详情
  getById: (id) => api.get(`/prescriptions/${id}`),
  // 创建处方
  create: (data) => api.post('/prescriptions', data),
  // 删除处方
  delete: (id) => api.delete(`/prescriptions/${id}`)
};

// 库存相关API
export const inventoryApi = {
  // 获取所有库存
  getAll: () => api.get('/inventory'),
  // 获取低库存预警
  getLowStock: () => api.get('/inventory/low-stock'),
  // 获取库存变动历史
  getHistory: () => api.get('/inventory/history'),
  // 入库操作
  inbound: (data) => api.post('/inventory/inbound', data),
  // 出库操作
  outbound: (data) => api.post('/inventory/outbound', data),
  // 盘点操作
  inventoryCheck: (data) => api.post('/inventory/inventory-check', data)
};

export default api;