当然，我可以帮助您编写完整的 API 文档。基于您提供的前端代码和之前的讨论，以下是针对您的预算管理系统中使用的主要 API 端点的详细文档。该文档涵盖了身份验证、数据获取以及错误处理等方面。

---

# API 文档

## 概述

本 API 文档详细描述了预算管理系统中各个端点的使用方法，包括请求方法、所需参数、响应格式以及可能的错误响应。所有 API 请求均需通过 JWT（JSON Web Token）进行身份验证。

---

## 认证

### 请求头

所有需要认证的 API 端点必须在请求头中包含以下字段：

```http
Authorization: Bearer <your_jwt_token>
```

- **Bearer**: 认证类型，固定为 `Bearer`。
- **<your_jwt_token>**: 用户的 JWT 令牌。

### 错误响应

如果缺少或提供了无效的 JWT 令牌，服务器将返回 `401 Unauthorized` 错误。

**示例响应：**

```json
{
  "error": "Invalid or missing authentication token."
}
```

---

## 端点详情

### 1. 用户注册

#### **Endpoint**

```
POST /register
```

#### **描述**

创建一个新的用户账户。

#### **请求参数**

| 参数      | 类型   | 必填 | 描述               |
| --------- | ------ | ---- | ------------------ |
| username  | string | 是   | 用户名，必须唯一   |
| password  | string | 是   | 用户密码，至少 6 位 |
| email     | string | 是   | 用户邮箱，必须唯一 |

#### **请求示例**

```http
POST /register HTTP/1.1
Host: your-api-domain.com
Content-Type: application/json

{
  "username": "john_doe",
  "password": "securePassword123",
  "email": "john@example.com"
}
```

#### **成功响应**

**状态码:** `201 Created`

**响应体:**

```json
{
  "message": "User registered successfully."
}
```

#### **错误响应**

| 状态码 | 描述                                    |
| ------ | --------------------------------------- |
| 400    | 请求参数错误（如缺少必填字段、邮箱或用户名已存在） |
| 500    | 服务器内部错误                          |

**示例响应（用户名已存在）：**

```json
{
  "error": "Username already exists."
}
```

### 2. 用户登录

#### **Endpoint**

```
POST /login
```

#### **描述**

用户登录，获取 JWT 令牌。

#### **请求参数**

| 参数      | 类型   | 必填 | 描述             |
| --------- | ------ | ---- | ---------------- |
| username  | string | 是   | 用户名           |
| password  | string | 是   | 用户密码         |

#### **请求示例**

```http
POST /login HTTP/1.1
Host: your-api-domain.com
Content-Type: application/json

{
  "username": "john_doe",
  "password": "securePassword123"
}
```

#### **成功响应**

**状态码:** `200 OK`

**响应体:**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### **错误响应**

| 状态码 | 描述                   |
| ------ | ---------------------- |
| 400    | 请求参数错误（如缺少字段） |
| 401    | 认证失败（用户名或密码错误） |
| 500    | 服务器内部错误         |

**示例响应（认证失败）：**

```json
{
  "error": "Invalid username or password."
}
```

### 3. 获取汇总数据

#### **Endpoint**

```
GET /summary
```

#### **描述**

根据指定的时间粒度（年、月、日、整体）获取用户的收入、支出和结余汇总数据。

#### **请求参数**

| 参数   | 类型   | 必填 | 描述                                       |
| ------ | ------ | ---- | ------------------------------------------ |
| period | string | 是   | 时间粒度，支持的值包括：`year`、`month`、`day`、`overall`。 |

- **`year`**: 按年汇总。
- **`month`**: 按月汇总。
- **`day`**: 按日汇总。
- **`overall`**: 整体汇总。

#### **请求示例**

```http
GET /summary?period=month HTTP/1.1
Host: your-api-domain.com
Authorization: Bearer <your_jwt_token>
```

#### **成功响应**

**状态码:** `200 OK`

**响应体:**

```json
{
  "summary": [
    {
      "year": 2024,
      "month": 4,
      "total_income": 15000,
      "total_expense": 8000,
      "balance": 7000
    },
    // 根据时间粒度返回多个汇总对象
  ]
}
```

**字段说明:**

| 字段           | 类型    | 描述                                     |
| -------------- | ------- | ---------------------------------------- |
| year           | integer | 年份                                     |
| month          | integer | 月份（仅在 `period` 为 `month` 或 `day` 时存在） |
| day            | integer | 日期（仅在 `period` 为 `day` 时存在）         |
| total_income   | number  | 总收入（单位：元）                         |
| total_expense  | number  | 总支出（单位：元）                         |
| balance        | number  | 结余（单位：元）                           |

#### **错误响应**

| 状态码 | 描述                                   |
| ------ | -------------------------------------- |
| 400    | 请求参数错误（如缺少 `period`）        |
| 401    | 未授权或令牌无效                       |
| 500    | 服务器内部错误                         |

**示例响应（缺少参数）：**

```json
{
  "error": "缺少必要的参数：period。"
}
```

### 4. 获取分类汇总数据（饼图数据）

#### **Endpoint**

```
GET /summary_pie
```

#### **描述**

根据指定的时间粒度和时间参数，获取用户的收入和支出分类汇总数据，用于生成饼图。

#### **请求参数**

| 参数   | 类型    | 必填 | 描述                                           |
| ------ | ------- | ---- | ---------------------------------------------- |
| period | string  | 是   | 时间粒度，支持的值包括：`year`、`month`、`day`、`overall`。 |
| year   | integer | 否   | 年份（当 `period` 为 `year`、`month`、`day` 时必填）          |
| month  | integer | 否   | 月份（当 `period` 为 `month`、`day` 时必填）               |
| day    | integer | 否   | 日期（当 `period` 为 `day` 时必填）                        |

**注：**

- 当 `period` 为 `overall` 时，不需要提供 `year`、`month` 或 `day` 参数。

#### **请求示例**

1. **按年汇总**

   ```http
   GET /summary_pie?period=year&year=2024 HTTP/1.1
   Host: your-api-domain.com
   Authorization: Bearer <your_jwt_token>
   ```

2. **按月汇总**

   ```http
   GET /summary_pie?period=month&year=2024&month=4 HTTP/1.1
   Host: your-api-domain.com
   Authorization: Bearer <your_jwt_token>
   ```

3. **按日汇总**

   ```http
   GET /summary_pie?period=day&year=2024&month=4&day=27 HTTP/1.1
   Host: your-api-domain.com
   Authorization: Bearer <your_jwt_token>
   ```

4. **整体汇总**

   ```http
   GET /summary_pie?period=overall HTTP/1.1
   Host: your-api-domain.com
   Authorization: Bearer <your_jwt_token>
   ```

#### **成功响应**

**状态码:** `200 OK`

**响应体:**

```json
{
  "period": "month",
  "year": 2024,
  "month": 4,
  "income_categories": [
    {
      "category": "工资",
      "amount": 10000
    },
    {
      "category": "投资",
      "amount": 5000
    }
  ],
  "expense_categories": [
    {
      "category": "餐饮",
      "amount": 7000
    },
    {
      "category": "交通",
      "amount": 2000
    },
    {
      "category": "娱乐",
      "amount": 1000
    }
  ]
}
```

**字段说明:**

| 字段               | 类型      | 描述                                     |
| ------------------ | --------- | ---------------------------------------- |
| period             | string    | 时间粒度，值为 `year`、`month`、`day` 或 `overall` |
| year               | integer   | 年份（当 `period` 为 `year`、`month`、`day` 时存在） |
| month              | integer   | 月份（当 `period` 为 `month`、`day` 时存在）          |
| day                | integer   | 日期（当 `period` 为 `day` 时存在）                   |
| income_categories  | array     | 收入分类数组，每个元素包含 `category` 和 `amount`        |
| expense_categories | array     | 支出分类数组，每个元素包含 `category` 和 `amount`       |

**收入分类元素说明:**

| 字段     | 类型   | 描述         |
| -------- | ------ | ------------ |
| category | string | 收入类别名称 |
| amount   | number | 收入金额（单位：元） |

**支出分类元素说明:**

| 字段     | 类型   | 描述         |
| -------- | ------ | ------------ |
| category | string | 支出类别名称 |
| amount   | number | 支出金额（单位：元） |

#### **错误响应**

| 状态码 | 描述                                     |
| ------ | ---------------------------------------- |
| 400    | 请求参数错误（如缺少必填参数或格式不正确） |
| 401    | 未授权或令牌无效                        |
| 500    | 服务器内部错误                          |

**示例响应（缺少参数）：**

```json
{
  "error": "缺少必要的参数：year 或 month。"
}
```

---

## 示例请求和响应

### 示例 1: 按月汇总

**请求：**

```http
GET /summary?period=month HTTP/1.1
Host: your-api-domain.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**响应：**

```json
{
  "summary": [
    {
      "year": 2024,
      "month": 4,
      "total_income": 15000,
      "total_expense": 8000,
      "balance": 7000
    }
  ]
}
```

**请求饼图数据：**

```http
GET /summary_pie?period=month&year=2024&month=4 HTTP/1.1
Host: your-api-domain.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**响应：**

```json
{
  "period": "month",
  "year": 2024,
  "month": 4,
  "income_categories": [
    {
      "category": "工资",
      "amount": 10000
    },
    {
      "category": "投资",
      "amount": 5000
    }
  ],
  "expense_categories": [
    {
      "category": "餐饮",
      "amount": 7000
    },
    {
      "category": "交通",
      "amount": 2000
    },
    {
      "category": "娱乐",
      "amount": 1000
    }
  ]
}
```

### 示例 2: 整体汇总

**请求：**

```http
GET /summary?period=overall HTTP/1.1
Host: your-api-domain.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**响应：**

```json
{
  "summary": [
    {
      "year": 2024,
      "total_income": 180000,
      "total_expense": 96000,
      "balance": 84000
    }
  ]
}
```

**请求饼图数据：**

```http
GET /summary_pie?period=overall HTTP/1.1
Host: your-api-domain.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**响应：**

```json
{
  "period": "overall",
  "income_categories": [
    {
      "category": "工资",
      "amount": 120000
    },
    {
      "category": "投资",
      "amount": 60000
    }
  ],
  "expense_categories": [
    {
      "category": "餐饮",
      "amount": 50000
    },
    {
      "category": "交通",
      "amount": 20000
    },
    {
      "category": "娱乐",
      "amount": 26000
    }
  ]
}
```

---

## 注意事项

1. **数据一致性**：
   - 确保前端在发送请求时提供的时间参数与后端数据库中的数据保持一致，避免因时区或格式问题导致的数据不匹配。

2. **性能优化**：
   - 对于数据量较大的请求（如 `overall`），建议在后端进行分页或数据聚合，以优化响应时间和减少带宽占用。

3. **安全性**：
   - 确保 JWT 令牌的安全存储，避免在客户端暴露敏感信息。
   - 后端应对所有输入参数进行严格验证，防止 SQL 注入或其他安全漏洞。

4. **错误处理**：
   - 前端应根据不同的错误类型（如 `400`、`401`、`500`）提供相应的用户反馈和处理逻辑。
   - 后端应提供清晰的错误信息，帮助前端开发者和用户理解问题所在。

5. **版本管理**：
   - 在 API 文档中注明版本信息，方便未来的更新和维护。
   - 例如，可以在每个端点的描述中添加版本号，如 `/summary (v1)`。

---

## 更新日志

| 版本 | 日期       | 更新内容                     |
| ---- | ---------- | ---------------------------- |
| 1.0  | 2024-04-27 | 初始文档发布                 |
| 1.1  | 2024-05-15 | 增加整体汇总功能的说明       |
| 1.2  | 2024-06-10 | 优化错误响应描述             |
| 1.3  | 2024-07-20 | 添加用户注册和登录端点       |
| ...  | ...        | ...                          |

---

## 联系方式

如果您在使用 API 时遇到任何问题或有任何建议，请通过以下方式联系我们：

- **电子邮件**: support@your-domain.com
- **电话**: +86-123-4567-8901
- **在线支持**: [your-support-page.com](http://your-support-page.com)

---

## 附录

### API 版本策略

- **主版本号 (Major)**: 当您做了不兼容的 API 修改时，增加主版本号。
- **次版本号 (Minor)**: 当您在保持向后兼容的前提下添加了功能时，增加次版本号。
- **修订号 (Patch)**: 当您做了向后兼容的问题修正时，增加修订号。

例如，`v1.0.0` 表示第一个主要版本，后续更新可为 `v1.1.0`、`v1.1.1` 等。

### 认证令牌

- **获取令牌**: 用户通过 `/login` 端点获取 JWT 令牌。
- **使用令牌**: 在每个需要认证的 API 请求中，在请求头中包含 `Authorization: Bearer <token>`。
- **令牌过期**: JWT 令牌具有有效期，过期后需要重新登录获取新令牌。

---

## 常见问题 (FAQ)

### 1. 如何获取 JWT 令牌？

用户需要通过 `/login` 端点使用有效的用户名和密码进行认证，成功后将收到 JWT 令牌。

### 2. 如果 JWT 令牌过期怎么办？

用户需要重新登录，通过 `/login` 端点获取新的 JWT 令牌。

### 3. 如何处理 `400 Bad Request` 错误？

确保所有必填参数已正确提供，参数格式符合要求。查看错误响应中的详细信息以了解具体问题。

### 4. 如何处理 `401 Unauthorized` 错误？

确认请求头中包含有效的 `Authorization` 令牌。如果令牌已过期，请重新登录获取新的令牌。

### 5. 如果遇到 `500 Internal Server Error`，该如何处理？

这是服务器内部错误，建议联系系统管理员或技术支持团队，提供错误日志以便排查问题。

---

## 示例代码

以下是使用 `curl` 命令行工具进行 API 请求的示例。

### 用户注册

```bash
curl -X POST http://your-api-domain.com/register \
-H "Content-Type: application/json" \
-d '{
  "username": "john_doe",
  "password": "securePassword123",
  "email": "john@example.com"
}'
```

### 用户登录

```bash
curl -X POST http://your-api-domain.com/login \
-H "Content-Type: application/json" \
-d '{
  "username": "john_doe",
  "password": "securePassword123"
}'
```

### 获取汇总数据

```bash
curl -X GET "http://your-api-domain.com/summary?period=month" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 获取分类汇总数据（饼图数据）

```bash
curl -X GET "http://your-api-domain.com/summary_pie?period=month&year=2024&month=4" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## 附加资源

- **API 测试工具**: [Postman](https://www.postman.com/)
- **JWT 详解**: [JWT官方文档](https://jwt.io/introduction/)
- **安全最佳实践**: [OWASP REST Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html)

---

希望以上文档能帮助您更好地理解和使用预算管理系统的 API。如果有任何进一步的问题或需要更多详细信息，请随时与我们联系！