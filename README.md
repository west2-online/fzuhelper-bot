# fzuhelper-bot

## 功能

* 推送福uu内测版更新日志
* BOT掉线通知

## 部署

### 前置需求

* 已安装 [Docker](https://docs.docker.com/engine/install/)和[Docker Compose](https://docs.docker.com/compose/install/)
* 一个已注册的QQ账号（用作机器人）
* 一个想好的GitHub Webhook密钥

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
#NoneBot驱动 (无需改动)
DRIVER=~fastapi 
#Webhook的密钥
WEBHOOK_SECRET=SECRET
#测试群号
TEST_GROUP_ID=785037622
#APP仓库的全名
APP_REPO=ACaiCat/WebHookTest
#离线飞书通知的Webhook地址
OFFLINE_NOTICE_WEBHOOK=https://www.feishu.cn/...
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

### 6. 测试BOT

在群中发送`/bot-ping` (首先得拉BOT进群)  
如果BOT正常就会响应`pong`

### 7. 添加Webhook

1. 在`仓库-Settings-Webhooks`选择`Add webhook`新建一个Webhook
2. 配置Webhook
    - Payload URL: `http(s)://address:port/github/webhook`
    - Content type: `application/json`
    - Secret: `webhook_secret`
    - Which events would you like to trigger this webhook?
        - `Let me select individual events.`  
          勾选`Releases`
        - `Send me everything.`

  > [!IMPORTANT]   
  > Bot的GitHub Webhook并不支持https交付。如果需要使用https交付，请配置Nginx等反代

3. 测试Webhook
   点开新建Webhook的Recent Deliveries可以看到最近的交付，如果ping事件正确响应，则Webhook配置正确

## BOT掉线重连

先重启`lagrange-onebot`容器

```bash
docker restart lagrange-onebot
```

然后再重新扫码登录

> [!NOTE]
> 如果被限制登录需要先在手机QQ上解除

> [!IMPORTANT]
> 如果重启容器后不显示二维码，可以尝试删除`data/keystore.json`和`data/device.json`再重启容器
> ```
> rm data/keystore.json data/device.json
> docker restart lagrange-onebot
> ```
