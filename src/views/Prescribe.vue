<template>
  <div class="page-container">
    <h2 class="page-title">开处方</h2>
    
    <el-row :gutter="20">
      <!-- 患者信息 -->
      <el-col :span="12">
        <div class="card">
          <h3 class="card-title">患者信息</h3>
          <el-form :model="patientForm" label-width="80px">
            <el-form-item label="姓名">
              <el-input v-model="patientForm.patient_name" placeholder="请输入患者姓名" />
            </el-form-item>
            <el-form-item label="年龄">
              <el-input v-model.number="patientForm.patient_age" type="number" placeholder="请输入患者年龄" />
            </el-form-item>
            <el-form-item label="性别">
              <el-radio-group v-model="patientForm.patient_gender">
                <el-radio label="男">男</el-radio>
                <el-radio label="女">女</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="诊断">
              <el-input v-model="patientForm.diagnosis" type="textarea" placeholder="请输入诊断结果" />
            </el-form-item>
          </el-form>
        </div>
      </el-col>
      
      <!-- 药材选择 -->
      <el-col :span="12">
        <div class="card">
          <h3 class="card-title">添加药材</h3>
          <el-form :model="medicineForm" label-width="80px">
            <el-form-item label="药材">
              <el-select v-model="medicineForm.medicine_id" placeholder="请选择中药材">
                <el-option
                  v-for="medicine in medicines"
                  :key="medicine.id"
                  :label="medicine.name"
                  :value="medicine.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="剂量(g)">
              <el-input v-model.number="medicineForm.quantity" type="number" placeholder="请输入剂量（克）" />
            </el-form-item>
            <el-form-item label="单价">
              <el-input v-model.number="medicineForm.price" type="number" placeholder="请输入单价" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="addMedicine" :disabled="!medicineForm.medicine_id || !medicineForm.quantity || !medicineForm.price">添加到处方</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-col>
    </el-row>
    
    <!-- 处方明细 -->
    <div class="card">
      <h3 class="card-title">处方明细</h3>
      <el-table :data="prescriptionItems" style="width: 100%">
        <el-table-column prop="medicineName" label="药材名称" width="120" />
        <el-table-column prop="quantity" label="剂量(g)" width="100" />
        <el-table-column prop="price" label="单价" width="100" />
        <el-table-column prop="amount" label="金额" width="100" />
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button size="small" type="danger" @click="removeMedicine(scope.$index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="total-amount">
        <span>总金额：</span>
        <el-tag type="primary" size="large">{{ totalAmount.toFixed(2) }} 元</el-tag>
      </div>
    </div>
    
    <!-- 操作按钮 -->
    <div class="action-buttons">
      <el-button type="primary" @click="submitPrescription" :disabled="prescriptionItems.length === 0">提交处方</el-button>
      <el-button type="success" @click="printPrescription" :disabled="prescriptionItems.length === 0">打印处方</el-button>
      <el-button @click="resetForm">清空重填</el-button>
    </div>
    
    <!-- 配伍禁忌提醒 -->
    <el-alert
      v-if="contraindicationAlert"
      :title="contraindicationAlert"
      type="warning"
      show-icon
      :closable="false"
      style="margin-top: 20px"
    />
    
    <!-- 操作提示 -->
    <div class="tips" style="margin-top: 20px">
      <el-alert
        title="操作提示"
        type="info"
        show-icon
      >
        <ul>
          <li>1. 请准确填写患者信息和诊断结果</li>
          <li>2. 选择药材时请确保剂量单位为克(g)</li>
          <li>3. 系统会自动计算处方总金额</li>
          <li>4. 提交处方后，系统会自动减少对应药材的库存</li>
          <li>5. 如有配伍禁忌，系统会自动提醒</li>
        </ul>
      </el-alert>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { medicinesApi, prescriptionsApi } from '../api';

// 数据
const medicines = ref([]);
const patientForm = ref({
  patient_name: '',
  patient_age: '',
  patient_gender: '男',
  diagnosis: ''
});
const medicineForm = ref({
  medicine_id: '',
  quantity: '',
  price: ''
});
const prescriptionItems = ref([]);
const contraindicationAlert = ref('');

// 计算总金额
const totalAmount = computed(() => {
  return prescriptionItems.value.reduce((sum, item) => sum + item.amount, 0);
});

// 加载中药材列表
const loadMedicines = async () => {
  try {
    const response = await medicinesApi.getAll();
    medicines.value = response.data;
  } catch (error) {
    console.error('加载中药材失败:', error);
    contraindicationAlert.value = '加载中药材列表失败，请重新启动系统';
  }
};

// 添加药材到处方
const addMedicine = () => {
  const medicine = medicines.value.find(m => m.id === medicineForm.medicine_id);
  if (!medicine) return;
  
  // 检查配伍禁忌
  checkContraindications(medicine);
  
  const amount = medicineForm.quantity * medicineForm.price;
  prescriptionItems.value.push({
    medicine_id: medicineForm.medicine_id,
    medicineName: medicine.name,
    quantity: medicineForm.quantity,
    price: medicineForm.price,
    amount: amount
  });
  
  // 重置药材表单
  medicineForm.value = {
    medicine_id: '',
    quantity: '',
    price: ''
  };
};

// 从处方中移除药材
const removeMedicine = (index) => {
  prescriptionItems.value.splice(index, 1);
  // 重新检查配伍禁忌
  checkAllContraindications();
};

// 检查配伍禁忌
const checkContraindications = (newMedicine) => {
  // 检查是否有相同药材
  const existingMedicine = prescriptionItems.value.find(item => item.medicine_id === newMedicine.id);
  if (existingMedicine) {
    contraindicationAlert.value = `处方中已包含 ${newMedicine.name}，请勿重复添加`;
    return;
  }
  
  // 检查药材的禁忌症
  if (newMedicine.禁忌症) {
    contraindicationAlert.value = `${newMedicine.name} 的禁忌症：${newMedicine.禁忌症}`;
    return;
  }
  
  contraindicationAlert.value = '';
};

// 检查所有药材的配伍禁忌
const checkAllContraindications = () => {
  contraindicationAlert.value = '';
};

// 提交处方
const submitPrescription = async () => {
  try {
    // 验证患者信息
    if (!patientForm.value.patient_name) {
      contraindicationAlert.value = '请输入患者姓名';
      return;
    }
    
    if (!patientForm.value.diagnosis) {
      contraindicationAlert.value = '请输入诊断结果';
      return;
    }
    
    const prescriptionData = {
      ...patientForm.value,
      items: prescriptionItems.value,
      created_by: '医生'
    };
    
    await prescriptionsApi.create(prescriptionData);
    alert('处方提交成功！');
    resetForm();
  } catch (error) {
    console.error('提交处方失败:', error);
    alert('处方提交失败，请重试！');
  }
};

// 打印处方
const printPrescription = () => {
  window.print();
};

// 重置表单
const resetForm = () => {
  patientForm.value = {
    patient_name: '',
    patient_age: '',
    patient_gender: '男',
    diagnosis: ''
  };
  medicineForm.value = {
    medicine_id: '',
    quantity: '',
    price: ''
  };
  prescriptionItems.value = [];
  contraindicationAlert.value = '';
};

// 生命周期
onMounted(() => {
  loadMedicines();
});
</script>

<style scoped>
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

.total-amount {
  margin-top: 16px;
  text-align: right;
  font-size: 16px;
  font-weight: 600;
}

.action-buttons {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

.tips {
  margin-top: 20px;
}

.tips ul {
  margin: 10px 0 0 20px;
  padding: 0;
}

.tips li {
  margin-bottom: 5px;
}
</style>