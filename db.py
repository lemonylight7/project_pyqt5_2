import sqlite3
from datetime import datetime

class DB:
    def __init__(self, db_file):
        conn = sqlite3.connect(db_file, check_same_thread=False)
        self.conn = conn

    def get_connection(self):
        return self.conn

    def __del__(self):
        self.conn.close()


class PostsModel:
    def __init__(self, connection):
        self.connection = connection
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' and name='posts'")
        row = cursor.fetchone()
        if row is None:
            self.init_table()

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS posts
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             title VARCHAR(100),
                             path TEXT,
                             thmb_path TEXT,
                             user_id INTEGER,
                             pub_date INTEGER
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, title, path, thmb_path, user_id):
        cursor = self.connection.cursor()
        pub_date = round(datetime.timestamp(datetime.now()))
        cursor.execute('''INSERT INTO posts
                          (title, path, thmb_path, user_id, pub_date)
                          VALUES (?,?,?,?,?)''', (title, path, thmb_path, user_id, pub_date))
        cursor.close()
        self.connection.commit()

    def get(self, post_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM posts WHERE id = ?", (str(post_id),))
        row = cursor.fetchone()
        return row

    def get_all(self, user_id=None):
        cursor = self.connection.cursor()
        if user_id:
            cursor.execute("SELECT * FROM posts WHERE user_id = ? ORDER BY pub_date DESC",
                           (user_id,))
        else:
            cursor.execute("SELECT * FROM posts ORDER BY pub_date DESC")
        rows = cursor.fetchall()
        return rows

    def delete(self, post_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM posts WHERE id = ?''', (str(post_id),))
        cursor.close()
        self.connection.commit()

    def update_title(self, post_id, title):
        cursor = self.connection.cursor()
        cursor.execute('''UPDATE posts SET title = ? WHERE id = ?''', (title, post_id))
        cursor.close()
        self.connection.commit()

    def get_count(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM posts WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return row[0]


class UsersModel:
    def __init__(self, connection):
        self.connection = connection
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' and name='users'")
        row = cursor.fetchone()
        if row is None:
            self.init_table()


    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             user_name VARCHAR(50),
                             password_hash VARCHAR(128),
                             admin INTEGER,
                             main_photo TEXT
                             )''')
        cursor.execute('''INSERT INTO users (user_name, password_hash, admin, main_photo)
                          VALUES (?,?,?,?)''', ('ermakova', 'pass', 0, 'static/img/no_photo.png'))
        cursor.execute('''INSERT INTO users (user_name, password_hash, admin, main_photo)
                          VALUES (?,?,?,?)''', ('avokamre', 'ssap', 0, 'static/img/no_photo.png'))
        cursor.execute('''INSERT INTO users (user_name, password_hash, admin, main_photo)
                          VALUES (?,?,?,?)''', ('ne_admin', 'ne_admin', 0, 'static/img/no_photo.png'))
        cursor.close()
        self.connection.commit()

    def insert(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users
                          (user_name, password_hash, admin, main_photo)
                          VALUES (?,?,?,?)''', (user_name, password_hash, 0, 'static/img/no_photo.png'))
        cursor.close()
        self.connection.commit()

    def get(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return row

    def get_by_name(self, user_name):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ?", (user_name,))
        row = cursor.fetchone()
        return row

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return rows

    def exists(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ? AND password_hash = ?",
                       (user_name, password_hash))
        row = cursor.fetchone()
        return (True, row[0]) if row else (False,)

    def update_user_info(self, user_id, key, value):
        cursor = self.connection.cursor()
        cursor.execute('''UPDATE users SET {} = ? WHERE id = ?'''.format(key), (str(value), user_id))
        cursor.close()
        self.connection.commit()


class SubsModel:
    def __init__(self, connection):
        self.connection = connection
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' and name='subscribers'")
        row = cursor.fetchone()
        if row is None:
            self.init_table()

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS subscribers
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             subject INTEGER,
                             object INTEGER
                             )''')
        cursor.execute('''INSERT INTO subscribers (subject, object)
                                  VALUES (?, ?)''', (1, 2))
        cursor.execute('''INSERT INTO subscribers (subject, object)
                                  VALUES (?, ?)''', (1, 3))
        cursor.execute('''INSERT INTO subscribers (subject, object)
                                  VALUES (?, ?)''', (2, 3))
        cursor.close()
        self.connection.commit()

    def subscribe(self, subject, object):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO subscribers (subject, object)
                                          VALUES (?, ?)''', (subject, object))
        self.connection.commit()

    def unsubscribe(self, subject, object):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM subscribers WHERE subject = ? and object = ?''', (subject, object))
        self.connection.commit()

    def get_subscriptions(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM subscribers WHERE subject = ?", (user_id,))
        row = cursor.fetchone()
        return row[0]

    def get_followers(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM subscribers WHERE object = ?", (user_id,))
        row = cursor.fetchone()
        return row[0]

    def check_subscribed(self, subject, object):
        cursor = self.connection.cursor()
        cursor.execute('''SELECT 1 FROM subscribers WHERE subject = ? and object = ?''', (subject, object))
        row = cursor.fetchone()
        if row is not None:
            return 1
        return 0


class LikesModel:
    def __init__(self, connection):
        self.connection = connection
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' and name='likes'")
        row = cursor.fetchone()
        if row is None:
            self.init_table()

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS likes
                            (
                             post_id INTEGER,
                             user_id INTEGER
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, post_id, user_id):
        cursor = self.connection.cursor()
        pub_date = round(datetime.timestamp(datetime.now()))
        cursor.execute('''INSERT INTO likes
                          (post_id, user_id)
                          VALUES (?,?)''', (str(post_id), user_id))
        cursor.close()
        self.connection.commit()

    def get_count(self, post_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT count(*) FROM likes WHERE post_id = ?", (str(post_id),))
        row = cursor.fetchone()
        return row[0]

    def get_your(self, post_id, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT 1 FROM likes WHERE post_id = ? and user_id = ?",
                           (str(post_id), user_id))
        rows = cursor.fetchone()
        if rows is None:
            return 0
        else:
            return 1

    def delete(self, post_id, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM likes WHERE post_id = ? and user_id = ?''',
                            (str(post_id),user_id))
        cursor.close()
        self.connection.commit()


class CommentsModel:
    def __init__(self, connection):
        self.connection = connection
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' and name='comments'")
        row = cursor.fetchone()
        if row is None:
            self.init_table()

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS comments
                            (
                             id INTEGER PRIMARY KEY AUTOINCREMENT,
                             post_id INTEGER,
                             user_id INTEGER,
                             comment TEXT,
                             pub_date INTEGER
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, post_id, user_id, comment):
        cursor = self.connection.cursor()
        pub_date = round(datetime.timestamp(datetime.now()))
        cursor.execute('''INSERT INTO comments
                          (post_id, user_id, comment, pub_date)
                          VALUES (?,?,?,?)''', (str(post_id), user_id, comment, pub_date))
        cursor.close()
        self.connection.commit()

    def get(self, post_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT -1, p.id, u.id, u.user_name, p.title, p.pub_date FROM posts p,"
                       " users u WHERE p.id = ? AND p.user_id=u.id", (str(post_id),))
        post_info = cursor.fetchone()
        rows = [post_info]
        cursor.execute("SELECT c.id, c.post_id, c.user_id, u.user_name, c.comment, c.pub_date FROM comments c,"
                       " users u WHERE c.post_id = ? and c.user_id=u.id ORDER BY c.id", (str(post_id),))
        rows = rows + cursor.fetchall()
        return rows

    def delete(self, comment_id, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM comments WHERE id = ? AND user_id = ?''', (comment_id, user_id))
        cursor.close()
        self.connection.commit()
