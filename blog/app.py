import sqlite3

import app
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort

import db
from blog.wrapper import login_required, admin_required
from flask import Flask
from flask_login import LoginManager, UserMixin

# 1. 必须先创建Flask应用实例
app = Flask(__name__)
app.config["SECRET_KEY"] = "mys455567y"  # 建议使用更复杂的密钥

# 2. 然后初始化LoginManager
login_manager = LoginManager()
login_manager.init_app(app)  # 现在app已经定义
login_manager.login_view = 'login'  # 指定登录路由

# 3. 正确的user_loader实现
class User(UserMixin):
    pass  # 根据你的用户模型实现

@login_manager.user_loader
def load_user(user_id):
    # 应该从数据库加载用户
    user = User()
    user.id = user_id
    return user  # 必须返回User对象或None



app.config["SECRET_KEY"] = "mys455567y"

# 调试模板路径

# 用户部分
@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/do_login",methods=["POST"])
def do_login():
    form = request.form
    name = form.get("name","")
    password = form.get("password", "")

    result = db.query_sql("select * from user where name=? and password=?", (name, password))
    if len(result) > 0:   #找到用户
        session["id"]= result[0][0]
        print("sessionId:",session["id"])
        return redirect(url_for("index"))
    else:
        return render_template("login.html", error="用户不存在或者密码错误")



@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/do_register", methods=["POST"])
def do_register():
    form = request.form
    name = form.get("name")
    password2 = form.get("password2", "")
    password = form.get("password", "")
    if name == "" or password != password2:
        return render_template("register.html", error="用户名为空或密码不一致")
    password = form.get("password","")
   

    db.exec_sql("insert into user( name , password)values(?,?)",(name, password))

    return redirect(url_for("login"))




@app.route("/change_password")
@login_required
def change_password():
    return render_template("change_password.html")


@app.route("/add")
@login_required
def add():
    return render_template("add.html")


@app.route("/do_add",methods=["POST"])

@login_required
def do_add():
    form = request.form
    title = form.get("title","")
    content = form.get("content","")

    db.exec_sql("insert into blog(title,content,uid) values(?,?,?)", (title,content,session["id"]))


    return redirect(url_for("index"))


@app.route("/logout")
@login_required
def logout():
    del session["id"]
    return redirect(url_for("login"))


@app.route("/delete")
@login_required
def delete():
    args = request.args
    id = args.get("id","")

    db.exec_sql("delete from blog where id = ?", [id])

    return redirect(url_for("index"))


@app.route("/edit")
@login_required
def edit():
    args = request.args
    id = args.get("id", "")
    date = db.query_sql("select * from blog where id = ?", [id])
    return render_template("edit.html", blog=date[0])

@app.route("/do_edit",methods=["POST"])
@login_required
def do_edit():
   form = request.form
   id = form.get("id","")
   title = form.get("title","")
   content = form.get("content","")

   db.exec_sql("update blog set title = ?, content = ? where id = ?", [title, content, id])
   return redirect(url_for("index"))


@app.route("/")
@login_required
def index():
    # 获取分页和搜索参数（保持原有逻辑）
    args = request.args
    key = args.get("key", "").strip()
    page = int(args.get("page", "1"))
    number_per_page = 5

    # 获取音乐数据（保持原有逻辑）
    conn = sqlite3.connect("musics.db")
    cur = conn.cursor()
    cur.execute("SELECT name, route FROM musics")
    songs = cur.fetchall()
    conn.close()

    # 获取博客列表（保持原有逻辑）
    blogs = db.query_sql(
        "SELECT * FROM blog WHERE (title LIKE ? OR content LIKE ?) ORDER BY id DESC LIMIT ?, ?",
        [f"%{key}%", f"%{key}%", (page - 1) * number_per_page, number_per_page]
    )

    # 为每篇博客查询对应的评论
    blogs_with_comments = []
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()

    for blog in blogs:
        blog_id = blog[0]  # 假设id是第一个字段
        cursor.execute("""
                       SELECT comment.content, comment.created_at, user.name
                       FROM comment
                                JOIN user ON comment.user_id = user.id
                       WHERE comment.blog_id = ?
                       ORDER BY comment.created_at DESC
                       """, (blog_id,))
        comments = cursor.fetchall()

        blogs_with_comments.append({
            "blog": blog,  # 博客数据
            "comments": comments  # 关联的评论列表
        })

    conn.close()

    return render_template(
        "index.html",
        blogs=blogs_with_comments,  # 传递整合后的数据
        page=page,
        songs=songs
    )

@app.route("/user_list")
@admin_required
def user_list():
    users = db.query_sql("select * from user")
    return render_template("user_list.html",users=users)




@app.route("/user_delete")
def user_delete():
    args = request.args
    id = int(args.get("id", "0"))

    db.exec_sql("delete from user where id = ?", [id])

    return redirect(url_for("user_list"))
#用户评论功能

def init_db():
    with sqlite3.connect('blog.db') as conn:
        cursor = conn.cursor()
        # 创建评论表（如果不存在）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id2 INTEGER PRIMARY KEY AUTOINCREMENT,
            blog_id INTEGER NOT NULL,
            user_name TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (blog_id) REFERENCES blog(id),
            FOREIGN KEY (user_id) REFERENCES user(id)
        )
        ''')
        conn.commit()


@app.route("/comment/<int:blog_id>")
@login_required
def comment(blog_id):
    try:
        conn = sqlite3.connect('blog.db')
        cursor = conn.cursor()

        # 获取博客内容
        cursor.execute("SELECT * FROM blog WHERE id =?", [blog_id])
        blog = cursor.fetchone()
        cursor.execute("DELETE FROM comment WHERE blog_id IS NULL;")
        # 获取关联评论（按时间倒序）
        cursor.execute("""
                       SELECT comment.content, comment.created_at, user.name
                       FROM comment
                                JOIN user ON comment.user_id = user.id
                       WHERE comment.blog_id = ?
                       ORDER BY comment.created_at DESC
                       """, (blog_id,))
        comments = cursor.fetchall()

        conn.close()

        if not blog:
            abort(404)

        return render_template("comment.html",
                               blog=blog,
                               comments=comments,
                               blog_id=blog_id)

    except Exception as e:
        print(f"数据库错误: {e}")
        abort(500)


@app.route("/do_comment", methods=["POST"])
@login_required
def do_comment():
    try:
        content = request.form.get("content", "").strip()
        blog_id = request.form.get("blog_id", "")

        if not content or not blog_id:
            flash("评论内容和博客ID不能为空")
            return redirect(url_for("index"))

        conn = sqlite3.connect('blog.db')
        cursor = conn.cursor()

        # 检查博客是否存在
        cursor.execute("SELECT id FROM blog WHERE id=?", (blog_id,))
        if not cursor.fetchone():
            flash("指定的博客不存在")
            return redirect(url_for("index"))

        # 插入评论
        conn.execute("PRAGMA timezone = '+08:00'")
        cursor.execute(
            "INSERT INTO comment (content, user_id, blog_id, created_at) VALUES (?, ?, ?, datetime('now'))",
            (content, session["id"], blog_id)
        )

        conn.commit()
        conn.close()

        flash("评论成功")
        return redirect(url_for("index"))

    except Exception as e:
        print(f"评论提交错误: {e}")
        flash("评论提交失败")
        return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)

