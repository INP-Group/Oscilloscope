# -*- encoding: utf-8 -*-

import PyQt4.QtCore as QtCore
from PyQt4.Qt import *

from src.base.baseplotwidget import BasePlotWidget
from src.base.baselines import Line, FuncLine
from src.base.baseplot import BaseDataPlot
from src.linesinfo import InfoLinesView, InfoMarkersView


class DataPlot(BaseDataPlot):

    def __init__(self, parent=None):
        super(DataPlot, self).__init__(parent)

        self.lineUData = None  # напряжения с последнего измерения
        self.lineAData = None  # устредненное напряжение за M измерений
        self.lineRefData = None  # эталонный сигнал


        self.list_functions = []

        return

    def drawLineOfFunction(self, text_func, points_cnt=1000, color=None, legend=""):
        '''
        Рисует на холсте график функции
        :param text_func:
        :param points_cnt:
        :param color:
        :param legend:
        :return:
        '''
        line = FuncLine(self)
        line.drawInit(text_func, points_cnt=points_cnt, color=color, legend=legend)
        line.drawOn()
        self.list_functions.append(line)

    def drawRandomLine(self):
        '''
        Рисует случайную линию по формуле.
        :return:
        '''
        random_name = "Random name %s" % (len(self.list_functions) + 1)
        line = FuncLine(self)
        line.drawInit("math.sin(random.random() ** 2 * math.pi * x) * random.random() * 2.0 ",
                      color=self._randomColor(), legend=random_name)
        line.drawOn()
        self.list_functions.append(line)

    @QtCore.pyqtSlot()
    def updateData(self):
        '''
        Обновляет все графики исходя из новых входных данных
        :return:
        '''

        def updateLine(line, data_x, data_y, self):
            if line is None:
                line = Line(self)
                line.setDataAndUpdate(data_x, data_y)
            else:
                line.setDataAndUpdate(data_x, data_y)
            return line

        if not self.is_pause:
            parent = self.parent()

            data1 = parent.getTData()
            data2 = parent.getUData()
            data3 = parent.getAData()
            data4 = parent.getRefData()

            # напряжения с последнего измерения
            self.lineUData = updateLine(self.lineUData, data1, data2[1], self)

            # устредненное напряжение за M измерений
            self.lineAData = updateLine(self.lineAData, data1, data3[1], self)

            # эталонный сигнал
            self.lineRefData = updateLine(self.lineRefData, data1, data4[1], self)

            for fu in self.list_functions:
                fu.redraw()
        else:
            pass

    @QtCore.pyqtSlot()
    def setPause(self):
        self.is_pause = not self.is_pause

    @QtCore.pyqtSlot()
    def zoomOff(self):
        self.clearZoomStack()

    @QtCore.pyqtSlot()
    def drawDefaultLines(self):
        # self.drawLineOfFunction("x ** 2")
        self.drawLineOfFunction("x")
        self.drawLineOfFunction("-x")
        self.drawLineOfFunction("2 * math.pi * x")
        self.drawLineOfFunction("4 * math.pi * x")


class PlotWidget(BasePlotWidget):
    '''
    Предполагается, что каждому PlotWidget соответствует только один Plot
    '''

    def __init__(self, parent=None):
        self.plot = DataPlot()
        BasePlotWidget.__init__(self, parent, self.plot)

        buttonMaxWidth = 200
        quitPB = QPushButton('Close')
        quitPB.setMaximumWidth(buttonMaxWidth)
        zoomPB = QPushButton('Zoom off')
        zoomPB.setMaximumWidth(buttonMaxWidth)
        defaultPB = QPushButton('Default')
        defaultPB.setMaximumWidth(buttonMaxWidth)

        pausePB = QPushButton('Pause')
        pausePB.setCheckable(True)
        pausePB.setMaximumWidth(buttonMaxWidth)


        self.h_layout_left = QVBoxLayout()
        self.v_layout = QHBoxLayout()
        self.v_layout_right = QVBoxLayout()


        self.h_layout_left.addWidget(zoomPB)
        self.h_layout_left.addWidget(pausePB)
        # self.h_layout.addWidget(defaultPB)

        self.h_layout_left.addWidget(QSplitter())
        self.h_layout_left.addWidget(quitPB)


        self.h_layout_left.setSizeConstraint(QLayout.SetMinimumSize)


        self.info_lines = InfoLinesView(self.plot)

        self.info_markers = InfoMarkersView(self.plot)
        self.v_layout_right.addWidget(self.info_lines)
        self.v_layout_right.addWidget(self.info_markers)

        self.v_layout_right.setSizeConstraint(QLayout.SetDefaultConstraint)


        self.v_layout.addLayout(self.h_layout_left)
        self.v_layout.addWidget(self.plot)
        self.v_layout.addLayout(self.v_layout_right)


        self.setLayout(self.v_layout)

        self.connect(pausePB, QtCore.SIGNAL('clicked()'), self.plot, QtCore.SLOT('setPause()'))
        self.connect(zoomPB, QtCore.SIGNAL('clicked()'), self.plot, QtCore.SLOT('zoomOff()'))
        self.connect(quitPB, QtCore.SIGNAL('clicked()'), qApp, QtCore.SLOT('quit()'))
        self.connect(defaultPB, QtCore.SIGNAL('clicked()'), self.plot, QtCore.SLOT('drawDefaultLines()'))





