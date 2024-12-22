要在前端使用 Axios 请求时支持基于 JWT 的用户认证，可以按照以下步骤更新前端代码：

### 在 Axios 请求中附加 Token

更新前端代码中的 Axios 配置，确保在所有请求的 `Authorization` 头部附加令牌：

```javascript
import axios from 'axios';

axios.defaults.baseURL = 'http://localhost:5000'; // 后端地址
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('token'); // 假设令牌存储在本地存储中
  if (token) {
    config.headers.Authorization = token;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});
```

### 登录后存储 Token

在用户登录成功后，将 Token 存储到本地存储中，并将其用于后续请求：

```javascript
async login() {
  try {
    const response = await axios.post('/login', this.loginForm);
    const token = response.data.token;
    localStorage.setItem('token', token); // 存储 Token
    alert('登录成功！');
    this.isLoggedIn = true;
    this.fetchRecords(); // 获取用户记录
    this.fetchSummary(); // 获取汇总信息
  } catch (error) {
    alert(error.response?.data?.error || '登录失败');
  }
}
```

### 在其他请求中自动使用 Token

所有请求将自动使用设置的 `Authorization` 头部。例如：

#### 添加记录

```javascript
async addRecord() {
  try {
    await axios.post('/records', this.recordForm);
    alert('记录添加成功！');
    this.fetchRecords(); // 刷新记录
  } catch (error) {
    alert(error.response?.data?.error || '添加记录失败');
  }
}
```

#### 获取记录

```javascript
async fetchRecords() {
  try {
    const response = await axios.get('/records');
    this.records = response.data;
  } catch (error) {
    alert('获取记录失败');
  }
}
```

#### 获取汇总信息

```javascript
async fetchSummary() {
  try {
    const response = await axios.get('/summary');
    this.summary = response.data;
  } catch (error) {
    alert('获取汇总信息失败');
  }
}
```

### 登出时清除 Token

在用户退出时，清除存储的 Token：

```javascript
logout() {
  localStorage.removeItem('token');
  this.isLoggedIn = false;
  alert('您已退出登录');
}
```

通过这些改动，前端将可以利用 Axios 和 JWT 实现安全的用户认证和 API 调用。如果需要我直接在代码中实现这些改动，请告诉我！