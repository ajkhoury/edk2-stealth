#!/usr/bin/env python3

import os
import sys

if __name__ == '__main__':
    with open('./enroll/binary-check.remove', 'r') as f:
        removelist = list(map(lambda s: s.strip(), f.readlines()))

    for path in removelist:
        sys.stdout.write("Removing %s\n" % (path))
        os.unlink(path)
