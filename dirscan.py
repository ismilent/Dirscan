#!/usr/bin/env python
# coding:utf-8

import sys
import optparse
import requests
import threading
import time
import signal

try:
    import queue as Queue
except Exception as e:
    import Queue

try:
    from urllib import parse as urlparse
except Exception as e:
    import urlparse

EXIT_CODE_ARG = -1
USER_AGENT = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'}

global is_exit
is_exit = False


# 退出信号处理
def signal_handler(signum, frame):
    global is_exit
    is_exit = True
    sys.exit()


# patch url
def patch_url(url):
    res = urlparse.urlparse(url)
    if not res.scheme:
        url = 'http://' + url.strip()
    if res.path[-1] != '/':
        url += '/'
    return url


class DirScan(object):
    """
    Class DirScan
    """
    _ext = None  # 扩展名
    _queue = Queue.Queue()
    _word_list = []  # 字典
    _thread_list = []  # 线程队列
    _lock = threading.Lock()  # 线程锁
    _custom_headers = USER_AGENT  # 自定义
    _target = []  # 目标地址

    def __init__(self, target=None, thread_num=20, ext=None, wordlist=None, recursion=2, timeout=5, target_file=None):
        if target:
            self._target.append(patch_url(target))
        if target_file:
            self._target.extend(self._load_target_file(target_file))
        self._thread_num = thread_num
        if ext:
            self._ext = ext
        if wordlist:
            self._word_list = word_list

        self._recursion = recursion  # 循环深度
        self._timeout = timeout  # 超时
        self._load_dir_dict()
        print(self._target)

    def _load_dir_dict(self):
        for word_file_path in self._word_list:
            try:
                with open(word_file_path, 'r') as f:
                    [self._queue.put(line) for line in f if line]
            except Exception as e:
                print(str(e))
                sys.exit(-2)

    def _load_target_file(self, target_file):
        with open(target_file, 'r') as f:
            return [patch_url(target) for target in f]

    def _scan(self, domain):
        global is_exit
        while not is_exit:
            if self._queue.empty():
                break
            try:
                sub = self._queue.get_nowait()
                target = domain + sub.strip('\n')
                self._lock.acquire()
                r = requests.get(target, headers=self._custom_headers, timeout=self._timeout, stream=True)
                code = r.status_code
                if code != 404:
                    print('[+][CODE %d] %s' % (code, target))
            except Exception as e:
                print('Thread...' + str(e) + sub)
            finally:
                time.sleep(0)
                self._lock.release()

    def run(self):
        for target in self._target:
            for i in range(self._thread_num):
                try:
                    requests.get(target)
                    t = threading.Thread(target=self._scan, args=(target,), name=str(i))
                    self._thread_list.append(t)
                    t.start()
                except Exception as e:
                    print('[-] failed to connect %s' % target)
                    # print(str(e))
            for t in self._thread_list:
                t.join()

        print('Finished.')


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    opt_parser = optparse.OptionParser('Usage: %prog [options] http://url/')
    opt_parser.add_option('-f', '--file', dest='target_file',
                          default=None, type='string', help='the target file')
    opt_parser.add_option('-t', '--threads', dest='thread_num',
                          default=20, type='int',
                          help='the thread number of program')
    opt_parser.add_option('-e', '--ext', dest='ext',
                          default=None, type='string',
                          help='the web script extension')
    opt_parser.add_option('-w', '--wordlist', dest='wordlist', type='string',
                          default='common.txt', help='the word list path')
    opt_parser.add_option('-r', '--recursive', dest='recursive',
                          default=2, type='int', help='the deep of scan')

    (options, args) = opt_parser.parse_args()
    if options.target_file:
        target = None
    else:
        if len(args) < 1:
            opt_parser.print_help()
            sys.exit(EXIT_CODE_ARG)
        target = args[0]

    # 获取文件列表
    word_list = options.wordlist.split(',')
    word_list = [x for x in word_list if x]
    if len(word_list) < 1:
        opt_parser.print_help()
        sys.exit(EXIT_CODE_ARG)
    if target:
        d = DirScan(target=target, thread_num=options.thread_num, ext=options.ext, wordlist=word_list,
                    target_file=options.target_file)
    else:
        d = d = DirScan(thread_num=options.thread_num, ext=options.ext, wordlist=word_list,
                        target_file=options.target_file)
    d.run()
