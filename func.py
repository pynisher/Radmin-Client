import win32gui
import win32con
import time
import subprocess
import os
import sys
import datetime
import configparser
import pyodbc
import sqlite3
from socket import *
import win32com.client
from PyQt5.QtWidgets import *
from options import Options

version_prog = '3.2.0'
comp_name = os.getenv('COMPUTERNAME', 'defaultValue').lower()
user_name = os.getlogin()

objShell = win32com.client.Dispatch("WScript.Shell")
my_doc_path = objShell.SpecialFolders("MyDocuments")    # путь к папке документов

globaluser = 'user'
globalclipboard = 0
check_not_done = []
show_passwords = 0
last_search = ['']

Colours = ('/1bpp', '/2bpp', '/4bpp', '/8bpp', '/16bpp', '/24bpp')
TypeConn = ('', ' /noinput', ' /file', ' /shutdown', ' /telnet')
ColorNames = ('1 бит', '2 бита', '4 бита', '8 бит', '16 бит', '24 бита')

addedit = [0, 0, '0']  # 1 параметр - новый элемент или редакция
# 2 параметр - ID текщего выбранного элемента (ID папки для нового подключения)
# 3 параметр - если было изменение то 1 если нет то 0
company_list = []  # Список организаций
folder_list = []  # Список папок
conn_list = []  # Список подключений общий
conn_list_all = []  # Список подключений общий
cur_list = []  # Список кураторов + пользователей
fld_list = {}  # Список папок временный (сначала заполняем в него, потом отбираем по куратору)

field_list = ['ID', 'Name', 'IP', 'port', 'AutoPass', 'psw', 'RA', 'colour',
              'Adress', 'HasProxy', 'Proxy', 'DefAct', 'Tel', 'Coment',
              'User', 'WorkTime', 'Curator', 'Firm', 'ping', 'Folder', 'OS', 'Provider']

display_admin = [
    ['Name', 200, 'Имя', 0],
    ['Firm', 50, 'Юрлицо', 1],
    ['Adress', 200, 'Адрес', 2],
    ['IP', 90, 'IP Адрес', 3],
    ['port', 40, 'Порт', 4],
    ['WorkTime', 80, 'Время работы', 5],
    ['Tel', 120, 'Телефон', 6],
    ['Coment', 200, 'Заметки', 7],
    ['OS', 120, 'ОС', 8],
    ['Curator', 80, 'Доступ', 9],
    ['ID1', 100, 'ID', 10],
]
display_curator = [
    ['Name', 200, 'Имя', 0],
    ['Firm', 120, 'Юрлицо', 1],
    ['Adress', 240, 'Адрес', 2],
    ['WorkTime', 100, 'Время работы', 3],
    ['Tel', 160, 'Телефон', 4],
    ['ID1', 100, 'ID', 5],
]
curator_selected = []


"""""""""""""""""""""""""""""""""""""""""""""""""""
" Функции работы с логами                         "
"""""""""""""""""""""""""""""""""""""""""""""""""""


# Очистка старых логов при запуске (если размер файла логов превышает 500кб)
def clearLog():
    clear_time = int(time.time()) - 30 * 24 * 60 * 60
    query = "DELETE FROM user_logs WHERE date<" + str(clear_time)
    writeToDb(query, islog=1)


# Запись в лог файл
def writeToLog(action, conn_id='1'):
    if conn_id == '1':
        query = "INSERT INTO user_logs(user_name, comp_name, date, action) VALUES ('" + user_name + "', '" \
                + comp_name + "', " + str(int(time.time())) + ", '" + action + "')"
    else:
        query = "INSERT INTO user_logs(user_name, comp_name, date, action, conn_id) VALUES ('" + user_name + "', '" \
                + comp_name + "', " + str(int(time.time())) + ", '" + action + "', " + str(conn_id) + ")"
    writeToDb(query, islog=1)


"""""""""""""""""""""""""""""""""""""""""""""""""""
" Функции работы с файлом локальных настроек      "
"""""""""""""""""""""""""""""""""""""""""""""""""""


# Чтение файла локальных настроек
def readLocalIni():
    global opt
    conf = configparser.ConfigParser()
    conf.read(my_doc_path + '\\Client\\options.ini')
    changes = 0
    try:
        opt.database_path = conf.get('Settings', 'DatabasePath')
    except:
        changes = 1
    try:
        opt.database_port = conf.get('Settings', 'DatabasePort')
    except:
        changes = 1
    try:
        opt.run_again = int(conf.get('Settings', 'RunAgain'))
    except:
        changes = 1
    try:
        opt.access_control = int(conf.get('Settings', 'AccessControl'))
    except:
        changes = 1
    try:
        opt.use_local_db = int(conf.get('Settings', 'UseLocalDB'))
    except:
        changes = 1

    try:
        opt.need_send_admin = int(conf.get('SendAdmin', 'NeedSend'))
    except:
        changes = 1
    try:
        opt.admin_host = conf.get('SendAdmin', 'AdminHost')
    except:
        changes = 1
    try:
        opt.admin_port = int(conf.get('SendAdmin', 'AdminPort'))
    except:
        changes = 1
    try:
        opt.admin_timeout = int(conf.get('SendAdmin', 'AdminTimeout'))
    except:
        changes = 1
    if changes:
        writeLocalIni()


# Сохранение файла локальных настроек
def writeLocalIni():
    config = configparser.RawConfigParser()
    config.add_section('Settings')
    config.set('Settings', 'DatabasePath', opt.database_path)
    config.set('Settings', 'DatabasePort', opt.database_port)
    config.set('Settings', 'RunAgain', str(opt.run_again))
    config.set('Settings', 'AccessControl', str(opt.access_control))
    config.set('Settings', 'UseLocalDB', str(opt.use_local_db))
    config.add_section('SendAdmin')
    config.set('SendAdmin', 'NeedSend', str(opt.need_send_admin))
    config.set('SendAdmin', 'AdminHost', opt.admin_host)
    config.set('SendAdmin', 'AdminPort', str(opt.admin_port))
    config.set('SendAdmin', 'AdminTimeout', str(opt.admin_timeout))
    with open(my_doc_path + '\\Client\\options.ini', 'w') as configfile:
        config.write(configfile)


# Проваеряет наличие папки и файла локальных настроек
def getLocalSettings():
    # проверить наличие папки настроек
    if not os.path.isdir(my_doc_path + '\\Client'):
        os.mkdir(my_doc_path + '\\Client')
    # проверить наличие файла
    if not os.path.isfile(my_doc_path + '\\Client\\options.ini'):
        writeLocalIni()     # создать файл с настройками по умолчанию
    # прочитать ини
    readLocalIni()


"""""""""""""""""""""""""""""""""""""""""""""""""""
" Общие функции                                   "
"""""""""""""""""""""""""""""""""""""""""""""""""""


# установить список полей для отображения для куратора или админа
def setDisplayField():
    for id_, kur in enumerate(cur_list):
        if kur[2].lower() == user_name.lower() and kur[4].lower() == comp_name.lower():
            return id_, display_curator
    return 0, display_admin


# получить список для отображения
def getDisplayList(sel_list):
    viewlist = []
    for item in conn_list:
        if item['Folder'] in sel_list:
            viewlist.append(item)
    return viewlist


# получить максимальный ID подключения
def getMaxListNum():
    max_num = 0
    for item in conn_list:
        if item['ID'] > max_num:
            max_num = item['ID']
    return max_num


# получить ID прокси подключения
def getProxyItem(item):
    for i in conn_list_all:
        if i['ID'] == int(item['Proxy']):
            return i


# сортировать список для отображения
def sortList(list_to_sort, key):
    return sorted(list_to_sort, key=lambda k: k[key])


# кодирование \ декодирование паролей
def setPsw(old, code):
    psw = ''
    for i in old:
        psw += chr(ord(i) + code)
    return psw


# Запись в БД изменений
def writeToDb(query, islog=0):
    if opt.use_local_db:
        data_conn = sqlite3.connect('rclient.db')
    else:
        data_conn = pyodbc.connect('DRIVER={SQL Server};SERVER=' + opt.database_path + ',' + opt.database_port
                                   + ';DATABASE=rclient;UID=sa;PWD=123456')
    data_cursor = data_conn.cursor()
    try:
        data_cursor.execute(query)
        if not islog:
            query = "UPDATE mod_time SET time=" + str(int(time.time()))
            data_cursor.execute(query)
        data_conn.commit()
    except:
        if not islog:
            QMessageBox.warning(None, 'Предупреждение',
                                """База данных временно недоступна. Изменения не записаны. 
                                Перезапустите программу и повторите попытку""")
    data_conn.close()


# Чтение из БД
def connectDb():
    if opt.use_local_db:
        data_conn = sqlite3.connect('rclient.db')
    else:
        data_conn = pyodbc.connect('DRIVER={SQL Server};SERVER=' + opt.database_path + ',' + opt.database_port
                                   + ';DATABASE=rclient;UID=sa;PWD=123456')
    return data_conn


#
def check_ini():
    global ini_modified
    query = "SELECT * FROM mod_time"
    try:  # Если ини доступно (на случай пропадания инета)
        data_conn = connectDb()
        data_cursor = data_conn.cursor()
        data_cursor.execute(query)
        last_mod = data_cursor.fetchone()[0]
        data_conn.close()
        if ini_modified + 1 < last_mod:  # Если кто-то другой изменил ини
            readdata()  # Прочитать изменения
            ini_modified = last_mod
            ftime = datetime.datetime.fromtimestamp(last_mod)
            status_bar_text1.setText('    База изменена: ' + ftime.strftime("%d-%m-%Y %H:%M:%S") + '\t')
    except:
        pass


"""""""""""""""""""""""""""""""""""""""""""""""""""
" Функции чтения и сохранения ini с данными       "
"""""""""""""""""""""""""""""""""""""""""""""""""""


# чтение ini файла в список
def readIni():
    global ini_modified

    try:
        data_conn = connectDb()
        data_cursor = data_conn.cursor()

        query = "SELECT * FROM mod_time"
        data_cursor.execute(query)
        ini_modified = data_cursor.fetchone()[0]
    except:
        QMessageBox.warning(None, 'Ошибка', 'Невозможно подключится к базе даныых. Программа будет закрыта')
        sys.exit(0)


# заполнение списков кураторов, фирм, путь к rclient.exe
def setConstants():
    global cur_list, company_list, display_field, kurator
    cur_list.clear()

    data_conn = connectDb()
    data_cursor = data_conn.cursor()

    query = "SELECT * from users"
    data_cursor.execute(query)
    rows = data_cursor.fetchall()
    for row in rows:
        row = list(row)
        row[3] = row[3].split(',')
        cur_list.append(row)

    kurator, display_field = setDisplayField()

    query = "SELECT * from firms"
    data_cursor.execute(query)
    company_list = data_cursor.fetchall()

    global RAPath
    path1 = "c:\Program Files\Radmin Viewer 3\Radmin.exe"           # проверяем
    path2 = "c:\Program Files (x86)\Radmin Viewer 3\Radmin.exe"     # 2 стандартных пути
    path3 = ""                                                      # и сохраненный
    if os.path.exists(my_doc_path + '\\Client\\rapath.ini'):
        with open(my_doc_path + '\\Client\\rapath.ini', 'r') as file:
            path3 = file.readline()
    if os.path.exists(path1):
        RAPath = path1
    elif os.path.exists(path2):
        RAPath = path2
    elif os.path.exists(path3):
        RAPath = path3
    else:                                                           # если ничего не подошло
        global app                                                  # запрашиваем и сохраняем
        app = QApplication(sys.argv)
        RAPath = QFileDialog.getOpenFileName(QWidget(), 'Открыть файл', 'C:', 'radmin.exe')[0]
        with open(my_doc_path + '\\Client\\rapath.ini', 'w') as file:
            file.write(RAPath)
    data_conn.close()


# заполнение списка папок
def setFolders():
    global fld_list
    fld_list = {}

    data_conn = connectDb()
    data_cursor = data_conn.cursor()

    query = "SELECT * from folders"
    data_cursor.execute(query)
    rows = data_cursor.fetchall()
    for row in rows:
        fld_list[row[0]] = [str(row[0]), str(row[2]), row[1]]
    data_conn.close()


# начальная инициализация данных из БД
def readdata(admin_mode=0):
    clearLog()
    readIni()
    setConstants()
    setFolders()
    folders = set()
    global folder_list, conn_list, conn_list_all, opt
    folder_list.clear()
    conn_list.clear()
    conn_list_all.clear()
    #############################################################
    " Заполнение списка подключений "
    data_conn = connectDb()
    data_cursor = data_conn.cursor()

    query = "SELECT * from connections"
    data_cursor.execute(query)
    rows = data_cursor.fetchall()
    data_conn.close()
    for row in rows:
        in_kurator = 0
        connection = dict(zip(field_list, row))

        connection['psw'] = setPsw(connection['psw'], 5)
        connection['ID1'] = str(len(conn_list))

        connection['Firm1'] = connection['Firm']
        for item in company_list:
            if item[0] == connection['Firm']:
                connection['Firm'] = item[1]

        connection['Curator1'] = connection['Curator']
        cur_text = ''
        for curator in connection['Curator'].split(','):
            for item in cur_list:
                if item[0] == int(curator):
                    cur_text = cur_text + item[1] + ' '
            if (curator in cur_list[kurator][3]) and kurator:
                in_kurator = 1
        connection['Curator'] = cur_text

        # Добавление папок для отображения
        if (kurator == 0 and not opt.access_control) or admin_mode == 1 or in_kurator == 1:
            if (connection['Folder'] not in folders) and connection['Folder'] != 0:
                folder_list.append(fld_list[connection['Folder']])
                folders = folders | {connection['Folder']}
            conn_list.append(connection)
        conn_list_all.append(connection)
    # Добавляем пустые папки для админа
    if kurator == 0 and not opt.access_control:
        for fld in fld_list:
            if int(fld_list[fld][0]) not in folders:
                folder_list.append(fld_list[fld])
                folders = folders | {int(fld_list[fld][0])}
    # Добавляем пустые родительские папки
    while True:
        change = 0
        for fld in folder_list:
            if (int(fld[1]) != 0) and (int(fld[1]) not in folders):
                folder_list.append(fld_list[int(fld[1])])
                folders = folders | {int(fld_list[int(fld[1])][0])}
                change = 1
                # Сортираем папки
                folder_list = sorted(folder_list, key=lambda k: k[0])
        if not change:
            break


# Create empty local DB
def createLocalDb():
    connect = sqlite3.connect('rclient.db')
    cur = connect.cursor()

    # создаем таблицу организаций с записью по умолчанию
    query = "CREATE TABLE firms(id INTEGER primary key, name TEXT)"
    cur.execute(query)
    query = "INSERT INTO firms(id, name) VALUES ( 0, '-')"
    cur.execute(query)
    connect.commit()

    # создаем таблицу пользователей с записью администратора
    query = "CREATE TABLE users(id INTEGER primary key, name TEXT, login TEXT, permissions TEXT, " \
            "comp_name varchar(20))"
    cur.execute(query)
    query = "INSERT INTO users(id , name , login , permissions, comp_name) VALUES(0, 'Admin', '', '0', '')"
    cur.execute(query)
    connect.commit()

    query = "CREATE TABLE folders(id INTEGER primary key, name TEXT, parent INTEGER)"
    cur.execute(query)
    connect.commit()

    query = """CREATE TABLE connections(id INTEGER primary key, name TEXT, ip TEXT, port TEXT, auto_pass INTEGER, 
            psw TEXT, ra INTEGER, colour INTEGER, adress TEXT, has_proxy INTEGER, proxy TEXT, def_act INTEGER, 
            tel TEXT, coment TEXT , user_name TEXT,work_time TEXT, curator TEXT, firm INTEGER, ping INTEGER, 
            folder INTEGER, os varchar(30), provider TEXT)"""
    cur.execute(query)
    connect.commit()

    query = "CREATE TABLE user_logs(user_name varchar(25), comp_name varchar(25), date INTEGER, " \
            "action varchar(50), conn_id INTEGER)"
    cur.execute(query)
    connect.commit()

    query = "CREATE TABLE mod_time(time INTEGER)"
    cur.execute(query)
    connect.commit()

    query = "INSERT INTO mod_time(time) VALUES (" + str(int(time.time())) + ")"
    cur.execute(query)
    connect.commit()
    connect.close()


# Сохраняет базу данных в локальную копию
def saveToDB():
    data_conn = connectDb()
    data_cursor = data_conn.cursor()

    connect = sqlite3.connect('rclient.db')
    cur = connect.cursor()
    # Заполнение таблицы организаций
    query = "SELECT * FROM firms"
    data_cursor.execute(query)
    firms_data = data_cursor.fetchall()

    try:
        query = "DROP TABLE firms"
        cur.execute(query)
        connect.commit()
    except:
        pass

    query = "CREATE TABLE firms(id INTEGER primary key, name TEXT)"
    cur.execute(query)
    connect.commit()

    for firm in firms_data:
        query = "INSERT INTO firms(id, name) VALUES (" + str(firm[0]) + ",'" + firm[1] + "')"
        cur.execute(query)
    connect.commit()

    # Заполнение таблицы кураторов
    query = "SELECT * FROM users"
    data_cursor.execute(query)
    users_data = data_cursor.fetchall()

    try:
        query = "DROP TABLE users"
        cur.execute(query)
        connect.commit()
    except:
        pass

    query = "CREATE TABLE users(id INTEGER primary key, name TEXT, login TEXT, permissions TEXT, " \
            "comp_name varchar(20))"
    cur.execute(query)
    connect.commit()

    for user in users_data:
        query = "INSERT INTO users(id , name , login , permissions, comp_name) VALUES(" + str(user[0]) + ", '" \
                + user[1] + "', '" + user[2] + "', '" + user[3] + "', '" + user[4] + "')"
        cur.execute(query)
    connect.commit()

    # Заполнение таблицы папок
    query = "SELECT * FROM folders"
    data_cursor.execute(query)
    folder_data = data_cursor.fetchall()

    try:
        query = "DROP TABLE folders"
        cur.execute(query)
        connect.commit()
    except:
        pass

    query = "CREATE TABLE folders(id INTEGER primary key, name TEXT, parent INTEGER)"
    cur.execute(query)
    connect.commit()

    for folder in folder_data:
        query = "INSERT INTO folders(id , name , parent) VALUES (" + str(folder[0]) + ", '" + folder[1] \
                + "', " + str(folder[2]) + ")"
        cur.execute(query)
    connect.commit()

    # Заполнение таблицы подключений
    query = "SELECT * FROM connections"
    data_cursor.execute(query)
    conn_data = data_cursor.fetchall()

    try:
        query = "DROP TABLE connections"
        cur.execute(query)
        connect.commit()
    except:
        pass

    query = """CREATE TABLE connections(id INTEGER primary key, name TEXT, ip TEXT, port TEXT, auto_pass INTEGER, 
                    psw TEXT, ra INTEGER, colour INTEGER, adress TEXT, has_proxy INTEGER, proxy TEXT, def_act INTEGER, 
                    tel TEXT, coment TEXT , user_name TEXT,work_time TEXT, curator TEXT, firm INTEGER, ping INTEGER, 
                    folder INTEGER, os varchar(30), provider TEXT)"""
    cur.execute(query)
    connect.commit()
    for item in conn_data:
        query = """INSERT INTO connections(id, name, ip, port, auto_pass, psw, ra, colour, adress, has_proxy, 
                    proxy, def_act, tel, coment, user_name, work_time, curator, firm, ping, folder, os, provider) VALUES(
                    {}, '{}', '{}', '{}', {}, '{}', {}, {}, '{}', {}, '{}', {}, '{}', '{}', '{}', '{}', '{}', {}, {}, {}, 
                    '{}','{}')"""
        query = query.format(str(item[0]), item[1], item[2], item[3], str(item[4]), item[5], item[6],
                             str(item[7]), item[8], str(item[9]), item[10], str(item[11]), item[12], item[13],
                             item[14], item[15], item[16], item[17], str(item[18]), str(item[19]), item[20],
                             item[21])
        cur.execute(query)
    connect.commit()

    # Создаем таблицу логов
    try:
        query = "DROP TABLE user_logs"
        cur.execute(query)
        connect.commit()
    except:
        pass
    query = "CREATE TABLE user_logs(user_name varchar(25), comp_name varchar(25), date INTEGER, " \
            "action varchar(50), conn_id INTEGER)"
    cur.execute(query)
    connect.commit()

    # Создаем таблицу mod_time
    try:
        query = "DROP TABLE mod_time"
        cur.execute(query)
        connect.commit()
    except:
        pass
    query = "CREATE TABLE mod_time(time INTEGER)"
    cur.execute(query)
    connect.commit()

    query = "INSERT INTO mod_time(time) VALUES (" + str(int(time.time())) + ")"
    cur.execute(query)
    connect.commit()
    connect.close()


"""""""""""""""""""""""""""""""""""""""""""""""""""
" Функции для реализации подключения и автопароля "
"""""""""""""""""""""""""""""""""""""""""""""""""""


# автопароль для 2 радмина
def autoPassRA2(ip, psw, cnt=100):
    text = 'Система безопасности Radmin: ' + ip
    wnd = 0
    while cnt > 0:
        wnd = win32gui.FindWindow(None, text)
        time.sleep(0.1)
        cnt -= 1
        if wnd > 0:
            break
    if cnt != 0:
        t = win32gui.FindWindowEx(wnd, None, 'Edit', None)
        win32gui.SendMessage(t, win32con.WM_SETTEXT, 0, psw)
        time.sleep(0.01)
        t = win32gui.FindWindowEx(wnd, None, 'Button', None)
        win32gui.SendMessage(t, win32con.BM_CLICK, 0, 0)


# автопароль для 3 радмина
def autoPassRA3(ip, login, psw, cnt=100):
    text = 'Система безопасности Radmin: ' + ip
    wnd = 0
    while cnt > 0:
        wnd = win32gui.FindWindow(None, text)
        time.sleep(0.1)
        cnt -= 1
        if wnd > 0:
            break
    if cnt != 0:
        try:
            t = win32gui.FindWindowEx(wnd, None, 'Edit', None)
            win32gui.SendMessage(t, win32con.WM_SETTEXT, 0, login)
            time.sleep(0.01)
            t = win32gui.FindWindowEx(wnd, t, 'Edit', None)
            win32gui.SendMessage(t, win32con.WM_SETTEXT, 0, psw)
            time.sleep(0.01)
            t = win32gui.FindWindowEx(wnd, None, 'Button', None)
            t = win32gui.FindWindowEx(wnd, t, 'Button', None)
            win32gui.SendMessage(t, win32con.BM_CLICK, 0, 0)
        except ValueError:
            pass


# автопароль для VNC
def autoPassVNC(psw, cnt=100):
    text = 'VNC Viewer : Authentication [No Encryption]'
    wnd = 0
    while cnt > 0:
        wnd = win32gui.FindWindow(None, text)
        time.sleep(0.1)
        cnt -= 1
        if wnd > 0:
            break
    if cnt != 0:
        t = win32gui.FindWindowEx(wnd, None, 'Edit', None)
        win32gui.SendMessage(t, win32con.WM_SETTEXT, 0, psw)
        time.sleep(0.01)
        t = win32gui.FindWindowEx(wnd, None, 'Button', None)
        win32gui.SendMessage(t, win32con.BM_CLICK, 0, 0)


# выбор типа обработчика автопароля
def autoPass(item):
    if item['RA'] == 2:
        autoPassRA2(item['IP'], item['psw'])
    else:
        autoPassRA3(item['IP'], item['User'], item['psw'])


# прямое подключение
def connectDirect(item, action, ap):
    """ Прямое подключение """
    path = '"' + RAPath + '" /connect:' + item['IP'] + ':' + item['port'] + ' '
    path += Colours[item['colour'] - 1] + TypeConn[action]
    subprocess.Popen(path, shell=True)
    if ap:
        autoPass(item)


# подключение через прокси
def connectProxy(item, action, ap):
    proxy_item = getProxyItem(item)
    path = '"' + RAPath + '" /connect:' + item['IP'] + ':' + item['port']
    path += ' /through:' + proxy_item['IP'] + ':' + proxy_item['port'] + ' '
    path += Colours[item['colour'] - 1] + TypeConn[action]
    subprocess.Popen(path, shell=True)
    if ap:
        autoPass(proxy_item)
        autoPass(item)


# заполнение файла vnc.vnc
def setIpToVNC(ip):
    vnc_data = []
    with open('vnc.vnc', 'r') as file:
        for line in file:
            vnc_data.append(line.rstrip())
    for line in range(len(vnc_data)):
        if vnc_data[line][:4] == 'Host':
            vnc_data[line] = 'Host=' + ip
    with open('vnc.vnc', 'w') as file:
        for line in vnc_data:
            file.write(line + '\n')


# подключение к vnc
def connectVNC(item, ap):
    setIpToVNC(item['IP'])
    path = 'vnc.vnc'
    subprocess.Popen(path, shell=True)
    if ap:
        autoPassVNC(item['psw'])


# определение типа подключения и запуск соответственного обработчика
def conn(item, action):
    ap = item['AutoPass']
    if action == 5:
        action = item['DefAct']
    elif action == 6:
        action = 0
        ap = 0
    if item['RA'] == 4:  # VNC
        writeToLog('VNC', item['ID'])
        connectVNC(item, ap)
    else:
        if action == 2:
            text = 'Rad /file'
        elif action == 3:
            text = 'Rad /shutdown'
        else:
            text = 'Rad'
        # Записать в лог
        writeToLog(text, item['ID'])

        if not item['HasProxy']:
            connectDirect(item, action, ap)
        else:
            connectProxy(item, action, ap)


"""""""""""""""""""""""""""""""""""""""""""""""""""
"   Функции работы с сокетами                     "
"""""""""""""""""""""""""""""""""""""""""""""""""""


# проверка доступности потров
def check_port(item, addlock):
    sockobj = socket(AF_INET, SOCK_STREAM)
    sockobj.settimeout(1)
    try:
        sockobj.connect((item['IP'], int(item['port'])))
    except:
        with addlock:
            check_not_done.append((item['Name'], item['IP'], item['port']))
    sockobj.close()


# отображения списка недоступных подключений
def showNotDone():
    with open(my_doc_path + '\\Client\\not_done.txt', 'w') as file:
        file.write(' Имя                               | IP адрес       | порт\n')
        file.write('-----------------------------------+----------------+------\n')
        for item in check_not_done:
            text = ' {:<34}| {:<15}| {:<5}'.format(item[0], item[1], item[2])
            file.write(text + '\n')
    # открыть файл
    os.startfile(my_doc_path + '\\Client\\not_done.txt')


# отправка данных об активности на сервер
def sendAdminData():
    ip = gethostbyname(gethostname())
    message = comp_name + ';' + ip + ';' + str(opt.admin_timeout) + ';' + version_prog + ';' + user_name

    sockobj = socket(AF_INET, SOCK_STREAM)
    sockobj.settimeout(1)
    try:
        sockobj.connect((opt.admin_host, opt.admin_port))
        sockobj.send(message.encode())
    except:
        pass

    sockobj.close()


"""""""""""""""""""""""""""""""""""""""""""""""""""
" Начальная инициализация                         "
"""""""""""""""""""""""""""""""""""""""""""""""""""
if not os.path.exists('rclient.db'):
    createLocalDb()
opt = Options()
getLocalSettings()
readdata()
if __name__ == '__main__':
    pass
