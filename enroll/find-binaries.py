#!/usr/bin/env python3

# Use heuristics to identify new files that maybe binaries.
# Flagged files need to be manually inspected and either added to the
# allow list (because they are safe to redistribute), or to the reject list
# (so that they'll be removed prior to orig.tar.xz generation).

import os
import re
import sys


def nameOK(name):
    OKPatterns = [r'\.gitignore', r'AUTHORS', r'FILE.LST', r'Change[lL]og',
                  r'COPYING', r'configure', r'FAQ', r'(GNU)?[Mm]akefile',
                  r'INDEX', r'LICENSE', r'README', r'TODO']
    OKRegexs = map(re.compile, OKPatterns)

    for r in OKRegexs:
        if r.match(name):
            return True
    return False


def extensionOK(name):
    OKExtensions = ['1', '3', 'ASL', 'asi', 'asl', 'aslc', 'Asm', 'asm',
                    'asm16', 'bat', 'bmp', 'c', 'CMM', 'cmm', 'cnf', 'cpp',
                    'css', 'dec', 'decTest', 'dlg', 'dsc', 'docx', 'dsp',
                    'dsw', 'el', 'env', 'fdf', 'g', 'gif', 'H', 'h', 'hpp',
                    'html', 'i', 'idf', 'in', 'inc', 'inf', 'info', 'ini',
                    'lds', 'log', 'lua', 'mak', 'makefile', 'md', 'nasm',
                    'nasmb', 'nsh', 'patch', 'pbxuser', 'pbxproj', 'pdf',
                    'pem', 'pl', 'png', 'pod', 'ps', 'py', 'r', 'rtf', 'S',
                    's', 'sct', 'sh', 'sln', 't', 'template', 'txt', 'uni',
                    'Vfr', 'vcproj', 'vfi', 'vfr', 'xml']
    ext = name.split('.')[-1]

    if ext in OKExtensions:
        return True
    return False


if __name__ == '__main__':
    top = './'
    for root, dirs, files in os.walk(top):
        with open('./enroll/binary-check.allow', 'r') as f:
            allowlist = list(map(lambda s: s.strip(), f.readlines()))

        ret = 0
        for name in files:
            relpath = os.path.join(root, name)[len(top):]
            if relpath in allowlist:
                continue
            if nameOK(name):
                continue
            if extensionOK(name):
                continue
            else:
                sys.stdout.write(
                    "WARNING: Possible binary %s\n" %
                    (os.path.join(root, name))
                )
                ret = -1
    sys.exit(ret)
