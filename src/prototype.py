# -*- encoding: utf-8 -*-

import sys

from PyQt4.Qt import *

from src.randomgenerator import RandomGenerator as Oscilloscope
from src.plotwidget import PlotWidget


class Application(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.setGeometry(200, 200, 700, 700)
        self.setWindowTitle('Generate NP data')

        self.plotWidget = PlotWidget(self)

        self.osc = Oscilloscope(self.plotWidget)

        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(self.plotWidget)
        self.setLayout(self.h_layout)

def oscil():
    os = Application()
    os.show()
    return os

def main():
    app = QApplication(sys.argv)
    bd = oscil()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
