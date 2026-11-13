# Docker Compose 云服务器部署

这个部署包会启动三个容器：

- `house-backend`：LangGraph 后端，端口 `8001`
- `house-frontend`：静态前端页面，端口 `5500`
- `house-postgres` / `house-redis`：LangGraph 运行时持久化和队列

房源业务数据不放在这个 compose 里，后端会连接你已有的 MySQL：

```text
DB_HOST=your-db-host-or-service-name
DB_PORT=3308
DB_NAME=bitehouse
DB_USER=your-db-user
```

## 1. 上传并解压

```bash
unzip house-agent-compose-deploy.zip -d ~/langgraph_project
cd ~/langgraph_project/house-agent
```

## 2. 配置环境变量

```bash
cp .env.example .env
nano .env
```

至少修改这些值：

```env
DEEPSEEK_API_KEY=your-deepseek-api-key
DB_PASSWORD=replace-with-your-mysql-password
POSTGRES_PASSWORD=replace-with-your-postgres-password
```

注意：`.env` 不要提交到 Git，也不要发给别人。

## 3. 一键启动

```bash
bash deploy.sh
```

访问地址：

```text
前端：http://your-server-ip-or-domain:5500/static/house.html
后端：http://your-server-ip-or-domain:8001/docs
```

## 4. 常用运维命令

```bash
docker compose ps
docker logs house-backend --tail=120
docker logs house-frontend --tail=80
docker compose restart house-backend
docker compose down
```

如果 `8001` 或 `5500` 被占用，修改 `docker-compose.yml` 左侧端口，例如：

```yaml
ports:
  - "8002:8001"
```

左侧是云服务器端口，右侧是容器内部端口。
