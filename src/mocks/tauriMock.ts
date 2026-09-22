// 浏览器演示模式：在非 Tauri 环境（普通浏览器 dev server）中拦截 invoke 调用，
// 用内存数据库返回拟真数据，使 UI 开发与演示不依赖 Rust 后端。
//
// 启用条件（见 main.tsx）：import.meta.env.DEV 且 window 中无 __TAURI_INTERNALS__。
// Tauri 窗口内永远不生效；生产构建中该模块仅为独立 chunk，不会被加载。
//
// 数据为《中国药典》常用中药材示例，仅供界面演示，不构成用药建议。

import type {
  BackupEntry,
  BatchImportResult,
  CompatibilityConflict,
  CreatePrescriptionInput,
  DashboardData,
  ExpiringBatch,
  Inventory,
  InventoryHistory,
  Medicine,
  MedicineImportRecord,
  OperationLog,
  Patient,
  PrescriptionItem,
  PrescriptionWithItems,
  StatisticsData,
} from '@/types';

// ==================== 内存数据库 ====================

interface Db {
  medicines: Medicine[];
  inventory: Inventory[];
  history: InventoryHistory[];
  prescriptions: (PrescriptionWithItems & { created_at: string })[];
  patients: Patient[];
  logs: OperationLog[];
  backups: BackupEntry[];
  nextId: { medicine: number; inventory: number; history: number; prescription: number; item: number; patient: number; log: number; backup: number };
}

const now = () => {
  const d = new Date();
  const p = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`;
};

const daysAgo = (n: number) => {
  const d = new Date();
  d.setDate(d.getDate() - n);
  const p = (n2: number) => String(n2).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
};

const daysLater = (n: number) => daysAgo(-n);

// 名称/别名/分类/性/味/归经/功效/主治/用法/用量/禁忌/基价
const HERB_SEED: [string, string, string, string, string, string, string, string, string, string, string, number][] = [
  ['甘草', '甜草/国老', '补虚药', '平', '甘', '脾、胃、肺、心经', '补脾益气，清热解毒，祛痰止咳，缓急止痛，调和诸药', '脾胃虚弱，倦怠乏力，心悸气短，咳嗽痰多，脘腹挛急疼痛', '煎服', '2-10g', '不宜与海藻、京大戟、红大戟、甘遂、芫花同用', 0.11],
  ['黄芪', '北芪/绵芪', '补虚药', '微温', '甘', '脾、肺经', '补气升阳，固表止汗，利水消肿，生津养血', '气虚乏力，食少便溏，中气下陷，表虚自汗，气虚水肿', '煎服', '9-30g', '表实邪盛、阴虚阳亢者不宜', 0.12],
  ['当归', '秦归/云归', '补虚药', '温', '甘、辛', '肝、心、脾经', '补血活血，调经止痛，润肠通便', '血虚萎黄，月经不调，经闭痛经，虚寒腹痛，肠燥便秘', '煎服', '6-12g', '湿盛中满、大便溏泄者慎用', 0.15],
  ['白芍', '杭芍/毫芍', '补虚药', '微寒', '苦、酸', '肝、脾经', '养血调经，敛阴止汗，柔肝止痛，平抑肝阳', '血虚萎黄，月经不调，自汗盗汗，胁痛腹痛，头痛眩晕', '煎服', '6-15g', '不宜与藜芦同用', 0.13],
  ['人参', '园参/高丽参', '补虚药', '微温', '甘、微苦', '脾、肺、心、肾经', '大补元气，复脉固脱，补脾益肺，生津养血，安神益智', '体虚欲脱，肢冷脉微，脾虚食少，津伤口渴，惊悸失眠', '另煎兑服', '3-9g', '不宜与藜芦、五灵脂同用', 1.8],
  ['白术', '于术/冬术', '补虚药', '温', '苦、甘', '脾、胃经', '健脾益气，燥湿利水，止汗，安胎', '脾虚食少，腹胀泄泻，痰饮眩悸，水肿自汗，胎动不安', '煎服', '6-12g', '阴虚内热、津液亏耗者慎用', 0.18],
  ['茯苓', '云苓/白茯苓', '利水渗湿药', '平', '甘、淡', '心、肺、脾、肾经', '利水渗湿，健脾，宁心', '水肿尿少，痰饮眩悸，脾虚食少，便溏泄泻，心神不安', '煎服', '10-15g', '虚寒精滑者忌服', 0.14],
  ['陈皮', '广陈皮/新会皮', '理气药', '温', '苦、辛', '肺、脾经', '理气健脾，燥湿化痰', '脘腹胀满，食少吐泻，咳嗽痰多', '煎服', '3-10g', '气虚及阴虚燥咳者不宜，吐血者慎服', 0.08],
  ['半夏', '旱半夏', '化痰止咳平喘药', '温', '辛', '脾、胃、肺经', '燥湿化痰，降逆止呕，消痞散结', '湿痰寒痰，咳喘痰多，痰饮眩悸，呕吐反胃，胸脘痞闷', '内服一般炮制后使用', '3-9g', '不宜与乌头类药材同用', 0.16],
  ['川芎', '芎䓖', '活血化瘀药', '温', '辛', '肝、胆、心包经', '活血行气，祛风止痛', '月经不调，经闭痛经，胸胁刺痛，跌扑肿痛，头痛风湿痹痛', '煎服', '3-10g', '阴虚火旺、多汗者慎用', 0.17],
  ['柴胡', '北柴胡', '解表药', '微寒', '苦', '肝、胆、肺经', '疏散退热，疏肝解郁，升举阳气', '感冒发热，寒热往来，肝郁气滞，胸胁胀痛，气虚下陷', '煎服', '3-10g', '肝阳上亢、阴虚火旺者慎用', 0.14],
  ['黄芩', '枯芩/子芩', '清热药', '寒', '苦', '肺、胆、脾、大肠、小肠经', '清热燥湿，泻火解毒，止血，安胎', '湿温暑湿，胸闷呕恶，肺热咳嗽，高热烦渴，胎动不安', '煎服', '3-10g', '脾胃虚寒者不宜', 0.13],
  ['金银花', '忍冬花/双花', '清热药', '寒', '甘', '肺、心、胃经', '清热解毒，疏散风热', '痈肿疔疮，喉痹，丹毒，风热感冒，温病发热', '煎服', '6-15g', '脾胃虚寒及气虚疮疡脓清者慎用', 0.35],
  ['连翘', '青翘/老翘', '清热药', '微寒', '苦', '肺、心、小肠经', '清热解毒，消肿散结，疏散风热', '痈疽，瘰疬，乳痈，丹毒，风热感冒，温病初起', '煎服', '6-15g', '脾胃虚寒者慎用', 0.22],
  ['板蓝根', '北板蓝根', '清热药', '寒', '苦', '心、胃经', '清热解毒，凉血利咽', '温疫时毒，发热咽痛，温毒发斑，痄腮，烂喉丹痧', '煎服', '9-15g', '体虚而无实火热毒者忌服', 0.1],
  ['生地黄', '干地黄/怀生地', '清热药', '寒', '甘、苦', '心、肝、肾经', '清热凉血，养阴生津', '热入营血，温毒发斑，吐血衄血，热病伤阴，津伤便秘', '煎服', '10-15g', '脾虚湿滞、腹满便溏者不宜', 0.14],
  ['麦冬', '杭麦冬/川麦冬', '补虚药', '微寒', '甘、微苦', '心、肺、胃经', '养阴生津，润肺清心', '肺燥干咳，阴虚痨嗽，喉痹咽痛，津伤口渴，心烦失眠', '煎服', '6-12g', '虚寒泄泻、湿浊中阻者慎用', 0.28],
  ['山药', '怀山药/薯蓣', '补虚药', '平', '甘', '脾、肺、肾经', '补脾养胃，生津益肺，补肾涩精', '脾虚食少，久泻不止，肺虚喘咳，肾虚遗精，带下尿频', '煎服', '15-30g', '湿盛中满或有积滞者不宜单独使用', 0.12],
  ['党参', '潞党/台党', '补虚药', '平', '甘', '脾、肺经', '健脾益肺，养血生津', '脾肺气虚，食少倦怠，咳嗽虚喘，气血不足，津伤口渴', '煎服', '9-30g', '不宜与藜芦同用', 0.2],
  ['丹参', '紫丹参', '活血化瘀药', '微寒', '苦', '心、肝经', '活血祛瘀，通经止痛，清心除烦，凉血消痈', '胸痹心痛，脘腹胁痛，月经不调，痛经经闭，心烦不眠', '煎服', '10-15g', '不宜与藜芦同用', 0.13],
  ['红花', '红蓝花', '活血化瘀药', '温', '辛', '心、肝经', '活血通经，散瘀止痛', '经闭痛经，恶露不行，癥瘕痞块，胸痹心痛，跌扑损伤', '煎服', '3-10g', '孕妇慎用', 0.9],
  ['桃仁', '山桃仁', '活血化瘀药', '平', '苦、甘', '心、肝、大肠经', '活血祛瘀，润肠通便，止咳平喘', '经闭痛经，癥瘕痞块，肺痈肠痈，肠燥便秘，咳嗽气喘', '煎服', '5-10g', '孕妇慎用', 0.25],
  ['桔梗', '苦桔梗', '化痰止咳平喘药', '平', '苦、辛', '肺经', '宣肺，利咽，祛痰，排脓', '咳嗽痰多，胸闷不畅，咽痛音哑，肺痈吐脓', '煎服', '3-10g', '阴虚久嗽、气逆及咯血者不宜', 0.15],
  ['杏仁', '苦杏仁', '化痰止咳平喘药', '微温', '苦', '肺、大肠经', '降气止咳平喘，润肠通便', '咳嗽气喘，胸满痰多，肠燥便秘', '煎服', '5-10g', '内服不宜过量，以免中毒；大便溏泻者慎用', 0.19],
  ['百合', '龙牙百合', '安神药', '寒', '甘', '心、肺经', '养阴润肺，清心安神', '阴虚燥咳，虚烦惊悸，失眠多梦，精神恍惚', '煎服', '6-12g', '风寒咳嗽及中寒便溏者不宜', 0.32],
  ['酸枣仁', '山枣仁', '安神药', '平', '甘、酸', '肝、胆、心经', '养心补肝，宁心安神，敛汗，生津', '虚烦不眠，惊悸多梦，体虚多汗，津伤口渴', '煎服', '10-15g', '实邪郁火者慎服', 0.85],
  ['远志', '细叶远志', '安神药', '温', '苦、辛', '心、肾、肺经', '安神益智，交通心肾，祛痰，消肿', '心肾不交，失眠多梦，健忘惊悸，咳痰不爽，疮疡肿毒', '煎服', '3-10g', '胃炎及胃溃疡者慎用', 0.45],
  ['龙骨', '五花龙骨', '安神药', '平', '甘、涩', '心、肝、肾经', '镇惊安神，平肝潜阳，收敛固涩', '心悸失眠，头晕目眩，自汗盗汗，遗精崩带', '先煎', '15-30g', '湿热实邪者忌服', 0.6],
  ['牡蛎', '左牡蛎', '平肝息风药', '微寒', '咸', '肝、胆、肾经', '重镇安神，潜阳补阴，软坚散结，收敛固涩', '惊悸失眠，眩晕耳鸣，瘰疬痰核，自汗盗汗', '先煎', '9-30g', '不宜多服久服', 0.3],
  ['天麻', '冬麻/明天麻', '平肝息风药', '平', '甘', '肝经', '息风止痉，平抑肝阳，祛风通络', '小儿惊风，癫痫抽搐，头痛眩晕，手足不遂，风湿痹痛', '煎服', '3-10g', '血虚动风者慎用', 1.1],
  ['杜仲', '思仙/木绵', '补虚药', '温', '甘', '肝、肾经', '补肝肾，强筋骨，安胎', '肝肾不足，腰膝酸痛，筋骨无力，头晕目眩，胎动不安', '煎服', '6-10g', '阴虚火旺者慎用', 0.28],
  ['枸杞子', '宁夏枸杞', '补虚药', '平', '甘', '肝、肾经', '滋补肝肾，益精明目', '虚劳精亏，腰膝酸痛，眩晕耳鸣，内热消渴，目昏不明', '煎服', '6-12g', '外感实热、脾虚泄泻者慎服', 0.4],
  ['菊花', '杭白菊/亳菊', '解表药', '微寒', '甘、苦', '肺、肝经', '疏散风热，平抑肝阳，清肝明目，清热解毒', '风热感冒，头痛眩晕，目赤肿痛，眼目昏花，疮痈肿毒', '煎服', '5-10g', '气虚胃寒、食少泄泻者慎用', 0.25],
  ['决明子', '草决明', '清热药', '微寒', '甘、苦、咸', '肝、大肠经', '清热明目，润肠通便', '目赤涩痛，羞明多泪，头痛眩晕，目暗不明，大便秘结', '煎服', '9-15g', '气虚便溏者不宜', 0.09],
  ['枳壳', '江枳壳', '理气药', '微寒', '苦、辛、酸', '脾、胃经', '理气宽中，行滞消胀', '胸胁气滞，胀满疼痛，食积不化，痰饮内停', '煎服', '3-10g', '孕妇慎用', 0.14],
  ['香附', '莎草根/香附米', '理气药', '平', '辛、微苦、微甘', '肝、脾、三焦经', '疏肝解郁，理气宽中，调经止痛', '肝郁气滞，胸胁胀痛，疝气疼痛，月经不调，乳房胀痛', '煎服', '6-10g', '气虚无滞、阴虚血热者慎用', 0.11],
];

// 十八反（简化子集，用于配伍演示）
const INCOMPATIBILITY: [string, string, string][] = [
  ['甘草', '海藻', '十八反：甘草反海藻'],
  ['甘草', '甘遂', '十八反：甘草反甘遂'],
  ['甘草', '芫花', '十八反：甘草反芫花'],
  ['半夏', '乌头', '十八反：半蒌贝蔹及攻乌'],
  ['贝母', '乌头', '十八反：半蒌贝蔹及攻乌'],
  ['人参', '藜芦', '十八反：诸参辛芍叛藜芦'],
  ['丹参', '藜芦', '十八反：诸参辛芍叛藜芦'],
  ['白芍', '藜芦', '十八反：诸参辛芍叛藜芦'],
];

const PATIENT_SEED: [string, string, number, string, string, string][] = [
  ['王秀英', '女', 58, '13872345678', '青霉素过敏', '高血压 8 年'],
  ['李建国', '男', 62, '13907234567', '', '2 型糖尿病、冠心病'],
  ['张雨薇', '女', 27, '18672345678', '海鲜过敏', ''],
  ['陈志强', '男', 45, '13607234589', '', '慢性胃炎 3 年'],
  ['刘芳', '女', 35, '15872345690', '花粉过敏', '过敏性鼻炎'],
  ['赵德柱', '男', 71, '13707234561', '', '腰椎间盘突出、前列腺增生'],
  ['孙丽娜', '女', 40, '19972345672', '', '甲状腺结节'],
  ['周文彬', '男', 33, '15072345683', '磺胺类过敏', '湿疹反复发作'],
];

const DIAGNOSES = [
  '脾胃虚弱，气血不足',
  '肝郁气滞，郁而化火',
  '风热感冒，咽痛咳嗽',
  '心肾不交，夜寐不安',
  '湿热下注，腰膝酸软',
  '痰湿内蕴，咳嗽痰多',
  '气滞血瘀，痛经',
  '阴虚火旺，五心烦热',
];

const DOCTORS = ['张大夫', '李大夫', '王大夫'];

// ==================== 初始化种子数据 ====================

function seedDb(): Db {
  const medicines: Medicine[] = HERB_SEED.map((h, i) => ({
    id: i + 1,
    name: h[0],
    alias: h[1],
    category: h[2],
    nature: h[3],
    taste: h[4],
    meridian: h[5],
    efficacy: h[6],
    indications: h[7],
    usage: h[8],
    dosage: h[9],
    contraindication: h[10],
    notes: '',
    created_at: `${daysAgo(180)} 09:00:00`,
    updated_at: `${daysAgo(30)} 15:30:00`,
  }));

  const inventory: Inventory[] = [];
  const history: InventoryHistory[] = [];
  let invId = 0;
  let histId = 0;

  medicines.forEach((m, i) => {
    const base = HERB_SEED[i][11];
    // 每味药 1-2 个批次；效期分布覆盖：已过期/近效期/正常/无期
    const batches = 1 + (i % 2);
    for (let b = 0; b < batches; b++) {
      invId += 1;
      // 少量低库存与零库存，触发库存预警展示
      const lowStock = i % 9 === 4;
      const zeroStock = i === 14;
      const qty = zeroStock ? 0 : lowStock ? 8 + (i % 5) : 80 + ((i * 13 + b * 29) % 200);
      const expiry =
        i === 3 && b === 0
          ? daysAgo(10) // 已过期
          : i % 5 === 2
            ? daysLater(20 + i) // 近效期 30 天内
            : daysLater(180 + i * 11);
      inventory.push({
        id: invId,
        medicine_id: m.id!,
        batch_no: `B2026${String(100 + i)}${b ? '-B' : ''}`,
        production_date: daysAgo(200 + i * 3),
        expiry_date: expiry,
        quantity: qty,
        unit: 'g',
        price: base * (1 + b * 0.08),
        min_stock: 30,
        notes: '',
        created_at: `${daysAgo(120 - i)} 10:00:00`,
        updated_at: `${daysAgo(5)} 16:20:00`,
      });
      histId += 1;
      history.push({
        id: histId,
        medicine_id: m.id!,
        medicine_name: m.name,
        type: '入库',
        quantity: qty + 20,
        price: base,
        total_amount: (qty + 20) * base,
        operator: '库管员',
        notes: '期初入库',
        batch_id: invId,
        created_at: `${daysAgo(120 - i)} 10:00:00`,
      });
    }
  });

  const patients: Patient[] = PATIENT_SEED.map((p, i) => ({
    id: i + 1,
    name: p[0],
    gender: p[1],
    age: p[2],
    phone: p[3],
    address: '本市',
    allergy: p[4],
    medical_history: p[5],
    notes: '',
    created_at: `${daysAgo(150 - i * 5)} 09:30:00`,
    updated_at: `${daysAgo(10)} 11:00:00`,
  }));

  // 近 30 天处方：每天 0-3 张
  const prescriptions: (PrescriptionWithItems & { created_at: string })[] = [];
  const logs: OperationLog[] = [];
  let prescId = 0;
  let itemId = 0;
  let logId = 0;

  for (let day = 29; day >= 0; day--) {
    const count = (day * 7 + 3) % 4; // 0-3 张
    for (let k = 0; k < count; k++) {
      prescId += 1;
      const patient = patients[(day + k) % patients.length];
      const itemCount = 6 + ((day + k * 2) % 7);
      const usedIdx = new Set<number>();
      const items: PrescriptionItem[] = [];
      let total = 0;
      for (let j = 0; j < itemCount; j++) {
        let idx = (day * 5 + k * 3 + j * 7) % medicines.length;
        while (usedIdx.has(idx)) idx = (idx + 1) % medicines.length;
        usedIdx.add(idx);
        const m = medicines[idx];
        const inv = inventory.find((v) => v.medicine_id === m.id);
        const price = inv?.price ?? HERB_SEED[idx][11];
        const qty = [6, 9, 10, 12, 15, 20, 30][(day + j) % 7];
        const amount = Math.round(qty * price * 100) / 100;
        total += amount;
        itemId += 1;
        items.push({
          id: itemId,
          prescription_id: prescId,
          medicine_id: m.id!,
          medicine_name: m.name,
          quantity: qty,
          unit: 'g',
          price,
          amount,
          batch_id: inv?.id ?? null,
        });
      }
      total = Math.round(total * 100) / 100;
      prescriptions.push({
        id: prescId,
        patient_name: patient.name!,
        patient_age: patient.age ?? null,
        patient_gender: patient.gender ?? '女',
        diagnosis: DIAGNOSES[(day + k) % DIAGNOSES.length],
        total_amount: total,
        created_by: DOCTORS[(day + k) % DOCTORS.length],
        created_at: `${daysAgo(day)} ${String(8 + ((k * 3) % 9)).padStart(2, '0')}:${String((k * 17) % 60).padStart(2, '0')}:00`,
        items,
      });
      logId += 1;
      logs.push({
        id: logId,
        operation_type: 'CREATE',
        target_type: 'prescription',
        target_id: prescId,
        operator: '',
        details: `创建处方: 患者 ${patient.name}`,
        created_at: prescriptions[prescriptions.length - 1].created_at,
      });
    }
  }

  const backups: BackupEntry[] = [
    {
      backup_path: 'C:/AppData/backups/medicine_system_demo1.db',
      file_size: 1_863_424,
      checksum: 'a1b2c3d4e5f60718293a4b5c6d7e8f9012345678abcdef012345678901234abcd',
      created_at: `${daysAgo(9)} 23:00:11`,
    },
    {
      backup_path: 'C:/AppData/backups/medicine_system_demo2.db',
      file_size: 1_720_320,
      checksum: 'b2c3d4e5f60718293a4b5c6d7e8f9012345678abcdef012345678901234abcda1',
      created_at: `${daysAgo(16)} 22:47:03`,
    },
  ];

  return {
    medicines,
    inventory,
    history,
    prescriptions,
    patients,
    logs,
    backups,
    nextId: {
      medicine: medicines.length + 1,
      inventory: invId + 1,
      history: histId + 1,
      prescription: prescId + 1,
      item: itemId + 1,
      patient: patients.length + 1,
      log: logId + 1,
      backup: 3,
    },
  };
}

const db = seedDb();

const respondOk = <T,>(data: T) => data;

// ==================== 查询实现 ====================

function medicineName(id: number) {
  return db.medicines.find((m) => m.id === id)?.name ?? '';
}

function aggregateLowStock() {
  const map = new Map<number, { total: number; min: number; name: string; unit: string }>();
  for (const inv of db.inventory) {
    const cur = map.get(inv.medicine_id);
    if (cur) {
      cur.total += inv.quantity;
      cur.min = Math.min(cur.min, inv.min_stock);
    } else {
      map.set(inv.medicine_id, {
        total: inv.quantity,
        min: inv.min_stock,
        name: medicineName(inv.medicine_id),
        unit: inv.unit,
      });
    }
  }
  return [...map.entries()]
    .filter(([, v]) => v.total <= v.min)
    .map(([id, v]) => ({
      medicine_id: id,
      medicine_name: v.name,
      quantity: Math.round(v.total * 10) / 10,
      min_stock: v.min,
      unit: v.unit,
    }));
}

function dashboardData(): DashboardData {
  const today = daysAgo(0);
  const todays = db.prescriptions.filter((p) => p.created_at.startsWith(today));
  const lowList = aggregateLowStock();
  const dailyTrend: DashboardData['daily_trend'] = [];
  for (let i = 6; i >= 0; i--) {
    const d = daysAgo(i);
    const dayPs = db.prescriptions.filter((p) => p.created_at.startsWith(d));
    dailyTrend.push({
      date: d,
      revenue: Math.round(dayPs.reduce((s, p) => s + p.total_amount, 0) * 100) / 100,
      prescription_count: dayPs.length,
    });
  }
  return {
    medicine_count: db.medicines.length,
    prescription_count: db.prescriptions.length,
    total_stock_value:
      Math.round(db.inventory.reduce((s, i) => s + i.quantity * i.price, 0) * 100) / 100,
    low_stock_count: lowList.length,
    low_stock_list: lowList.slice(0, 20),
    recent_prescriptions: [...db.prescriptions]
      .sort((a, b) => b.id! - a.id!)
      .slice(0, 10)
      .map(({ items: _items, ...p }) => p),
    today_prescription_count: todays.length,
    today_revenue: Math.round(todays.reduce((s, p) => s + p.total_amount, 0) * 100) / 100,
    daily_trend: dailyTrend,
  };
}

function statisticsData(start: string, end: string): StatisticsData {
  const inRange = db.prescriptions.filter((p) => {
    const d = p.created_at.slice(0, 10);
    return d >= start && d <= end;
  });
  const total = Math.round(inRange.reduce((s, p) => s + p.total_amount, 0) * 100) / 100;
  const byName = new Map<string, { q: number; amt: number }>();
  const byDate = new Map<string, { c: number; amt: number }>();
  for (const p of inRange) {
    for (const it of p.items) {
      const cur = byName.get(it.medicine_name) ?? { q: 0, amt: 0 };
      cur.q += it.quantity;
      cur.amt += it.amount;
      byName.set(it.medicine_name, cur);
    }
    const d = p.created_at.slice(0, 10);
    const cur = byDate.get(d) ?? { c: 0, amt: 0 };
    cur.c += 1;
    cur.amt += p.total_amount;
    byDate.set(d, cur);
  }
  const count = inRange.length;
  return {
    summary: {
      prescription_count: count,
      total_amount: total,
      medicine_kinds: byName.size,
      avg_amount: count ? Math.round((total / count) * 100) / 100 : 0,
    },
    top_medicines: [...byName.entries()]
      .sort((a, b) => b[1].amt - a[1].amt)
      .slice(0, 10)
      .map(([name, v]) => ({
        medicine_name: name,
        total_quantity: Math.round(v.q * 10) / 10,
        total_amount: Math.round(v.amt * 100) / 100,
      })),
    daily_trend: [...byDate.entries()]
      .sort((a, b) => a[0].localeCompare(b[0]))
      .map(([date, v]) => ({
        date,
        prescription_count: v.c,
        total_amount: Math.round(v.amt * 100) / 100,
      })),
  };
}

// ==================== 命令分发 ====================

type Handler = (args: Record<string, unknown>) => unknown;

const handlers: Record<string, Handler> = {
  list_medicines: ({ keyword, category, nature }) => {
    let list = db.medicines;
    const kw = (keyword as string)?.toLowerCase();
    if (kw) {
      list = list.filter(
        (m) =>
          m.name.toLowerCase().includes(kw) ||
          (m.alias ?? '').toLowerCase().includes(kw) ||
          (m.efficacy ?? '').toLowerCase().includes(kw),
      );
    }
    if (category) list = list.filter((m) => m.category === category);
    if (nature) list = list.filter((m) => m.nature === nature);
    return list;
  },

  create_medicine: ({ medicine }) => {
    const m = medicine as Medicine;
    const id = db.nextId.medicine++;
    db.medicines.push({ ...m, id, created_at: now(), updated_at: now() });
    pushLog('CREATE', 'medicine', id, `创建药材: ${m.name}`);
    return id;
  },

  update_medicine: ({ medicine }) => {
    const m = medicine as Medicine;
    const idx = db.medicines.findIndex((v) => v.id === m.id);
    if (idx >= 0) {
      db.medicines[idx] = { ...db.medicines[idx], ...m, updated_at: now() };
      pushLog('UPDATE', 'medicine', m.id!, `更新药材: ${m.name}`);
    }
    return null;
  },

  delete_medicine: ({ id }) => {
    const m = db.medicines.find((v) => v.id === id);
    db.medicines = db.medicines.filter((v) => v.id !== id);
    db.inventory = db.inventory.filter((v) => v.medicine_id !== id);
    if (m) pushLog('DELETE', 'medicine', id as number, `删除药材: ${m.name}`);
    return null;
  },

  list_inventory: () =>
    db.inventory.map((i) => ({
      ...i,
      medicine_name: medicineName(i.medicine_id),
      category: db.medicines.find((m) => m.id === i.medicine_id)?.category ?? '',
    })),

  update_stock: ({ medicineId, change, isIn, operator, notes, batchNo, productionDate, expiryDate }) => {
    const mid = medicineId as number;
    const qty = change as number;
    const name = medicineName(mid);
    if (isIn) {
      const batch = ((batchNo as string) || '').trim() || `B${Date.now()}`;
      const existing = db.inventory.find((v) => v.medicine_id === mid && v.batch_no === batch);
      if (existing) {
        existing.quantity += qty;
        if (expiryDate) existing.expiry_date = expiryDate as string;
        if (productionDate) existing.production_date = productionDate as string;
        pushHistory(mid, name, '入库', qty, existing.price, existing.id!, operator as string | undefined, (notes as string) ?? '');
      } else {
        const ref = db.inventory.find((v) => v.medicine_id === mid);
        const id = db.nextId.inventory++;
        db.inventory.push({
          id,
          medicine_id: mid,
          batch_no: batch,
          production_date: (productionDate as string) || null,
          expiry_date: (expiryDate as string) || null,
          quantity: qty,
          unit: ref?.unit ?? 'g',
          price: ref?.price ?? 0,
          min_stock: ref?.min_stock ?? 30,
          notes: '',
          created_at: now(),
          updated_at: now(),
        });
        pushHistory(mid, name, '入库', qty, ref?.price ?? 0, id, operator as string | undefined, (notes as string) ?? '');
      }
    } else {
      // FEFO 近效期优先
      const batches = db.inventory
        .filter((v) => v.medicine_id === mid && v.quantity > 0)
        .sort((a, b) => {
          const av = a.expiry_date ?? '9999-12-31';
          const bv = b.expiry_date ?? '9999-12-31';
          return av.localeCompare(bv);
        });
      let remaining = qty;
      for (const b of batches) {
        if (remaining <= 0) break;
        const deduct = Math.min(b.quantity, remaining);
        b.quantity -= deduct;
        remaining -= deduct;
        pushHistory(mid, name, '出库', deduct, b.price, b.id!, operator as string | undefined, (notes as string) ?? '手动出库');
      }
      if (remaining > 0.001) {
        throw new Error(`库存不足：需要 ${qty}，缺口 ${Math.round(remaining * 1000) / 1000}`);
      }
    }
    pushLog('STOCK', 'inventory', mid, `库存变更: ${name}`);
    return null;
  },

  adjust_stock: ({ inventoryId, targetQuantity, operator, notes }) => {
    const inv = db.inventory.find((v) => v.id === inventoryId);
    if (!inv) throw new Error('批次不存在');
    const diff = (targetQuantity as number) - inv.quantity;
    inv.quantity = targetQuantity as number;
    pushHistory(inv.medicine_id, medicineName(inv.medicine_id), '调整', diff, inv.price, inv.id!, operator as string | undefined, (notes as string) ?? '盘点调整');
    return null;
  },

  list_inventory_history: ({ medicineId, historyType, startDate, endDate, limit }) => {
    let list = db.history;
    if (medicineId) list = list.filter((h) => h.medicine_id === medicineId);
    if (historyType) list = list.filter((h) => h.type === historyType);
    if (startDate) list = list.filter((h) => h.created_at!.slice(0, 10) >= startDate);
    if (endDate) list = list.filter((h) => h.created_at!.slice(0, 10) <= endDate);
    return list
      .sort((a, b) => b.id! - a.id!)
      .slice(0, (limit as number) ?? 200)
      .map((h) => ({ ...h, medicine_name: medicineName(h.medicine_id) || h.medicine_name }));
  },

  list_expiring_batches: ({ days }) => {
    const horizon = daysLater((days as number) ?? 30);
    return db.inventory
      .filter(
        (i) => i.expiry_date && i.expiry_date !== '' && i.quantity > 0 && i.expiry_date <= horizon,
      )
      .map((i) => ({
        id: i.id!,
        medicine_id: i.medicine_id,
        medicine_name: medicineName(i.medicine_id),
        batch_no: i.batch_no,
        expiry_date: i.expiry_date!,
        quantity: i.quantity,
        unit: i.unit,
        price: i.price,
      })) as ExpiringBatch[];
  },

  list_prescriptions: ({ keyword, startDate, endDate, limit }) => {
    let list = db.prescriptions;
    const kw = (keyword as string)?.toLowerCase();
    if (kw) {
      list = list.filter(
        (p) => p.patient_name.toLowerCase().includes(kw) || p.diagnosis.toLowerCase().includes(kw),
      );
    }
    if (startDate) list = list.filter((p) => p.created_at.slice(0, 10) >= startDate);
    if (endDate) list = list.filter((p) => p.created_at.slice(0, 10) <= endDate);
    return list
      .sort((a, b) => b.id! - a.id!)
      .slice(0, (limit as number) ?? 500);
  },

  create_prescription: ({ input }) => {
    const inp = input as CreatePrescriptionInput;
    const id = db.nextId.prescription++;
    const items = inp.items.map((it) => ({
      ...it,
      id: db.nextId.item++,
      prescription_id: id,
    }));
    // 模拟 FEFO 扣减
    for (const it of items) {
      let remaining = it.quantity;
      const batches = db.inventory
        .filter((v) => v.medicine_id === it.medicine_id && v.quantity > 0)
        .sort((a, b) => (a.expiry_date ?? '9999-12-31').localeCompare(b.expiry_date ?? '9999-12-31'));
      for (const b of batches) {
        if (remaining <= 0) break;
        const deduct = Math.min(b.quantity, remaining);
        b.quantity -= deduct;
        remaining -= deduct;
        it.batch_id = b.id;
        pushHistory(it.medicine_id, it.medicine_name, '出库', deduct, b.price, b.id!, inp.created_by, '处方出库');
      }
    }
    db.prescriptions.push({
      id,
      patient_name: inp.patient_name,
      patient_age: inp.patient_age ?? null,
      patient_gender: inp.patient_gender,
      diagnosis: inp.diagnosis,
      total_amount: inp.total_amount,
      created_by: inp.created_by,
      created_at: now(),
      items,
    });
    pushLog('CREATE', 'prescription', id, `创建处方: 患者 ${inp.patient_name}`);
    return id;
  },

  delete_prescription: ({ id }) => {
    const idx = db.prescriptions.findIndex((p) => p.id === id);
    if (idx < 0) throw new Error(`处方 id=${id} 不存在`);
    const p = db.prescriptions[idx];
    // 精确回扣
    for (const it of p.items) {
      const batch = db.inventory.find((v) => v.id === it.batch_id);
      if (batch) batch.quantity += it.quantity;
      pushHistory(it.medicine_id, it.medicine_name, '退库', it.quantity, it.price, it.batch_id ?? 0, '', '删除处方回扣');
    }
    db.prescriptions.splice(idx, 1);
    pushLog('DELETE', 'prescription', id as number, '删除处方（回扣库存）');
    return null;
  },

  get_dashboard_data: () => dashboardData(),

  get_statistics: ({ startDate, endDate }) =>
    statisticsData(startDate as string, endDate as string),

  check_compatibility: ({ medicineNames }) => {
    const names = medicineNames as string[];
    const conflicts: CompatibilityConflict[] = [];
    for (const [a, b, desc] of INCOMPATIBILITY) {
      if (names.includes(a) && names.includes(b)) {
        conflicts.push({ medicine1: a, medicine2: b, description: desc });
      }
    }
    return conflicts;
  },

  batch_import_medicines: ({ records }) => {
    let inserted = 0;
    let updated = 0;
    const errors: string[] = [];
    for (const r of records as MedicineImportRecord[]) {
      const name = (r.name ?? '').trim();
      if (!name) {
        errors.push('名称为空');
        continue;
      }
      const existing = db.medicines.find((m) => m.name === name);
      const qty = Number(r.quantity ?? 0) || 0;
      const price = Number(r.price ?? 0) || 0;
      if (existing) {
        Object.assign(existing, r, { updated_at: now() });
        updated += 1;
        if (qty > 0) {
          const id = db.nextId.inventory++;
          db.inventory.push({
            id,
            medicine_id: existing.id!,
            batch_no: `导入批次-${Date.now()}-${updated}`,
            production_date: null,
            expiry_date: null,
            quantity: qty,
            unit: r.unit || 'g',
            price,
            min_stock: Number(r.min_stock ?? 0) || 0,
            notes: '',
            created_at: now(),
            updated_at: now(),
          });
        }
      } else {
        const id = db.nextId.medicine++;
        db.medicines.push({
          id,
          name,
          alias: r.alias,
          category: r.category,
          nature: r.nature,
          taste: r.taste,
          meridian: r.meridian,
          efficacy: r.efficacy,
          indications: r.indications,
          usage: r.usage,
          dosage: r.dosage,
          contraindication: r.contraindication,
          notes: r.notes,
          created_at: now(),
          updated_at: now(),
        });
        inserted += 1;
        if (qty > 0) {
          const invId = db.nextId.inventory++;
          db.inventory.push({
            id: invId,
            medicine_id: id,
            batch_no: '初始库存',
            production_date: null,
            expiry_date: null,
            quantity: qty,
            unit: r.unit || 'g',
            price,
            min_stock: Number(r.min_stock ?? 0) || 0,
            notes: '',
            created_at: now(),
            updated_at: now(),
          });
        }
      }
    }
    return { inserted, updated, errors } as BatchImportResult;
  },

  export_medicines_csv: () => {
    const header = 'name,alias,category,nature,taste,meridian,efficacy,indications,usage,dosage,contraindication,notes';
    const lines = db.medicines.map((m) =>
      [m.name, m.alias ?? '', m.category ?? '', m.nature ?? '', m.taste ?? '', m.meridian ?? '', m.efficacy ?? '', m.indications ?? '', m.usage ?? '', m.dosage ?? '', m.contraindication ?? '', m.notes ?? '']
        .map((v) => (/[",\n]/.test(v) ? `"${v.replace(/"/g, '""')}"` : v))
        .join(','),
    );
    return '\uFEFF' + [header, ...lines].join('\r\n');
  },

  download_import_template: () =>
    '\uFEFFname,alias,category,nature,taste,meridian,efficacy,indications,usage,dosage,contraindication,notes,quantity,unit,price,min_stock\r\n人参,园参,补虚药,微温,甘/微苦,脾/肺/心/肾经,大补元气,体虚欲脱,煎服,3-9g,反藜芦,示例,50,g,1.8,30\r\n黄芪,北芪,补虚药,微温,甘,脾/肺经,补气升阳,气虚乏力,煎服,9-30g,表实邪盛者不宜,示例,100,g,0.12,30',

  save_text_to_downloads: ({ filename }) => `C:\\Users\\Demo\\Downloads\\${filename as string}`,

  list_operation_logs: ({ operationType, targetType, startDate, endDate, limit }) => {
    let list = db.logs;
    if (operationType) list = list.filter((l) => l.operation_type === operationType);
    if (targetType) list = list.filter((l) => l.target_type === targetType);
    if (startDate) list = list.filter((l) => l.created_at!.slice(0, 10) >= startDate);
    if (endDate) list = list.filter((l) => l.created_at!.slice(0, 10) <= endDate);
    return list.sort((a, b) => b.id! - a.id!).slice(0, (limit as number) ?? 200);
  },

  generate_prescription_html: ({ prescriptionId }) => {
    const p = db.prescriptions.find((v) => v.id === prescriptionId);
    if (!p) throw new Error(`处方 id=${prescriptionId} 不存在`);
    const rows = p.items
      .map(
        (it, i) =>
          `<tr><td style='text-align:center'>${i + 1}</td><td>${it.medicine_name}</td><td style='text-align:right'>${it.quantity}</td><td style='text-align:center'>${it.unit}</td><td style='text-align:right'>¥${it.price.toFixed(2)}</td><td style='text-align:right'>¥${it.amount.toFixed(2)}</td></tr>`,
      )
      .join('');
    return `<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><title>中药处方笺 #${p.id}</title></head><body style="font-family:sans-serif;padding:32px"><h1 style="text-align:center;letter-spacing:8px">中药处方笺</h1><p style="text-align:center;color:#888">处方笺 #${p.id}</p><div style="display:flex;justify-content:space-between;border-bottom:2px solid #333;padding-bottom:8px"><div>患者：${p.patient_name}（${p.patient_gender}${p.patient_age ?? ''}岁）</div><div>开方人：${p.created_by}</div></div><p>诊断：${p.diagnosis}</p><table border="1" cellpadding="6" cellspacing="0" width="100%" style="border-collapse:collapse"><tr><th>序号</th><th>药材</th><th>数量</th><th>单位</th><th>单价</th><th>金额</th></tr>${rows}</table><p style="text-align:right;font-size:18px"><b>合计：<span style="color:#dc2626">¥${p.total_amount.toFixed(2)}</span></b></p></body></html>`;
  },

  list_patients: ({ keyword }) => {
    let list = db.patients;
    const kw = (keyword as string)?.toLowerCase();
    if (kw) {
      list = list.filter((p) => p.name.toLowerCase().includes(kw) || (p.phone ?? '').includes(kw));
    }
    return list;
  },

  create_patient: ({ patient }) => {
    const p = patient as Patient;
    const id = db.nextId.patient++;
    db.patients.push({ ...p, id, created_at: now(), updated_at: now() });
    pushLog('CREATE', 'patient', id, `建档: ${p.name}`);
    return id;
  },

  update_patient: ({ patient }) => {
    const p = patient as Patient;
    const idx = db.patients.findIndex((v) => v.id === p.id);
    if (idx >= 0) {
      db.patients[idx] = { ...db.patients[idx], ...p, updated_at: now() };
      pushLog('UPDATE', 'patient', p.id!, `更新档案: ${p.name}`);
    }
    return null;
  },

  delete_patient: ({ id }) => {
    const p = db.patients.find((v) => v.id === id);
    const used = db.prescriptions.some((x) => x.patient_name === p?.name);
    if (used) throw new Error('该患者存在处方记录，无法删除');
    db.patients = db.patients.filter((v) => v.id !== id);
    if (p) pushLog('DELETE', 'patient', id as number, `删除档案: ${p.name}`);
    return null;
  },

  get_patient_statistics: ({ name }) => {
    const list = db.prescriptions.filter((p) => p.patient_name === name);
    return {
      prescription_count: list.length,
      total_amount: Math.round(list.reduce((s, p) => s + p.total_amount, 0) * 100) / 100,
      first_visit: list.length ? list[list.length - 1].created_at.slice(0, 10) : null,
      last_visit: list.length ? list[0].created_at.slice(0, 10) : null,
    };
  },

  create_backup: () => {
    const ts = now().replace(/[-: ]/g, '').slice(0, 14);
    const entry: BackupEntry = {
      backup_path: `C:/AppData/backups/medicine_system_${ts}.db`,
      file_size: 1_800_000 + db.prescriptions.length * 512,
      checksum: 'demo0checksum0000000000000000000000000000000000000000000000000000',
      created_at: now(),
    };
    db.backups.unshift(entry);
    pushLog('BACKUP', 'database', 0, '创建数据库备份');
    return entry;
  },

  list_backups: () => db.backups,

  restore_backup: () => {
    pushLog('RESTORE', 'database', 0, '从备份还原（演示）');
    return null;
  },

  delete_backup: () => {
    pushLog('DELETE', 'backup', 0, '删除备份（演示）');
    return null;
  },

  check_for_update: () => ({
    version: '1.3.0',
    release_name: '当前版本（演示模式无更新）',
    changelog: '',
    download_url: '',
    file_size: 0,
    checksum: '',
  }),

  check_and_download_silently: () => ({
    has_update: false,
    info: { version: '1.3.0', release_name: '演示模式', changelog: '', download_url: '', file_size: 0, checksum: '' },
    downloaded_path: '',
  }),

  download_update: () => {
    throw new Error('演示模式下不支持下载更新');
  },

  install_update: () => {
    throw new Error('演示模式下不支持安装更新');
  },
};

// ==================== 辅助 ====================

function pushHistory(
  medicineId: number,
  medicineNameStr: string,
  type: string,
  quantity: number,
  price: number,
  batchId: number,
  operator: string | undefined,
  notes: string,
) {
  db.history.push({
    id: db.nextId.history++,
    medicine_id: medicineId,
    medicine_name: medicineNameStr,
    type,
    quantity,
    price,
    total_amount: Math.round(quantity * price * 100) / 100,
    operator: operator ?? '',
    notes,
    batch_id: batchId,
    created_at: now(),
  });
}

function pushLog(opType: string, targetType: string, targetId: number, details: string) {
  db.logs.push({
    id: db.nextId.log++,
    operation_type: opType,
    target_type: targetType,
    target_id: targetId,
    operator: '',
    details,
    created_at: now(),
  });
}

// ==================== 安装拦截 ====================

export function installTauriMock(): void {
  const w = window as unknown as {
    __TAURI_INTERNALS__?: {
      invoke: (cmd: string, args?: Record<string, unknown>) => Promise<unknown>;
      transformCallback: (cb: (r: unknown) => void) => number;
    };
  };

  let callbackId = 0;
  w.__TAURI_INTERNALS__ = {
    transformCallback: (cb) => {
      callbackId += 1;
      (window as unknown as Record<string, unknown>)[`_${callbackId}`] = cb;
      return callbackId;
    },
    invoke: (cmd: string, args: Record<string, unknown> = {}) => {
      const handler = handlers[cmd];
      // 统一模拟 Tauri invoke 的微任务异步行为
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          if (!handler) {
            reject(new Error(`演示模式未实现命令: ${cmd}`));
            return;
          }
          try {
            resolve(respondOk(handler(args)));
          } catch (e) {
            reject(String(e instanceof Error ? e.message : e));
          }
        }, 60);
      });
    },
  };

  console.info(
    '%c[演示模式] 检测到非 Tauri 环境，已启用浏览器演示数据（仅前端内存，不落盘）',
    'color:#2D5F3F;font-weight:bold',
  );
}
