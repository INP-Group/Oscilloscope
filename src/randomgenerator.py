# -*- encoding: utf-8 -*-



import random
import numpy as np

import PyQt4.QtCore as QtCore

from src.base.basegenerator import BaseGenerator


class RandomGenerator(BaseGenerator):
    '''
    Является классом-генератором данных
    '''

    def __init__(self, plotWidget):
        BaseGenerator.__init__(self, plotWidget)

        self.tdata = None  # [N], это данные по времени (то что по шкале х рисуют), нс
        self.udata = None  # [2][N] - напряжения с последнего измерения, В
        self.adata = None  # [2][N] - устредненное напряжение за M измерений, В
        self.refdata = None  # [2][N] - эталонный сигнал, В

        self.chanAName = self.addChannel(self.getTData, self.getAData)
        self.chanUName = self.addChannel(self.getTData, self.getUData, 'lala1')
        self.chanRefName = self.addChannel(self.getTData, self.getRefData)

        self.connect(self, QtCore.SIGNAL('updateData()'), QtCore.SLOT('updateArrays()'))
        self.connect(self, QtCore.SIGNAL('updateData2()'), QtCore.SLOT('updateArrays2()'))

        self.ctimer = QtCore.QTimer()
        self.ctimer.singleShot(self._getRandomSleep(), self.randomTimeSlot)
        self.ctimer.singleShot(self._getRandomSleep(), self.randomTimeSlot2)

    def _GRNPA(self, min_value=-1, max_value=1, size=10):
        '''
        GRNPA = Get random numpy array
        :param min_value:
        :param max_value:
        :param size:
        :return:
        '''
        return np.random.uniform(min_value, max_value, size=size)

    @QtCore.pyqtSlot()
    def updateArrays(self):
        '''
        Обновление массивов с данными
        tdata[N] - это данные по времени (то что по шкале х рисуют), нс
        udata[2][N] - напряжения с последнего измерения, В
        adata[2][N] - устредненное напряжение за M измерений, В
        refdata[2][N] - эталонный сигнал, В

        :return:
        '''
        size = 30
        #self._GRNPA(-50, 50, size=size)
        self.tdata = self._GRNPA(-100, 50, size=size)
        self.udata = np.array([[], self._GRNPA(400, 5, size=size)])

        self.tdata.sort()  # сортирует массив времени

        self.emit(QtCore.SIGNAL('newDataT()'))

        self.updateX(self.chanUName)
        self.updateY(self.chanUName)


    @QtCore.pyqtSlot()
    def updateArrays2(self):
        '''
        Обновление массивов с данными
        tdata[N] - это данные по времени (то что по шкале х рисуют), нс
        udata[2][N] - напряжения с последнего измерения, В
        adata[2][N] - устредненное напряжение за M измерений, В
        refdata[2][N] - эталонный сигнал, В

        :return:
        '''
        size = 30


        self.tdata = self._GRNPA(-100, 50, size=size)
        self.adata = np.array([[], self._GRNPA(1200, -100, size=size)])
        self.refdata = np.array([[], self._GRNPA(-1000, -2000, size=size)])

        self.tdata.sort()  # сортирует массив времени

        self.emit(QtCore.SIGNAL('newDataT()'))

        self.updateX(self.chanAName)
        self.updateX(self.chanRefName)

        self.updateY(self.chanAName)
        self.updateY(self.chanRefName)


    def getTData(self):
        return self.tdata

    def getUData(self):
        return self.udata

    def getAData(self):
        return self.adata

    def getRefData(self):
        return self.refdata

    def _getRandomSleep(self):
        '''
        Генерирует случайный интервал для таймера (таймер кидает сигнал)
        :return:
        '''
        return random.random() * 1000 # ms2sec

    def randomTimeSlot(self):
        '''
        Отсылает сигнал и засыпает на случайное время
        :return:
        '''
        self.emit(QtCore.SIGNAL('updateData()'))
        self.ctimer.singleShot(self._getRandomSleep(), self.randomTimeSlot)

    def randomTimeSlot2(self):
        '''
        Отсылает сигнал и засыпает на случайное время
        :return:
        '''
        self.emit(QtCore.SIGNAL('updateData2()'))
        self.ctimer.singleShot(self._getRandomSleep(), self.randomTimeSlot2)