import sqlite3

conn = sqlite3.connect("blogs.db")
cur = conn.cursor()
cur.execute("create table if not exists user(id integer primary key autoincrement, name , password)")
cur.execute("create table if not exists blog(id integer primary key autoincrement, title , content, uid)")
conn.commit()
conn.close()

conn = sqlite3.connect("musics.db")
cur = conn.cursor()
cur.execute("create table if not exists music_name(id integer primary key autoincrement, name , singer,route)")
cur.execute("create table if not exists musics(id integer primary key autoincrement, name , singer,route)")
conn.commit()
conn.close()

import sqlite3


def init_db():
    conn = sqlite3.connect("blog.db")
    cur = conn.cursor()

    # 原有表创建语句
    cur.execute("CREATE TABLE IF NOT EXISTS user(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, password TEXT)")
    cur.execute(
        "CREATE TABLE IF NOT EXISTS blog(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, user_id INTEGER)")

    # 新增评论表创建语句
    cur.execute('''
                CREATE TABLE IF NOT EXISTS comment
                (
                    id2         INTEGER PRIMARY KEY AUTOINCREMENT,
                    content    TEXT    NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id    INTEGER NOT NULL,
                    blog_id    INTEGER NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES user (id),
                    FOREIGN KEY (blog_id) REFERENCES blog (id)
                )
                ''')

    conn.commit()
    conn.close()


# 调用初始化函数
init_db()



#cur.execute("select * from user")
#v=cur.fetchall()
#print(v)
#conn.close()
