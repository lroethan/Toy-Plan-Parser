import os
import pymysql
import json

def flatten_json(json_obj, sep="_"):
    result = {}
    def flatten(obj, name=''):
        if isinstance(obj, dict):
            for key, value in obj.items():
                flatten(value, name + key + sep)
        elif isinstance(obj, list):
            i = 0
            for value in obj:
                flatten(value, name + str(i) + sep)
                i += 1
        else:
            result[name[:-1]] = obj

    flatten(json_obj)
    return result


# TiDB数据库连接信息
host = '127.0.0.1'
port = 4000
user = 'root'
password = ''
db = 'imdbload'

# SQL 文件目录和结果保存目录
sql_dir = '../join-order-benchmark/queries/'
result_dir = '../JOB-sql-plan/'

# 创建结果保存目录
if not os.path.exists(result_dir):
    os.makedirs(result_dir)

# 连接数据库
conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db)

# 遍历 SQL 文件，执行 EXPLAIN 并保存结果
for sql_file in os.listdir(sql_dir):
    if sql_file.endswith('.sql'):
        # 读取 SQL 文件内容
        with open(os.path.join(sql_dir, sql_file), 'r') as f:
            sql = f.read().strip()

        # 执行 EXPLAIN
        with conn.cursor() as cursor:
            cursor.execute("EXPLAIN format='tidb_json' " + sql)
            explain_text = '\n'.join([row[0] for row in cursor.fetchall()])
            json_obj = json.loads(explain_text)
            compressed_expain_text = json.dumps(flatten_json(json_obj))

        # 保存结果
        result_file = os.path.join(result_dir, os.path.splitext(sql_file)[0] + '.txt')
        with open(result_file, 'w') as f:
            f.write(sql + '\n\n' + explain_text + '\n\n' + compressed_expain_text)

# 关闭数据库连接
conn.close()
