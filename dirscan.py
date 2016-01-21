#!/usr/bin/env python
# coding:utf-8

import sys
import optparse
import requests
import threading
import time
import signal
import copy
from multiprocessing import cpu_count
from multiprocessing import Manager
import multiprocessing

try:
    import queue as Queue
except Exception as e:
    import Queue

try:
    from urllib import parse as urlparse
except Exception as e:
    import urlparse

EXIT_CODE_ARG = -1
USER_HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'}

global is_exit
is_exit = False


# 退出信号处理
def signal_handler(signum, frame):
    global is_exit
    is_exit = True
    sys.exit()


def print_line(line):
    sys.stdout.write('\r' + line.strip())
    sys.stdout.flush()
    # time.sleep(0.05)
    sys.stdout.write('\r' + ' ' * len(line))
    sys.stdout.flush()


# patch url
def patch_url(url):
    res = urlparse.urlparse(url.strip())
    if not res.scheme:
        url = 'http://' + url.strip()
    return url


MAX_PROCESS_NUM = cpu_count()


# 线程函数
def scan(domain, queue, timeout, headers, lock):
    global is_exit
    while not is_exit:
        if queue.empty():
            break
        try:
            lock.acquire()
            sub = queue.get_nowait()
            target = domain + sub.strip('\n')
            r = requests.get(target, headers=headers, timeout=timeout, stream=True)
            code = r.status_code
            # print_line('[x][Scan URL:] %s' % (target,))
            if code != 404:
                print('\r[+][CODE %d] %s' % (code, target.strip()))
        except Exception as e:
            pass
            # print('Thread...' + str(e) + sub)
        finally:
            lock.release()
            time.sleep(0)


# 进程函数
def Worker(target, queue, thread_num, timeout, headers):
    thread_list = []
    lock = threading.Lock()
    for i in range(thread_num):
        t = threading.Thread(target=scan, args=(target, queue, timeout, headers, lock))
        thread_list.append(t)
        t.start()
    for t in thread_list:
        t.join()


class DirScan(object):
    """
    Class DirScan
    """
    _ext = None  # 扩展名
    _word_list = []  # 字典
    _process_list = []  # 线程队列
    _lock = threading.Lock()  # 线程锁
    _custom_headers = USER_HEADERS  # 自定义
    _target = []  # 目标地址
    _process_count = 0
    _manager = Manager()
    _queue = _manager.Queue()

    def __init__(self, target=None, process_num=10, thread_num=10, ext=None, wordlist=None, recursion=2,
                 timeout=5,
                 target_file=None):
        if target:
            self._target.append(patch_url(target))
        if target_file:
            self._target.extend(self._load_target_file(target_file))
        self._thread_num = thread_num
        if ext:
            self._ext = ext
        if wordlist:
            self._word_list = word_list

        self._process_num = process_num  # 进程数量
        self._recursion = recursion  # 循环深度
        self._timeout = timeout  # 超时
        self._pool = multiprocessing.Pool(processes=MAX_PROCESS_NUM)
        self._load_dir_dict()

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

            # def _Worker(self, target, queue, thread_num):

    def run(self):
        for target in self._target:
            queue = copy.copy(self._queue)
            # print 'qsize: %d' % queue.qsize()
            try:
                requests.get(target, timeout=3)
                for i in range(self._process_num):
                    if self._process_count < self._process_num:
                        # target, queue, thread_num, timeout, headers
                        result = self._pool.apply_async(Worker, (
                            target, queue, self._thread_num, self._timeout, self._custom_headers))
                        self._process_count += 1
                self._pool.close()
                self._pool.join()
                if result.successful():
                    print 'successful'
                self._process_count = 0
            except Exception as e:
                print str(e)
                print('[-] failed to connect %s' % target)

        print('\r[+]Finished.')


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    opt_parser = optparse.OptionParser('Usage: %prog [options] http://url/')
    opt_parser.add_option('-f', '--file', dest='target_file',
                          default=None, type='string', help='the target file')
    opt_parser.add_option('-t', '--threads', dest='thread_num',
                          default=10, type='int',
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
