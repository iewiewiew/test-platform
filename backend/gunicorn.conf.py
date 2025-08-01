# 绑定地址和端口
bind = "0.0.0.0:5001"
# 工作进程数
workers = 4
# 工作模式（sync为同步模式，gevent为协程模式）
worker_class = "gevent"
# 访问日志文件
accesslog = "./log/access.log"
# 错误日志文件
errorlog = "./log/error.log"
# 日志级别
loglevel = "info"