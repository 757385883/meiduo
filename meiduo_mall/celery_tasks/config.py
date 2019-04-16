# celery r配置文件

#配置任务队列 在redis中的消息队列，用来存储异步任务
# 指定使用redis的14号数据库
broker_url = "redis://192.168.0.6/14"