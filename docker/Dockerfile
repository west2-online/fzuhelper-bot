FROM python:3.13-slim

RUN apt-get update
RUN apt-get install curl -y

WORKDIR /app

ENV TZ=Asia/Shanghai
ENV PYTHONPATH=/app

ENV MAX_WORKERS=1

COPY .. /app/

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install uv
RUN uv sync --frozen


CMD ["uv", "run", "nb", "run"]
