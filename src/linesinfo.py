# -*- encoding: utf-8 -*-

import PyQt4.QtCore as QtCore
from PyQt4.Qt import *
import numpy

class InfoView(QTextEdit):

    def __init__(self, plot):
        super(InfoView, self).__init__()

        self.plot = plot
        self.setStyleSheet("background-color: #E6E6E3")
        self.setAutoFillBackground(True)
        self.setReadOnly(True)
        self.setMinimumWidth(300)



class InfoLinesView(InfoView):

    def __init__(self, plot):
        super(InfoLinesView, self).__init__(plot)

        self.plot.updateLinesInfo.connect(self.updateText)


    def updateText(self, list_text):
        def form_output(elem):
            str = """
{name}:
      max\t\t\tmin
 x:  {max_x}\t{min_x}
 y:  {max_y}\t{min_y}
            """.format(**elem)
            return str

        # print form_output(list_text[0])
        self.clear()
        result_text = ""
        for x in list_text:
            result_text += form_output(x)
        self.append(result_text)


class InfoMarkersView(InfoView):

    def __init__(self, plot):
        super(InfoMarkersView, self).__init__(plot)

        self.plot.updateMarkersInfo.connect(self.updateText)


    def updateText(self, list_text):
        hz_list_dicts = []
        vt_list_dicts = []


        for dic in list_text:
            if dic.get("direction") == 'hz':
                hz_list_dicts.append(dic)
            else:
                vt_list_dicts.append(dic)

        x_size = len(hz_list_dicts)
        y_size = len(vt_list_dicts)
        row_labels = []

        values_hz = numpy.zeros((x_size, x_size))
        for i in xrange(0, x_size):
            # row_labels.append(hz_list_dicts[i].get("name"))
            for j in xrange(0, x_size):
                values_hz[i][j] = hz_list_dicts[i].get("value") - hz_list_dicts[j].get("value")


        # print "     A   B   C   D   E"
        result_text = ""
        row_labels = list(xrange(0, x_size))
        i = 0
        for row_label, row in zip(row_labels, values_hz):
            result_text += '%s [%s]\n' % (row_label, ' '.join('%03s' % i for i in row))

        # for i in xrange(1, len(hz_list_dicts)):
        #     for j in xrange(i + 1, len(hz_list_dicts))
        '''
        for (int i = 0; i < N; i++)
            for (int j = i + 1; j < N; j++)
                delta between i and j
        '''


        crossing_dict = {}
        for info in vt_list_dicts:
            for crossing in info.get("crossing"):
                if crossing_dict.has_key(crossing[0]):
                    crossing_dict[crossing[0]].append(crossing[1])
                else:
                    crossing_dict[crossing[0]] = [crossing[1]]
            # print info.get("crossing")

        #print crossing_dict

        crossing_text = "\n\n"
        for key, value in crossing_dict.items():
            line_crossing = "%s\t" % key
            for it in value:
                line_crossing += "%s\t" % it
            line_crossing += "\n"

            crossing_text += line_crossing


        self.clear()
        #self.append(result_text)
        self.append(crossing_text)