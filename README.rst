######################
le1-ex4-checker
######################

What' this?
=============
実験1課題4のチェッカ

How to use
=============
Run
-------------
::

        % ./check.py [OPTIONS] SOURCE


Option
-------------
::

        -h, --help            show this help message and exit
        -d DELIMITER, --delimiter=DELIMITER
                              最初に読み込む10個の自然数について区切り子を指定します．
        -l, --leak-check      valgrind でメモリリークをチェックします


Requirements
=============
- python (>= 2.6)

Note
=============
- 出力に余分な改行が含まれていると死ぬかも
- ソースいじってstdoutへの出力が print_list 21回分のみになるように調整した方が安全かも

Author
=============
- seikichi@kmc.gr.jp
