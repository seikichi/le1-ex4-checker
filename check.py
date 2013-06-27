#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import sys

from commands import getstatusoutput
from optparse import OptionParser
from random import randint
from subprocess import Popen, STDOUT, PIPE

MIN_VALUE = 1
MAX_VALUE = 9999

# set options
parser = OptionParser()
parser.add_option('-d', '--delimiter', dest='delimiter', default='\n',
                  help=u'最初に読み込む10個の自然数の区切り子を指定します')
parser.add_option('-l', '--leak-check', dest='leack_check', default=False,
                  action='store_true', help=u'valgrind でメモリリークをチェックします')
parser.add_option('-e', '--extra-exercise-mode', dest='extra_exercise_mode', default=False,
                  action='store_true', help=u'発展課題モード．insert と delete が交互に発生します．')
options, args = parser.parse_args()

if not args:
    print >>sys.stderr, 'check.py [options] source-code'
    exit(-1)
source = args[0]

# build source
status, output = getstatusoutput('LANG=C gcc -Wall -Wextra %s' %  source)
if status:
    print >>sys.stderr, '[Compile Error]'
    print >>sys.stderr, output
    exit(-1)
print >>sys.stderr, '[Compile Succceeded (%d warnings)]' % output.count('warning')

def make_extra_exercise_testcases():
    testcases = []
    testcases.append(
        [MIN_VALUE] * 10 +
        ['delete %d' % MIN_VALUE] +
        ['insert %d' % MIN_VALUE] +
        ['delete %d' % MIN_VALUE] +
        ['insert %d' % MIN_VALUE] +
        ['delete %d' % MIN_VALUE])
    # 10 insert & 10 delete
    testcases.append(
        [MIN_VALUE] * 10 +
        ['insert %d' % MIN_VALUE for _ in range(10)] +
        ['delete %d' % MIN_VALUE for _ in range(10)])
    testcases.append(
        [MAX_VALUE] * 10 +
        ['insert %d' % MAX_VALUE for _ in range(10)] +
        ['delete %d' % MAX_VALUE for _ in range(10)])
    for i in range(300):
        testcases.append(
            [randint(MIN_VALUE, MIN_VALUE+10) for _ in range(10)] +
            ['insert %d' % randint(MIN_VALUE, MIN_VALUE+10) for _ in range(10)] +
            ['delete %d' % randint(MIN_VALUE, MIN_VALUE+10) for _ in range(10)])
    for i in range(500):
        # (insert (rand(5, 10) times) -> delete (rand(5, 10) times)) * 20
        t = [randint(MIN_VALUE, MIN_VALUE+10) for _ in range(10)]
        for i in range(20):
            if i % 2 == 0:
                t.extend(['insert %d' % randint(MIN_VALUE, MIN_VALUE+10) for _ in range(randint(5, 20))])
            else:
                t.extend(['delete %d' % randint(MIN_VALUE, MIN_VALUE+10) for _ in range(randint(5, 20))])
        testcases.append(t)
    # 1000 insert ;-p
    testcases.append(
        [randint(MIN_VALUE, MIN_VALUE+10) for _ in range(10)] +
        ['insert %d' % randint(MIN_VALUE, MIN_VALUE+10) for _ in range(1000)])
    return testcases

def make_testcases():
    testcases = [
        [MIN_VALUE] * 30,
        [MAX_VALUE] * 30,
    ]
    for i in range(300):
        testcases.append([randint(MIN_VALUE, MIN_VALUE+10) for _ in range(30)])
    for i in range(300):
        testcases.append([randint(MAX_VALUE-20, MAX_VALUE) for _ in range(30)])
    for i in range(100):
        testcases.append([randint(MIN_VALUE, MAX_VALUE) for _ in range(30)])
    return testcases

# insert & delte functions (for verification)
def insert(x, l):
    ret = l[:]
    for i, y in enumerate(ret):
        if x <= y:
            ret.insert(i, x)
            break
    else:
        ret.insert(len(ret), x)
    return ret

def delete(x, l):
    ret = l[:]
    while x in ret:
        ret.remove(x)
    return ret

leak = False
wrong_output_num = False
pat = re.compile(r'^((\d+)\s*)*$')
result = 'Accepted'

if options.extra_exercise_mode:
    testcases = make_extra_exercise_testcases()
else:
    testcases = make_testcases()

for i, testcase in enumerate(testcases):
    print 'Case %d:' % (i+1),
    ok = True
    res = 'Passed'

    # プロセスに与える入力を作成
    input = ''
    input += options.delimiter.join(map(str, testcase[0:10])) + '\n'
    input += '\n'.join(map(str, testcase[10:])) + '\n'

    # 実行して出力を output に格納
    proc = Popen(['./a.out'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    print >>proc.stdin, input
    output, _ = proc.communicate()
    # 実行時エラー？
    if proc.returncode:
        print 'Runtime Error'
        print '\tinput: %s' % repr(input)
        result = 'Runtime Error'
        break

    def check(expected, actual, error_type):
        if expected != actual:
            print 'Wrong Answer (%s error)' % error_type
            print '\texpected: %s' % repr(expected)
            print '\t but was: %s' % repr(actual)
            print '\tinput:%s' % repr(input)
            return False
        else: return True

    ls = []
    for line in output.split('\n'):
        line = line.strip()
        if pat.match(line):
          ls.append(map(int, line.split()))

    # 出力の行数が足りてない場合は
    # 「deleteで空になったら終了するプログラム」だと見なす
    if len(ls) < len(testcase) - 10 + 2:
        wrong_output_num = True
        while len(ls) <= len(testcase) - 10 + 2:
            ls.append([])
        res = 'Presentation Error'

    # 入力の最初の10個から開始して
    l = testcase[0:10]
    ok = check(l, ls[0], 'initialize')

    if not options.extra_exercise_mode:
        # 10回挿入して
        for j in range(10):
            if not ok: break
            l = insert(testcase[10+j], l)
            ok = check(l, ls[1+j], 'insert')
        # 10回削除
        for j in range(10):
            if not ok: break
            l = delete(testcase[10+10+j], l)
            ok = check(l, ls[1+10+j], 'delete')
    else:
        for j, operation in enumerate(testcase[10:]):
            if not ok: break
            operation_type, value = operation.split()
            value = int(value)
            if operation_type.startswith('insert'):
                l = insert(value, l)
            else:
                l = delete(value, l)
            ok = check(l, ls[1 + j], operation_type)

    if not ok:
        result = 'Wrong Answer'
        break

    if options.leack_check:
        # valgrind で再チェック
        proc = Popen(['valgrind', '--leak-check=full', './a.out'],
                     stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        print >>proc.stdin, input
        output = proc.communicate()[0]
        if int(re.search(r'(\d+)\s+errors', output).group(1)):
            leak = True
            res = 'Error in valgrind'
    print res
    if res not in  ('Passed', 'Presentation Error'):
        print '\tinput:%s' % repr(input)

# 結果を出力
if leak:
    result += ' (Error in valgrind) '
if wrong_output_num:
    result += ' (Presentation Error!)'

print 'Result: %s!!!' % result


