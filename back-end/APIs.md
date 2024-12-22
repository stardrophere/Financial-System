# API 文档

## 1. 注册新用户
- **接口地址：** `/register`
- **请求方法：** `POST`
- **请求 JSON：**
  ```json
  {
      "username": "用户名",
      "password": "密码"
  }
  ```
- **响应 JSON：**
  - 成功：
    ```json
    {"message": "用户注册成功。"}
    ```
  - 错误：
    ```json
    {"error": "错误信息"}
    ```
- **状态码：**
  - `201`：用户注册成功。
  - `400`：缺少字段或用户已存在。

## 2. 用户登录
- **接口地址：** `/login`
- **请求方法：** `POST`
- **请求 JSON：**
  ```json
  {
      "username": "用户名",
      "password": "密码"
  }
  ```
- **响应 JSON：**
  - 成功：
    ```json
    {"message": "登录成功。", "user_id": 用户ID}
    ```
  - 错误：
    ```json
    {"error": "无效的凭据。"}
    ```
- **状态码：**
  - `200`：登录成功。
  - `401`：无效的凭据。

## 3. 添加新记录
- **接口地址：** `/records`
- **请求方法：** `POST`
- **请求 JSON：**
  ```json
  {
      "user_id": 用户ID,
      "amount": 金额,
      "category": "类别",
      "type": "income 或 expense"
  }
  ```
- **响应 JSON：**
  - 成功：
    ```json
    {"message": "记录添加成功。"}
    ```
  - 错误：
    ```json
    {"error": "所有字段都是必填项。"}
    ```
- **状态码：**
  - `201`：记录添加成功。
  - `400`：缺少字段。

## 4. 获取用户所有记录
- **接口地址：** `/records/<user_id>`
- **请求方法：** `GET`
- **响应 JSON：**
  ```json
  [
      {
          "id": 记录ID,
          "amount": 金额,
          "category": "类别",
          "date": "日期",
          "type": "income 或 expense"
      },
      ...
  ]
  ```
- **状态码：**
  - `200`：记录获取成功。

## 5. 编辑记录
- **接口地址：** `/records/<record_id>`
- **请求方法：** `PUT`
- **请求 JSON：**
  ```json
  {
      "amount": 新金额,
      "category": "新类别",
      "type": "income 或 expense",
      "date": "新日期 (可选)"
  }
  ```
- **响应 JSON：**
  - 成功：
    ```json
    {"message": "记录更新成功。"}
    ```
  - 错误：
    ```json
    {"error": "记录未找到。"}
    ```
- **状态码：**
  - `200`：记录更新成功。
  - `404`：记录未找到。

## 6. 删除记录
- **接口地址：** `/records/<record_id>`
- **请求方法：** `DELETE`
- **响应 JSON：**
  - 成功：
    ```json
    {"message": "记录删除成功。"}
    ```
  - 错误：
    ```json
    {"error": "记录未找到。"}
    ```
- **状态码：**
  - `200`：记录删除成功。
  - `404`：记录未找到。

## 7. 获取收支汇总
- **接口地址：** `/summary/<user_id>`
- **请求方法：** `GET`
- **响应 JSON：**
  ```json
  {
      "total_income": 总收入,
      "total_expense": 总支出,
      "balance": 结余
  }
  ```
- **状态码：**
  - `200`：汇总获取成功。
