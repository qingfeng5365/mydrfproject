本项目基于drf、uwsgi、sqlite构建，支持docker部署，环境要求linux系统。

docker build -t mydrfproject:v1 .

docker run -dp 8002:8002 --name mydrfproject mydrfproject:v1
