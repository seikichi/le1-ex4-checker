#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import re
from random import randint
from optparse import OptionParser
from subprocess import Popen, STDOUT, PIPE
from commands import getstatusoutput

MIN_VALUE = 1
MAX_VALUE = 9999

# オプション設定
parser = OptionParser()
parser.add_option("-d", "--delimiter", dest="delimiter", default="\n",
                  help=u"最初に読み込む10個の自然数について区切り子を指定します．(デフォルトは '\n')")
parser.add_option("-l", "--leak-check", dest="leack_check", default=False,
                  action="store_true", help=u"valgrind でメモリリークをチェックします")
options, args = parser.parse_args()

if not args:
    print >>sys.stderr, "check.py [options] source-code"
    exit(-1)
source = args[0]

# ソースをコンパイル (エラーなら終了)
status, output = getstatusoutput('LANG=C gcc -Wall -Wextra %s' %  source)
if status:
    print >>sys.stderr, "[Compile Error]"
    print >>sys.stderr, output
    exit(-1)
print >>sys.stderr, "[Compile Succceeded (%d warnings)]" % output.count('warning')

# テストケース生成
testcases = [
    [MIN_VALUE] * 30,
    [MAX_VALUE] * 30,
]

# とりあえず100個ランダムに
for i in range(100):
    testcases.append([randint(MIN_VALUE, MAX_VALUE) for _ in range(30)])
# ランダムだと delete が発生しにくいので，範囲を絞って1000個
for i in range(500):
    testcases.append([randint(MIN_VALUE, MIN_VALUE+10) for _ in range(30)])
for i in range(500):
    testcases.append([randint(MAX_VALUE-20, MAX_VALUE) for _ in range(30)])

# 解をチェックするために insert と delete を作っとく
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
pat = re.compile(r'^((\d+)\s*)*$')
result = "Accepted"

for i, testcase in enumerate(testcases):
    print "Case %d:" % (i+1),
    ok = True

    # プロセスに与える入力を作成
    input = ""
    input += options.delimiter.join(map(str, testcase[0:10])) + '\n'
    input += '\n'.join(map(str, testcase[10:30])) + '\n'

    # 実行して出力を output に格納
    proc = Popen(['./a.out'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    print >>proc.stdin, input
    output, _ = proc.communicate()
    # 実行時エラー？
    if proc.returncode:
        print "Runtime Error"
        result = "Runtime Error"
        break

    def check(expected, actual, error_type):
        if expected != actual:
            print "Wrong Answer (%s error)" % error_type
            print "\texpected: %s" % repr(expected)
            print "\t but was: %s" % repr(actual)
            return False
        else: return True

    ls = []
    for line in output.split('\n'):
        line = line.strip()
        if pat.match(line): ls.append(map(int, line.split()))

    # 入力の最初の10個から開始して
    l = testcase[0:10]
    ok = check(l, ls[0], 'initialize')

    # 10回挿入して
    for i in range(10):
        if not ok: break
        l = insert(testcase[10+i], l)
        ok = check(l, ls[1+i], 'insert')
    # 10回削除
    for i in range(10):
        if not ok: break
        l = delete(testcase[10+10+i], l)
        ok = check(l, ls[1+10+i], 'delete')

    if not ok:
        result = "Wrong Answer"
        break

    res = "Passed"
    if options.leack_check:
        # valgrind で再チェック
        proc = Popen(['valgrind', '--leak-check=full', './a.out'], stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        print >>proc.stdin, input
        output = proc.communicate()[0]
        if int(re.search(r'(\d+)\s+errors', output).group(1)):
            leak = True
            res = "Memory Leak"
    print res

# 結果を出力
if leak:
    result += "(!!! Memory Leak !!!)"
print "\n!!!%s!!!" % result

