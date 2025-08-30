# fzuhelper-bot

## 部署

### 1. 克隆仓库

```bash
git clone https://github.com/ACaiCat/fzuhelper-bot.git
cd fzuhelper-bot
```

### 2. 配置环境变量
```bash
cp .env.example .env
```

编辑 `.env` 文件，配置必要的环境变量：

```ini
DRIVER=~fastapi
WEBHOOK_SECRET=SECRET
TEST_GROUP_ID=785037622
APP_REPO=ACaiCat/WebHookTest
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

### 4. 使用 Docker Compose 部署

```bash
docker-compose up -d
```

### 5. 登录 QQ 机器人

查看Lagrange.OneBot日志并扫描二维码登录：

```bash
docker logs -f lagrange-onebot
```

> [!NOTE]
> 如果控制台中的二维码无法扫描，可以打开 `data/qr-0.png` 文件扫描图片中的二维码。

### 5. 测试BOT

在群中发送`/bot-ping` (首先得拉BOT进群)  
如果BOT正常就会响应`pong`