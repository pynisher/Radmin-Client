# -*- coding: utf-8 -*-
__author__ = 'Admin'
from addedit import *
from func import *


# Груповая установка статусов для действий
def groupSetEnabled(items, status):
    for item in items:
        item.setEnabled(status)


"""
    Отображает список папок слева
"""


class MyTree(QTreeView):

    def __init__(self):
        super().__init__()
        self.selFolders = (0,)
        self.menu = QMenu(self)
        self.model = QStandardItemModel(self)
        self.folders = {}
        self.initUI()

    " Начальная инициализация "
    def initUI(self):
        self.setHeaderHidden(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)  # Режим выбора
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)      # Запретить редактирование
        self.pressed.connect(self.clickItem)
        self.setActions()

        self.setModel(self.model)
        self.setData()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.myMenu)

    " Заполнение таблицы "
    def setData(self, selected_folder='0'):
        self.model.clear()
        sel_item = 0
        " Заполнение дерева папок "
        parent_item = self.model.invisibleRootItem()

        item = QStandardItem("\\")
        item.setIcon(QIcon('img\\folder.png'))
        parent_item.appendRow(item)
        self.expand(self.model.indexFromItem(item))

        self.folders = {'0': self.model.indexFromItem(item)}

        for folder in folder_list:
            item = QStandardItem(folder[2])
            if folder[0] == selected_folder:
                sel_item = item
            item.setIcon(QIcon('img\\folder.png'))
            parent_item = self.model.itemFromIndex(self.folders[folder[1]])
            parent_item.appendRow(item)
            self.folders[folder[0]] = self.model.indexFromItem(item)
        if selected_folder == '0':
            self.setCurrentIndex(self.model.index(0, 0))
        else:
            self.setCurrentIndex(self.model.indexFromItem(sel_item))
            self.selFolders = (int(selected_folder),)

    " Установка действия "
    def setAction(self, text, shortcut, icon, action):
        act = QAction(text, self)
        act.setShortcut(shortcut)
        act.setIcon(QIcon(icon))
        act.triggered.connect(action)
        return act

    " Установка действий "
    # noinspection PyAttributeOutsideInit
    def setActions(self):
        self.delfolderAction = self.setAction("Удалить папку", '',
                                         'img\\delfolder.png', self.delFolder)
        self.editfolderAction = self.setAction("Переименовать папку", '',
                                         'img\\editfolder.png', self.editFolder)
        self.addfolderAction = self.setAction("Новая папка", 'F7',
                                         'img\\addfolder.png', self.addFolder)
        self.addconnAction = self.setAction("Новое подключение", 'Ins',
                                         'img\\addconn.png', connList.addConn)

    " Добавление действий "
    def addUserActions(self):
        self.menu.clear()
        if globaluser == 'admin':
            self.menu.addAction(self.delfolderAction)
            self.menu.addAction(self.editfolderAction)
            self.menu.addSeparator()
            self.menu.addAction(self.addfolderAction)
            self.menu.addAction(self.addconnAction)

    " контекстное меню "
    def myMenu(self, pos):
        # добавление действий
        self.addUserActions()
        # отображение меню
        self.menu.exec_(self.mapToGlobal(pos))

    " при изменении выбраных элементов "
    def selectionChanged(self, sel1, sel2):
        if globaluser == 'user':
            groupSetEnabled((self.delfolderAction, self.editfolderAction,
                             self.addfolderAction, self.addconnAction), False)
            try:
                groupSetEnabled((toolbar.delfolderAction, toolbar.editfolderAction,
                                 toolbar.addfolderAction), False)
            except:
                pass
        else:
            if len(self.selectedIndexes()) == 1:
                groupSetEnabled((self.delfolderAction, self.editfolderAction,
                                 self.addfolderAction, self.addconnAction,
                                 toolbar.delfolderAction, toolbar.editfolderAction,
                                 toolbar.addfolderAction, toolbar.addconnAction), True)
                if self.selectedIndexes()[0] == self.folders['0']:
                    groupSetEnabled((self.delfolderAction, self.editfolderAction,
                                 toolbar.delfolderAction, toolbar.editfolderAction),
                                    False)
            else:  # выбрано больше одной папки  или не выбрано ниодной
                groupSetEnabled((self.delfolderAction, self.editfolderAction,
                                 self.addfolderAction, self.addconnAction,
                                 toolbar.delfolderAction, toolbar.editfolderAction,
                                 toolbar.addfolderAction, toolbar.addconnAction), False)

        super().selectionChanged(sel1, sel2)

    " при нажатии мыши "
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:            # если ПКМ
            if self.indexAt(event.pos()).row() == -1:   # за пределами папок
                self.clearSelection()                   # очистить выбор

        super().mousePressEvent(event)

    " При клике мышки "
    def clickItem(self):
        # перерисовать все значки в закрытые папки
        self.model.itemFromIndex(self.folders['0']).setIcon(QIcon('img\\folder.png'))
        for folder in folder_list:
            self.model.itemFromIndex(self.folders[folder[0]]).setIcon(QIcon('img\\folder.png'))
        # поставить значки открытой папки у выделенных
        self.selFolders = ()
        for item in self.selectedIndexes():
            self.model.itemFromIndex(item).setIcon(QIcon('img\\openfolder.png'))
            for i in self.folders:
                if self.folders[i] == item:
                    self.selFolders = self.selFolders + (int(i),)

        # отобразить список подключений
        connList.setData(self.selFolders)

    " Удаление папки "
    def delFolder(self):
        id_ = self.getID()
        for item in conn_list:
            if item['Folder'] == int(id_):
                QMessageBox.warning(self, 'Предупреждение',
"""Папка не пустая. Запрещено удалять папку, в которой есть подключения.""")
                return
        for folder in folder_list:
            if folder[1] == id_:
                QMessageBox.warning(self, 'Предупреждение',
"""Папка содержит влеженные папки. Запрещено удалять папку, в которой есть вложенные папки.""")
                return
        for folder in folder_list:
            if folder[0] == id_:
                folder_list.pop(folder_list.index(folder))

        query = "DELETE FROM folders WHERE id=" + str(id_)
        writeToDb(query)

        self.setData()
        connList.setData((0, ))

    " Переименование папки "
    def editFolder(self):
        id_ = self.getID()
        text, ok = QInputDialog.getText(self, 'Переименовать',
                                        'Введите новое название:',
                                        QLineEdit.Normal,
                                        self.selectedIndexes()[0].data(),
                                        Qt.CoverWindow)
        if ok and text:
            for folder in folder_list:
                if folder[0] == id_:
                    folder[2] = text
            self.setData(id_)

            query = "UPDATE folders SET name='" + text + "' WHERE id=" + str(id_)
            writeToDb(query)

            connList.setData(self.selFolders)

    " Добавление папки "
    def addFolder(self):
        id_ = self.getID()
        max_folder = 0
        parent_folder = ['0', '0', '\\']
        for folder in folder_list:
            if folder[0] == id_:
                parent_folder = folder
            if int(folder[0]) > max_folder:
                max_folder = int(folder[0])
        text, ok = QInputDialog.getText(self, 'Новая папка в "'
                                        + parent_folder[2] + '"',
                                        'Введите название папки:',
                                        QLineEdit.Normal, '', Qt.CoverWindow)
        if ok and text:
            folder_list.append([str(max_folder+1), parent_folder[0], text])

            query = "INSERT INTO folders(id , name , parent) VALUES (" + str(max_folder+1) + ", '" + text + "', " + \
                    parent_folder[0] + ")"
            writeToDb(query)

            self.setData(folder_list[-1][0])
            connList.setData(self.selFolders)

    " Получить ID выделенной папки "
    def getID(self):
        for i in self.folders:
            if self.folders[i] == self.selectedIndexes()[0]:
                return i


"""
    Отображает список подключений
"""


class MyList(QTreeView):

    def __init__(self):
        super().__init__()
        self.hidden_field = len(display_field) - 1
        self.menu = QMenu(self)
        self.model = QStandardItemModel(self)
        self.initUI()

    " конструктор отображения "
    def initUI(self):
        global folderTree, statusBarText1, statusBarText2, toolbar, \
            status_bar_text1, status_bar_text2, status_bar_text4

        # настройка отображения списка
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setIndentation(0)
        self.setSortingEnabled(True)
        self.setAllColumnsShowFocus(True)
        self.setAlternatingRowColors(True)
        # установка действий
        self.setActions()
        # установка модели и начальное заполнение таблицы
        self.setModel(self.model)
        self.setData((0,))
        # контекстное меню
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.myMenu)
        # действия для быстрых клавиш
        self.addAction(self.fullAction)
        self.addAction(self.viewAction)
        self.addAction(self.fileAction)
        self.addAction(self.pingAction)
        self.addAction(self.ipAction)
        self.addAction(self.shutdownAction)
        self.addAction(self.searchAction)

    " установка одного действия "
    def setAction(self, text, shortcut, icon, action):
        act = QAction(text, self)
        if shortcut:
            act.setShortcut(shortcut)
            act.setIconVisibleInMenu(True)
        if icon:
            act.setIcon(QIcon(icon))
        act.triggered.connect(action)
        return act

    " установка действий для контекстного меню и гарячих клавиш "
    # noinspection PyAttributeOutsideInit
    def setActions(self):
        def_font = QFont('Times', 8, 75)
        self.defAction = self.setAction("Подключение по умолчанию", 'Enter',
                                        '', self.defConn)
        self.defAction.setFont(def_font)

        self.fullAction = self.setAction("Полный контроль", 'Alt+C',
                                         'img\\full.png', self.fullConn)
        self.viewAction = self.setAction("Просмотр", 'Alt+V',
                                         'img\\view.png', self.viewConn)
        self.fileAction = self.setAction("Передача файлов", 'Alt+F',
                                         'img\\file.png', self.fileConn)
        self.pingAction = self.setAction("Пинговать", 'Alt+P',
                                         'img\\ping.png', self.ping)
        self.telnetAction = self.setAction("Telnet", 'Alt+T',
                                           'img\\telnet.png', self.telnetConn)
        self.nopassAction = self.setAction("Полный контроль без автопароля", '',
                                           'img\\full.png', self.nopassConn)
        self.ipAction = self.setAction("Копировать IP адрес в буфер",
                                       'Ctrl+Alt+C', 'img\\copy.png', self.copyIP)
        self.shutdownAction = self.setAction("Выключить", 'Alt+S',
                                            'img\\shutdown.png', self.downConn)
        self.addconnAction = self.setAction("Новое соединение", 'Ins',
                                            'img\\addconn.png', self.addConn)
        self.editconnAction = self.setAction("Переименовать", 'F2',
                                            'img\\editconn.png', self.editConn)
        self.delconnAction = self.setAction("Удалить соединение", 'Del',
                                            'img\\delconn.png', self.delConn)
        self.propertiesAction = self.setAction("Свойства соединения", 'Space',
                                               'img\\properties.png', self.properties)
        self.copyAction = self.setAction("Копировать", 'Ctrl+C',
                                         'img\\copy.png', self.copyConn)
        self.pasteAction = self.setAction("Вставить", 'Ctrl+V',
                                          'img\\paste.png', self.pasteConn)
        self.newconnAction = self.setAction("Быстрое подключение", 'F3',
                                            'img\\newconn.png', self.newConn)
        self.portscanAction = self.setAction("Сканировать порт", '', '', self.portScan)
        self.historyAction = self.setAction("История по узлу", '', '', self.connHistory)
        self.searchAction = self.setAction("Поиск", 'Ctrl+F', '', self.searchText)

    " создание меню для конкретного пользователя "
    def addUserActions(self):
        self.menu.clear()
        self.menu.addAction(self.defAction)
        self.menu.addSeparator()
        self.menu.addAction(self.fullAction)
        self.menu.addAction(self.viewAction)
        self.menu.addAction(self.fileAction)
        if globaluser == 'admin':
            self.menu.addAction(self.shutdownAction)
        self.menu.addAction(self.pingAction)
        self.menu.addSeparator()
        if globaluser == 'admin':
            self.menu.addAction(self.addconnAction)
            self.menu.addAction(self.editconnAction)
            self.menu.addAction(self.delconnAction)
            self.menu.addAction(self.propertiesAction)
            self.menu.addSeparator()
            self.menu.addAction(self.copyAction)
            self.menu.addAction(self.pasteAction)
            self.menu.addSeparator()
        self.menu.addAction(self.newconnAction)
        self.menu.addAction(self.telnetAction)
        self.menu.addAction(self.nopassAction)
        self.menu.addAction(self.ipAction)
        if globaluser == 'admin':
            self.menu.addAction(self.portscanAction)
            self.menu.addAction(self.historyAction)
        self.menu.addAction(self.searchAction)

    " Заполнение таблицы "
    def setData(self, sel_folders):
        self.model.clear()

        # Установка заголовков.
        headers = []
        for i in display_field:
            headers.append(i[2])
        self.model.setHorizontalHeaderLabels(headers)
        for i in display_field:
            self.setColumnWidth(i[3], i[1])
        self.hideColumn(self.hidden_field)

        # Заполнение таблицы
        self.display_list = getDisplayList(sel_folders)
        # noinspection PyAttributeOutsideInit
        self.display_list = sortList(self.display_list, 'Name')
        lo_count = set()
        night_count = 0

        for item in self.display_list:
            val = ()
            for field in display_field:
                val = val + (QStandardItem(item[field[0]]),)
                if item['Name'][-8:] == '(Золото)':  # золотые магазины
                    val[field[3]].setBackground(QColor('#ffff99'))
                if item['Coment'][:3] == '!!!':  # красным неработающие
                    val[field[3]].setBackground(QColor('#ff8888'))
            if item['RA'] == 2:
                val[0].setIcon(QIcon('img\\ra2.png'))
            elif item['RA'] == 3:
                val[0].setIcon(QIcon('img\\ra3.png'))
            else:
                val[0].setIcon(QIcon('img\\vnc.png'))
            # проверяем суточный ли ломбард
            if item['WorkTime'] == '24':
                night_count += 1
            if item['Name'].find('_') > 0:
                lo_count = lo_count | {item['Name'].split('_')[0]}

            self.model.appendRow(val)
        self.setCurrentIndex(self.model.index(0, 0))

        status_text = '    Всего: ' + str(len(self.display_list)) + ' узлов.  '
        if len(lo_count) > 0:
            status_text += str(len(lo_count)) + ' отделений.  '
        if night_count > 0:
            status_text += str(night_count) + ' суточных.'
        status_bar_text2.setText('{:<70}'.format(status_text))

    " контекстное меню "
    def myMenu(self, pos):
        # добавление действий
        self.addUserActions()
        # отображение меню
        pos.setY(pos.y()+22)
        self.menu.exec_(self.mapToGlobal(pos))

    " при нажатии мыши "
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            if self.indexAt(event.pos()).row() == -1:
                self.clearSelection()
                self.setCurrentIndex(self.model.index(self.currentIndex().row(), 0))

        super().mousePressEvent(event)

    " при изменении выбраных элементов "
    def selectionChanged(self, sel1, sel2):
        rows = set()    # находим количество выделеных строк
        for item in self.selectedIndexes():
            rows = rows | {item.row()}

        if len(self.selectedIndexes()) == 0:  # если кликнуть на пустом поле
            # отключение действий для панели инструментов
            # в попытке из за того, что при первом вызове тулбар еще не создан
            try:
                groupSetEnabled((toolbar.delconnAction, toolbar.editconnAction,
                                 toolbar.shutdownAction, toolbar.fullAction,
                                 toolbar.viewAction, toolbar.fileAction,
                                 toolbar.pingAction), False)
                if globaluser == 'user':
                    groupSetEnabled((toolbar.addconnAction, ), False)
            except:
                pass
            # отключение действий для контекстного меню
            groupSetEnabled((self.defAction, self.fullAction, self.viewAction, self.fileAction, self.pingAction,
                             self.telnetAction, self.nopassAction, self.ipAction, self.shutdownAction,
                             self.editconnAction, self.delconnAction, self.propertiesAction, self.copyAction,
                             self.portscanAction, self.historyAction), False)
        else:
            # включение действий для панели инструментов
            # в попытке из за того, что при первом вызове тулбар еще не создан
            try:
                groupSetEnabled((toolbar.fullAction, toolbar.viewAction,
                                 toolbar.fileAction, toolbar.pingAction), True)
            except:
                pass
            # включение действий для контекстного меню
            groupSetEnabled((self.defAction, self.fullAction, self.viewAction, self.fileAction, self.pingAction,
                             self.telnetAction, self.nopassAction, self.ipAction, self.shutdownAction,
                             self.editconnAction, self.delconnAction, self.propertiesAction, self.copyAction,
                             self.portscanAction, self.historyAction), True)
            if globaluser == 'admin':
                groupSetEnabled((toolbar.addconnAction, toolbar.delconnAction,
                                 toolbar.editconnAction,
                                 toolbar.shutdownAction), True)
            if len(rows) == 1:
                groupSetEnabled((self.ipAction, self.editconnAction, self.delconnAction, self.propertiesAction,
                                 self.copyAction, self.portscanAction, self.historyAction), True)
                if globaluser == 'admin':
                    groupSetEnabled((toolbar.delconnAction, toolbar.editconnAction), True)

        if len(rows) > 1:
            groupSetEnabled((toolbar.delconnAction, toolbar.editconnAction,
                             self.ipAction, self.editconnAction, self.delconnAction, self.propertiesAction,
                             self.copyAction, self.portscanAction, self.historyAction), False)

        if globalclipboard == 0:
            groupSetEnabled((self.pasteAction, ), False)
        else:
            groupSetEnabled((self.pasteAction, ), True)

        try:    # Если выбрано больше одной папки - отключить добавление нового подключения
            if len(folderTree.selectedIndexes()) != 1:
                groupSetEnabled((toolbar.addconnAction, self.addconnAction,
                                 self.pasteAction), False)
        except:
            pass
        try:
            ind = int(self.model.index(self.currentIndex().row(), self.hidden_field).data())
            status_bar_text4.setText('    ' + ColorNames[int(conn_list[ind]['colour'])-1] + '    ')
            if show_passwords:
                status_bar_text5.setText('    ' + conn_list[ind]['psw'] + '     ')
            status_bar_text6.setText('    ' + conn_list[ind]['Provider'].split('\n')[0] + '    ')
        except:
            pass
        super().selectionChanged(sel1, sel2)

    " при нажатии на клавиатуре "
    def keyPressEvent(self, e):
        if e.key() in {Qt.Key_Return, Qt.Key_Enter}:
            self.connItem()
        else:
            super().keyPressEvent(e)

    " двойной клик "
    def mouseDoubleClickEvent(self, e):
        self.connItem()

    " быстрый поиск "
    def keyboardSearch(self, text):
        super().keyboardSearch(text)
        self.clearSelection()
        self.setCurrentIndex(self.model.index(self.currentIndex().row(), 0))

    " Подключение по умолчанию "
    def defConn(self):
        self.connItem()

    " Полный контроль "
    def fullConn(self):
        self.connItem(0)

    "Просмотр"
    def viewConn(self):
        self.connItem(1)

    " Передача файлов "
    def fileConn(self):
        self.connItem(2)

    " выключить "
    def downConn(self):
        self.connItem(3)

    " Пинговать "
    def ping(self):
        ip = self.currentIndex().sibling(self.currentIndex().row(), 3).data()
        path = 'ping ' + ip + ' -t'
        subprocess.Popen(path, shell=False)

    " Telnet "
    def telnetConn(self):
        self.connItem(4)

    " Полный контроль без автопароля "
    def nopassConn(self):
        self.connItem(6)

    " Копировать IP адрес в буфер "
    def copyIP(self):
        ip = self.currentIndex().sibling(self.currentIndex().row(), 3).data()
        QApplication.clipboard().setText(ip)

    " Новое соединение "
    def addConn(self):
        addedit[0] = 0
        addedit[1] = folderTree.selFolders[0]
        addedit[2] = '0'
        edit_wnd = AddEditWidget(self)
        edit_wnd.destroyed.connect(self.refreshList)        # обновить список
        edit_wnd.show()

    " Переименовать "
    def editConn(self):
        id_ = int(self.currentIndex().sibling(self.currentIndex().row(), self.hidden_field).data())
        text, ok = QInputDialog.getText(self, 'Переименовать',
                                        'Введите новое название:',
                                        QLineEdit.Normal, conn_list[id_]['Name'],
                                        Qt.CoverWindow)
        if ok and text:
            conn_list[id_]['Name'] = text

            query = "UPDATE connections SET name='" + text + "' WHERE id=" + str(id_)
            writeToDb(query)

            self.setData(folderTree.selFolders)

    " Удалить соединение "
    def delConn(self):
        i = int(self.currentIndex().sibling(self.currentIndex().row(), self.hidden_field).data())
        msg = QMessageBox(self)
        msg.addButton("Да", QMessageBox.AcceptRole)
        msg.addButton("Нет", QMessageBox.RejectRole)
        msg.setText('Вы действительно хотите удалить ' + conn_list[i]['Name'] + ' ?')
        msg.setWindowTitle('Удаление')
        msg.setIcon(QMessageBox.Question)
        reply = msg.exec_()
        if reply == 0:
            i_ = conn_list[i]['ID']
            conn_list.pop(i)                    # Удалить запись
            while True:
                if i == len(conn_list):
                    break
                conn_list[i]['ID1'] = str(i)    # Перезаполнить все ID после удаленного
                i += 1
                if i == len(conn_list):
                    break

            query = "DELETE FROM connections WHERE id=" + str(i_)
            writeToDb(query)

            self.setData(folderTree.selFolders)

    " Свойства соединения "
    def properties(self):
        addedit[0] = 1
        addedit[1] = int(self.currentIndex().sibling(self.currentIndex().row(),
                                                 self.hidden_field).data())
        addedit[2] = '0'
        edit_wnd = AddEditWidget(self)
        edit_wnd.destroyed.connect(self.refreshList)        # обновить список
        edit_wnd.show()

    " Копировать "
    def copyConn(self):
        global globalclipboard
        globalclipboard = conn_list[int(self.model.index(self.selectedIndexes()[0].row(),
                                                         self.hidden_field).data())]

    " Вставить "
    def pasteConn(self):
        item = dict(globalclipboard)            # важно именно скопировать словарь
        item['ID1'] = str(len(conn_list))
        item['ID'] = getMaxListNum() + 1
        item['Folder'] = folderTree.selFolders[0]
        conn_list.append(item)

        q_text = """INSERT INTO connections(id, name, ip, port, auto_pass, psw, ra, colour, adress, has_proxy, proxy, 
                def_act, tel, coment, user_name, work_time, curator, firm, ping, folder) VALUES(
                {}, '{}', '{}', '{}', {}, '{}', {}, {}, '{}', {}, '{}', {}, '{}', '{}', '{}', '{}', '{}', {}, {}, {})"""
        query = q_text.format(str(item['ID']), item['Name'], item['IP'], item['port'], str(item['AutoPass']),
                              setPsw(item['psw'], -5), str(item['RA']), str(item['colour']), item['Adress'],
                              str(item['HasProxy']), item['Proxy'], str(item['DefAct']), item['Tel'], item['Coment'],
                              item['User'], item['WorkTime'], item['Curator1'], str(item['Firm1']), str(item['ping']),
                              str(item['Folder']))
        writeToDb(query)

        self.setData(folderTree.selFolders)

    " Быстрое подключение "
    def newConn(self):
        new_conn = FastConnWidget(self)
        new_conn.show()

    def refreshList(self):
        if addedit[2] == '1':
            self.setData(folderTree.selFolders)
        if addedit[0] == 1:         # выделить редактируемый елемент
            for i in range(len(self.display_list)):
                if self.display_list[i]['ID1'] == str(addedit[1]):
                    self.setCurrentIndex(self.model.index(i, 0))

    def portScan(self):
        text = '5000'
        while True:
            text, ok = QInputDialog.getText(self, 'Сканирование портов', 'Введите порт:', QLineEdit.Normal,
                                            text, Qt.CoverWindow)
            if ok and text:
                id_ = int(self.currentIndex().sibling(self.currentIndex().row(), self.hidden_field).data())
                item = conn_list[id_]
                sockobj = socket(AF_INET, SOCK_STREAM)
                sockobj.settimeout(1)
                try:
                    sockobj.connect((item['IP'], int(text)))
                    QMessageBox.information(self, 'Скан портов', 'Порт доступен')
                except:
                    QMessageBox.information(self, 'Скан портов', 'Порт недоступен')
                sockobj.close()
            else:
                break

    def connHistory(self):
        id_ = int(self.currentIndex().sibling(self.currentIndex().row(), self.hidden_field).data())
        ha = HistoryWidget(conn_list[id_]['ID'], self)
        ha.show()

    def searchText(self):
        search = FastSearch(self, self)
        search.show()

    " подключение "
    def connItem(self, auto_action=5):
        # Найти индексы выделенных строк и отправить в поток для подключения
        rows = set()
        for item in self.selectedIndexes():         # Находим номера выдленных строк
            rows = rows | {item.row()}

        for row in rows:                            # Запускаем в поток, передаем индекс
            threading.Thread(target=conn,
                             args=(conn_list[int(self.model.index(row, self.hidden_field).data())],
                                   auto_action)).start()


"""
    Панель инструментов
"""


class MyToolBar(QToolBar):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setActions()
        self.setMovable(False)
        self.setIconSize(QSize(26, 26))

        self.addAction(self.newconnAction)
        self.addSeparator()
        self.addAction(self.addfolderAction)
        self.addAction(self.delfolderAction)
        self.addAction(self.editfolderAction)
        self.addSeparator()
        self.addAction(self.addconnAction)
        self.addAction(self.delconnAction)
        self.addAction(self.editconnAction)
        self.addSeparator()
        self.addAction(self.fullAction)
        self.addAction(self.viewAction)
        self.addAction(self.fileAction)
        self.addAction(self.shutdownAction)
        self.addAction(self.pingAction)

    def setAction(self, icon, action):
        act = QAction(self)
        act.setIcon(QIcon(icon))
        act.triggered.connect(action)
        return act

    # noinspection PyAttributeOutsideInit
    def setActions(self):
        self.newconnAction = self.setAction('img\\newconn_big.png', connList.newConn)
        self.addfolderAction = self.setAction('img\\addfolder_big.png', folderTree.addFolder)
        self.delfolderAction = self.setAction('img\\delfolder_big.png', folderTree.delFolder)
        self.editfolderAction = self.setAction('img\\editfolder_big.png', folderTree.editFolder)
        self.addconnAction = self.setAction('img\\addconn_big.png', connList.addConn)
        self.delconnAction = self.setAction('img\\delconn_big.png', connList.delConn)
        self.editconnAction = self.setAction('img\\editconn_big.png', connList.editConn)
        self.fullAction = self.setAction('img\\full_big.png', connList.fullConn)
        self.viewAction = self.setAction('img\\view_big.png', connList.viewConn)
        self.fileAction = self.setAction('img\\file_big.png', connList.fileConn)
        self.shutdownAction = self.setAction('img\\shutdown_big.png', connList.downConn)
        self.pingAction = self.setAction('img\\ping_big.png', connList.ping)

        groupSetEnabled((self.addfolderAction, self.delfolderAction,
                         self.editfolderAction, self.addconnAction,
                         self.delconnAction, self.editconnAction,
                         self.shutdownAction), False)


"""
    Главное меню
"""


class MyMenu(QMenuBar):

    def __init__(self):
        super().__init__()
        self.prefMenu = QMenu('Настройки')
        self.tasksMenu = QMenu('Задачи')
        self.editMenu = QMenu('Редактировать')
        self.setActions()
        self.initUI()

    " Создание меню "
    def initUI(self):
        self.clear()
        self.prefMenu.clear()
        self.addMenu(self.prefMenu)
        self.prefMenu.addAction(self.userAction)
        self.prefMenu.addAction(self.adminAction)
        self.addAction(self.exitAction)

    " Установка действи для меню "
    # noinspection PyAttributeOutsideInit
    def setActions(self):
        self.exitAction = QAction('Выход', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.triggered.connect(app.exit)

        self.userAction = QAction('Пользователь', self)
        self.userAction.triggered.connect(self.user)
        self.userAction.setCheckable(True)
        self.userAction.setChecked(True)

        self.adminAction = QAction('Администратор', self)
        self.adminAction.triggered.connect(self.admin)
        self.adminAction.setCheckable(True)

        self.checkAction = QAction('Проверить выделенные', self)
        self.checkAction.triggered.connect(self.check)

        self.checkallAction = QAction('Проверить все', self)
        self.checkallAction.triggered.connect(self.checkAll)

        self.settingAction = QAction('Настройки', self)
        self.settingAction.triggered.connect(self.settings)

        self.histotyAction = QAction('История посещений', self)
        self.histotyAction.triggered.connect(self.history)

        self.addcurAction = QAction('Добавить руководителя в выбранные подключения', self)
        self.addcurAction.triggered.connect(self.addCurator)

        self.removecurAction = QAction('Убрать руководителя из выбранных подключений', self)
        self.removecurAction.triggered.connect(self.removeCurator)

        self.saveAction = QAction('Сохранить базу в локальный файл', self)
        self.saveAction.triggered.connect(self.saveDataToDb)

        self.showpswAction = QAction('Показывать пароли', self)
        self.showpswAction.triggered.connect(self.showPsw)
        self.showpswAction.setCheckable(True)

        self.findipAction = QAction('Поиск IP адреса', self)
        self.findipAction.triggered.connect(self.ipSearch)

        self.editFirmAction = QAction('Редактировать организации', self)
        self.editFirmAction.triggered.connect(self.editFirm)

        self.editCuratorAction = QAction('Редактировать кураторов', self)
        self.editCuratorAction.triggered.connect(self.editCurator)

    " Редактировать организации "
    def editFirm(self):
        ef = EditFirmsWidget(self)
        ef.show()

    def editCurator(self):
        ef = EditCuratorWidget(self)
        ef.show()

    " выгрузить базу в файл "
    def saveDataToDb(self):
        try:
            saveToDB()

            QMessageBox.information(self, 'Сохранение базы', 'База сохранена успешно')
        except:
            QMessageBox.information(self, 'Сохранение базы', 'База сохранена с ошибками')

    " Переключения в режим пользователя "
    def user(self):
        self.adminAction.setChecked(False)
        self.userAction.setChecked(True)
        global globaluser
        globaluser = 'user'
        self.setAll()
        connList.removeAction(connList.addconnAction)
        connList.removeAction(connList.editconnAction)
        connList.removeAction(connList.delconnAction)
        connList.removeAction(connList.propertiesAction)
        connList.removeAction(connList.copyAction)
        connList.removeAction(connList.pasteAction)
        folderTree.removeAction(folderTree.addfolderAction)
        # Изминение меню
        self.initUI()

        if kurator > 0 or opt.access_control:
            try:
                readdata()
                folderTree.setData()
                connList.setData((0,))
            except:
                pass

    " Переключение в режим администратора"
    def admin(self):
        text, ok = QInputDialog.getText(self, 'Авторизация', 'Введите пароль:',
                                        QLineEdit.Password, '', Qt.CoverWindow)
        psw = time.strftime("%H%M", time.localtime())
        psw = psw[::-1]
        if ok and text == psw:
            self.userAction.setChecked(False)
            self.adminAction.setChecked(True)
            global globaluser
            globaluser = 'admin'
            self.setAll()
            connList.addAction(connList.addconnAction)
            connList.addAction(connList.editconnAction)
            connList.addAction(connList.delconnAction)
            connList.addAction(connList.propertiesAction)
            connList.addAction(connList.copyAction)
            if globalclipboard != 0:
                connList.addAction(connList.pasteAction)
            folderTree.addAction(folderTree.addfolderAction)
            # Изминение меню
            self.clear()
            self.addMenu(self.prefMenu)
            self.prefMenu.addAction(self.userAction)
            self.prefMenu.addAction(self.adminAction)
            self.prefMenu.addSeparator()
            self.prefMenu.addAction(self.settingAction)
            self.prefMenu.addAction(self.showpswAction)

            self.addMenu(self.tasksMenu)
            self.tasksMenu.addAction(self.histotyAction)
            self.tasksMenu.addAction(self.addcurAction)
            self.tasksMenu.addAction(self.removecurAction)
            self.tasksMenu.addAction(self.findipAction)
            self.tasksMenu.addSeparator()
            self.tasksMenu.addAction(self.saveAction)
            self.tasksMenu.addSeparator()
            self.tasksMenu.addAction(self.checkAction)
            self.tasksMenu.addAction(self.checkallAction)

            self.addMenu(self.editMenu)
            self.editMenu.addAction(self.editFirmAction)
            self.editMenu.addAction(self.editCuratorAction)

            self.addAction(self.exitAction)

            if kurator > 0 or opt.access_control:
                try:
                    readdata(1)
                    folderTree.setData()
                    connList.setData((0,))
                except:
                    pass
        else:
            if ok:
                QMessageBox.warning(self, 'Неверный пароль',
                                'Введен неправильный пароль')
            self.adminAction.setChecked(False)

    " Установка общих настроек для администратора и пользователя"
    @staticmethod
    def setAll():
        connList.clearSelection()
        connList.setCurrentIndex(connList.model.index(connList.currentIndex().row(), 0))
        connList.addUserActions()
        folderTree.clearSelection()
        folderTree.setCurrentIndex(folderTree.currentIndex())
        folderTree.addUserActions()

    " Открыть настройки программы "
    def settings(self):
        sets = SettingsWidget(self)
        sets.show()

    " Показывать пароли "
    def showPsw(self):
        global show_passwords
        if self.showpswAction.isChecked():
            show_passwords = 1
        else:
            show_passwords = 0
        status_bar_text5.setText(' ' * 20)

    " Поиск по IP "
    def ipSearch(self):
        text, ok = QInputDialog.getText(self, 'Поиск IP', 'Введите IP:', QLineEdit.Normal, '', Qt.CoverWindow)
        if ok and text:
            found = []
            for item in conn_list:
                if item['IP'] == text:
                    found.append(item)
            if len(found) > 0:
                msgtext = text + ' пренадлежит следующим подключениям:\n'
                for item in found:
                    if item['Folder'] == 0:
                        fldtext = '\\'
                    else:
                        fldtext = fld_list[item['Folder']][2]
                    msgtext += item['Name'] + ' в папке ' + fldtext + '\n'
                QMessageBox.information(self, 'Поиск IP', msgtext)
            else:
                QMessageBox.information(self, 'Поиск IP', 'IP ' + text + ' не найден')

    " Добавить куратора "
    def addCurator(self):
        global curator_selected
        curator_selected.clear()
        sel_cur = SelectCurator(self)
        sel_cur.destroyed.connect(self.addcurAct)
        sel_cur.show()

    @staticmethod
    def addcurAct():
        global curator_selected, connList
        if len(curator_selected) > 0:
            cur = curator_selected[0]
            rows = set()
            for item in connList.selectedIndexes():  # Находим номера выдленных строк
                rows = rows | {item.row()}

            for row in rows:
                id_ = int(connList.model.index(row, connList.hidden_field).data())
                item = conn_list[id_]
                kur_list = set(item['Curator1'].split(','))
                kur_list = kur_list | {str(cur)}
                conn_list[id_]['Curator1'] = ','.join(kur_list)
                cur_text = ''
                for curator in kur_list:
                    for item in cur_list:
                        if item[0] == int(curator):
                            cur_text = cur_text + item[1] + ' '
                conn_list[id_]['Curator'] = cur_text
                # записываем в Базу
                query = "UPDATE connections SET curator='{}' WHERE id={}"
                query = query.format(conn_list[id_]['Curator1'], conn_list[id_]['ID'])
                writeToDb(query)

            connList.setData(folderTree.selFolders)

    # Удалить куратора
    def removeCurator(self):
        global curator_selected
        curator_selected.clear()
        sel_cur = SelectCurator(self)
        sel_cur.destroyed.connect(self.removecurAct)
        sel_cur.show()

    @staticmethod
    def removecurAct():
        global curator_selected, connList
        if len(curator_selected) > 0:
            cur = curator_selected[0]
            rows = set()
            for item in connList.selectedIndexes():  # Находим номера выдленных строк
                rows = rows | {item.row()}

            for row in rows:
                id_ = int(connList.model.index(row, connList.hidden_field).data())
                item = conn_list[id_]
                kur_list = set(item['Curator1'].split(','))
                kur_list = kur_list - {str(cur)}
                conn_list[id_]['Curator1'] = ','.join(kur_list)
                cur_text = ''
                for curator in kur_list:
                    for item in cur_list:
                        if item[0] == int(curator):
                            cur_text = cur_text + item[1] + ' '
                conn_list[id_]['Curator'] = cur_text
                # записываем в Базу
                query = "UPDATE connections SET curator='{}' WHERE id={}"
                query = query.format(conn_list[id_]['Curator1'], conn_list[id_]['ID'])
                writeToDb(query)

            connList.setData(folderTree.selFolders)

    " Открыть историю посещений "
    def history(self):
        sa = ShowHistoryWidget(self)
        sa.show()

    " Проверка доступности всех отмеченных "
    @staticmethod
    def checkAll():
        rows = []
        for item in conn_list:  # Находим отмеченные строки
            if item['ping'] == 1:
                rows.append(item)

        addlock = threading.Lock()
        threads = []
        for row in rows:  # Запускаем в поток, передаем элемент
            thread = threading.Thread(target=check_port, args=(row, addlock))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

        showNotDone()
        check_not_done.clear()

    " Проверка доступности выделенных "
    @staticmethod
    def check():
        rows = set()
        for item in connList.selectedIndexes():         # Находим номера выдленных строк
            rows = rows | {item.row()}

        addlock = threading.Lock()
        threads = []
        for row in rows:                            # Запускаем в поток, передаем индекс
            thread = threading.Thread(target=check_port,
                    args=(conn_list[int(connList.model.index(row, connList.hidden_field).data())],
                          addlock))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

        showNotDone()
        check_not_done.clear()


"""
    Отображает центальный экран (дерево папок и список)
"""


class MainWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.editWnd = None
        self.initUI()

    def initUI(self):
        global connList, folderTree
        connList = MyList()
        connList.setFrameShape(QFrame.StyledPanel)

        folderTree = MyTree()
        folderTree.setFrameShape(QFrame.StyledPanel)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(folderTree)
        splitter.addWidget(connList)
        splitter.setSizes([100, 600])

        hbox = QVBoxLayout()
        hbox.setSpacing(0)
        hbox.setContentsMargins(3, 0, 3, 0)
        hbox.addWidget(splitter)

        self.setLayout(hbox)


"""
    Главное окно программы
"""


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.timer_checkini = QTimer()
        self.timer_sendlogs = QTimer()
        self.initUI()
        style_sheet = """
            QTreeView {
                alternate-background-color: #f3ffef;
            }"""
        self.setStyleSheet(style_sheet)

    def initUI(self):
        global status_bar_text1, status_bar_text2, status_bar_text3, status_bar_text4, status_bar_text5, \
            status_bar_text6, toolbar

        statusbar = QStatusBar()
        self.setStatusBar(statusbar)
        status_bar_text1 = QLabel('')
        status_bar_text2 = QLabel('')
        status_bar_text3 = QLabel('')
        status_bar_text4 = QLabel('')
        status_bar_text5 = QLabel(' '*20)
        status_bar_text6 = QLabel(' '*20)
        statusbar.addWidget(status_bar_text1)
        statusbar.addWidget(status_bar_text2)
        statusbar.addWidget(status_bar_text3)
        statusbar.addWidget(status_bar_text4)
        statusbar.addWidget(status_bar_text5)
        statusbar.addWidget(status_bar_text6)

        my_menu = MyMenu()
        self.setMenuBar(my_menu)

        self.setCentralWidget(MainWidget())

        toolbar = MyToolBar()
        self.addToolBar(toolbar)

        ftime = datetime.datetime.fromtimestamp(ini_modified)
        status_bar_text1.setText('    База изменена: ' + ftime.strftime("%d-%m-%Y %H:%M:%S") + '\t')
        status_bar_text3.setText('    Комп`ютер: ' + comp_name + '\tПользователь: ' + user_name + '\t')

        # Таймер для проверки даты изменения ини файла
        self.timer_checkini.timeout.connect(self.checkIni)
        self.timer_checkini.start(5000)

        if opt.need_send_admin:
            sendAdminData()
            self.timer_sendlogs.timeout.connect(sendAdminData)
            self.timer_sendlogs.start(opt.admin_timeout*60000)

        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon('img\\mainwin.png'))
        self.setWindowTitle('Клиент для Radmin & VNC & RDP Вер. ' + version_prog)
        writeToLog('Программа запущена')
        self.show()

    " Действия для таймера проверки ini "
    @staticmethod
    def checkIni():
        threading.Thread(target=check_ini).start()

    def closeEvent(self, event):
        writeToLog('Программа закрыта')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setKeyboardInputInterval(1000)
    wnd = win32gui.FindWindow(None, 'Клиент для Radmin & VNC & RDP Вер. ' + version_prog)
    if wnd > 0 and opt.run_again:
        QMessageBox.warning(None, 'Повторный запуск', 'Другая копия этой программы уже запущена!')
        app.exit()
    else:
        ex = MainWindow()
        ex.show()
        sys.exit(app.exec_())
