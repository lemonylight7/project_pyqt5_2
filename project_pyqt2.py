import sys
import os
from datetime import datetime
from PyQt5 import uic
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QTableWidgetItem
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PIL import Image, ImageDraw, ImageFilter
from db import DB, PostsModel, UsersModel, LikesModel, CommentsModel, SubsModel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_user = ''
        self.reg = ''
        self.del_dialog = ''
        self.db = DB("project.db")
        self.hello()

    def hello(self):
        uic.loadUi('design/hello.ui', self)
        pixmap = QPixmap('design/insta.png')
        self.icon.setPixmap(pixmap)
        self.autorisation.clicked.connect(self.login)
        self.registration.clicked.connect(self.register)

    def login(self):
        uic.loadUi('design/autorisation.ui', self)
        pixmap = QPixmap('design/little_insta.png')
        self.icon.setPixmap(pixmap)
        if self.reg != '':
            self.reg.close()
            self.reg = ''
        self.enter.clicked.connect(self.check_password)
        self.back.clicked.connect(self.hello)

    def check_password(self):
        if self.login_line.text() != '' and self.password_line.text() != '':
            user = UsersModel(self.db.get_connection()).get_by_name(self.login_line.text())
            if user:
                if user[2] == self.password_line.text():
                    self.warning.setText('')
                    self.current_user = user
                    self.current_page = user
                    self.show_page()
                elif user[2] != self.password_line.text():
                    self.warning.move(210, 390)
                    self.warning.setText('Неверное имя пользователя или пароль. Попробуйте еще раз.')
            else:
                self.warning.move(210, 390)
                self.warning.setText('Неверное имя пользователя или пароль. Попробуйте еще раз.')
        else:
            self.warning.move(330, 390)
            self.warning.setText('Заполните все поля.')

    def register(self):
        uic.loadUi('design/registration.ui', self)
        pixmap = QPixmap('design/little_insta.png')
        self.icon.setPixmap(pixmap)
        self.reg_but.clicked.connect(self.new_user)
        self.back.clicked.connect(self.hello)

    def new_user(self):
        if self.login_line.text() != '' and self.password_line.text() != '' and self.password_line_2.text() != '':
            user = UsersModel(self.db.get_connection()).get_by_name(self.login_line.text())
            if not user:
                if self.password_line.text() == self.password_line_2.text():
                    UsersModel(self.db.get_connection()).insert(self.login_line.text(), self.password_line.text())
                    self.reg = RegDialog()
                    self.reg.show()
                    self.reg.ok.clicked.connect(self.login)
                else:
                    self.warning.move(330, 390)
                    self.warning.setText('Пароли не совпадают.')
            else:
                self.warning.move(290, 390)
                self.warning.setText('Это имя пользователя уже занято.')
        else:
            self.warning.move(330, 390)
            self.warning.setText('Заполните все поля.')

    def show_page(self):
        uic.loadUi('design/main.ui', self)
        self.username.setText(self.current_user[1])
        pixmap = QPixmap('design/little_insta.png')
        if self.del_dialog != '':
            self.del_dialog.close()
            self.del_dialog = ''
        if self.current_page != self.current_user:
            subs = SubsModel(self.db.get_connection())
            self.sub.show()
            self.add_photo.hide()
            self.edit_profile.hide()
            if subs.check_subscribed(self.current_user[0], self.current_page[0]):
                self.sub.setText('Отписаться')
                self.sub.setStyleSheet('font: 16pt "Yu Gothic UI Semilight";'
                                       'color: rgb(0, 170, 255);'
                                       'border-style: outset;'
                                       'border-width: 2px;'
                                       'border-radius: 10px;'
                                       'border-color: rgb(0, 170, 255);'
                                       'min-width: 3em;'
                                       'padding: 6px;'
                                       'background-color: rgb(255, 255, 255);')
            else:
                self.sub.setText('Подписаться')
                self.sub.setStyleSheet('font: 16pt "Yu Gothic UI Semilight";'
                                       'color: rgb(255, 255, 255);'
                                       'border-style: outset;'
                                       'border-width: 2px;'
                                       'border-radius: 10px;'
                                       'border-color: rgb(0, 170, 255);'
                                       'min-width: 3em;'
                                       'padding: 6px;'
                                       'background-color: rgb(0, 170, 255);')
            self.sub.clicked.connect(self.sub_unsub)
        else:
            self.sub.hide()
            self.add_photo.show()
            self.edit_profile.show()
        self.icon.setPixmap(pixmap)
        self.exit.clicked.connect(self.quit)
        ### данные о пользователе ###
        posts = PostsModel(self.db.get_connection())
        all_posts = []
        for i in posts.get_all(self.current_page[0]):
            all_posts.append({'pub_date': datetime.fromtimestamp(i[5]).strftime('%d.%m.%Y %H:%M'),
                              'title': i[1], 'thumb': i[3], 'userid': i[4], 'pid': i[0]})
        users = UsersModel(self.db.get_connection())
        subs = SubsModel(self.db.get_connection())
        user_data = users.get(self.current_page[0])
        user_info = {'username': user_data[1], 'main_photo': user_data[4],
                     'followers_count': subs.get_followers(self.current_page[0]),
                     'subscriptions_count': subs.get_subscriptions(self.current_page[0]),
                     'posts_count': posts.get_count(self.current_page[0]), 'userid': self.current_page[0]}
        img_name = '/'.join(
            user_info['main_photo'].split('/')[:-1]) + '/circle_' + user_info['main_photo'].split('/')[-1]
        if not os.path.exists(img_name):
            img = Image.open(user_info['main_photo'])
            img_circle = mask_circle_solid(img, (255, 255, 255), 0, offset=0)
            img_circle.save(img_name)
        pixmap = QPixmap(img_name)
        pixmap_resized = pixmap.scaled(100, 100, QtCore.Qt.KeepAspectRatio)
        self.main_photo.setPixmap(pixmap_resized)
        self.username_2.setText(user_info['username'])
        self.stats.setText('Публикации: {}  Подписчики: {}  Подписки: {}'.format(user_info['posts_count'],
                                                                                 user_info['followers_count'],
                                                                                 user_info['subscriptions_count']))
        self.edit_profile.clicked.connect(self.edit)
        self.add_photo.clicked.connect(self.add)
        ### начало таблицы с фотографиями ###
        posts = PostsModel(self.db.get_connection())
        all_posts = []
        for i in posts.get_all(self.current_page[0]):
            all_posts.append({'pub_date': datetime.fromtimestamp(i[5]).strftime('%d.%m.%Y %H:%M'),
                              'title': i[1], 'thumb': i[3], 'userid': i[4], 'pid': i[0]})
        self.table.setColumnCount(3)
        self.row_count = user_info['posts_count'] // 3 if user_info['posts_count'] % 3 == 0 else user_info[
                                                                                                'posts_count'] // 3 + 1
        self.table.setRowCount(self.row_count)
        for i in range(0, self.row_count):
            for j in range(0, 3):
                if i * 3 + j < len(all_posts):
                    image = ImageWidget(all_posts[i * 3 + j]['thumb'], self)
                    self.table.setCellWidget(i, j, image)
        self.table.cellClicked[int, int].connect(self.show_post)
        ### поиск пользователя ###
        self.find_user.clicked.connect(self.search_user)
        self.username.clicked.connect(self.return_home)

    def sub_unsub(self):
        subs = SubsModel(self.db.get_connection())
        if subs.check_subscribed(self.current_user[0], self.current_page[0]):
            subs.unsubscribe(self.current_user[0], self.current_page[0])
        else:
            subs.subscribe(self.current_user[0], self.current_page[0])
        self.show_page()

    def return_home(self):
        self.current_page = self.current_user
        self.show_page()

    def search_user(self):
        username = self.search_line.text()
        users = UsersModel(self.db.get_connection())
        user = users.get_by_name(username)
        if not user:
            self.warning.setText('Пользователя с таким именем не существует.')
        else:
            self.warning.setText('')
            self.current_page = user
            self.show_page()

    def show_post(self, *params):
        if len(params) > 1:
            self.r = params[0]
            self.c = params[1]
        uic.loadUi('design/show_post.ui', self)
        if self.del_dialog != '':
            self.del_dialog.close()
            self.del_dialog = ''
        if self.current_page != self.current_user:
            self.settings_combo.hide()
        self.send.show()
        self.save_desc.hide()
        self.username.setText(self.current_page[1])
        img_name = '/'.join(self.current_page[4].split('/')[:-1]) + '/circle_' + self.current_page[4].split('/')[-1]
        pixmap = QPixmap(img_name)
        pixmap_resized = pixmap.scaled(71, 61, QtCore.Qt.KeepAspectRatio)
        self.main_photo.setPixmap(pixmap_resized)
        self.arrow.clicked.connect(self.show_page)
        posts = PostsModel(self.db.get_connection())
        all_posts = []
        for i in posts.get_all(self.current_page[0]):
            all_posts.append({'pub_date': datetime.fromtimestamp(i[5]).strftime('%d.%m.%Y %H:%M'),
                              'title': i[1], 'thumb': i[3], 'userid': i[4], 'pid': i[0]})
        if self.r * 3 + self.c > len(all_posts) - 1:
            self.show_page()
            return
        self.cur_post = posts.get(all_posts[self.r * 3 + self.c]['pid'])
        pixmap = QPixmap(self.cur_post[2])
        pixmap_resized = pixmap.scaled(781, 401, QtCore.Qt.KeepAspectRatio)
        r_width = pixmap_resized.width()
        self.photo.move(957//2 - r_width//2, 100)
        self.photo.setPixmap(pixmap_resized)
        likes = LikesModel(self.db.get_connection())
        count = likes.get_count(self.cur_post[0])
        self.likes.setText(str(count))

        if likes.get_your(self.cur_post[0], self.current_user[0]):
            self.like.setIcon(QIcon('design/heart_red.png'))
            self.like.setIconSize(QtCore.QSize(51, 51))
            self.like.clicked.connect(self.del_like)
        else:
            self.like.setIcon(QIcon('design/heart_white.png'))
            self.like.setIconSize(QtCore.QSize(51, 51))
            self.like.clicked.connect(self.add_like)
        comments_ = CommentsModel(self.db.get_connection())
        users = UsersModel(self.db.get_connection())
        comments = comments_.get(self.cur_post[0])
        comment_count = len(comments)
        self.comments.setRowCount(comment_count)
        for i in range(0, comment_count):
            user = users.get(comments[i][2])[1]
            item = QTableWidgetItem(user)
            item.setFont(QFont('Yu Gothic UI Semibold', 16))
            item.setTextAlignment(QtCore.Qt.AlignRight)
            self.comments.setItem(i, 0, item)
            self.comments.setItem(i, 1, QTableWidgetItem(comments[i][4]))
            time = QLabel(time_converter(comments[i][5]))
            time.setStyleSheet('color: rgb(208, 208, 208); font: Yu Gothic UI Semibold; font-size: 16px;')
            self.comments.setCellWidget(i, 2, time)
            if comments[i][2] == self.current_user[0] and comments[i][0] != -1:
                image = QLabel('картинка')
                pixmap = QPixmap('design/can.png')
                pixmap_resized = pixmap.scaled(15, 15, QtCore.Qt.KeepAspectRatio)
                image.setPixmap(pixmap_resized)
                self.comments.setCellWidget(i, 3, image)
        self.comments.resizeColumnsToContents()
        self.comments.cellClicked[int, int].connect(self.del_comment)
        self.send.clicked.connect(self.add_comment)
        self.settings_combo.setItemIcon(0, QIcon('design/tools.png'))
        self.settings_combo.activated[str].connect(self.settings)

    def settings(self, option):
        if option == 'Удалить':
            self.del_dialog = DelDialog()
            self.del_dialog.show()
            self.del_dialog.yes.clicked.connect(self.delete_post)
            self.del_dialog.no.clicked.connect(self.show_post)
        elif option == 'Изменить описание':
            self.comment_line.setText(self.cur_post[1])
            self.send.hide()
            self.save_desc.show()
            self.save_desc.clicked.connect(self.change_post)

    def delete_post(self):
        posts = PostsModel(self.db.get_connection())
        posts.delete(self.cur_post[0])
        self.cur_post = ''
        self.show_page()

    def change_post(self):
        posts = PostsModel(self.db.get_connection())
        posts.update_title(self.cur_post[0], self.comment_line.text())
        self.comment_line.setText('')
        self.send.show()
        self.save_desc.hide()
        self.show_post(self.r, self.c)

    def add_comment(self):
        comments_ = CommentsModel(self.db.get_connection())
        if self.comment_line.text() != '':
            comments_.insert(self.cur_post[0], self.current_user[0], self.comment_line.text())
            self.show_post(self.r, self.c)

    def del_comment(self, r, c):
        comments_ = CommentsModel(self.db.get_connection())
        comments = comments_.get(self.cur_post[0])
        if c == 3 and comments[r][2] == self.current_user[0] and comments[r][0] != -1:
            comments_.delete(comments[r][0], self.current_user[0])
            self.show_post(self.r, self.c)

    def add_like(self):
        likes = LikesModel(self.db.get_connection())
        likes.insert(self.cur_post[0], self.current_user[0])
        self.show_post(self.r, self.c)

    def del_like(self):
        likes = LikesModel(self.db.get_connection())
        likes.delete(self.cur_post[0], self.current_user[0])
        self.show_post(self.r, self.c)

    def edit(self):
        uic.loadUi('design/edit.ui', self)
        pixmap = QPixmap('design/little_insta.png')
        self.icon.setPixmap(pixmap)
        self.cancel.clicked.connect(self.show_page)
        self.save_data.clicked.connect(self.save)
        self.choose_file.clicked.connect(self.show_dialog)

    def save(self):
        users = UsersModel(self.db.get_connection())
        if self.new_name.text() != '':
            user = UsersModel(self.db.get_connection()).get_by_name(self.new_name.text())
        else:
            user = None
        if not user and self.new_name.text() != '':
            users.update_user_info(self.current_user[0], 'user_name', self.new_name.text())
            self.current_user = UsersModel(self.db.get_connection()).get_by_name(self.new_name.text())
            self.current_page = self.current_user
            self.warning.setText('')
        elif user and self.new_name.text() != '':
            if user[1] != self.current_user[1]:
                self.warning.setText('Это имя пользователя уже занято.')
            elif user[1] == self.current_user[1]:
                self.warning.setText('')
        if not user or user[1] == self.current_user[1]:
            if self.new_password.text() != '' and self.new_password.text() == self.new_password_2.text():
                users.update_user_info(self.current_user[0], 'password_hash', self.new_password.text())
                self.current_user = UsersModel(self.db.get_connection()).get_by_name(self.current_user[1])
                self.current_page = self.current_user
                self.warning.setText('')
            elif self.new_password.text() != self.new_password_2.text():
                self.warning.setText('Пароли не совпадают.')
        elif user[1] != self.current_user[1]:
            self.warning.setText('Это имя пользователя уже занято.')
        if self.filename.text() != '':
            save_filename, thmb_filename = save_file(self.filename.text(), self.current_user[0])
            users.update_user_info(self.current_user[0], 'main_photo', thmb_filename)
            self.current_page = self.current_user
        if self.warning.text() == '':
            self.show_page()

    def show_dialog(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home')[0]
        self.filename.setText(fname)

    def add(self):
        uic.loadUi('design/add.ui', self)
        pixmap = QPixmap('design/little_insta.png')
        self.icon.setPixmap(pixmap)
        self.cancel.clicked.connect(self.show_page)
        self.choose_file.clicked.connect(self.show_dialog)
        self.upload_photo.clicked.connect(self.upload)

    def upload(self):
        if self.filename.text() != '':
            save_filename, thmb_filename = save_file(self.filename.text(), self.current_user[0])
            posts = PostsModel(self.db.get_connection())
            posts.insert(self.description.toPlainText(), save_filename, thmb_filename, self.current_user[0])
            self.show_page()
        else:
            self.warning.setText('Сначала загрузите фото.')

    def quit(self):
        self.hello()
        self.current_user = ''
        self.current_page = ''


class RegDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('design/reg_ended.ui', self)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)


class DelDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('design/del_dialog.ui', self)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)


class ImageWidget(QWidget):
    def __init__(self, imagePath, parent):
        super(ImageWidget, self).__init__(parent)
        self.picture = QtGui.QPixmap(imagePath)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(0, 0, self.picture)


def make_thumbnail(infile, outfile):
    im = Image.open(infile)
    xsize, ysize = im.size
    if xsize > ysize:
        crop_size = (xsize/2 - ysize/2, 0, xsize/2 + ysize/2, ysize)
    else:
        crop_size = (0, ysize/2 - xsize/2, xsize, ysize/2 + xsize/2)
    im = im.crop(box=crop_size)
    im.thumbnail((300, 300))
    im.save(outfile)


def save_file(f, id):
    filename = f.split('/')[-1]
    img = Image.open(f)
    save_filename = "static/img/usr_{0}/{1}_{2}".format(
        id, round(datetime.timestamp(datetime.now())), filename
    )
    thmb_filename = "static/img/usr_{0}/thmb/{1}_{2}".format(
        id, round(datetime.timestamp(datetime.now())), filename
    )
    os.makedirs('static/img/usr_{}'.format(id), exist_ok=True)
    os.makedirs('static/img/usr_{}/thmb'.format(id), exist_ok=True)
    img.save(save_filename)
    make_thumbnail(save_filename, thmb_filename)
    return (save_filename, thmb_filename)


def mask_circle_solid(pil_img, background_color, blur_radius, offset=0):
    background = Image.new(pil_img.mode, pil_img.size, background_color)
    offset = blur_radius * 2 + offset
    mask = Image.new("L", pil_img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))
    return Image.composite(pil_img, background, mask)


def time_converter(s):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    date = str(datetime.utcfromtimestamp(s))
    date = date.split()
    time = date[1].split(':')
    time = ':'.join([str(int(time[0]) + 3), time[1], time[2]])
    pretty_date = ' '.join([str(int(date[0].split('-')[2])),
                            months[int(date[0].split('-')[1])-1],
                            date[0].split('-')[0], time])
    return pretty_date


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
