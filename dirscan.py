#!/usr/bin/env python
#coding:utf-8

import sys
import optparse
import requests
import threading
import time


try:
    import queue as Queue
except Exception as e:
    import Queue

try:
    from urllib import parse as urlparse
except Exception as e:
    import urlparse

EXIT_CODE_ARG = -1
USER_AGENT ={'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'}


class DirScan(object):
    """
    Class DirScan
    """
    _ext = None
    _queue = Queue.Queue()
    _word_list = []
    _thread_list = []
    _lock = threading.Lock()
    _user_agent = USER_AGENT

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
                with open(word_file_path, 'r') as f:
                    for line in f:
                        self._queue.put(line)
            except Exception as e:
                print(str(e))
                sys.exit(-2)


    def _scan(self):
        while True:
            if self._queue.empty():
                break
            try:
                sub = self._queue.get_nowait()
                target = self._target + sub.strip()
                self._lock.acquire()
                r = requests.get(target, headers=USER_AGENT, timeout=5)
                code = r.status_code
                if code == 200:
                    print('[+][CODE 200] %s' % (target,))
                if code == 403:
                    print('[+][CODE 403] %s' % (target,))
                if code == 304:
                    print('[+][CODE 304] %s' % (target,))
                self._lock.release()
            except Exception as e:
                print(str(e))
            finally:
                pass

    def run(self):
        for i in range(self._thread_num):
            t = threading.Thread(target=self._scan, name=str(i))
            self._thread_list.append(t)
            t.start()

        for t in self._thread_list:
            t.join()


if __name__ == '__main__':
    opt_parser = optparse.OptionParser('Usage: ')
    opt_parser.add_option('-t', '--threads', dest='thread_num',
                      default=5, type='int',
                      help='The thread number of program')
    opt_parser.add_option('-e', '--ext', dest='ext',
                      default=None, type='string',
                      help='The web script extension')
    opt_parser.add_option('-w', '--wordlist', dest='wordlist', type='string',
                      help='The word list path')

    (options, args) = opt_parser.parse_args()
    if len(args) < 1 or not options.wordlist:
        opt_parser.print_help()
        sys.exit(EXIT_CODE_ARG)

    word_list = options.wordlist.split(',')
    word_list = [x for x in word_list if x]
    if len(word_list) < 1:
        opt_parser.print_help()
        sys.exit(EXIT_CODE_ARG)

    d = DirScan(target=args[0], thread_num=options.thread_num, ext=options.ext, wordlist=word_list)
    d.run()