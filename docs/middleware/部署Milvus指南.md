# 本地部署Milvus服务的最简单方式

## 一、前提条件

### 1.1 安装Docker和Docker Compose

#### Windows系统
1. **启用WSL2**：
   ```powershell
   # 以管理员身份运行PowerShell
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   # 重启计算机
   ```

2. **安装Docker Desktop**：
   - 从官网下载并安装：https://www.docker.com/products/docker-desktop
   - 安装时勾选"使用WSL2引擎"

3. **配置镜像加速器**：
   - 打开Docker Desktop设置
   - 进入"Docker引擎"配置项
   - 添加国内镜像源：
     ```json
     {
       "registry-mirrors": [
         "https://docker.mirrors.ustc.edu.cn",
         "https://hub-mirror.c.163.com",
         "https://registry.docker-cn.com"
       ]
     }
     ```
   - 点击"应用并重启"

#### Linux系统
```bash
# 安装Docker
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io

# 安装Docker Compose
sudo apt-get install docker-compose-plugin

# 配置镜像加速器
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": ["https://docker.mirrors.ustc.edu.cn"]
}
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker
```

## 二、部署Milvus

### 2.1 下载Docker Compose配置文件

```bash
# 创建项目目录
mkdir milvus-demo && cd milvus-demo

# 下载配置文件（Windows使用PowerShell或WSL2）
wget https://github.com/milvus-io/milvus/releases/download/v2.4.23/milvus-standalone-docker-compose.yml -O docker-compose.yml
```

### 2.2 启动Milvus服务

```bash
docker compose up -d
```

### 2.3 验证服务状态

```bash
docker compose ps
```

正常运行时应显示三个容器：
- milvus-etcd
- milvus-minio
- milvus-standalone

## 三、使用Milvus

### 3.1 连接Milvus

Milvus服务默认监听端口：
- 服务端口：19530
- WebUI端口：9091（部分版本）

### 3.2 安装可视化工具Attu（可选）

```bash
docker run -d \
  -p 8000:3000 \
  -e MILVUS_URL=host.docker.internal:19530 \
  --name attu \
  zilliz/attu:latest
```

访问 http://localhost:8000 即可使用Attu管理Milvus

## 四、停止和删除服务

```bash
# 停止服务
docker compose down

# 删除数据（谨慎操作）
rm -rf volumes
```

## 五、常见问题排查

1. **端口冲突**：修改docker-compose.yml中的端口映射
2. **启动超时**：检查网络连接，配置国内镜像源
3. **权限问题**：执行`chmod 777 ./volumes`赋予权限

## 六、连接到项目

在我们的智能测试用例平台中，配置文件已默认指向本地Milvus服务：
- 主机：localhost
- 端口：19530
- 集合名：knowledge_base

部署完成后，重启平台后端服务即可自动连接。