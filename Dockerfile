FROM python:3.9
LABEL maintainer="eilhyo"
RUN groupadd -r myuser && useradd -r -g myuser myuser
RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get install -y libpcre3 libpcre3-dev \
    && rm -rf /var/lib/apt/lists/*
# COPY pip.conf /root/.pip/pip.conf
RUN mkdir -p /var/www/html/mysite6
WORKDIR /var/www/html/mysite6
ADD . /var/www/html/mysite6
# RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN sed -i 's/\r//' ./start.sh
RUN chmod +x ./start.sh 
RUN chown -R myuser:myuser /var/www/html/mysite6
# 切换到非root用户
USER myuser

# 设置容器启动时执行的命令和参数
CMD ["./start.sh"]