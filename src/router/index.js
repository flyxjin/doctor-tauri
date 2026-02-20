import { createRouter, createWebHistory } from 'vue-router';

// 导入页面组件
const Medicines = () => import('../views/Medicines.vue');
const Prescribe = () => import('../views/Prescribe.vue');
const Inventory = () => import('../views/Inventory.vue');
const History = () => import('../views/History.vue');

const routes = [
  {
    path: '/',
    redirect: '/medicines'
  },
  {
    path: '/medicines',
    name: 'medicines',
    component: Medicines,
    meta: { title: '中药材管理' }
  },
  {
    path: '/prescribe',
    name: 'prescribe',
    component: Prescribe,
    meta: { title: '处方开具' }
  },
  {
    path: '/inventory',
    name: 'inventory',
    component: Inventory,
    meta: { title: '库存管理' }
  },
  {
    path: '/history',
    name: 'history',
    component: History,
    meta: { title: '处方历史' }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 路由守卫，设置页面标题
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || '中药材销售管理系统';
  next();
});

export default router;