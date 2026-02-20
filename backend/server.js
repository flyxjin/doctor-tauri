const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');

// 导入数据库连接
const { initializeDB } = require('./config/db');

const app = express();
const port = 3001;

// 中间件
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// 静态文件服务
app.use(express.static(path.join(__dirname, '../dist')));

// 路由
const medicinesRouter = require('./routes/medicines');
const prescriptionsRouter = require('./routes/prescriptions');
const inventoryRouter = require('./routes/inventory');

app.use('/api/medicines', medicinesRouter);
app.use('/api/prescriptions', prescriptionsRouter);
app.use('/api/inventory', inventoryRouter);

// 健康检查
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok' });
});

// 所有其他请求都返回index.html
app.use((req, res) => {
  res.sendFile(path.join(__dirname, '../dist/index.html'));
});

// 启动服务器
async function startServer() {
  try {
    // 初始化数据库
    await initializeDB();
    
    // 启动服务器
    app.listen(port, () => {
      console.log(`服务器运行在 http://localhost:${port}`);
    });
  } catch (error) {
    console.error('启动服务器失败:', error.message);
  }
}

// 调用启动函数
startServer();