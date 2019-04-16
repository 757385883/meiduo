# 定义异步任务的文件，名字必须是tasks

# 异步任务就是定义一个函数，然后使用celery_app装饰



from meiduo_mall.celery_tasks.main import celery_app
from meiduo_mall.celery_tasks.sms.yuntongxun.sms import CCP
from . import constants
# 具体的异步任务 name='send_sms_code' 给异步任务起名字
@celery_app.task(name='send_sms_code')
def send_sms_code(mobile,sms_code):
    CCP().send_template_sms(mobile,sms_code, [constants.IMAGE_CODE_REDIS_EXPIRES // 60], 1)


# 在终端找到含有 celery_tasks的目录下
# 输入 celery -A celery_tasks.main worker -l info
# 启动worker 执行异步任务