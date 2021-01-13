#!/usr/bin/python3
class M3U:
    extm3u = None
    class INF:
        title = None
        stream = None
        def __init__(self,str1,str2):
            self.title = str1
            self.stream = str2
        def getName(self):
            return self.title[self.title.rfind(',')+1:]
    extinf = None
    def __init__(self,lines=None,empty=False):
        if empty :
            self.extm3u = "#EXTM3U"
            self.extinf = []
            return
        str1 = None
        str2 = None
        self.extinf = []
        for line in lines:
            if isinstance(line, bytes) :
                line = line.decode('utf-8')
            line = line.rstrip('\n')
            if line.find("#EXTINF") == 0:
                str1 = line
            elif line.find("#EXTGRP") == 0:
                continue
            elif str1:
                str2 = line
                self.extinf.append(self.INF(str1, str2))
                str1 = None
            elif line.find("#EXTM3U") == 0:
                self.extm3u = line
    def get_dict_arr(self):
        return [{ 'title': ei.getName(), 'value': ei.stream } for ei in self.extinf]
"""
def main():
    with open('/home/abp/flask-tutorial/flaskr/hd.m3u') as f:
        lines = f.readlines()
    m3u = M3U(lines)
    resm3u = M3U(lines,True)
    print(resm3u.extm3u)
    for l in m3u.extinf:
        print(l.getName())


main()
"""