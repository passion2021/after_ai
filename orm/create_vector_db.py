#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/9/22 11:50
# @Author  : 李明轩
# @File    : create_vec_db.py
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
db_name = "lryk"
# 1. 先连接默认数据库（postgres）创建新数据库
conn = psycopg2.connect(
    host="36.134.51.155",
    port=5432,
    user="postgres",  # 改成你的用户名
    password=os.getenv("POSTGRESQL_PASSWORD"),
    dbname="postgres"  # 先连接已有数据库
)
conn.autocommit = True  # CREATE DATABASE 需要 autocommit
cur = conn.cursor()
cur.execute(f"CREATE DATABASE {db_name};")
print(f"数据库 {db_name} 创建成功。")
cur.close()
conn.close()

# 2. 连接新数据库启用 pgvector
conn = psycopg2.connect(
    host="36.134.51.155",
    port=5432,
    user="postgres",
    password=os.getenv("POSTGRESQL_PASSWORD"),
    dbname=db_name
)
cur = conn.cursor()
cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
print("pgvector 扩展启用成功。")

cur.close()
conn.commit()
conn.close()
