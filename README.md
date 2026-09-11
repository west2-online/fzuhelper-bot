# fzuhelper-bot

## 功能

* 推送福uu 内测版更新日志
* AI 生成更新日志
* 上传福uu 测试版apk

## 部署

### 前置需求

* 已安装 [Docker](https://docs.docker.com/engine/install/)和[Docker Compose](https://docs.docker.com/compose/install/)
* QQ 官方机器人账号

### 1. 下载并解压release

```bash
wget https://github.com/west2-online/fzuhelper-bot/releases/download/edge/docker-fzuhelper-bot.tar.gz
tar -xzf docker-fzuhelper-bot.tar.gz
cd docker-fzuhelper-bot
```

### 2. 配置环境变量

```bash
cp .env.example .env
nano .env
```

### 3. 配置 Docker Compose

复制 docker-compose 模板并重命名：

```bash
cp docker-compose.yml docker-compose.override.yml
```

编辑 `docker-compose.override.yml` 文件，配置端口映射等：

```yaml
services:
  nonebot:
    ports:
      - "8080:8080"
```

### 4. 使用Docker Compose部署

```bash
docker compose up -d
```
