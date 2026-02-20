<template>
  <div class="page-container">
    <h2 class="page-title">处方历史</h2>
    
    <!-- 搜索和筛选 -->
    <div class="toolbar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索患者姓名"
        style="width: 300px; margin-right: 10px"
        clearable
      />
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        style="margin-right: 10px"
      />
      <el-button type="primary" @click="searchPrescriptions">搜索</el-button>
      <el-button @click="resetSearch">重置</el-button>
    </div>
    
    <!-- 处方列表 -->
    <el-table :data="filteredPrescriptions" style="width: 100%">
      <el-table-column prop="id" label="处方ID" width="80" />
      <el-table-column prop="patient_name" label="患者姓名" width="120" />
      <el-table-column prop="patient_age" label="年龄" width="80" />
      <el-table-column prop="patient_gender" label="性别" width="80" />
      <el-table-column prop="diagnosis" label="诊断" />
      <el-table-column prop="total_amount" label="总金额" width="100" />
      <el-table-column prop="created_by" label="开方医生" width="100" />
      <el-table-column prop="created_at" label="开方时间" width="180" />
      <el-table-column label="操作" width="180">
        <template #default="scope">
          <el-button size="small" type="primary" @click="viewPrescription(scope.row.id)">查看详情</el-button>
          <el-button size="small" type="danger" @click="deletePrescription(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="prescriptions.length"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
    
    <!-- 处方详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="处方详情"
      width="800px"
    >
      <div v-if="currentPrescription">
        <div class="prescription-header">
          <div class="prescription-info">
            <p><strong>处方ID:</strong> {{ currentPrescription.prescription.id }}</p>
            <p><strong>患者姓名:</strong> {{ currentPrescription.prescription.patient_name }}</p>
            <p><strong>年龄:</strong> {{ currentPrescription.prescription.patient_age }}岁</p>
            <p><strong>性别:</strong> {{ currentPrescription.prescription.patient_gender }}</p>
            <p><strong>诊断:</strong> {{ currentPrescription.prescription.diagnosis }}</p>
            <p><strong>总金额:</strong> {{ currentPrescription.prescription.total_amount.toFixed(2) }}元</p>
            <p><strong>开方医生:</strong> {{ currentPrescription.prescription.created_by }}</p>
            <p><strong>开方时间:</strong> {{ currentPrescription.prescription.created_at }}</p>
          </div>
        </div>
        <div class="prescription-items">
          <h4>处方明细</h4>
          <el-table :data="currentPrescription.items" style="width: 100%">
            <el-table-column prop="name" label="药材名称" width="120" />
            <el-table-column prop="quantity" label="剂量（g）" width="100" />
            <el-table-column prop="unit" label="单位" width="80" />
            <el-table-column prop="price" label="单价" width="100" />
            <el-table-column prop="amount" label="金额" width="100" />
          </el-table>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
          <el-button type="success" @click="printPrescription">打印处方</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { prescriptionsApi } from '../api';

// 数据
const prescriptions = ref([]);
const searchQuery = ref('');
const dateRange = ref([]);
const currentPage = ref(1);
const pageSize = ref(10);

// 对话框状态
const detailDialogVisible = ref(false);
const currentPrescription = ref(null);

// 过滤后的处方列表
const filteredPrescriptions = computed(() => {
  let filtered = prescriptions.value;
  
  // 按患者姓名搜索
  if (searchQuery.value) {
    filtered = filtered.filter(prescription => 
      prescription.patient_name.toLowerCase().includes(searchQuery.value.toLowerCase())
    );
  }
  
  // 按日期范围过滤
  if (dateRange.value && dateRange.value.length === 2) {
    const startDate = new Date(dateRange.value[0]);
    const endDate = new Date(dateRange.value[1]);
    filtered = filtered.filter(prescription => {
      const prescriptionDate = new Date(prescription.created_at);
      return prescriptionDate >= startDate && prescriptionDate <= endDate;
    });
  }
  
  // 分页
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filtered.slice(start, end);
});

// 加载处方列表
const loadPrescriptions = async () => {
  try {
    const response = await prescriptionsApi.getAll();
    prescriptions.value = response.data;
  } catch (error) {
    console.error('加载处方失败:', error);
  }
};

// 搜索处方
const searchPrescriptions = () => {
  // 这里可以实现更复杂的搜索逻辑，目前使用前端过滤
  currentPage.value = 1;
};

// 重置搜索
const resetSearch = () => {
  searchQuery.value = '';
  dateRange.value = [];
  currentPage.value = 1;
};

// 查看处方详情
const viewPrescription = async (id) => {
  try {
    const response = await prescriptionsApi.getById(id);
    currentPrescription.value = response.data;
    detailDialogVisible.value = true;
  } catch (error) {
    console.error('加载处方详情失败:', error);
  }
};

// 删除处方
const deletePrescription = async (id) => {
  try {
    if (confirm('确定要删除该处方吗？')) {
      await prescriptionsApi.delete(id);
      await loadPrescriptions();
    }
  } catch (error) {
    console.error('删除处方失败:', error);
  }
};

// 打印处方
const printPrescription = () => {
  // 这里可以实现打印逻辑
  window.print();
};

// 分页处理
const handleSizeChange = (size) => {
  pageSize.value = size;
};

const handleCurrentChange = (current) => {
  currentPage.value = current;
};

// 生命周期
onMounted(() => {
  loadPrescriptions();
});
</script>

<style scoped>
.toolbar {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.prescription-header {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e8e8e8;
}

.prescription-info {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.prescription-items {
  margin-top: 20px;
}

.prescription-items h4 {
  margin-bottom: 10px;
  font-weight: 600;
}
</style>