#!/usr/bin/env python
#coding:utf-8

import sys
import Queue
import optparse
import requests
import threading
import urlparse


class DirScan(object):
    """
    Class DirScan
    """
    _ext = 'php'
    _queue = Queue.Queue()

    def __init__(self, target, thread_num=5, ext=None):
        self._target = self._patch_url(target)
        self._thread_num = thread_num
        if not None:
            self._ext = ext

    def _patch_url(self, url):
        res = urlparse.urlparse(url)
        if not res.scheme:
            url = 'http://' + url
        return url

    def run(self):
        pass


if __name__ == '__main__':
    parser = optparse.OptionParser('Usage: ')
    parser.add_option('-t', '--threads', dest='thread_num',
                      default=5, type='int',
                      help='')
    parser.add_option('-e', '--ext', dest='ext',
                      default='php', type='string',
                      help='')
    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.print_help()
        sys.exit(-1)

    d = DirScan(target=args[0], thread_num=options.thread_num, ext=options.ext)
    d.run()