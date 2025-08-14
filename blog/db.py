import sqlite3


def query_sql(sql,param=[]):
    conn = sqlite3.connect("blog.db")
    cur = conn.cursor()
    cur.execute(sql,param)
    date = cur.fetchall()
    cur.close()
    conn.close()
    return date


def exec_sql(sql,param=[]):
    conn = sqlite3.connect("blog.db")
    cur = conn.cursor()
    cur.execute(sql,param)
    conn.commit()
    conn.close()


