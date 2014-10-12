# -*- encoding: utf-8 -*-



from PyQt4.Qt import *

from src.base.baseplot import BaseDataPlot


class BasePlotWidget(QWidget):
    '''
    Предполагается, что каждому PlotWidget соответствует только один Plot
    '''

    updateXArray = pyqtSignal('QString', list)
    updateYArray = pyqtSignal('QString', list)

    def __init__(self, parent=None, plot=None):
        QWidget.__init__(self, parent)
        self.channels = {}
        if plot is None:
            self.plot = BaseDataPlot(self)
        else:
            self.plot = plot
        self.updateXArray.connect(self.plot.updateLineX)
        self.updateYArray.connect(self.plot.updateLineY)

    @pyqtSlot('QString')
    def updateXChannel(self, name):
        '''
        Пробросить данные из канала в сам Plot. Надо учитывать какую именно линию обновить
        :param value:
        :return:
        '''
        self.updateXArray.emit(str(name), list(self.channels[str(name)].getXArray()))

    @pyqtSlot('QString')
    def updateYChannel(self, name):
        '''
        Канал возвращает двумерный numpy массив, значения хранятся во втором элементе
        :param name:
        :return:
        '''
        self.updateYArray.emit(str(name), list(self.channels[str(name)].getYArray()[1]))

    def addChannel(self, channel):
        '''
        Добавить объект канала на Plot
        :param channel:
        :return:
        '''
        self.channels[channel.getName()] = channel
        signalX, signalY = channel.getSignals()
        signalX.connect(self.updateXChannel)
        signalY.connect(self.updateYChannel)
        self.plot.regLineByName(channel.getName())