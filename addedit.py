import threading
from func import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


"""
    Отображает окно редактирования\добавления
"""


class AddEditWidget(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window)
        if addedit[0]:
            self.item = conn_list[addedit[1]]
        self.panel1 = QFrame()
        self.panel2 = QFrame()
        self.panel3 = QFrame()
        self.panel4 = QFrame()
        self.panel5 = QFrame()
        self.panel6 = QFrame()
        self.nameEdit = QLineEdit(self.panel1)
        self.ipEdit = QLineEdit(self.panel1)
        self.portEdit = QLineEdit(self.panel1)
        self.colourCombo = QComboBox(self.panel1)
        self.checkCombo = QCheckBox('Проверять доступность', self.panel1)
        self.actionCombo = QComboBox(self.panel1)

        self.hasproxyCheck = QCheckBox('Подключится через прокси сервер', self.panel2)
        self.proxyList = ProxyListView(self.panel2)

        self.autopassCombo = QComboBox(self.panel3)
        self.raCombo = QComboBox(self.panel3)
        self.loginEdit = QLineEdit(self.panel3)
        self.passEdit = QLineEdit(self.panel3)
        self.passCheck = QCheckBox('Отобразить пароль', self.panel3)

        self.adrEdit = QLineEdit(self.panel4)
        self.telEdit = QLineEdit(self.panel4)
        self.timeEdit = QLineEdit(self.panel4)
        self.firmCombo = QComboBox(self.panel4)
        self.commentEdit = QLineEdit(self.panel4)

        self.curatorList = CurListView(self.panel5)

        self.winEdit = QLineEdit(self.panel6)
        self.providerEdit = QTextEdit(self.panel6)

        self.okButton = QPushButton("OK")
        self.cancelButton = QPushButton("Закрыть")
        self.initUI()

    " создание формы и панелей"
    def initUI(self):
        self.okButton.clicked.connect(self.saveAndExit)

        self.cancelButton.clicked.connect(self.closeWin)
        
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.setContentsMargins(10, 0, 10, 10)
        hbox.addWidget(self.okButton)
        hbox.addWidget(self.cancelButton)

        self.panel1.setFixedSize(400, 160)

        panel = QTabWidget(self)
        panel.addTab(self.panel1, 'Общие')
        panel.addTab(self.panel2, 'Прокси')
        panel.addTab(self.panel3, 'Пароль')
        panel.addTab(self.panel4, 'Контакты')
        panel.addTab(self.panel5, 'Доступ')
        panel.addTab(self.panel6, 'Тех. инфо ')
        panel.setStyleSheet("QComboBox { background-color: #ffffff; }")
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(panel)
        vbox.addLayout(hbox)

        self.setPanelItems()
        
        self.setLayout(vbox)
        self.setFixedSize(406, 225)
        if addedit[0] == 0:
            fld_name = ''
            for fld in folder_list:
                if int(fld[0]) == addedit[1]:
                    fld_name = fld[2]
            self.setWindowTitle('Новое соединение ( ' + fld_name + ' )')
        else:
            self.setWindowTitle('Свойства соединения: ' +
                                conn_list[addedit[1]]['Name'])
        self.setWindowModality(Qt.WindowModal)
        self.setAttribute(Qt.WA_DeleteOnClose, True)

    " заполнение панелей "
    def setPanelItems(self):
        #####################################################
        #                   Панель 1                        #
        #####################################################
        self.panel1.setStyleSheet("QFrame { background-color: #f3f3f3; border-color: #f3f3f3; }")
    
        QLabel('Название', self.panel1).move(10, 19)
        QLabel('IP адрес', self.panel1).move(10, 56)
        QLabel('Порт', self.panel1).move(280, 56)
        QLabel('Цветов', self.panel1).move(10, 93)
        QLabel('Действие по умолчанию (двойной клик)',
               self.panel1).move(10, 130)

        self.nameEdit.move(75, 17)
        self.nameEdit.setFixedWidth(315)
        self.nameEdit.setFocus()

        self.ipEdit.move(75, 54)
        self.ipEdit.setFixedWidth(185)

        self.portEdit.move(320, 54)
        self.portEdit.setFixedWidth(70)
        self.portEdit.setText('5000')

        self.colourCombo.move(75, 90)
        self.colourCombo.setFixedHeight(22)
        self.colourCombo.addItems(['1 бит', '2 бита', '4 бита',
                        '8 бит', '16 бит', '24 бита'])
        self.colourCombo.setCurrentIndex(3)

        self.checkCombo.move(240, 90)

        self.actionCombo.move(240, 127)
        self.actionCombo.setFixedWidth(150)
        self.actionCombo.setFixedHeight(22)
        self.actionCombo.addItems(['Полный контроль', 'Просмотр', 
                        'Передача файлов'])
        #####################################################
        #                   Панель 2                        #
        #####################################################

        self.panel2.setStyleSheet("QFrame { background-color: #f3f3f3; border-color: #f3f3f3; }")

        self.hasproxyCheck.move(5, 5)
        self.hasproxyCheck.stateChanged.connect(self.hasproxyChecked)

        self.proxyList.move(5, 25)

        self.hasproxyCheck.toggle()
        self.hasproxyCheck.setCheckState(Qt.Unchecked)
        if addedit[0] == 1 and conn_list[addedit[1]]['HasProxy'] == 1:
            self.hasproxyCheck.setCheckState(Qt.Checked)

        #####################################################
        #                   Панель 3                        #
        #####################################################
        self.panel3.setStyleSheet(
            "QFrame { background-color: #f3f3f3; border-color: #f3f3f3; }")

        QLabel('Режим автопароля', self.panel3).move(20, 18)
        QLabel('Версия Radmin', self.panel3).move(20, 51)
        QLabel('Логин (для Radmin 3)', self.panel3).move(20, 84)
        QLabel('Пароль', self.panel3).move(20, 117)

        self.autopassCombo.move(200, 16)
        self.autopassCombo.setFixedSize(180, 22)
        self.autopassCombo.addItems(['Вручную', 'Автоматически'])
        self.autopassCombo.setCurrentIndex(1)

        self.raCombo.move(200, 49)
        self.raCombo.setFixedSize(180, 22)
        self.raCombo.addItems(['Radmin 2', 'Radmin 3', 'VNC', 'RDP'])
        self.raCombo.setCurrentIndex(1)

        self.loginEdit.move(200, 82)
        self.loginEdit.setFixedSize(180, 20)

        self.passEdit.move(200, 115)
        self.passEdit.setFixedSize(180, 20)
        self.passEdit.setEchoMode(QLineEdit.Password)

        self.passCheck.move(200, 140)
        self.passCheck.stateChanged.connect(self.passChecked)
        #####################################################
        #                   Панель 4                        #
        #####################################################
        self.panel4.setStyleSheet(
            "QFrame { background-color: #f3f3f3; border-color: #f3f3f3; }")
        QLabel('Адресс:', self.panel4).move(15, 15)
        QLabel('Телефон:', self.panel4).move(15, 45)
        QLabel('Время работы:', self.panel4).move(15, 75)
        QLabel('Юр. лицо:', self.panel4).move(15, 105)
        QLabel('Заметка:', self.panel4).move(15, 135)

        self.adrEdit.move(100, 13)
        self.adrEdit.setFixedSize(280, 20)

        self.telEdit.move(100, 43)
        self.telEdit.setFixedSize(280, 20)

        self.timeEdit.move(100, 73)
        self.timeEdit.setFixedSize(280, 20)

        self.firmCombo.move(100, 103)
        self.firmCombo.setFixedSize(280, 22)
        firms = []
        for item in company_list:
            firms.append(item[1])
        self.firmCombo.addItems(firms)

        self.commentEdit.move(100, 133)
        self.commentEdit.setFixedSize(280, 20)
        #####################################################
        #                   Панель 5                        #
        #####################################################
        self.panel5.setStyleSheet(
            "QFrame { background-color: #f3f3f3; border-color: #f3f3f3; }")
        self.curatorList.move(5, 5)
        #####################################################
        #                   Панель 6                        #
        #####################################################
        self.panel6.setStyleSheet("QFrame { background-color: #f3f3f3; border-color: #f3f3f3; }")
        self.panel6.setStyleSheet("QTextEdit { background-color: #ffffff; }")

        QLabel('ОС:', self.panel6).move(15, 15)
        QLabel('Провайдер:', self.panel6).move(15, 45)
        self.winEdit.move(50, 13)
        self.winEdit.setFixedSize(340, 20)

        self.providerEdit.move(10, 65)
        self.providerEdit.setFixedSize(380, 85)
        #####################################################
        #       Заполнение в режиме редактирования          #
        #####################################################
        if addedit[0] == 1:
            self.nameEdit.setText(self.item['Name'])
            self.ipEdit.setText(self.item['IP'])
            self.portEdit.setText(self.item['port'])
            self.colourCombo.setCurrentIndex(self.item['colour']-1)
            self.actionCombo.setCurrentIndex(self.item['DefAct'])
            if self.item['ping']:
                self.checkCombo.setChecked(True)

            self.autopassCombo.setCurrentIndex(self.item['AutoPass'])
            self.raCombo.setCurrentIndex(self.item['RA']-2)
            self.loginEdit.setText(self.item['User'])
            self.passEdit.setText(self.item['psw'])

            self.adrEdit.setText(self.item['Adress'])
            self.telEdit.setText(self.item['Tel'])
            self.timeEdit.setText(self.item['WorkTime'])
            self.winEdit.setText(self.item['OS'])
            self.firmCombo.setCurrentIndex(self.item['Firm1'])
            self.commentEdit.setText(self.item['Coment'])
            self.providerEdit.setText(self.item['Provider'])

    " сохранить и выйти "
    def saveAndExit(self):
        data_correct = True
        if len(self.nameEdit.text()) == 0:
            data_correct = False
        if len(self.ipEdit.text()) == 0:
            data_correct = False
        if len(self.portEdit.text()) == 0:
            data_correct = False
        proxy_item = 0
        if self.hasproxyCheck.isChecked():
            if len(self.proxyList.selectedIndexes()) > 0:
                index = self.proxyList.currentIndex().row()
                if index > self.proxyList.folderCount - 1:
                    proxy_item = self.proxyList.item_list[index -
                                                   self.proxyList.folderCount]
                else:
                    data_correct = False
            else:
                data_correct = False

        if data_correct:
            item = dict()
            item['Name'] = self.nameEdit.text()
            item['IP'] = self.ipEdit.text()
            item['port'] = self.portEdit.text()
            item['colour'] = self.colourCombo.currentIndex()+1
            item['DefAct'] = self.actionCombo.currentIndex()
        
            if self.hasproxyCheck.isChecked():
                item['HasProxy'] = 1
                item['Proxy'] = str(proxy_item['ID'])
            else:
                item['HasProxy'] = 0
                item['Proxy'] = ''

            item['AutoPass'] = self.autopassCombo.currentIndex()
            item['RA'] = self.raCombo.currentIndex()+2
            item['User'] = self.loginEdit.text()
            item['psw'] = self.passEdit.text()
                
            item['Adress'] = self.adrEdit.text()
            item['Tel'] = self.telEdit.text()
            item['WorkTime'] = self.timeEdit.text()
            item['Firm1'] = company_list[self.firmCombo.currentIndex()][0]
            item['Firm'] = company_list[self.firmCombo.currentIndex()][1]
            item['Coment'] = self.commentEdit.text()
            if self.checkCombo.isChecked():
                item['ping'] = 1
            else:
                item['ping'] = 0

            cur_lst = ''
            cur_full_list = ''
            for cur in self.curatorList.selectedIndexes():
                cur_lst += str(cur_list[cur.row()][0]) + ','
                cur_full_list += cur.data() + ' '
            item['Curator1'] = cur_lst[:-1]
            item['Curator'] = cur_full_list[:-1]
            item['OS'] = self.winEdit.text()
            item['Provider'] = self.providerEdit.toPlainText()

            if addedit[0]:
                item['Folder'] = self.item['Folder']
                item['ID'] = self.item['ID']
                item['ID1'] = self.item['ID1']
            else:
                item['Folder'] = addedit[1]
                item['ID'] = getMaxListNum()+1
                item['ID1'] = str(len(conn_list))
            if addedit[0]:
                id_ = 0
                for i in conn_list:
                    if i['ID1'] == str(addedit[1]):
                        id_ = i['ID']
                        break
                conn_list[addedit[1]] = item

                q_text = """UPDATE connections SET id={}, name='{}', ip='{}', port='{}', auto_pass={}, psw='{}', ra={}, 
                colour={}, adress='{}', has_proxy={}, proxy='{}', def_act={}, tel='{}', coment='{}', user_name='{}', 
                work_time='{}', curator='{}', firm={}, ping={}, folder={}, os='{}', provider='{}' WHERE ID={}"""
                query = q_text.format(str(item['ID']), item['Name'], item['IP'], item['port'], str(item['AutoPass']),
                                      setPsw(item['psw'], -5), str(item['RA']), str(item['colour']), item['Adress'],
                                      str(item['HasProxy']), item['Proxy'], str(item['DefAct']), item['Tel'],
                                      item['Coment'], item['User'], item['WorkTime'], item['Curator1'],
                                      str(item['Firm1']), str(item['ping']), str(item['Folder']), item['OS'],
                                      item['Provider'], str(id_))

            else:
                conn_list.append(item)

                q_text = """INSERT INTO connections(id, name, ip, port, auto_pass, psw, ra, colour, adress, has_proxy, 
                proxy, def_act, tel, coment, user_name, work_time, curator, firm, ping, folder, os, provider) 
                VALUES({}, '{}', '{}', '{}', {}, '{}', {}, {}, '{}', {}, '{}', {}, '{}', '{}', '{}', '{}', '{}', {}, {}, 
                {}, '{}', '{}')"""
                query = q_text.format(str(item['ID']), item['Name'], item['IP'], item['port'], str(item['AutoPass']),
                                      setPsw(item['psw'], -5), str(item['RA']), str(item['colour']), item['Adress'],
                                      str(item['HasProxy']), item['Proxy'], str(item['DefAct']), item['Tel'],
                                      item['Coment'], item['User'], item['WorkTime'], item['Curator1'],
                                      str(item['Firm1']), str(item['ping']), str(item['Folder']), item['OS'],
                                      item['Provider'])
            writeToDb(query)

            addedit[2] = '1'
            self.close()
        else:
            QMessageBox.warning(self, 'Некорректные данные',
""" \t\tВведены некоректные данные\n
    Поля 'Название', 'IP адрес' и 'Порт' должны быть заполнены
              Если выбрана опция подключится через прокси,
               то в списке ниже должен быть выбран прокси""")

    " при изменении галочки: показывать пароль"
    def passChecked(self, state):
        if state == Qt.Checked:
            self.passEdit.setEchoMode(QLineEdit.Normal)
        else:
            self.passEdit.setEchoMode(QLineEdit.Password)

    " при изменении галочки: есть прокси "
    def hasproxyChecked(self, state):
        if state == Qt.Checked:
            self.proxyList.setDisabled(False)
        else:
            self.proxyList.setDisabled(True)

    " выход по ескейпу "
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    " закрытие окна"
    def closeWin(self):
        self.close()


"""
    Отображает дерево для выбора прокси подключения
"""


class ProxyListView(QListView):

    def __init__(self, parent):
        super().__init__(parent)
        self.folders = []
        self.model = QStandardItemModel(self)
        self.folder = 0
        self.folderCount = 0
        self.item_list = []
        self.initUI()

    " начальная настройки и выбор "
    def initUI(self):
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setStyleSheet("QListView { background-color: #ffffff;}")
        self.setFixedSize(390, 130)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setWrapping(True)

        self.setModel(self.model)
        item = 0
        proxy_item = 0
        if addedit[0] == 0:
            self.folder = 0
        else:
            item = conn_list[addedit[1]]
            if item['HasProxy'] == 1:
                proxy_item = getProxyItem(item)
                self.folder = proxy_item['Folder']
            else:
                self.folder = item['Folder']

        self.setData()

        if addedit[0] == 1:
            if item['HasProxy'] == 1:
                for i in range(len(self.item_list)):
                    if self.item_list[i] == proxy_item:
                        self.setCurrentIndex(self.model.index(self.folderCount + i, 0))

    " заполнение "
    def setData(self):
        self.model.clear()
        self.folders.clear()
        row_count = 0
        if self.folder > 0:
            lvlup_item = QStandardItem(' .. ')
            self.model.appendRow(lvlup_item)
            row_count += 1
            self.folders.append(['0', '0', '0'])
        for f in folder_list:
            if int(f[1]) == self.folder:
                fld = QStandardItem(f[2])
                fld.setIcon(QIcon('img\\folder.png'))
                self.model.appendRow(fld)
                self.folders.append(f)
                row_count += 1

        self.folderCount = row_count
        self.item_list = getDisplayList((self.folder,))

        for i in self.item_list:
            itm = QStandardItem(i['Name'])
            itm.setIcon(QIcon('img\\item.png'))
            self.model.appendRow(itm)
            row_count += 1
        self.clearSelection()

    " при двойном клике мыши"
    def mouseDoubleClickEvent(self, e):
        sel_index = self.selectedIndexes()[0].row()
        if sel_index < self.folderCount:
            if self.folder > 0 and sel_index == 0:
                for f in folder_list:
                    if int(f[0]) == self.folder:
                        self.folder = int(f[1])
            else:
                self.folder = int(self.folders[sel_index][0])
        self.setData()


"""
    Отображает список кураторов
"""


class CurListView(QListView):

    def __init__(self, parent):
        super().__init__(parent)
        self.model = QStandardItemModel(self)
        self.initUI()

    " соззание и заполнение списка "
    def initUI(self):
        self.setFixedSize(390, 150)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setStyleSheet("QListView { background-color: #ffffff;}")
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWrapping(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.setModel(self.model)
        # Создание списка
        for curator in cur_list:
            self.model.appendRow(QStandardItem(curator[1]))

        # Установка кураторов в режиме редактирования
        selection_model = self.selectionModel()

        if addedit[0] == 1:
            curators = conn_list[addedit[1]]['Curator1'].split(',')
            for curator in curators:
                for id_, item in enumerate(cur_list):
                    if item[0] == int(curator):
                        selection_model.select(self.model.index(id_, 0), QItemSelectionModel.Toggle)
        else:
            self.setCurrentIndex(self.model.index(0, 0))

    " при изминении "
    def selectionChanged(self, selection1, selection2):
        if len(self.selectedIndexes()) == 0:
            self.setCurrentIndex(self.model.index(self.currentIndex().row(), 0))
        super().selectionChanged(selection1, selection2)


"""
    Отображает окно быстрого подключения
"""


class FastConnWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window)
        self.panel = QFrame()
        self.proxyList = ProxyListView(self.panel)
        self.hasproxyCheck = QCheckBox('Подключится через прокси сервер',
                                       self.panel)
        self.raCombo = QComboBox(self.panel)
        self.actionCombo = QComboBox(self.panel)
        self.portEdit = QLineEdit(self.panel)
        self.ipEdit = QLineEdit(self.panel)
        self.cancelButton = QPushButton("Закрыть")
        self.okButton = QPushButton("Подключится")
        self.initUI()

    " создание формы и начальные установки"
    def initUI(self):
        self.okButton.clicked.connect(self.fastconAction)

        self.cancelButton.clicked.connect(self.closeWin)
        
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.setContentsMargins(10, 0, 10, 10)
        hbox.addWidget(self.okButton)
        hbox.addWidget(self.cancelButton)

        self.panel.setFrameShadow(QFrame.Raised)
        self.panel.setFrameShape(QFrame.Panel)
        self.panel.setFixedSize(410, 245)
        self.setPanelItems()
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.panel)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        
        self.setFixedSize(410, 285)
        self.setWindowTitle('Быстрое подключение')
        self.setWindowModality(Qt.WindowModal)

    " заполнение формы "
    def setPanelItems(self):
        self.panel.setStyleSheet("QComboBox { background-color: #ffffff; }")
        
        QLabel('IP адрес', self.panel).move(10, 15)
        QLabel('Порт', self.panel).move(250, 15)
        QLabel('Действие', self.panel).move(10, 50)
        QLabel('Radmin', self.panel).move(250, 50)

        self.ipEdit.move(75, 13)
        self.ipEdit.setFixedWidth(155)

        self.portEdit.move(310, 13)
        self.portEdit.setFixedWidth(85)
        self.portEdit.setText('5000')

        self.actionCombo.move(75, 47)
        self.actionCombo.setFixedSize(157, 22)
        self.actionCombo.addItems(['Полный контроль', 'Просмотр', 
                        'Передача файлов'])

        self.raCombo.move(310, 47)
        self.raCombo.setFixedSize(87, 22)
        self.raCombo.addItems(['Radmin 2', 'Radmin 3'])
        self.raCombo.setCurrentIndex(1)

        self.hasproxyCheck.move(10, 80)
        self.hasproxyCheck.stateChanged.connect(self.hasproxyChecked)

        self.proxyList.move(10, 105)

        self.hasproxyCheck.toggle()
        self.hasproxyCheck.setCheckState(Qt.Unchecked)

    " при изменении состояния галочки"
    def hasproxyChecked(self, state):
        if state == Qt.Checked:
            self.proxyList.setDisabled(False)
        else:
            self.proxyList.setDisabled(True)

    " подключение по ентеру и закрытие по ескейпу"
    def keyPressEvent(self, e):
        if e.key() in {Qt.Key_Return, Qt.Key_Enter}:        
            self.fastconAction()
        elif e.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(e)

    " подключение "
    def fastconAction(self):
        data_correct = True
        proxy_item = 0
        if len(self.ipEdit.text()) == 0:
            data_correct = False
        if len(self.portEdit.text()) == 0:
            data_correct = False
        if self.hasproxyCheck.isChecked():
            if len(self.proxyList.selectedIndexes()) > 0:
                index = self.proxyList.currentIndex().row()
                if index > self.proxyList.folderCount - 1:
                    proxy_item = self.proxyList.item_list[index -
                                                   self.proxyList.folderCount]
                else:
                    data_correct = False
            else:
                data_correct = False
        if data_correct:
            item = dict()
            item['Name'] = 'Fast Connect'
            item['IP'] = self.ipEdit.text()
            item['port'] = self.portEdit.text()
            item['colour'] = 4
            item['DefAct'] = self.actionCombo.currentIndex()
            item['User'] = ''
            item['psw'] = ''
        
            if self.hasproxyCheck.isChecked():
                item['HasProxy'] = 1
                # item['Proxy'] = str(proxy_item['Folder']) + '.' + str(proxy_item['ID'])
                item['Proxy'] = str(proxy_item['ID'])
            else:
                item['HasProxy'] = 0
                item['Proxy'] = ''

            item['AutoPass'] = 0
            item['RA'] = self.raCombo.currentIndex()+2
            threading.Thread(target=conn, args=(item, 6)).start()
            self.close()
        else:
            QMessageBox.warning(self, 'Некорректные данные',
""" \t      Введены некоректные данные\n
    Поля 'IP адрес' и 'Порт' должны быть заполнены
     Если выбрана опция подключится через прокси,
      то в списке ниже должен быть выбран прокси""")

    " закрытие "
    def closeWin(self):
        self.close()


"""
    Отображает окно настроек
"""


class SettingsWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window)
        self.panel = QFrame()
        self.datapathEdit = QLineEdit(self.panel)
        self.dataportEdit = QLineEdit(self.panel)

        self.admhostEdit = QLineEdit(self.panel)
        self.admportEdit = QLineEdit(self.panel)
        self.admtimeEdit = QLineEdit(self.panel)
        self.runcontrolCheck = QCheckBox('Контроль повторного запуска', self.panel)
        self.accessCheck = QCheckBox('Контроль доступа (нужен перезапуск программы)', self.panel)
        self.localdbCheck = QCheckBox('Использовать локальную базу (нужен перезапуск программы)', self.panel)
        self.senddataCheck = QCheckBox('Отправлять данные на сервер (нужен перезапуск программы)', self.panel)
        self.cancelButton = QPushButton("Закрыть")
        self.okButton = QPushButton("Сохранить")
        self.initUI()

    " создание формы "
    def initUI(self):
        self.okButton.clicked.connect(self.okAction)

        self.cancelButton.clicked.connect(self.closeWin)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.setContentsMargins(10, 0, 10, 10)
        hbox.addWidget(self.okButton)
        hbox.addWidget(self.cancelButton)

        self.panel.setFrameShadow(QFrame.Raised)
        self.panel.setFrameShape(QFrame.Panel)
        self.panel.setFixedSize(410, 245)
        self.setPanelItems()
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.panel)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.setFixedSize(410, 285)
        self.setWindowTitle('Настройки')
        self.setWindowModality(Qt.WindowModal)

    " заполнение формы элементами "
    def setPanelItems(self):
        self.runcontrolCheck.move(10, 10)

        self.accessCheck.move(10, 35)

        self.localdbCheck.move(10, 60)

        QLabel('Адресс базы данных:', self.panel).move(12, 90)
        QLabel('Порт:', self.panel).move(310, 90)

        self.datapathEdit.move(130, 87)
        self.datapathEdit.setFixedWidth(170)

        self.dataportEdit.move(350, 87)
        self.dataportEdit.setFixedWidth(45)

        line = QFrame(self.panel)
        line.setGeometry(QRect(5, 120, 400, 4))
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        self.senddataCheck.move(10, 135)
        self.senddataCheck.stateChanged.connect(self.senddataChecked)

        QLabel('Сервер:', self.panel).move(12, 165)
        QLabel('Порт:', self.panel).move(190, 165)
        QLabel('Интервал:', self.panel).move(300, 165)

        self.admhostEdit.move(60, 162)
        self.admhostEdit.setFixedWidth(120)

        self.admportEdit.move(225, 162)
        self.admportEdit.setFixedWidth(65)

        self.admtimeEdit.move(360, 162)
        self.admtimeEdit.setFixedWidth(35)

        self.setSettings()

    " заполнение элементов данными "
    def setSettings(self):
        if opt.run_again:
            self.runcontrolCheck.setCheckState(Qt.Checked)
        else:
            self.runcontrolCheck.setCheckState(Qt.Unchecked)

        if opt.access_control:
            self.accessCheck.setCheckState(Qt.Checked)
        else:
            self.accessCheck.setCheckState(Qt.Unchecked)

        if opt.use_local_db:
            self.localdbCheck.setCheckState(Qt.Checked)
        else:
            self.localdbCheck.setCheckState(Qt.Unchecked)

        self.datapathEdit.setText(opt.database_path)
        self.dataportEdit.setText(opt.database_port)

        if opt.need_send_admin:
            self.senddataCheck.setCheckState(Qt.Checked)
        else:
            self.senddataCheck.setCheckState(Qt.Unchecked)
            self.admhostEdit.setDisabled(True)
            self.admportEdit.setDisabled(True)
            self.admtimeEdit.setDisabled(True)
        self.admhostEdit.setText(opt.admin_host)
        self.admportEdit.setText(str(opt.admin_port))
        self.admtimeEdit.setText(str(opt.admin_timeout))

    " при изменении состояния галочки отправки данных "
    def senddataChecked(self, state):
        if state == Qt.Checked:
            self.admhostEdit.setDisabled(False)
            self.admportEdit.setDisabled(False)
            self.admtimeEdit.setDisabled(False)
        else:
            self.admhostEdit.setDisabled(True)
            self.admportEdit.setDisabled(True)
            self.admtimeEdit.setDisabled(True)

    " выход по ескейпу "
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    " сохранение изменений и выход "
    def okAction(self):
        global opt
        if self.runcontrolCheck.isChecked():
            opt.run_again = 1
        else:
            opt.run_again = 0

        if self.accessCheck.isChecked():
            opt.access_control = 1
        else:
            opt.access_control = 0

        if self.localdbCheck.isChecked():
            opt.use_local_db = 1
        else:
            opt.use_local_db = 0

        opt.database_path = self.datapathEdit.text()
        opt.database_port = self.dataportEdit.text()

        if self.senddataCheck.isChecked():
            opt.need_send_admin = 1
        else:
            opt.need_send_admin = 0

        opt.admin_host = self.admhostEdit.text()
        opt.admin_port = self.admportEdit.text()
        opt.admin_timeout = self.admtimeEdit.text()

        writeLocalIni()
        self.close()

    " закрытие окна "
    def closeWin(self):
        self.close()


"""
    Отображает окно редактирования организаций
"""


class EditFirmsWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window)
        self.panel = QFrame()
        self.cancelButton = QPushButton("Закрыть")
        self.listView = QListView(self.panel)
        self.listModel = QStandardItemModel()
        self.firmEdit = QLineEdit(self.panel)
        self.renameBtn = QPushButton('Переименовать', self.panel)
        self.delBtn = QPushButton('Удалить', self.panel)
        self.addBtn = QPushButton('Добавить', self.panel)
        self.index = 0
        self.initUI()

    " создание формы "
    def initUI(self):

        self.cancelButton.clicked.connect(self.closeWin)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.setContentsMargins(10, 10, 10, 10)
        hbox.addWidget(self.cancelButton)

        self.panel.setFrameShadow(QFrame.Raised)
        self.panel.setFrameShape(QFrame.Panel)
        self.panel.setFixedSize(410, 245)
        self.setPanelItems()
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.panel)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.setFixedSize(410, 285)
        self.setWindowTitle('Редактирование организаций')
        self.setWindowModality(Qt.WindowModal)

    " заполнение формы элементами "
    def setPanelItems(self):
        self.listView.move(10, 15)
        self.listView.setFixedSize(200, 220)
        self.listView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listView.setModel(self.listModel)
        self.listView.selectionModel().selectionChanged.connect(self.listSelChange)
        self.fillList()

        self.firmEdit.move(225, 15)
        self.firmEdit.setFixedWidth(170)

        self.renameBtn.move(225, 50)
        self.renameBtn.setFixedWidth(170)
        self.renameBtn.clicked.connect(self.renameAct)

        self.delBtn.move(225, 85)
        self.delBtn.setFixedWidth(170)
        self.delBtn.clicked.connect(self.delAct)

        self.addBtn.move(225, 208)
        self.addBtn.setFixedWidth(170)
        self.addBtn.clicked.connect(self.addAct)

        self.listView.setCurrentIndex(self.listModel.index(0, 0))

    def fillList(self):
        self.listModel.clear()
        for firm in company_list:
            self.listModel.appendRow(QStandardItem(firm[1]))

    def listSelChange(self):
        self.firmEdit.setText(self.listView.currentIndex().data())
        self.index = self.listView.currentIndex().row()

    def renameAct(self):
        company_list[self.index] = (company_list[self.index][0], self.firmEdit.text())
        self.fillList()
        self.listView.setCurrentIndex(self.listModel.index(self.index, 0))
        # записываем в базу
        query = "UPDATE firms SET name='" + self.firmEdit.text() + "' WHERE id=" + str(company_list[self.index][0])
        writeToDb(query)

    def delAct(self):
        find = False
        for item in conn_list:
            if item['Firm1'] == company_list[self.index][0]:
                find = True
                break
        if not find:
            # записываем в базу
            query = "DELETE FROM firms WHERE id=" + str(company_list[self.index][0])
            writeToDb(query)

            company_list.pop(self.index)
            self.fillList()
            self.listView.setCurrentIndex(self.listModel.index(0, 0))
        else:
            QMessageBox.warning(self, 'Ошибка удаления',
                                'Запрещено удалять организацию, которая используется в подключениях')

    def addAct(self):
        text, ok = QInputDialog.getText(self, 'Новая организация', 'Введите название:', QLineEdit.Normal, '',
                                        Qt.CoverWindow)
        if ok and text:
            max_firm = 0
            for i in company_list:
                if i[0] > max_firm:
                    max_firm = i[0]
            company_list.append((max_firm + 1, text))
            self.fillList()
            # записываем в базу
            query = "INSERT INTO firms (id, name) VALUES (" + str(max_firm + 1) + ",'" + text + "')"
            writeToDb(query)

    " выход по ескейпу "
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    " закрытие окна "
    def closeWin(self):
        self.close()


"""
    Отображает окно редактирования кураторов
"""


class EditCuratorWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window)
        self.panel = QFrame()
        self.cancelButton = QPushButton("Закрыть")

        self.curView = QListView(self.panel)
        self.nameEdit = QLineEdit(self.panel)
        self.userEdit = QLineEdit(self.panel)
        self.compEdit = QLineEdit(self.panel)
        self.listView = QListView(self.panel)
        self.listModel = QStandardItemModel()
        self.curModel = QStandardItemModel()

        self.renameBtn = QPushButton('Сохранить', self.panel)
        self.delBtn = QPushButton('Удалить', self.panel)
        self.addBtn = QPushButton('Добавить', self.panel)
        self.index = 0

        self.initUI()

    " заполнение формы элементами "
    def initUI(self):
        self.cancelButton.clicked.connect(self.closeWin)
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.setContentsMargins(10, 10, 10, 10)
        hbox.addWidget(self.cancelButton)

        self.panel.setFrameShadow(QFrame.Raised)
        self.panel.setFrameShape(QFrame.Panel)
        self.panel.setFixedSize(460, 290)
        self.setPanelItems()
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.panel)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.setFixedSize(460, 330)
        self.setWindowTitle('Редактирование кураторов')
        self.setWindowModality(Qt.WindowModal)

    " заполнение панели элементами "
    def setPanelItems(self):
        self.listView.move(170, 105)
        self.listView.setFixedSize(280, 140)
        self.listView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listView.setWrapping(True)
        self.listView.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.listView.setModel(self.listModel)
        self.listView.selectionModel().selectionChanged.connect(self.listSelChange)
        self.fillList()

        self.curView.move(10, 10)
        self.curView.setFixedSize(150, 270)
        self.curView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.curView.setSelectionMode(QAbstractItemView.SingleSelection)

        self.curView.setModel(self.curModel)
        self.curView.selectionModel().selectionChanged.connect(self.curlistChange)
        self.fillcurList()
        self.curView.setCurrentIndex(self.curModel.index(0, 0))

        QLabel('Куратор:', self.panel).move(172, 12)
        QLabel('Имя пользователя:', self.panel).move(172, 37)
        QLabel('Имя компютера:', self.panel).move(172, 62)
        QLabel('Доступ к отделениям:', self.panel).move(172, 87)

        self.nameEdit.move(300, 10)
        self.nameEdit.setFixedWidth(150)

        self.userEdit.move(300, 35)
        self.userEdit.setFixedWidth(150)

        self.compEdit.move(300, 60)
        self.compEdit.setFixedWidth(150)

        self.renameBtn.move(170, 255)
        self.renameBtn.setFixedWidth(80)
        self.renameBtn.clicked.connect(self.renameAct)

        self.delBtn.move(270, 255)
        self.delBtn.setFixedWidth(80)
        self.delBtn.clicked.connect(self.delAct)

        self.addBtn.move(370, 255)
        self.addBtn.setFixedWidth(80)
        self.addBtn.clicked.connect(self.addAct)

    " при изменении в списке"
    def listSelChange(self):
        if len(self.listView.selectedIndexes()) == 0:
            self.listView.setCurrentIndex(self.listModel.index(self.listView.currentIndex().row(), 0))

    " заполнить список "
    def fillList(self):
        self.listModel.clear()
        for curator in cur_list:
            self.listModel.appendRow(QStandardItem(curator[1]))

    " заполнить список "
    def fillcurList(self):
        self.curModel.clear()
        for curator in cur_list:
            self.curModel.appendRow(QStandardItem(curator[1]))

    " при выборе в списке слева "
    def curlistChange(self):
        self.index = self.curView.selectedIndexes()[0].row()
        self.nameEdit.setText(cur_list[self.index][1])
        self.userEdit.setText(cur_list[self.index][2])
        self.compEdit.setText(cur_list[self.index][4])
        self.fillList()
        selection_model = self.listView.selectionModel()

        for curator in cur_list[self.index][3]:
            for id_, cur in enumerate(cur_list):
                if cur[0] == int(curator):
                    selection_model.select(self.listModel.index(id_, 0), QItemSelectionModel.Toggle)

    def renameAct(self):
        ind = self.index
        cur_list[self.index][1] = self.nameEdit.text()
        cur_list[self.index][2] = self.userEdit.text()
        cur_list[self.index][4] = self.compEdit.text()

        cur_lst = []
        cur_text = ''
        for cur in self.listView.selectedIndexes():
            cur_lst.append(str(cur_list[cur.row()][0]))
            cur_text += str(cur_list[cur.row()][0]) + ','
        cur_list[self.index][3] = cur_lst

        self.fillList()
        self.fillcurList()
        self.curView.setCurrentIndex(self.curModel.index(ind, 0))
        # записываем в базу
        query = "UPDATE users SET name='{}', login='{}', permissions='{}', comp_name='{}' WHERE id={}"
        query = query.format(self.nameEdit.text(), self.userEdit.text(), cur_text[:-1], self.compEdit.text(),
                             str(cur_list[self.index][0]))
        writeToDb(query)

    def delAct(self):
        find = False
        for item in conn_list:
            if str(cur_list[self.index][0]) in item['Curator1'].split(','):
                find = True
                break
        if not find:
            # записываем в базу
            query = "DELETE FROM users WHERE id=" + str(cur_list[self.index][0])
            writeToDb(query)

            cur_list.pop(self.index)
            self.fillList()
            self.fillcurList()
            self.curView.setCurrentIndex(self.curModel.index(0, 0))
        else:
            QMessageBox.warning(self, 'Ошибка удаления',
                                'Запрещено удалять куратора, который используется в подключениях')

    def addAct(self):
        text, ok = QInputDialog.getText(self, 'Новый куратор', 'Введите ФИО:', QLineEdit.Normal, '',
                                        Qt.CoverWindow)
        if ok and text:
            max_cur = 0
            for i in cur_list:
                if i[0] > max_cur:
                    max_cur = i[0]
            cur_list.append([max_cur+1, text, '', [str(max_cur+1)], ''])
            self.fillList()
            self.fillcurList()
            self.curView.setCurrentIndex(self.curModel.index(0, 0))
            # записываем в базу
            query = "INSERT INTO users (id , name , login , permissions, comp_name) VALUES ( {}, '{}', '{}', '{}','{}')"
            query = query.format(str(max_cur + 1), text, '', str(max_cur + 1), '')
            writeToDb(query)

    " выход по ескейпу "
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    " закрытие окна "
    def closeWin(self):
        self.close()


class ShowHistoryWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window)
        self.panel = QFrame()
        self.cancelButton = QPushButton("Закрыть")
        self.userCombo = QListView(self.panel)
        self.histList = QTreeView(self.panel)
        self.model = QStandardItemModel()
        self.userModel = QStandardItemModel()
        self.index = 0
        self.users = []
        self.initUI()

    " заполнение формы элементами "
    def initUI(self):
        self.cancelButton.clicked.connect(self.closeWin)
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.setContentsMargins(10, 10, 10, 10)
        hbox.addWidget(self.cancelButton)

        self.panel.setFrameShadow(QFrame.Raised)
        self.panel.setFrameShape(QFrame.Panel)
        self.panel.setFixedSize(850, 210)
        self.panel.setStyleSheet("QComboBox { background-color: #ffffff; }")
        self.setPanelItems()
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.panel)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.setFixedSize(850, 250)
        self.setWindowTitle('История посещений')
        self.setWindowModality(Qt.WindowModal)

    " заполнение панели элементами "
    def setPanelItems(self):
        self.histList.move(290, 10)
        self.histList.setFixedSize(550, 190)
        self.histList.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.histList.setSelectionMode(QAbstractItemView.SingleSelection)
        self.histList.setModel(self.model)

        QLabel('Пользователь: ', self.panel).move(12, 10)
        self.userCombo.move(10, 30)
        self.userCombo.setFixedSize(270, 170)

        self.userCombo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.userCombo.setSelectionMode(QAbstractItemView.SingleSelection)

        self.userCombo.setModel(self.userModel)
        self.userCombo.selectionModel().selectionChanged.connect(self.comboChanged)
        self.fillCombo()

    def fillCombo(self):
        query = "SELECT user_name, comp_name FROM user_logs GROUP BY user_name, comp_name"
        data_conn = connectDb()
        data_cursor = data_conn.cursor()
        data_cursor.execute(query)
        self.users = data_cursor.fetchall()
        data_conn.close()
        id_ = 0
        for ind, user in enumerate(self.users):
            self.userModel.appendRow(QStandardItem(user[0] + ' \ ' + user[1]))
            if user[0] == user_name and user[1] == comp_name:
                id_ = ind
        self.userCombo.setCurrentIndex(self.userModel.index(id_, 0))

    def comboChanged(self):
        self.index = self.userCombo.selectedIndexes()[0].row()
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['Время подключения', 'Действие', 'Узел'])
        self.histList.setColumnWidth(0, 160)
        self.histList.setColumnWidth(1, 160)
        self.histList.setColumnWidth(2, 210)

        query = """SELECT user_logs.date, user_logs.action, connections.name 
        FROM user_logs LEFT JOIN connections ON user_logs.conn_id=connections.id
        WHERE user_logs.user_name='{}' and user_logs.comp_name='{}' 
        ORDER BY user_logs.date DESC"""
        query = query.format(self.users[self.index][0], self.users[self.index][1])
        data_conn = connectDb()
        data_cursor = data_conn.cursor()
        data_cursor.execute(query)
        logs = data_cursor.fetchall()
        data_conn.close()
        for log in logs:
            time_ = datetime.datetime.fromtimestamp(log[0]).strftime('%d.%m.%Y %H:%M:%S')
            self.model.appendRow((QStandardItem(time_), QStandardItem(log[1]), QStandardItem(log[2])))

    " выход по ескейпу "
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    " закрытие окна "
    def closeWin(self):
        self.close()


class HistoryWidget(QWidget):

    def __init__(self, conn_id, parent=None):
        super().__init__(parent, Qt.Window)
        self.panel = QFrame()
        self.cancelButton = QPushButton("Закрыть")
        self.histList = QTreeView(self.panel)
        self.model = QStandardItemModel()
        self.id = conn_id
        self.initUI()

    " заполнение формы элементами "
    def initUI(self):
        self.cancelButton.clicked.connect(self.closeWin)
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.setContentsMargins(10, 10, 10, 10)
        hbox.addWidget(self.cancelButton)

        self.panel.setFrameShadow(QFrame.Raised)
        self.panel.setFrameShape(QFrame.Panel)
        self.panel.setFixedSize(620, 180)
        self.setPanelItems()
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.panel)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.setFixedSize(620, 220)
        name = ''
        for item in conn_list:
            if item['ID'] == self.id:
                name = item['Name']
                break
        self.setWindowTitle('История посещений : ' + name)
        self.setWindowModality(Qt.WindowModal)

    " заполнение панели элементами "
    def setPanelItems(self):
        self.histList.move(10, 10)
        self.histList.setFixedSize(600, 160)
        self.histList.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.histList.setSelectionMode(QAbstractItemView.SingleSelection)
        self.histList.setModel(self.model)
        self.fillList()

    def fillList(self):
        self.model.setHorizontalHeaderLabels(['Время подключения', 'Пользователь', 'Компютер', 'Действие'])
        self.histList.setColumnWidth(0, 160)
        self.histList.setColumnWidth(1, 140)
        self.histList.setColumnWidth(2, 140)
        self.histList.setColumnWidth(3, 140)

        query = """SELECT user_logs.date, user_logs.user_name, user_logs.comp_name, user_logs.action 
        FROM user_logs LEFT JOIN connections ON user_logs.conn_id=connections.id
        WHERE user_logs.conn_id={} ORDER BY user_logs.date DESC"""
        query = query.format(self.id)
        data_conn = connectDb()
        data_cursor = data_conn.cursor()
        data_cursor.execute(query)
        logs = data_cursor.fetchall()
        data_conn.close()
        for log in logs:
            time_ = datetime.datetime.fromtimestamp(log[0]).strftime('%d.%m.%Y %H:%M:%S')
            self.model.appendRow((QStandardItem(time_), QStandardItem(log[1]), QStandardItem(log[2]),
                                  QStandardItem(log[3])))

    " выход по ескейпу "
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    " закрытие окна "
    def closeWin(self):
        self.close()


class SelectCurator(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window)
        self.panel = QFrame()
        self.cancelButton = QPushButton("Закрыть")
        self.okButton = QPushButton("Выбрать")
        self.curCombo = QComboBox(self.panel)
        self.initUI()

    " заполнение формы элементами "
    def initUI(self):
        self.cancelButton.clicked.connect(self.closeWin)
        self.okButton.clicked.connect(self.okAction)
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.setContentsMargins(10, 10, 10, 10)
        hbox.addWidget(self.okButton)
        hbox.addWidget(self.cancelButton)

        self.panel.setFrameShadow(QFrame.Raised)
        self.panel.setFrameShape(QFrame.Panel)
        self.panel.setFixedSize(200, 50)
        self.panel.setStyleSheet("QComboBox { background-color: #ffffff; }")
        self.setPanelItems()
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.panel)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.setFixedSize(200, 90)
        self.setWindowTitle('Выберите руководителя')
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowModality(Qt.WindowModal)

    " заполнение панели элементами "
    def setPanelItems(self):
        self.curCombo.move(10, 10)
        self.curCombo.setFixedSize(180, 22)
        for cur in cur_list:
            self.curCombo.addItem(cur[1])

    " выход по ескейпу "
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    def okAction(self):
        global curator_selected
        curator_selected.append(self.curCombo.currentIndex())
        self.close()

    " закрытие окна "
    def closeWin(self):
        self.close()


class FastSearch(QWidget):

    def __init__(self, connlist, parent=None):
        super().__init__(parent, Qt.Window)
        self.panel = QFrame()
        self.cancelButton = QPushButton("Закрыть")
        self.okButton = QPushButton("Поиск")
        self.searchEdit = QLineEdit(self.panel)
        self.startCheck = QCheckBox("Искать с текущего элемента", self.panel)
        self.connList = connlist
        self.initUI()

    " заполнение формы элементами "
    def initUI(self):
        self.cancelButton.clicked.connect(self.closeWin)
        self.okButton.clicked.connect(self.okAction)
        hbox = QVBoxLayout()
        hbox.addStretch(1)
        hbox.setContentsMargins(10, 10, 10, 10)
        hbox.addWidget(self.okButton)
        hbox.addWidget(self.cancelButton)

        self.panel.setFrameShadow(QFrame.Raised)
        self.panel.setFrameShape(QFrame.Panel)
        self.panel.setFixedSize(210, 70)
        self.panel.setStyleSheet("QComboBox { background-color: #ffffff; }")
        self.setPanelItems()
        vbox = QHBoxLayout()
        vbox.addStretch(1)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.panel)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.setFixedSize(310, 70)
        self.setWindowTitle('Быстрый поиск')
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowModality(Qt.WindowModal)

    " заполнение панели элементами "
    def setPanelItems(self):
        global last_search
        self.searchEdit.move(12, 12)
        self.searchEdit.setFixedSize(180, 22)
        self.searchEdit.setText(last_search[0])
        self.searchEdit.setFocus()
        self.searchEdit.setSelection(0, len(self.searchEdit.text()))
        self.searchEdit.returnPressed.connect(self.enterEdit)

        self.startCheck.move(12, 42)
        self.startCheck.setCheckState(Qt.Checked)

    def enterEdit(self):
        self.okAction()

    " выход по ескейпу "
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.closeWin()
        if e.key() == Qt.Key_Enter:
            self.okAction()

    def okAction(self):
        if self.startCheck.isChecked():
            for i in range(self.connList.model.rowCount() - self.connList.selectedIndexes()[0].row()-1):
                i_ = i + self.connList.selectedIndexes()[0].row() + 1
                if self.searchEdit.text():
                    name_ = self.connList.model.index(i_, 2).data().lower()
                    if name_.find(self.searchEdit.text().lower()) >= 0:
                        self.connList.setCurrentIndex(self.connList.model.index(i_, 0))
                        return
        else:
            for i in range(self.connList.model.rowCount()):
                i_ = i
                if self.searchEdit.text():
                    name_ = self.connList.model.index(i_, 2).data().lower()
                    if name_.find(self.searchEdit.text().lower()) >= 0:
                        self.connList.setCurrentIndex(self.connList.model.index(i_, 0))
                        return
        QMessageBox.information(self, 'Поиск', 'Нет больше совпадений')

    " закрытие окна "
    def closeWin(self):
        global last_search
        last_search.clear()
        last_search.append(self.searchEdit.text())
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SelectCurator()
    ex.show()
    sys.exit(app.exec_())
