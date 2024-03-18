##  前端 ♝

建议使用yarn，项目提供了`yarn.lock`，使用其他包管理器，容易出现版本依赖问题。

```bash
# 克隆项目
git clone https://github.com/tahitimoon/LunarLink.git

# 进入项目目录
cd LunarLink/frontend

# 安装依赖
yarn install --registry=https://registry.npmmirror.com

# 启动服务
yarn start
# 浏览器访问 http://127.0.0.1:8888
# config/index.js 文件可配置启动端口等参数
# config/dev.env.js 文件可配置后端接口地址
# config/prod.env.js 文件保持不变
# 构建生产环境
# yarn build
```
