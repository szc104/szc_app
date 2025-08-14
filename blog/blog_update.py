import sqlite3

conn = sqlite3.connect("blog.db.db")
cur = conn.cursor()
def do_update():
    cur.execute("SELECT rowid, title, content, uid, created_at FROM blog ORDER BY rowid")
    records = cur.fetchall()
    for new_id, (old_id, title, content, uid, created_at) in enumerate(records, start=1):
        cur.execute("UPDATE blog SET id = ? WHERE rowid = ?", (new_id, old_id))
        conn.commit()
cur.close()
conn.close()
