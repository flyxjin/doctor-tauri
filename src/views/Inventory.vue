<template>
  <div class="page-container">
    <h2 class="page-title">库存管理</h2>
    
    <!-- 库存预警 -->
    <el-alert
      v-if="lowStockItems.length > 0"
      :title="`有 ${lowStockItems.length} 种中药材库存不足`"
      type="warning"
      show-icon
      :closable="false"
      style="margin-bottom: 20px"
    >
      <div>
        <span v-for="item in lowStockItems" :key="item.id" style="margin-right: 10px">
          {{ item.name }} (剩余: {{ item.quantity }}g)
        </span>
      </div>
    </el-alert>
    
    <!-- 操作按钮 -->
    <div class="toolbar">
      <el-button type="primary" @click="activeTab = 'inbound'">入库</el-button>
      <el-button type="primary" @click="activeTab = 'outbound'">出库</el-button>
      <el-button type="primary" @click="activeTab = 'check'">盘点</el-button>
      <el-button type="primary" @click="activeTab = 'history'">库存历史</el-button>
    </div>
    
    <!-- 库存列表 -->
    <div class="card">
      <h3 class="card-title">库存列表</h3>
      <el-table :data="inventory" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="药材名称" width="120" />
        <el-table-column prop="quantity" label="库存数量（g）" width="120" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="price" label="单价" width="100" />
        <el-table-column prop="min_stock" label="最低库存" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.quantity <= scope.row.min_stock ? 'danger' : 'success'">
              {{ scope.row.quantity <= scope.row.min_stock ? '低库存' : '正常' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <!-- 入库/出库/盘点表单 -->
    <div class="card">
      <h3 class="card-title">{{ tabTitles[activeTab] }}</h3>
      
      <!-- 入库表单 -->
      <div v-if="activeTab === 'inbound'">
        <el-form :model="inboundForm" label-width="80px">
          <el-form-item label="药材">
            <el-select v-model="inboundForm.medicine_id" placeholder="请选择中药材">
              <el-option
                v-for="medicine in medicines"
                :key="medicine.id"
                :label="medicine.name"
                :value="medicine.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="数量">
            <el-input v-model.number="inboundForm.quantity" type="number" placeholder="请输入入库数量（g）" />
          </el-form-item>
          <el-form-item label="单价">
            <el-input v-model.number="inboundForm.price" type="number" placeholder="请输入单价" />
          </el-form-item>
          <el-form-item label="操作人">
            <el-input v-model="inboundForm.operator" placeholder="请输入操作人" />
          </el-form-item>
          <el-form-item label="备注">
            <el-input v-model="inboundForm.notes" type="textarea" placeholder="请输入备注" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="submitInbound" :disabled="!inboundForm.medicine_id || !inboundForm.quantity || !inboundForm.price || !inboundForm.operator">确认入库</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 出库表单 -->
      <div v-if="activeTab === 'outbound'">
        <el-form :model="outboundForm" label-width="80px">
          <el-form-item label="药材">
            <el-select v-model="outboundForm.medicine_id" placeholder="请选择中药材">
              <el-option
                v-for="item in inventory"
                :key="item.medicine_id"
                :label="item.name"
                :value="item.medicine_id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="数量">
            <el-input v-model.number="outboundForm.quantity" type="number" placeholder="请输入出库数量（g）" />
          </el-form-item>
          <el-form-item label="单价">
            <el-input v-model.number="outboundForm.price" type="number" placeholder="请输入单价" />
          </el-form-item>
          <el-form-item label="操作人">
            <el-input v-model="outboundForm.operator" placeholder="请输入操作人" />
          </el-form-item>
          <el-form-item label="备注">
            <el-input v-model="outboundForm.notes" type="textarea" placeholder="请输入备注" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="submitOutbound" :disabled="!outboundForm.medicine_id || !outboundForm.quantity || !outboundForm.price || !outboundForm.operator">确认出库</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 盘点表单 -->
      <div v-if="activeTab === 'check'">
        <el-form :model="checkForm" label-width="80px">
          <el-form-item label="药材">
            <el-select v-model="checkForm.medicine_id" placeholder="请选择中药材">
              <el-option
                v-for="item in inventory"
                :key="item.medicine_id"
                :label="item.name"
                :value="item.medicine_id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="实际数量">
            <el-input v-model.number="checkForm.actual_quantity" type="number" placeholder="请输入实际库存数量（g）" />
          </el-form-item>
          <el-form-item label="操作人">
            <el-input v-model="checkForm.operator" placeholder="请输入操作人" />
          </el-form-item>
          <el-form-item label="备注">
            <el-input v-model="checkForm.notes" type="textarea" placeholder="请输入备注" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="submitCheck" :disabled="!checkForm.medicine_id || !checkForm.actual_quantity || !checkForm.operator">确认盘点</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 库存历史 -->
      <div v-if="activeTab === 'history'">
        <el-table :data="inventoryHistory" style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="药材名称" width="120" />
          <el-table-column prop="type" label="类型" width="80">
            <template #default="scope">
              <el-tag :type="scope.row.type === '入库' ? 'success' : scope.row.type === '出库' ? 'danger' : 'warning'">
                {{ scope.row.type }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量（g）" width="100" />
          <el-table-column prop="price" label="单价" width="100" />
          <el-table-column prop="total_amount" label="总金额" width="100" />
          <el-table-column prop="operator" label="操作人" width="100" />
          <el-table-column prop="notes" label="备注" />
          <el-table-column prop="created_at" label="操作时间" width="180" />
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { medicinesApi, inventoryApi } from '../api';

// 数据
const medicines = ref([]);
const inventory = ref([]);
const lowStockItems = ref([]);
const inventoryHistory = ref([]);

// 标签页
const activeTab = ref('inbound');
const tabTitles = {
  inbound: '入库管理',
  outbound: '出库管理',
  check: '库存盘点',
  history: '库存历史'
};

// 表单数据
const inboundForm = ref({
  medicine_id: '',
  quantity: '',
  price: '',
  operator: '',
  notes: ''
});

const outboundForm = ref({
  medicine_id: '',
  quantity: '',
  price: '',
  operator: '',
  notes: ''
});

const checkForm = ref({
  medicine_id: '',
  actual_quantity: '',
  operator: '',
  notes: ''
});

// 加载中药材列表
const loadMedicines = async () => {
  try {
    const response = await medicinesApi.getAll();
    medicines.value = response.data;
  } catch (error) {
    console.error('加载中药材失败:', error);
  }
};

// 加载库存列表
const loadInventory = async () => {
  try {
    const response = await inventoryApi.getAll();
    inventory.value = response.data;
    // 更新低库存列表
    updateLowStockItems();
  } catch (error) {
    console.error('加载库存失败:', error);
  }
};

// 加载低库存预警
const loadLowStock = async () => {
  try {
    const response = await inventoryApi.getLowStock();
    lowStockItems.value = response.data;
  } catch (error) {
    console.error('加载低库存失败:', error);
  }
};

// 加载库存历史
const loadInventoryHistory = async () => {
  try {
    const response = await inventoryApi.getHistory();
    inventoryHistory.value = response.data;
  } catch (error) {
    console.error('加载库存历史失败:', error);
  }
};

// 更新低库存列表
const updateLowStockItems = () => {
  lowStockItems.value = inventory.value.filter(item => item.quantity <= item.min_stock);
};

// 提交入库
const submitInbound = async () => {
  try {
    await inventoryApi.inbound(inboundForm.value);
    alert('入库成功！');
    // 重置表单
    inboundForm.value = {
      medicine_id: '',
      quantity: '',
      price: '',
      operator: '',
      notes: ''
    };
    // 重新加载库存
    await loadInventory();
    await loadInventoryHistory();
  } catch (error) {
    console.error('入库失败:', error);
    alert('入库失败，请重试！');
  }
};

// 提交出库
const submitOutbound = async () => {
  try {
    await inventoryApi.outbound(outboundForm.value);
    alert('出库成功！');
    // 重置表单
    outboundForm.value = {
      medicine_id: '',
      quantity: '',
      price: '',
      operator: '',
      notes: ''
    };
    // 重新加载库存
    await loadInventory();
    await loadInventoryHistory();
  } catch (error) {
    console.error('出库失败:', error);
    alert('出库失败，请重试！');
  }
};

// 提交盘点
const submitCheck = async () => {
  try {
    await inventoryApi.inventoryCheck(checkForm.value);
    alert('盘点成功！');
    // 重置表单
    checkForm.value = {
      medicine_id: '',
      actual_quantity: '',
      operator: '',
      notes: ''
    };
    // 重新加载库存
    await loadInventory();
    await loadInventoryHistory();
  } catch (error) {
    console.error('盘点失败:', error);
    alert('盘点失败，请重试！');
  }
};

// 生命周期
onMounted(async () => {
  await loadMedicines();
  await loadInventory();
  await loadLowStock();
  await loadInventoryHistory();
});
</script>

<style scoped>
.toolbar {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.card {
  margin-bottom: 20px;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e8e8e8;
}
</style>