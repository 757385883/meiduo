from django.core.files.storage import  Storage

from meiduo_mall.meiduo_mall import settings


class MyStorage(Storage):
    """
    自定义文件存储方案：将文件转存到fdfs
    """
    def __init__(self,client_config= None,host = None):
        self.client_config = client_config or settings.client_config
        """
        使用构造方法实现传参，因为无论是配置文件，还是url的路径主机地址，都可能发生改变，当然要有默认值，不穿也可以
        """
    def _open(self,name,mode='rb'):
        """
        打开文件是被调用的
        这个自定义的类，是做文件的存储的，不会涉及到文件的打开，
        所以没有实际的用处，但是文档要求我，如果想要自定义存储方案，必须写此方法，所以pass

        """
        pass

    def _save(self,name ,content):
        """
        保存文件时被调用的
        就是要借这个方法调用的时机，将发送给应用的文件，存储到fastdfs

        :param name:要保存的文件的名字
        :param content: 要保存的文件对象，file类型的对象，通过read（）读取文件对象中的存储的文件二进制
        :return:
        """
        # 创建 fastdfs 客户端对象
        client = Fdfs_client('客户端的配置文件')

        # 调用上传方法：upload_by_buffer(文件的二进制)，利用要保存的文件的二进制上传到fdfs
        ret = client.upload_by_buffer(content.read())

        #判断是否收藏成功
        if ret.get('Status') != 'Uploda successed':
            raise   Exception('ERROR')
        # 读取出file_id
        file_id = ret.get('Remote file_id')
        # 返回file_id
        # _save()的返回值，会自动的次存储到ImageFiled字段的模型类属性中，并且自动的同步到数据库
        return file_id
    def exists(self, name):
        """
        如果文件已经存在，就返回Ture ，那么该文件不在存储，save（）方法不会被调用
        :param name: 判断是否存在的文件的名字
        :return: False：告诉应用，要保存的name对应的文件不存在，就会调用save（）

       """
        return False

    def url(self,file_id):
        """
        为什么要重写url方法呢？
        因为前段在通过字段获取图片路径时，只能获取到存储在字段中的file_Id，
        并不是完整的url路径，以至于前段不能从服务器中找到相应的图片资源
        所以这里要重写 ，凭借完整的路径
        返回文件的相对路径
        :param name: 文件的名字
        :return:
        """
        return 'http://fastdfs 主机地址：8888/' + file_id