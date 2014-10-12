# -*- encoding: utf-8 -*-


import random
import PyQt4.Qwt5   as Qwt
import math

import PyQt4.QtCore as QtCore
from PyQt4.Qt import *
import sys

from src.base.baselines import Line
from operator import itemgetter

class Marker(Qwt.QwtPlotMarker):

    def __init__(self, plot, direction='hz'):
        super(Qwt.QwtPlotMarker, self).__init__()
        self.crossingValues = []
        self.plot = plot
        self.direction = direction
        self._init_marker()

        if self.direction == 'vt':
            self.key_dec = QtCore.Qt.Key_Left
            self.key_inc = QtCore.Qt.Key_Right
        else:
            self.key_dec = QtCore.Qt.Key_Down
            self.key_inc = QtCore.Qt.Key_Up
        self.key_inc_modif = ''
        self.key_dec_modif = ''

        #todo
        self.name = '1'


    def process_key(self, e):
        '''
        Обработка события нажатия клавиш
        Учитываются модификаторы
        :param e:
        :return:
        '''

        key = e.key()

        if self.key_inc == key:
            if (not self.key_inc_modif and int(e.modifiers()) == 0) or \
                    (self.key_inc_modif and int(e.modifiers()) == self.key_inc_modif):
                self.increase()

        if self.key_dec == key:
            if (not self.key_dec_modif and int(e.modifiers()) == 0) or\
                    (self.key_dec_modif and int(e.modifiers()) == self.key_dec_modif):
                self.decrease()

    def _randomValue(self):
        '''
        Возвращает случайное значение
        :return:
        '''
        return random.random() * self._getDirectStep(5)

    def _init_marker(self):
        '''
        Прописывание значений по умолчанию для маркера
        :return:
        '''
        value = self._randomValue()
        if self.direction == 'vt':
            self.setLabel(Qwt.QwtText('x = %s' % value))
            self.setLineStyle(Qwt.QwtPlotMarker.VLine)
        else:
            self.setLabel(Qwt.QwtText('y = %s' % value))
            self.setLineStyle(Qwt.QwtPlotMarker.HLine)

        self.setLabelAlignment(Qt.AlignRight | Qt.AlignTop)
        self.setValue(value)
        self.attach(self.plot)
        self.plot.replot()

    def isHz(self):
        '''
        Возвращает 1 если горизонтальный маркер, 0 если вертикальный
        :return:
        '''
        return self.lineStyle() % 2

    def bindIncModifier(self, key):
        '''
        Прописать модификатор для сочетания клавиш для увеличения значения
        marker.bindIncModifier(Qt.ControlModifier)
        :param key:
        :return:
        '''
        self.key_inc_modif = key

    def bindDecModifier(self, key):
        '''
        Прописать модификатор для сочетания клавиш для уменьшения значения
        marker.bindDecModifier(Qt.ControlModifier)
        :param key:
        :return:
        '''
        self.key_dec_modif = key

    def bindInc(self, key):
        '''
        Прописать клавишу для увеличения значения
        marker.bindInc(QtCore.Qt.Key_Right)
        :param key:
        :return:
        '''
        self.key_inc = key

    def bindDec(self, key):
        '''
        Прописать клавишу для уменьшения значения
        marker.bindDec(QtCore.Qt.Key_Right)
        :param key:
        :return:
        '''
        self.key_dec = key

    def setValue(self, value):
        '''
        Установить значение для маркера
        :param value:
        :return:
        '''
        if self.isHz():
            self.setYValue(value)
        else:
            self.setXValue(value)

    def _getDirectStep(self, percent=1):
        '''
        Вычисляет шаг для маркера
        :param percent:
        :return:
        '''
        if self.isHz():
            a, b = self.plot.getYScale()
        else:
            a, b = self.plot.getXScale()
        coef = (abs(a) + abs(b)) / 100.0
        return coef * percent

    def getValue(self):
        '''
        Возвращает текущее значение маркера
        :return:
        '''
        if self.isHz():
            return self.value().y()
        else:
            return self.value().x()

    def getCurText(self):
        '''
        Возвращает текущее состояние записи маркера
        :return:
        '''
        if self.isHz():
            return Qwt.QwtText('y = %s' % self.getValue())
        else:
            return Qwt.QwtText('x = %s' % self.getValue())

    def increase(self):
        '''
        Опустить маркер вниз
        :return:
        '''
        self.setValue(self.getValue() + self._getDirectStep())
        self.setLabel(self.getCurText())
        self.plot.replot()

    def decrease(self):
        '''
        Поднять маркер на верх
        :return:
        '''
        self.setValue(self.getValue() - self._getDirectStep())
        self.setLabel(self.getCurText())
        self.plot.replot()

    def getInfo(self):
        values = self.crossingValues
        self.crossingValues = []
        return {
            'direction': self.direction,
            'value': self.getValue(),
            'name': self.name,
            'crossing': values,
        }

    def addCrossingValueY(self, lineName, value):
        self.crossingValues.append((lineName, value))


class BaseDataPlot(Qwt.QwtPlot):

    updateLinesInfo = pyqtSignal(list)
    updateMarkersInfo = pyqtSignal(list)

    def __init__(self, parent):
        super(BaseDataPlot, self).__init__(parent)
        self.setMinimumWidth(600)
        self.plot_lines = {}
        self.markers = []
        self.is_pause = False

        self.setTitlePlot(u'Multiple plot sample')
        self.legend = Qwt.QwtLegend(self)

        # оси
        self.setAxisTitle(Qwt.QwtPlot.xBottom, "Time, ns")
        self.setAxisTitle(Qwt.QwtPlot.yLeft, "U, V")

        self.setAxisAutoScale(Qwt.QwtPlot.xBottom)
        self.setAxisAutoScale(Qwt.QwtPlot.yLeft)

        # сетка
        self.grid = Qwt.QwtPlotGrid()
        self.grid.attach(self)
        self.grid.setPen(QPen(Qt.black, 0, Qt.DotLine))

        self.__initZooming()
        self.__initMarker()



    def replotLines(self):
        if not self.is_pause:
            self.replot()

    def markerCrossing(self):
        # Примитивная реализация кода из qwt6
        # int currentPosX = pos.x()
        # QPointF d = curve1->sample(currentPosX)
        # print d.y()

        if self.plot_lines and self.markers:
            for marker in self.markers:
                if not marker.isHz():
                    valueM = marker.getValue()

                    for line in self.plot_lines.values():
                        points = zip(line.getDataX(), line.getDataY())
                        points = sorted(points, key=itemgetter(0))
                        min = (sys.maxint, 0)
                        max = (-sys.maxint - 1, 0)

                        for x in points:
                            if x[0] < valueM:
                                min = x
                            if x[0] > valueM:
                                max = x
                                break

                        k = (max[1] - min[1]) / (max[0] - min[0])  + 0.0001
                        y2 = k * (max[0] - min[0]) + min[1]

                        marker.addCrossingValueY(line.getName(), y2)


    def replot(self, *args, **kwargs):

        super(BaseDataPlot, self).replot(*args, **kwargs)
        self.updateInfoLines()
        self.updateInfoMarkers()
        self.markerCrossing()


    def __initMarker(self):
        '''
        Добавление маркеров на холст
        :return:
        '''
        self.step_move_marker = 1.0

        self.markers.append(Marker(self, 'vt'))
        self.markers.append(Marker(self, 'hz'))

        marker = Marker(self, 'vt')
        marker.bindIncModifier(Qt.ControlModifier)
        marker.bindInc(QtCore.Qt.Key_Right)

        marker.bindDecModifier(Qt.ControlModifier)
        marker.bindDec(QtCore.Qt.Key_Left)

        self.markers.append(marker)

        marker2 = Marker(self, 'hz')
        marker2.bindIncModifier(Qt.ControlModifier)
        marker2.bindInc(QtCore.Qt.Key_Up)

        marker2.bindDecModifier(Qt.ControlModifier)
        marker2.bindDec(QtCore.Qt.Key_Down)

        self.markers.append(marker2)

        self.replot()

    def __initZooming(self):
        '''
        Initialize zooming
        :return:
        '''
        self.zoomer = Qwt.QwtPlotZoomer(Qwt.QwtPlot.xBottom,
                                        Qwt.QwtPlot.yLeft,
                                        Qwt.QwtPicker.DragSelection,
                                        Qwt.QwtPicker.AlwaysOff,
                                        self.canvas())
        self.zoomer.setRubberBandPen(QPen(Qt.red))
        self.zoomer.setTrackerPen(QPen(Qt.red))
        self.magnifier = Qwt.QwtPlotMagnifier(self.canvas())

    def clearZoomStack(self):
        '''
        Auto scale and clear the zoom stack
        :return:
        '''
        self.setAxisAutoScale(Qwt.QwtPlot.xBottom)
        self.setAxisAutoScale(Qwt.QwtPlot.yLeft)
        self.replot()
        self.zoomer.setZoomBase()

    @pyqtSlot('QString', list)
    def updateLineX(self, name, values):
        '''
        ОБновить линию name новыми значениями по X
        :param name: название линии
        :param values: значения
        :return:
        '''
        self.plot_lines[str(name)].setXArray(values)

    @pyqtSlot('QString', list)
    def updateLineY(self, name, values):
        '''
        ОБновить линию name новыми значениями по Y
        :param name: название линии
        :param values: значения
        :return:
        '''
        self.plot_lines[str(name)].setYArray(values)

    def regLineByName(self, name, type='Line'):
        '''
        Зарегистрировать новую линию
        :param name: название линии
        :param type: тип линии Line, FuncLine
        :return:
        '''
        line = None
        if type == 'Line':
            line = Line(self)
        self.plot_lines[str(name)] = line
        line.setName(str(name))

    def contextMenuEvent(self, event):
        '''
        Меню по клику правой кнопки на холст
        :param event:
        :return:
        '''
        menu = QMenu(self)
        quitAction = menu.addAction("Quit")
        backgroundColorAction = menu.addAction("Backgroud color")

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == quitAction:
            exit(0)
        elif action == backgroundColorAction:
            self.setCanvasBackground(self._generateRandomBackground())
            self.replot()

    def _generateRandomBackground(self):
        '''
        Генерирует случайный цвет для фона холста
        :return:
        '''
        return self._randomColor()

    def keyPressEvent(self, event):
        '''
        Обработка нажатий клавиш
        :param event:
        :return:
        '''
        if type(event) == QKeyEvent:
            event.accept()
            for marker in self.markers:
                marker.process_key(event)
        else:
            event.ignore()

    def _getCoefScale(self, flag=True):
        '''
        Вычисляет коэфициент. Согласно которому можно переводить значения пикселя в его значение на графике
        :param flag:
        :return:
        '''
        if flag:
            a, b = self.getXScale()
            coef = (abs(a) + abs(b)) / self.canvas().width()
            return coef
        else:
            a, b = self.getYScale()
            coef = (abs(a) + abs(b)) / self.canvas().height()
            return coef

    def getCoordX(self, event, variant=True):
        '''
        Получение х координаты имея event
        :param event:
        :param variant:
        :return:
        '''
        coef_x = self._getCoefScale()
        canvasX = event.x() - self.canvas().x()
        width = self.canvas().width()
        center_x = width / 2
        coord1_x = canvasX - width / 2.0
        coord2_x = canvasX - center_x

        if variant:
            return coord1_x * coef_x
        else:
            return coord2_x * coef_x

    def getCoordY(self, event, variant=True):
        '''
        Получение y координаты имея event
        :param event:
        :param variant:
        :return:
        '''
        coef_y = self._getCoefScale(False)
        canvasY = event.y() - self.canvas().y()
        height = self.canvas().height()
        center_y = height / 2
        coord1_y = height / 2.0  - canvasY
        coord2_y = -1 * (canvasY - center_y)
        if variant:
            return coord1_y * coef_y
        else:
            return coord2_y * coef_y

    def checkSelectedLines(self, event):
        '''
        Проверяет есть ли по месту клика линия (фунция)
        :param event:
        :return:
        '''
        for func in self.list_functions:
            if not func.func is None:
                if func.checkSelect(event):
                    return True, func
        return False, None

    def mousePressEvent(self, event):
        '''
        Обработка клика.
        :param event:
        :return:
        '''
        result = self.checkSelectedLines(event)
        if result[0]:
            self.showLineMenu(event, result[1])

    def mouseReleaseEvent(self, event):
        cursor = QCursor()

    def sizeHint(self):
        return QtCore.QSize(800, 800)

    def setTitlePlot(self, title):
        '''
        Установит название плота
        :param title:
        :return:
        '''
        self.title = title
        self.setTitle(self.title)

    def getYScale(self):
        '''
        Отдает min_x, max_x исходя из текущей системы координат
        :return:
        '''
        return self.axisScaleDiv(Qwt.QwtPlot.yLeft).lowerBound(), self.axisScaleDiv(Qwt.QwtPlot.yLeft).upperBound()

    def getXScale(self):
        '''
        Отдает min_y, max_y исходя из текущей системы координат
        :return:
        '''
        return self.axisScaleDiv(Qwt.QwtPlot.xBottom).lowerBound(), self.axisScaleDiv(Qwt.QwtPlot.xBottom).upperBound()

    def _randomColor(self):
        '''
        Генерирует случайный цвет
        :return:
        '''
        red = 100 + random.random() * 150
        green = 100 + random.random() * 150
        blue = 100 + random.random() * 150
        alpha = 91 + random.random() * 100
        return QColor(red, green, blue, alpha)


    # --------------------
    #todo перенести в сам объект линии
    def showLineMenu(self, event, line_object):
        '''
        Меню линии
        :param event:
        :param line_object:
        :return:
        '''

        def setColorLine(color, line_object):
            line_object.setLineColor(color)

        menu = QMenu(self)

        lineOffAction = None
        lineOnAction = None
        colorAction = None

        if line_object.getStatus():
            lineOffAction = menu.addAction("Off")
            colorAction = menu.addAction("Color picker")
        else:
            lineOnAction = menu.addAction("On")

        removeAction = menu.addAction("Delete")

        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action == removeAction:
            line_object.drawOff()
            del line_object
        elif action == lineOnAction:
            line_object.drawOn()
        elif action == lineOffAction:
            line_object.drawOff()
        elif action == colorAction:
            dlg = QColorDialog(self)
            dlg.setCurrentColor(line_object.color)

            if dlg.exec_():
                setColorLine(dlg.currentColor(), line_object)


    def updateInfoLines(self):
        data = []
        for name, line in self.plot_lines.items():
            data.append(line.getInfo())

        self.updateLinesInfo.emit(data)

    def updateInfoMarkers(self):
        data = []
        for market in self.markers:
            data.append(market.getInfo())

        self.updateMarkersInfo.emit(data)


