# celery 运行的入口
#celery是个独立的服务器，尽量不适用别人的文件，都自己新建

# 创建celery 的客户端以下

#第一步，创建celery实例,并制定别名，没有实际意义
from celery import Celery

# 在发送邮件的异步任务中，需要用到django的配置文件，
# 所以我们需要修改celery的启动文件main.py，在其中指明celery可以读取的django配
# 为celery使用django配置文件进行设置
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'

# 创建异步实例
celery_app = Celery('meiduo')

# 加载配置文件，配置了broker_url，让app知道异步任务队列在哪里
celery_app.config_from_object('celery_tasks.config')

# 自动的将异步任务文件夹添加到celery_app，
# 这样celery客户端会自动找到异步任务文件
celery_app.autodiscover_tasks('celery_tasks.sms','celery_tasks.email')