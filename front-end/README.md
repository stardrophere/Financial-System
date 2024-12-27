# 项目启动指南

## 前提条件

在开始之前，请确保您的系统上已经安装了以下软件：

- Node.js (推荐版本 14.x 或更高)
- npm (Node.js 包管理器，通常随 Node.js 一起安装)

## 克隆项目

首先，克隆项目代码库到本地：

```bash
git clone https://github.com/stardrophere/LLM-homework.git
cd front-end
```

## 安装依赖

在项目根目录下运行以下命令来安装所有必要的依赖：

```bash
npm install
```

## 配置环境变量

根据需要配置项目的环境变量。通常，您可以在项目根目录下创建一个 `.env` 文件，并在其中添加所需的环境变量。例如：

```bash
VUE_APP_API_BASE_URL=http://localhost:5173
```

## 启动开发服务器

安装完依赖后，运行以下命令启动开发服务器：

```bash
npm run dev
```

开发服务器启动后，您可以在浏览器中访问 `http://localhost:5000` 查看项目。

## 构建项目

如果您需要构建项目以供生产环境使用，请运行以下命令：

```bash
npm run build
```

构建完成后，生成的文件将位于 `dist` 目录中。


## 其他命令

- `npm run lint`：运行代码检查工具以确保代码风格一致。
- `npm run lint --fix`：自动修复代码中的可修复问题。

## 结束

以上就是项目的基本启动指南。如果您在启动过程中遇到任何问题，请参考项目的文档或联系项目维护者。