# -*- coding: utf-8 -*-

from __future__ import print_function

import re
import os
import sys
import unittest

lib_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, lib_dir)

import upyun

try:
    import config
except ImportError:
    print('plz make config.py refer to config.py.sample in the tests dir')
    exit(1)


# ------------------ CONFIG ---------------------
BUCKETNAME = config.bucketname
USERNAME = config.username
PASSWORD = config.password
# -----------------------------------------------


ascii_content = '''
    abcdefghijklmnopqrstuvwxyz
    01234567890112345678901234
    !@#$%^&*()-=[]{};':',.<>/?
    01234567890112345678901234
    abcdefghijklmnopqrstuvwxyz
'''


class TestUpYun(unittest.TestCase):

    def setUp(self):
        self.up = upyun.UpYun(BUCKETNAME, USERNAME, PASSWORD, timeout=30,
                         endpoint=upyun.ED_AUTO)
        self.rootpath = '/upyun-python-sdk/'
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.img_dir = os.path.join(self.test_dir, 'img')

    def test_binary(self):
        img_name = '%sunix.png' % self.rootpath
        f1 = open(os.path.join(self.img_dir, 'unix.png'))
        len_f1 = os.fstat(f1.fileno()).st_size
        self.up.put(img_name, f1)
        f1.close()

        f2 = open(os.path.join(self.img_dir, 'xinu.png'), 'w')
        self.up.get(img_name, value=f2)
        f2.flush()
        len_f2 = os.fstat(f2.fileno()).st_size
        f2.close()

        self.assertEqual(len_f1, len_f2)

    def test_ascii(self):
        ascii_file = '%sascii.txt' % self.rootpath
        self.up.put(ascii_file, ascii_content, checksum=True)
        res = self.up.get(ascii_file)
        self.assertEqual(ascii_content, res)

    def test_dir(self):
        self.up.mkdir('%stemp' % self.rootpath)
        res = self.up.getlist('/')
        self.assertIsNotNone(res)
        d = None
        for i in res:
            if i['name'] == self.rootpath.strip('/'):
                d = i
                break
        self.assertIsNotNone(d)
        self.assertEqual(d['type'], 'F')
        self.assertEqual(d['size'], '0')

    def test_getinfo(self):
        img_name = '%sunix.png' % self.rootpath
        with open(os.path.join(self.img_dir, 'unix.png')) as f:
            self.up.put(img_name, f)
        res = self.up.getinfo(img_name)
        self.assertEqual(res['file-size'], '90833')
        self.assertEqual(res['file-type'], 'file')

    def test_delete(self):
        img_name = '%sunix.png' % self.rootpath
        with open(os.path.join(self.img_dir, 'unix.png')) as f:
            self.up.put(img_name, f)
        res = self.up.getinfo(img_name)
        self.assertIsNotNone(res)

        self.up.delete(img_name)
        try:
            self.up.getinfo(img_name)
        except upyun.UpYunServiceException as e:
            self.assertEqual(e.status, 404)
        else:
            raise Exception('upyun exception')

        dir_name = '%stemp' % self.rootpath
        self.up.mkdir(dir_name)
        res = self.up.getinfo(dir_name)
        self.assertIsNotNone(res)

        self.up.delete(dir_name)
        try:
            self.up.getinfo(dir_name)
        except upyun.UpYunServiceException as e:
            self.assertEqual(e.status, 404)
        else:
            raise Exception('upyun exception')

    def test_usage(self):
        res = self.up.usage()
        self.assertTrue(int(res) > 0)
        self.assertTrue(re.match('\d+', res))


if __name__ == '__main__':
    unittest.main()
