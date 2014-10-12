# -*- encoding: utf-8 -*-

import PyQt4.Qwt5   as Qwt
import random
import numpy as np

from PyQt4.Qt import *


class BaseLine(object):

    def __init__(self, plot):
        self.status = False
        self.plot = plot
        self.name = 'random'

        self.dataX = []
        self.dataY = []

        '''
        Базовая инициализация линии
        '''
        self.func = None

        self.text_func = None
        self.points_cnt = 10000
        self.color = self._generateRandomColorLines()
        self.legend = ""
        self.linewidth = 3
        self.min_x, self.max_x = self.plot.getXScale()

        '''
        Иницилиация кривой
        '''
        self.curve = Qwt.QwtPlotCurve(self.legend)

        self.curve.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Ellipse,
                                      QBrush(Qt.yellow),
                                      QPen(Qt.blue),
                                      QSize(5, 5)))


        pen = QPen(self.color, self.linewidth, Qt.SolidLine)
        self.curve.setPen(pen)
        self.curve.attach(self.plot)

    def getDataX(self):
        return self.dataX

    def getDataY(self):
        return self.dataY

    def getInfo(self):
        if self.dataX and self.dataY:
            result_info = {
                'name': self.name,
                'max_x': max(self.dataX),
                'max_y': max(self.dataY),
                'min_x': min(self.dataY),
                'min_y': min(self.dataX),
            }

            return result_info
        else:
            return {
                'name': '',
                'max_x': 0,
                'max_y': 0,
                'min_x': 0,
                'min_y': 0,
            }

    def setName(self, name):
        '''
        Установка названия линии (совпадает с названием канала)
        :param name:
        :return:
        '''
        self.name = name

    def getName(self):
        '''
        Получение названия линии
        :return:
        '''
        return self.name

    def _updateLine(self):
        '''
        Перерисовать линию
        :return:
        '''
        self.curve.setData(self.dataX, self.dataY)
        self.replot()

    def setXArray(self, values, update=True):
        '''
        Обновить массив X значений лини
        :param values:
        :param update: если True, то обновит линию на холсте
        :return:
        '''
        self.dataX = list(values)
        if update:
            self._updateLine()

    def setYArray(self, values, update=True):
        '''
        Обновить массив Y значений лини
        :param values:
        :param update: если True, то обновит линию на холсте
        :return:
        '''
        self.dataY = values
        if update:
            self._updateLine()

    def setDataAndUpdate(self, data_x, data_y):
        '''
        Одновременно установить массивы X и Y
        :param data_x:
        :param data_y:
        :return:
        '''
        self.setXArray(data_x, False)
        self.setYArray(data_y, False)

        self._updateLine()

    def getStatus(self):
        '''
        Получить статус (отображается/скрыта) линии
        :return:
        '''
        return self.status

    def _randomColor(self):
        '''
        Примитивная генерация случайнго цвета
        :return:
        '''
        red = 100 + random.random() * 150
        green = 100 + random.random() * 150
        blue = 100 + random.random() * 150
        alpha = 91 + random.random() * 100
        return QColor(red, green, blue, alpha)

    def _generateRandomColorLines(self):
        '''
        Добавить в функцию randomColor возможность указывать границы цветов
        :return:
        '''
        return self._randomColor()

    def setLineColor(self, color):
        '''
        Установить цвет линии
        :param color:
        :return:
        '''
        self.color = color
        pen = QPen(self.color, self.linewidth, Qt.SolidLine)
        self.curve.setPen(pen)
        self.replot()

    def getValueOfX(self, x):
        '''
        Вычисление значения функции по х
        :param x:
        :return:
        '''
        return self.func(x)

    def redraw(self):
        '''
        Перерисовать с учетом нового масштаба
        :return:
        '''
        self.min_x, self.max_x = self.plot.getXScale()
        x = np.linspace(self.min_x, self.max_x, self.points_cnt)
        vfc = np.vectorize(self.func)
        y1 = vfc(x)
        self.setDataAndUpdate(x, y1)

    def replot(self):
        '''
        Перерисовать (обновить холст)
        :return:
        '''

        self.plot.replotLines()

    def drawOn(self):
        '''
        Включить рисование линии
        :return:
        '''
        self.status = True
        self.curve.attach(self.plot)
        self.replot()

    def drawOff(self):
        '''
        Выключить рисование линии
        :return:
        '''
        self.status = False
        self.curve.attach(None)
        self.replot()

    def checkSelect(self, event):
        '''
        Проверяет попадет ли клик по линии
        :param line_object:
        :return:
        '''

        def calc_pr(value, percent=3):
            '''
            Вычисляет значения на percent меньше и больше чем value
            :param value:
            :param percent:
            :return:
            '''
            v1 = value * ((100 - percent) / 100.0)
            v2 = value * ((100 + percent) / 100.0)
            return min(v1, v2), max(v1, v2)

        def check(x, y):
            '''
            Сравнивает значения x и y с определенными границами (из calc_pr)
            :param x:
            :param y:
            :return:
            '''
            small, big = calc_pr(x)

            if y > small and y < big:
                return True
            else:
                return False

        real1_x = self.plot.getCoordX(event, False)
        real1_y = self.plot.getCoordY(event, False)

        real2_x = self.plot.getCoordX(event, True)
        real2_y = self.plot.getCoordY(event, True)

        if check(self.getValueOfX(real1_x), real1_y) or check(self.getValueOfX(real2_x), real2_y):
            return True
        return False

class Line(BaseLine):
    pass

class FuncLine(BaseLine):

    def drawInit(self, text_func, points_cnt=1000, color=None, legend=""):
        '''
        Рисование линии исходя из текстовой функции
        :param text_func:
        :param points_cnt:
        :param color:
        :param legend:
        :return:
        '''
        def create_func(text):
            return eval('lambda x: %s' % text)

        def get_color(color):
            if color is None:
                color = self._generateRandomColorLines()
            return color

        def get_legend(legend, text_func):
            if not legend:
                # legend = u'RandomLine %s' % self.cnt_lines
                legend = text_func
            return legend

        func = create_func(text_func)

        self.func = func

        self.text_func = text_func
        self.points_cnt = points_cnt
        self.color = get_color(color)
        self.legend = get_legend(legend, text_func)

        x = np.linspace(self.min_x, self.max_x, points_cnt)
        vfc = np.vectorize(func)
        y1 = vfc(x)

        self.setDataAndUpdate(x, y1)