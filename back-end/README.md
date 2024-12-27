# 项目文档

本项目是一个基于 Flask 的 Web 应用，提供用户认证、记录管理、数据汇总和文件上传等功能。本文档包括详细的 API 文档和启动指南，帮助你快速理解和部署应用。

---

## 目录

1. [API 文档](#api-文档)
    - [认证](#认证)
        - [用户注册](#用户注册)
        - [用户登录](#用户登录)
    - [记录管理](#记录管理)
        - [添加记录](#添加记录)
        - [获取记录](#获取记录)
        - [更新记录](#更新记录)
        - [删除记录](#删除记录)
    - [数据汇总](#数据汇总)
        - [获取汇总信息](#获取汇总信息)
        - [获取分类汇总信息（饼图数据）](#获取分类汇总信息饼图数据)
    - [文件上传](#文件上传)
        - [上传 Excel 文件并导入数据库](#上传-excel-文件并导入数据库)
2. [启动指南](#启动指南)
    - [前提条件](#前提条件)
    - [安装步骤](#安装步骤)
    - [配置](#配置)
    - [数据库初始化](#数据库初始化)
    - [运行应用](#运行应用)
    - [数据库迁移](#数据库迁移)
    - [常见问题](#常见问题)

---

## API 文档

### 认证

#### 用户注册

- **URL:** `/register`
- **方法:** `POST`
- **描述:** 用户注册，创建一个新用户账户。

##### 请求

- **Headers:** `Content-Type: application/json`
- **Body:**

    ```json
    {
        "username": "字符串，必填，用户名，必须唯一",
        "password": "字符串，必填，密码"
    }
    ```

##### 示例

```json
{
    "username": "john_doe",
    "password": "securepassword123"
}
```

##### 成功响应

- **状态码:** `201 Created`
- **Body:**

    ```json
    {
        "message": "用户注册成功。"
    }
    ```

##### 失败响应

- **状态码:** `400 Bad Request`
- **Body:**

    ```json
    {
        "error": "用户名和密码是必填项。"
    }
    ```

    或

    ```json
    {
        "error": "用户已存在。"
    }
    ```

#### 用户登录

- **URL:** `/login`
- **方法:** `POST`
- **描述:** 用户登录，验证用户名和密码，并返回 JWT 令牌。

##### 请求

- **Headers:** `Content-Type: application/json`
- **Body:**

    ```json
    {
        "username": "字符串，必填，用户名",
        "password": "字符串，必填，密码"
    }
    ```

##### 示例

```json
{
    "username": "john_doe",
    "password": "securepassword123"
}
```

##### 成功响应

- **状态码:** `200 OK`
- **Body:**

    ```json
    {
        "message": "登录成功。",
        "token": "JWT 令牌"
    }
    ```

##### 失败响应

- **状态码:** `400 Bad Request`
- **Body:**

    ```json
    {
        "error": "用户不存在。"
    }
    ```

    或

    ```json
    {
        "error": "账号或密码错误。"
    }
    ```

---

### 记录管理

> **注意:** 以下所有记录管理的 API 需要在请求头中包含 `Authorization` 字段，格式为 `Bearer <JWT Token>`。

#### 添加记录

- **URL:** `/records`
- **方法:** `POST`
- **描述:** 添加一条收入或支出记录，关联到当前用户。

##### 请求

- **Headers:**
    - `Content-Type: application/json`
    - `Authorization: Bearer <JWT Token>`
- **Body:**

    ```json
    {
        "amount": 1000.0,             // 浮点数，必填，金额
        "category": "工资",             // 字符串，必填，类别
        "type": "income",             // 字符串，必填，类型："income" 或 "expense"
        "note": "备注信息",              // 字符串，可选，备注
        "timeStamp": 1700000000        // 整数，可选，时间戳（单位：毫秒）
    }
    ```

##### 示例

```json
{
    "amount": 5000.0,
    "category": "工资",
    "type": "income",
    "note": "五月工资",
    "timeStamp": 1683000000000
}
```

##### 成功响应

- **状态码:** `200 OK`
- **Body:**

    ```json
    {
        "message": "记录添加成功。"
    }
    ```

##### 失败响应

- **状态码:** `400 Bad Request`
- **Body:**

    ```json
    {
        "error": "无效的时间戳。"
    }
    ```

    或

    ```json
    {
        "error": "记录添加失败",
        "details": "错误详情信息"
    }
    ```

#### 获取记录

- **URL:** `/records`
- **方法:** `GET`
- **描述:** 获取当前用户的所有收入或支出记录。

##### 请求

- **Headers:**
    - `Authorization: Bearer <JWT Token>`

##### 成功响应

- **状态码:** `200 OK`
- **Body:**

    ```json
    [
        {
            "id": 1,
            "amount": 5000.0,
            "category": "工资",
            "date": "2024-05-01 09:00",
            "time": "2024-05-01 09:00",
            "timeStamp": 1714537200000,
            "type": "income",
            "note": "五月工资"
        },
        {
            "id": 2,
            "amount": 200.0,
            "category": "餐饮",
            "date": "2024-05-02 12:30",
            "time": "2024-05-02 12:30",
            "timeStamp": 1714629000000,
            "type": "expense",
            "note": "午餐"
        }
        // 更多记录...
    ]
    ```

#### 更新记录

- **URL:** `/records/<record_id>`
- **方法:** `PUT`
- **描述:** 更新指定的记录信息。

##### 请求

- **Headers:**
    - `Content-Type: application/json`
    - `Authorization: Bearer <JWT Token>`
- **URL 参数:**
    - `record_id` (整数，必填，记录的唯一标识符)
- **Body:**

    ```json
    {
        "amount": 6000.0,              // 浮点数，可选，新的金额
        "category": "奖金",             // 字符串，可选，新的类别
        "type": "income",              // 字符串，可选，新的类型："income" 或 "expense"
        "timeStamp": 1700000000,       // 整数，可选，新的时间戳（单位：毫秒）
        "note": "更新后的备注"            // 字符串，可选，新的备注
    }
    ```

##### 示例

```json
{
    "amount": 5500.0,
    "note": "修正金额"
}
```

##### 成功响应

- **状态码:** `200 OK`
- **Body:**

    ```json
    {
        "message": "记录更新成功。",
        "updated_date": "2024-05-01 10:00"
    }
    ```

##### 失败响应

- **状态码:** `404 Not Found`
- **Body:**

    ```json
    {
        "error": "记录未找到。"
    }
    ```

    或

    ```json
    {
        "error": "无效的时间戳。"
    }
    ```

#### 删除记录

- **URL:** `/records/<record_id>`
- **方法:** `DELETE`
- **描述:** 删除指定的记录。

##### 请求

- **Headers:**
    - `Authorization: Bearer <JWT Token>`
- **URL 参数:**
    - `record_id` (整数，必填，记录的唯一标识符)

##### 成功响应

- **状态码:** `200 OK`
- **Body:**

    ```json
    {
        "message": "记录删除成功。"
    }
    ```

##### 失败响应

- **状态码:** `404 Not Found`
- **Body:**

    ```json
    {
        "error": "记录未找到。"
    }
    ```

---

### 数据汇总

#### 获取汇总信息

- **URL:** `/summary`
- **方法:** `GET`
- **描述:** 获取当前用户的收入、支出和结余的汇总信息，支持按年、月、日或自定义时间范围。

##### 请求

- **Headers:**
    - `Authorization: Bearer <JWT Token>`
- **查询参数:**
    - `period` (字符串，可选，取值 `'year'`、`'month'`、`'day'`、`'overall'` 或 `'custom'`。默认 `'overall'`)
    - `start_date` (字符串，可选，格式 `'YYYY-MM-DD'`，仅在 `period=custom` 时有效)
    - `end_date` (字符串，可选，格式 `'YYYY-MM-DD'`，仅在 `period=custom` 时有效)

##### 示例请求

- 按年汇总:

    ```
    GET /summary?period=year
    ```

- 自定义时间范围:

    ```
    GET /summary?period=custom&start_date=2024-01-01&end_date=2024-06-30
    ```

##### 成功响应

- **状态码:** `200 OK`
- **Body 示例:**

    - **按年:**

        ```json
        {
            "period": "year",
            "summary": [
                {
                    "year": 2024,
                    "total_income": 60000.0,
                    "total_expense": 30000.0,
                    "balance": 30000.0
                },
                {
                    "year": 2025,
                    "total_income": 70000.0,
                    "total_expense": 35000.0,
                    "balance": 35000.0
                }
            ]
        }
        ```

    - **自定义时间范围:**

        ```json
        {
            "period": "custom",
            "summary": [
                {
                    "year": 2024,
                    "month": 1,
                    "day": 15,
                    "total_income": 5000.0,
                    "total_expense": 2000.0,
                    "balance": 3000.0
                },
                {
                    "year": 2024,
                    "month": 1,
                    "day": 20,
                    "total_income": 3000.0,
                    "total_expense": 1500.0,
                    "balance": 1500.0
                }
                // 更多汇总数据...
            ]
        }
        ```

    - **整体汇总:**

        ```json
        {
            "period": "overall",
            "summary": [
                {
                    "total_income": 130000.0,
                    "total_expense": 65000.0,
                    "balance": 65000.0
                }
            ]
        }
        ```

##### 失败响应

- **状态码:** `400 Bad Request`
- **Body:**

    ```json
    {
        "error": "无效的 period 参数。可选值为 'year'、'month'、'day'、'overall' 或 'custom'。"
    }
    ```

    或

    ```json
    {
        "error": "获取汇总信息时出错。"
    }
    ```

#### 获取分类汇总信息（饼图数据）

- **URL:** `/summary_pie`
- **方法:** `GET`
- **描述:** 获取当前用户的收入和支出按类别的汇总信息，适用于生成饼图。

##### 请求

- **Headers:**
    - `Authorization: Bearer <JWT Token>`
- **查询参数:**
    - `period` (字符串，可选，取值 `'year'`、`'month'`、`'day'`、`'overall'`。默认 `'overall'`)
    - `year` (整数，可选，当 `period` 为 `'year'`、`'month'` 或 `'day'` 时必填)
    - `month` (整数，可选，当 `period` 为 `'month'` 或 `'day'` 时必填)
    - `day` (整数，可选，当 `period` 为 `'day'` 时必填)

##### 示例请求

- 按年分类汇总:

    ```
    GET /summary_pie?period=year&year=2024
    ```

- 按月分类汇总:

    ```
    GET /summary_pie?period=month&year=2024&month=5
    ```

- 按天分类汇总:

    ```
    GET /summary_pie?period=day&year=2024&month=5&day=15
    ```

##### 成功响应

- **状态码:** `200 OK`
- **Body 示例:**

    - **按年:**

        ```json
        {
            "period": "year",
            "year": 2024,
            "income_categories": [
                {"category": "工资", "amount": 50000.0},
                {"category": "投资", "amount": 10000.0}
            ],
            "expense_categories": [
                {"category": "餐饮", "amount": 15000.0},
                {"category": "交通", "amount": 5000.0}
            ]
        }
        ```

    - **按月:**

        ```json
        {
            "period": "month",
            "year": 2024,
            "month": 5,
            "income_categories": [
                {"category": "工资", "amount": 5000.0},
                {"category": "奖金", "amount": 2000.0}
            ],
            "expense_categories": [
                {"category": "餐饮", "amount": 2000.0},
                {"category": "娱乐", "amount": 1000.0}
            ]
        }
        ```

    - **整体汇总:**

        ```json
        {
            "period": "overall",
            "income_categories": [
                {"category": "工资", "amount": 130000.0},
                {"category": "投资", "amount": 20000.0}
            ],
            "expense_categories": [
                {"category": "餐饮", "amount": 30000.0},
                {"category": "交通", "amount": 10000.0},
                {"category": "娱乐", "amount": 5000.0}
            ]
        }
        ```

##### 失败响应

- **状态码:** `400 Bad Request`
- **Body:**

    ```json
    {
        "error": "无效的 period 参数。可选值为 'year'、'month'、'day' 或 'overall'。"
    }
    ```

    或

    ```json
    {
        "error": "缺少必要的参数：year。"
    }
    ```

    或

    ```json
    {
        "error": "获取分类汇总信息时出错。"
    }
    ```

---

### 文件上传

#### 上传 Excel 文件并导入数据库

- **URL:** `/upload`
- **方法:** `POST`
- **描述:** 上传一个 Excel 文件，解析文件内容并将数据导入 `Record` 表。

##### 请求

- **Headers:**
    - `Content-Type: multipart/form-data`
    - `Authorization: Bearer <JWT Token>`
- **Body:**
    - `file`: Excel 文件，必须为 `.xls` 或 `.xlsx` 格式。

##### 示例

使用 `curl` 命令上传文件：

```bash
curl -X POST http://localhost:5000/upload \
  -H "Authorization: Bearer <JWT Token>" \
  -F "file=@/path/to/your/file.xlsx"
```

##### 成功响应

- **状态码:** `200 OK`
- **Body:**

    ```json
    {
        "message": "文件上传并导入成功。",
        "imported_records": 50
    }
    ```

##### 失败响应

- **状态码:** `400 Bad Request`
- **Body:**

    ```json
    {
        "error": "未找到文件。"
    }
    ```

    或

    ```json
    {
        "error": "无效的文件类型。只能上传 .xls 或 .xlsx 文件。"
    }
    ```

    或

    ```json
    {
        "error": "Excel 文件缺少必要的列。缺少列：时间, 类别"
    }
    ```

    或

    ```json
    {
        "error": "处理文件时出错。"
    }
    ```

---

## 启动指南

### 前提条件

在开始之前，请确保你的系统满足以下条件：

- **操作系统:** Windows, macOS 或 Linux
- **Python:** 3.7 及以上版本
- **Git:** 可选，用于代码版本控制
- **虚拟环境工具:** `venv`（内置于 Python 3.3+）

### 安装步骤

1. **克隆仓库**


    ```bash
    git clone https://github.com/stardrophere/LLM-homework.git
    cd LLM-homework
    ```


2. **创建虚拟环境**

    推荐使用 Python 的虚拟环境来隔离项目依赖：

    ```bash
    python3 -m venv venv
    ```

    > **注意:** 如果使用 Windows，激活虚拟环境的命令为 `venv\Scripts\activate`。

3. **激活虚拟环境**

    - **macOS/Linux:**

        ```bash
        source venv/bin/activate
        ```

    - **Windows:**

        ```bash
        venv\Scripts\activate
        ```

4. **安装依赖**

    使用 `pip` 安装项目所需的所有依赖：

    ```bash
    pip install -r requirements.txt
    ```


### 配置

1. **环境变量**

    为了增强安全性和灵活性，建议通过环境变量配置敏感信息。可以使用 `.env` 文件来管理环境变量，结合 `python-dotenv` 包（如果已安装）。

    创建一个 `.env` 文件在项目根目录，并添加以下内容：

    ```env
    SECRET_KEY=your_secret_key
    DATABASE_URL=sqlite:///user_info.db
    UPLOAD_FOLDER=uploads
    ```

    > **注意:** 如果不使用 `.env` 文件，确保在 `app/config.py` 中提供了默认值或其他方式加载配置。

2. **配置文件**

    项目已包含 `app/config.py`，你可以根据需要修改其中的配置。

    ```python
    # app/config.py

    import os

    class Config:
        SECRET_KEY = os.environ.get('SECRET_KEY', 'manwhatcanisay')
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///user_info.db')
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ```

### 数据库初始化

1. **初始化数据库**

    本项目使用 SQLite 作为数据库。如果需要使用其他数据库（如 PostgreSQL、MySQL），请相应地修改 `DATABASE_URL`。

    ```bash
    # 确保虚拟环境已激活
    python run.py
    ```

    应用首次运行时，会自动创建数据库和所需的表。

2. **使用 Flask-Migrate 进行数据库迁移**

    如果对数据库模型进行了修改，建议使用 Flask-Migrate 进行迁移管理。

    - **初始化迁移目录**

        ```bash
        flask db init
        ```

    - **生成迁移脚本**

        ```bash
        flask db migrate -m "描述迁移内容"
        ```

    - **应用迁移**

        ```bash
        flask db upgrade
        ```

    > **提示:** 确保在 `app/__init__.py` 中已初始化 `migrate`。

### 运行应用

1. **启动开发服务器**

    确保虚拟环境已激活，并在项目根目录运行：

    ```bash
    python run.py
    ```

    默认情况下，应用会在 `http://0.0.0.0:5000` 运行，并开启调试模式。

2. **访问应用**

    使用浏览器或 API 客户端（如 Postman）访问：

    ```
    http://localhost:5000/
    ```

### 数据库迁移

本项目使用 Flask-Migrate 管理数据库迁移。以下是常用的迁移命令：

- **初始化迁移环境**

    ```bash
    flask db init
    ```

- **生成迁移脚本**

    每次修改数据库模型后，运行：

    ```bash
    flask db migrate -m "描述迁移内容"
    ```

- **应用迁移**

    ```bash
    flask db upgrade
    ```

- **回滚迁移**

    回滚到上一个迁移版本：

    ```bash
    flask db downgrade
    ```

### 常见问题

#### 1. 无法激活虚拟环境

- **解决方法:**
    - 确认你使用的命令与操作系统匹配。
    - 确认虚拟环境已正确创建。
    - 在 Windows 上，确保使用 PowerShell 或 CMD 运行激活命令。

#### 2. 数据库连接失败

- **解决方法:**
    - 检查 `DATABASE_URL` 是否正确配置。
    - 确保数据库服务（如使用 PostgreSQL）正在运行。
    - 查看应用日志获取详细错误信息。

#### 3. 文件上传失败

- **解决方法:**
    - 确认上传的文件类型为 `.xls` 或 `.xlsx`。
    - 检查上传目录是否存在且具有写权限。
    - 查看应用日志了解具体错误。

#### 4. JWT 令牌无效或过期

- **解决方法:**
    - 确认 JWT 令牌正确传递在 `Authorization` 头中。
    - 检查服务器时间是否正确，避免因时差导致令牌过期。
    - 确认 `SECRET_KEY` 一致，确保令牌签发和验证使用相同的密钥。

---

## 附录

### 项目结构

```
your_project/
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── records.py
│   │   ├── summary.py
│   │   └── upload.py
│   ├── utils.py
│   ├── config.py
│   └── extensions.py
│
├── migrations/
│
├── uploads/
│
├── requirements.txt
├── run.py
└── .gitignore
```

### 依赖列表 (`requirements.txt`)

确保 `requirements.txt` 包含以下依赖：

```txt
Flask
Flask-Cors
Flask-SQLAlchemy
Flask-Migrate
Werkzeug
PyJWT
pytz
pandas
python-dotenv
```

> **提示:** 根据实际需要添加或删除依赖。

### 启动脚本 (`run.py`)

```python
# run.py

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### 配置文件 (`app/config.py`)

```python
# app/config.py

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'manwhatcanisay')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///user_info.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
```

---
