# 使用Docker运行智能测试用例平台后端服务

由于Windows环境存在一些特定的兼容性问题，我们推荐使用Docker来运行后端服务。这种方式可以避免Windows系统级别的asyncio错误和依赖冲突。

## 前提条件

1. 已安装Docker Desktop for Windows
2. 已启动Docker服务
3. 本地已安装Milvus服务并运行在127.0.0.1:19530

## 构建Docker镜像

1. 打开命令提示符或PowerShell
2. 导航到项目目录：
   ```bash
   cd d:\github\ai-case-generate-platform\backend
   ```
3. 构建Docker镜像：
   ```bash
   docker build -t ai-case-platform-backend .
   ```

## 运行Docker容器

### 方法1：连接到本地Milvus服务

```bash
# 运行容器并映射端口
docker run -d -p 8000:8000 --name ai-case-platform \
  --network="host" \
  ai-case-platform-backend
```

### 方法2：使用Docker网络

如果本地Milvus也在Docker中运行，可以使用Docker网络来连接：

```bash
# 创建Docker网络
docker network create milvus-network

# 将Milvus容器连接到网络（如果尚未连接）
docker network connect milvus-network milvus-standalone

# 运行后端服务并连接到相同网络
docker run -d -p 8000:8000 --name ai-case-platform \
  --network="milvus-network" \
  -e MILVUS_HOST="milvus-standalone" \
  -e MILVUS_PORT="19530" \
  ai-case-platform-backend
```

## 验证服务

1. 检查容器是否正常运行：
   ```bash
   docker ps
   ```

2. 查看容器日志：
   ```bash
   docker logs ai-case-platform
   ```

3. 访问API文档：
   ```
   http://localhost:8000/docs
   ```

## 停止和删除容器

```bash
# 停止容器
docker stop ai-case-platform

# 删除容器
docker rm ai-case-platform

# 删除镜像（可选）
docker rmi ai-case-platform-backend
```

## 注意事项

1. 使用`--network="host"`参数可以让Docker容器直接访问主机的网络，这样可以轻松连接到本地运行的Milvus服务

2. 如果使用Docker网络方式，请确保Milvus容器的名称是`milvus-standalone`，或者根据实际情况修改环境变量`MILVUS_HOST`

3. 服务启动后，可以通过http://localhost:8000/docs访问Swagger UI来测试所有API接口

4. 如果需要修改代码并重新运行，可以使用以下命令：
   ```bash
   docker stop ai-case-platform
   docker rm ai-case-platform
   docker build -t ai-case-platform-backend .
   docker run -d -p 8000:8000 --name ai-case-platform --network="host" ai-case-platform-backend
   ```

## 故障排除

1. 如果容器无法启动，请检查日志：
   ```bash
   docker logs ai-case-platform
   ```

2. 如果无法连接到Milvus服务，请确保：
   - Milvus服务正在运行
   - 容器和Milvus服务在同一个网络中
   - Milvus的主机名和端口配置正确

3. 如果遇到依赖安装问题，请重新构建镜像：
   ```bash
   docker build --no-cache -t ai-case-platform-backend .
   ```

通过使用Docker，我们可以避免Windows环境下的各种兼容性问题，确保服务能够稳定运行。