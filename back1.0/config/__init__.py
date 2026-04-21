import pymysql

# 配置 pymysql 作为 MySQL 的驱动
pymysql.install_as_MySQLdb()

# 绕过 mysqlclient 版本检查
pymysql.version_info = (2, 2, 1, "final", 0)
