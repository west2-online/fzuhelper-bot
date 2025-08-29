# fzuhelper-bot

## 部署

### 1. 克隆仓库

```bash
git clone https://github.com/ACaiCat/fzuhelper-bot.git
cd fzuhelper-bot
```

### 2. 配置 Docker Compose

复制 docker-compose 模板并重命名：

```bash
cp docker-compose.yml docker-compose.override.yml
```

编辑 `docker-compose.override.yml` 文件，配置必要的环境变量：

```yaml
services:
  nonebot:
    ports:
      - "8080:8080"
    environment:
      WEBHOOK_SECRET: YOUR_SECRET_HERE  # 替换为您的WebHook密钥
      TEST_GROUP_ID: 785037622          # 测试群号
      APP_REPO: ACaiCat/WebHookTest     # 完整仓库名
    # 其他配置...
```

### 3. 使用 Docker Compose 部署

```bash
docker-compose up -d
```

### 4. 登录 QQ 机器人

查看Lagrange.OneBot日志并扫描二维码登录：

```bash
docker logs -f lagrange-onebot
```

> [!NOTE]
> 如果控制台中的二维码无法扫描，可以打开 `data/qr-0.png` 文件扫描图片中的二维码。
