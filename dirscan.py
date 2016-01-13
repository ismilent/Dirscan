#!/usr/bin/env python
#coding:utf-8

import sys
import Queue
import optparse
import requests
import threading
import urlparse


EXIT_CODE_ARG = -1

class DirScan(object):
    """
    Class DirScan
    """
    _ext = None
    _queue = Queue.Queue()
    _word_list = []
    _thread_list = []

    def __init__(self, target, thread_num=5, ext=None, wordlist=None):
        self._target = self._patch_url(target)
        self._thread_num = thread_num
        if ext:
            self._ext = ext
        if wordlist:
            self._word_list = word_list

        self._load_dir_dict()

    def _patch_url(self, url):
        res = urlparse.urlparse(url)
        if not res.scheme:
            url = 'http://' + url
        return url

    def _load_dir_dict(self):
        for word_file_path in self._word_list:
            try:
                with file(word_file_path, 'r') as f:
                    for line in f:
                        self._queue.put(line)
            except Exception as e:
                print str(e)
                sys.exit(-2)


    def _scan(self):
        while True:
            print 'threading...'
            if self._queue.empty():
                break
            try:
                sub = self._queue.get()
                target = self._target + sub
            except Exception as e:
                print str(e)

    def run(self):
        for i in xrange(self._thread_num):
            t = threading.Thread(target=self._scan, name=str(i))
            self._thread_list.append(t)
            t.start()

        for t in self._thread_list:
            t.join()


if __name__ == '__main__':
    parser = optparse.OptionParser('Usage: ')
    parser.add_option('-t', '--threads', dest='thread_num',
                      default=5, type='int',
                      help='The thread number of program')
    parser.add_option('-e', '--ext', dest='ext',
                      default=None, type='string',
                      help='The web script extension')
    parser.add_option('-w', '--wordlist', dest='wordlist', type='string',
                      help='The word list path')

    (options, args) = parser.parse_args()
    if len(args) < 1 or not options.wordlist:
        parser.print_help()
        sys.exit(EXIT_CODE_ARG)

    word_list = options.wordlist.split(',')
    word_list = [x for x in word_list if x]
    if len(word_list) < 1:
        parser.print_help()
        sys.exit(EXIT_CODE_ARG)

    d = DirScan(target=args[0], thread_num=options.thread_num, ext=options.ext, wordlist=word_list)
    d.run()