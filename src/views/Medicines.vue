<template>
  <div class="page-container">
    <h2 class="page-title">中药材管理</h2>
    
    <!-- 搜索和添加按钮 -->
    <div class="toolbar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索中药材名称"
        style="width: 300px; margin-right: 10px"
        clearable
      />
      <el-button type="primary" @click="showAddDialog = true">添加中药材</el-button>
    </div>
    
    <!-- 中药材列表 -->
    <el-table :data="filteredMedicines" style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="名称" width="120" />
      <el-table-column prop="nature" label="性味" width="100" />
      <el-table-column prop="taste" label="归经" width="100" />
      <el-table-column prop="meridian" label="功效" width="200" />
      <el-table-column prop="efficacy" label="用法" width="150" />
      <el-table-column prop="dosage" label="用量" width="100" />
      <el-table-column label="操作" width="180">
        <template #default="scope">
          <el-button size="small" type="primary" @click="editMedicine(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteMedicine(scope.row.id)">删除</el-button>
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
        :total="medicines.length"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
    
    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
    >
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="请输入中药材名称" />
        </el-form-item>
        <el-form-item label="性味">
          <el-input v-model="form.nature" placeholder="请输入性味" />
        </el-form-item>
        <el-form-item label="归经">
          <el-input v-model="form.taste" placeholder="请输入归经" />
        </el-form-item>
        <el-form-item label="功效">
          <el-input v-model="form.meridian" placeholder="请输入功效" />
        </el-form-item>
        <el-form-item label="用法">
          <el-input v-model="form.efficacy" placeholder="请输入用法" />
        </el-form-item>
        <el-form-item label="用量">
          <el-input v-model="form.dosage" placeholder="请输入用量" />
        </el-form-item>
        <el-form-item label="禁忌症">
          <el-input v-model="form.禁忌症" type="textarea" placeholder="请输入禁忌症" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveMedicine">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { medicinesApi } from '../api';

// 数据
const medicines = ref([]);
const searchQuery = ref('');
const currentPage = ref(1);
const pageSize = ref(10);

// 对话框状态
const dialogVisible = ref(false);
const showAddDialog = ref(false);
const dialogTitle = ref('添加中药材');

// 表单数据
const form = ref({
  id: '',
  name: '',
  nature: '',
  taste: '',
  meridian: '',
  efficacy: '',
  dosage: '',
  禁忌症: ''
});

// 过滤后的中药材列表
const filteredMedicines = computed(() => {
  const filtered = medicines.value.filter(medicine => 
    medicine.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
  // 分页
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filtered.slice(start, end);
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

// 编辑中药材
const editMedicine = (row) => {
  form.value = { ...row };
  dialogTitle.value = '编辑中药材';
  dialogVisible.value = true;
};

// 删除中药材
const deleteMedicine = async (id) => {
  try {
    await medicinesApi.delete(id);
    await loadMedicines();
  } catch (error) {
    console.error('删除中药材失败:', error);
  }
};

// 保存中药材
const saveMedicine = async () => {
  try {
    if (form.value.id) {
      // 更新
      await medicinesApi.update(form.value.id, form.value);
    } else {
      // 添加
      await medicinesApi.add(form.value);
    }
    await loadMedicines();
    dialogVisible.value = false;
    resetForm();
  } catch (error) {
    console.error('保存中药材失败:', error);
  }
};

// 重置表单
const resetForm = () => {
  form.value = {
    id: '',
    name: '',
    nature: '',
    taste: '',
    meridian: '',
    efficacy: '',
    dosage: '',
    禁忌症: ''
  };
};

// 分页处理
const handleSizeChange = (size) => {
  pageSize.value = size;
};

const handleCurrentChange = (current) => {
  currentPage.value = current;
};

// 监听添加对话框显示
const watchAddDialog = () => {
  if (showAddDialog.value) {
    dialogTitle.value = '添加中药材';
    resetForm();
    dialogVisible.value = true;
    showAddDialog.value = false;
  }
};

// 生命周期
onMounted(() => {
  loadMedicines();
});

// 监听showAddDialog变化
watchAddDialog();
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
</style>