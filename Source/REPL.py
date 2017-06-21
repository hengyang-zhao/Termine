#!/usr/bin/env python3

from Shell import Shell

def Main():

    s = Shell()

    while True:

        a = input("termine> ")
        s.run(a)

        for o in s.getOutput():
            print('out: %s' % o)

if __name__ == '__main__':
    Main()
