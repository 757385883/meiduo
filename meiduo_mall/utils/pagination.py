"""
分页效果，全局使用，所以定义在其他工具里，便于使用
PageNumberPagination 分页后端自动实现分页效果
1.在这里自定义分页效果
2.在配置文件中 ，指定自定义后的分页类
3.
"""

from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 2 # 分页展示条数，默认
    page_size_query_param = 'page_size'
    max_page_size = 20 # 最大条数