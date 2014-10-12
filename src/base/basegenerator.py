# -*- encoding: utf-8 -*-

from random import choice
from string import lowercase

import PyQt4.QtCore as QtCore
from PyQt4.Qt import *


class ChannelData(QObject):

    signalX = pyqtSignal('QString')  # Сигналы для проброски сигналов от генератора к холсту
    signalY = pyqtSignal('QString')  # Сигналы для проброски сигналов от генератора к холсту

    def __init__(self, plotWidget, funcGetX, funcGetY, name='random'):
        QObject.__init__(self)
        self.plotWidget = plotWidget
        self.getXData = funcGetX
        self.getYData = funcGetY

        if name == 'random':
            name = self._genRandomStr()

        self.name = name

    def getXArray(self):
        '''
        Функция отдачи массива X значений
        '''
        return self.getXData()

    def getYArray(self):
        '''
        Функция отдачи массива Y значений
        '''
        return self.getYData()

    def setName(self, name):
        '''
        Установить название канала
        '''
        self.name = name

    def getName(self):
        '''
        Получить название канала
        '''
        return self.name

    def updateY(self):
        '''
        Послать сигнал, что массив Y обновился
        '''
        self.signalY.emit(self.name)

    def updateX(self):
        '''
        Послать сигнал, что массив X обновился
        '''
        self.signalX.emit(self.name)

    def getSignals(self):
        '''
        Вернуть объекты сигналов из канала
        '''
        return self.signalX, self.signalY

    def _genRandomStr(self, len=5):
        '''
        сгенерировать случайную строку длиной len
        '''
        return "".join(choice(lowercase) for i in range(len))


class BaseGenerator(QObject):
    '''
    Является классом-генератором данных
    '''
    def __init__(self, plotWidget):
        QObject.__init__(self)

        self.channels = {}
        self.plotWidget = plotWidget

    def addChannel(self, getXDataFunc, getYDataFunc, name='random'):
        '''
        Добавить канал plotWidget
        :param getXDataFunc: функция, которая возвращает массив с значениями по X
        :param getYDataFunc: функция, которая возвращает массив с значениями по Y
        :param name: название калана
        :return:
        '''
        name = self.createChannel(getXDataFunc, getYDataFunc, name)
        self.regChannelOnPlot(name)
        return name

    def createChannel(self, getXDataFunc, getYDataFunc, name='random'):
        '''
        Создать объект канала
        :param getXDataFunc: функция, которая возвращает массив с значениями по X
        :param getYDataFunc: функция, которая возвращает массив с значениями по Y
        :param name: название калана
        :return:
        '''
        chan = ChannelData(self.plotWidget, getXDataFunc, getYDataFunc, name)
        chanName = chan.getName()
        self.channels[chanName] = chan
        return chanName

    def regChannelOnPlot(self, name):
        '''
        Привязать определенный с названием name к self.plotWidget
        :param name:
        :return:
        '''
        self.plotWidget.addChannel(self.channels[name])

    def updateX(self, name):
        '''
        Послать сигнал, что канал с названием name обновился
        :param name:
        :return:
        '''
        self.channels[name].updateX()

    def updateY(self, name):
        '''
        Послать сигнал, что канал с названием name обновился
        :param name:
        :return:
        '''
        self.channels[name].updateY()
