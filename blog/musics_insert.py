import sqlite3

conn = sqlite3.connect("musics.db")
cur = conn.cursor()

import os
def get_music_files(folder_path):
    music_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.mp3', '.flac', '.wav', '.ogg', '.m4a')):
                file_path = os.path.join(root, file)
                music_files.append({
                    'file_name': file,
                    'file_path': file_path,
                    # 从文件名中提取可能的歌名（去掉扩展名）
                    'title': os.path.splitext(file)[0]
                })
    return music_files
# 使用示例
if __name__ == "__main__":
    music_folder = "static/music"  # 替换为你的音乐文件夹路径
    songs = get_music_files(music_folder)

    for song in songs:
        cur.execute("""INSERT INTO musics (name,route,singer)VALUES (?,?,?)""", (song['title'],song['file_path'],'未知歌手'))


        cur.execute("DELETE FROM musics WHERE id NOT IN (SELECT MIN(id) FROM musics GROUP BY name,singer)")
        cur.execute("SELECT rowid, name, singer, route FROM musics ORDER BY rowid")

        records = cur.fetchall()
        for new_id, (old_id, name, singer, route) in enumerate(records, start=1):
            cur.execute("UPDATE musics SET id = ? WHERE rowid = ?", (new_id, old_id))

        conn.commit()

cur.close()
conn.close()

