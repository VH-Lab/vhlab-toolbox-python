import unittest
import os
import tempfile
import shutil
import vlt.file
import time

class TestFile(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_isfilepathroot(self):
        if os.name == 'nt':
            self.assertTrue(vlt.file.isfilepathroot('C:\\test'))
            self.assertTrue(vlt.file.isfilepathroot('\\test'))
            self.assertFalse(vlt.file.isfilepathroot('test'))
        else:
            self.assertTrue(vlt.file.isfilepathroot('/test'))
            self.assertFalse(vlt.file.isfilepathroot('test'))

    def test_isfile(self):
        f = os.path.join(self.test_dir, 'test.txt')
        with open(f, 'w') as fid:
            fid.write('hello')
        self.assertTrue(vlt.file.isfile(f))
        self.assertFalse(vlt.file.isfile(os.path.join(self.test_dir, 'nonexistent.txt')))

    def test_fullfilename(self):
        f = 'test.txt'
        full = vlt.file.fullfilename(f)
        self.assertTrue(os.path.isabs(full))
        self.assertTrue(full.endswith('test.txt'))

    def test_createpath(self):
        d = os.path.join(self.test_dir, 'subdir', 'subsubdir')
        f = os.path.join(d, 'test.txt')
        b, err = vlt.file.createpath(f)
        self.assertTrue(b)
        self.assertTrue(os.path.isdir(d))

        # Test existing path
        b, err = vlt.file.createpath(f)
        self.assertTrue(b)

    def test_touch(self):
        f = os.path.join(self.test_dir, 'touch_test.txt')
        vlt.file.touch(f)
        self.assertTrue(os.path.isfile(f))

        # Test existing file
        with open(f, 'w') as fid:
            fid.write('content')
        vlt.file.touch(f)
        with open(f, 'r') as fid:
            content = fid.read()
        self.assertEqual(content, 'content') # Should not overwrite

        # Test creating path
        f2 = os.path.join(self.test_dir, 'newdir', 'touch_test2.txt')
        vlt.file.touch(f2)
        self.assertTrue(os.path.isfile(f2))

    def test_text2cellstr(self):
        f = os.path.join(self.test_dir, 'lines.txt')
        with open(f, 'w') as fid:
            fid.write('line1\nline2\nline3')
        lines = vlt.file.text2cellstr(f)
        self.assertEqual(lines, ['line1', 'line2', 'line3'])

    def test_addline(self):
        f = os.path.join(self.test_dir, 'addline.txt')
        b, err = vlt.file.addline(f, 'line1')
        self.assertTrue(b)
        with open(f, 'r') as fid:
            content = fid.read()
        self.assertEqual(content.strip(), 'line1')

        b, err = vlt.file.addline(f, 'line2')
        self.assertTrue(b)
        with open(f, 'r') as fid:
            lines = fid.read().splitlines()
        self.assertEqual(lines, ['line1', 'line2'])

    def test_lock_file(self):
        f = os.path.join(self.test_dir, 'lockfile.txt')
        res, key = vlt.file.checkout_lock_file(f)
        self.assertEqual(res, 1)
        self.assertTrue(os.path.isfile(f))

        # Try to checkout again
        res2, key2 = vlt.file.checkout_lock_file(f, checkloops=1)
        self.assertEqual(res2, -1)

        # Release
        b = vlt.file.release_lock_file(f, key)
        self.assertTrue(b)
        self.assertFalse(os.path.isfile(f))

        # Release with wrong key
        res, key = vlt.file.checkout_lock_file(f)
        b = vlt.file.release_lock_file(f, 'wrongkey')
        self.assertFalse(b)
        self.assertTrue(os.path.isfile(f))
        vlt.file.release_lock_file(f, key)

    def test_isfolder(self):
        d = os.path.join(self.test_dir, 'testdir')
        os.mkdir(d)
        self.assertTrue(vlt.file.isfolder(d))
        self.assertFalse(vlt.file.isfolder(os.path.join(self.test_dir, 'nonexistentdir')))

        f = os.path.join(self.test_dir, 'test.txt')
        with open(f, 'w') as fid:
            fid.write('hello')
        self.assertFalse(vlt.file.isfolder(f))

    def test_textfile2char(self):
        f = os.path.join(self.test_dir, 'char.txt')
        with open(f, 'w') as fid:
            fid.write('hello world')
        s = vlt.file.textfile2char(f)
        self.assertEqual(s, 'hello world')

    def test_str2text(self):
        f = os.path.join(self.test_dir, 'str2text.txt')
        vlt.file.str2text(f, 'hello world')
        with open(f, 'r') as fid:
            content = fid.read()
        self.assertEqual(content, 'hello world')

    def test_dirstrip(self):
        l = ['.', '..', 'file1', '.git', 'file2']
        res = vlt.file.dirstrip(l)
        self.assertEqual(res, ['file1', 'file2'])

        # Test with dicts
        l_dicts = [{'name': '.'}, {'name': 'file1'}, {'name': '.DS_Store'}]
        res_dicts = vlt.file.dirstrip(l_dicts)
        self.assertEqual(res_dicts, [{'name': 'file1'}])

        # Test empty
        self.assertEqual(vlt.file.dirstrip([]), [])

    def test_dirlist_trimdots(self):
        l = ['.', '..', 'file1', '.git', 'file2']
        res = vlt.file.dirlist_trimdots(l)
        self.assertEqual(res, ['file1', 'file2'])

    def test_findfiletype(self):
        # Create structure
        # test_dir/
        #   file1.txt
        #   file2.doc
        #   sub/
        #     file3.txt
        #     file4.doc
        os.makedirs(os.path.join(self.test_dir, 'sub'))

        f1 = os.path.join(self.test_dir, 'file1.txt')
        f2 = os.path.join(self.test_dir, 'file2.doc')
        f3 = os.path.join(self.test_dir, 'sub', 'file3.txt')
        f4 = os.path.join(self.test_dir, 'sub', 'file4.doc')

        for f in [f1, f2, f3, f4]:
            with open(f, 'w') as fid:
                fid.write('')

        files = vlt.file.findfiletype(self.test_dir, '.txt')
        self.assertEqual(len(files), 2)
        self.assertTrue(f1 in files)
        self.assertTrue(f3 in files)

        files_doc = vlt.file.findfiletype(self.test_dir, '.doc')
        self.assertEqual(len(files_doc), 2)
        self.assertTrue(f2 in files_doc)
        self.assertTrue(f4 in files_doc)

    def test_filebackup(self):
        f = os.path.join(self.test_dir, 'backup_test.txt')
        with open(f, 'w') as fid:
            fid.write('content')

        # First backup
        bk1 = vlt.file.filebackup(f)
        self.assertTrue(os.path.isfile(bk1))
        self.assertTrue('bkup001' in bk1)

        # Second backup
        bk2 = vlt.file.filebackup(f)
        self.assertTrue(os.path.isfile(bk2))
        self.assertTrue('bkup002' in bk2)

        # Test delete orig
        bk3 = vlt.file.filebackup(f, DeleteOrig=True)
        self.assertTrue(os.path.isfile(bk3))
        self.assertTrue('bkup003' in bk3)
        self.assertFalse(os.path.isfile(f))

        # Error if exceeded
        # Make a dummy file to simulate limit
        f2 = os.path.join(self.test_dir, 'limit_test.txt')
        with open(f2, 'w') as fid:
            fid.write('c')

        # Manually create backups 1-9
        for i in range(1, 10):
             path = os.path.join(self.test_dir, f'limit_test_bkup{i}.txt')
             with open(path, 'w') as fid: fid.write('c')

        with self.assertRaises(Exception):
             vlt.file.filebackup(f2, Digits=1, ErrorIfDigitsExceeded=True)

        # Let's test just digits=1 with one existing
        f3 = os.path.join(self.test_dir, 'digit_test.txt')
        with open(f3, 'w') as fid: fid.write('c')
        # make backups 1-8
        for i in range(1, 10):
             path = os.path.join(self.test_dir, f'digit_test_bkup{i}.txt')
             with open(path, 'w') as fid: fid.write('c')

        # Now we have bkup1...bkup9. Next one should fail if Digits=1
        with self.assertRaises(Exception):
            vlt.file.filebackup(f3, Digits=1)

    def test_searchreplacefiles_shell(self):
        # Only run on posix
        if os.name != 'posix':
            return

        f1 = os.path.join(self.test_dir, 'replace1.txt')
        f2 = os.path.join(self.test_dir, 'replace2.txt')

        with open(f1, 'w') as fid: fid.write('hello world')
        with open(f2, 'w') as fid: fid.write('hello there')

        # We need to be in the directory for find . to work as expected relative to CWD,
        # or we need to pass a pattern that matches the files.
        # The function executes `find . ...` so it searches CWD.
        # We must change CWD to test_dir.

        cwd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            vlt.file.searchreplacefiles_shell('replace*.txt', 'hello', 'goodbye')

            with open(f1, 'r') as fid: c1 = fid.read()
            with open(f2, 'r') as fid: c2 = fid.read()

            self.assertEqual(c1, 'goodbye world')
            self.assertEqual(c2, 'goodbye there')
        finally:
            os.chdir(cwd)

    def test_manifest(self):
        # Create structure
        # test_dir/
        #   target/
        #     file1.txt
        #     subdir/
        #       file2.txt

        target = os.path.join(self.test_dir, 'target')
        os.makedirs(os.path.join(target, 'subdir'))

        with open(os.path.join(target, 'file1.txt'), 'w') as f: f.write('')
        with open(os.path.join(target, 'subdir', 'file2.txt'), 'w') as f: f.write('')

        fileList, isDir = vlt.file.manifest(target)

        # Paths relative to test_dir (parent of target)
        # Expected:
        # target
        # target/file1.txt
        # target/subdir
        # target/subdir/file2.txt

        # Note: manifest returns contents of the folder AND the subfolders?
        # MATLAB: searchPattern = fullfile(folderPath, '**', '*');
        # This includes everything inside folderPath.
        # But wait, does it include folderPath itself? No, **/* implies inside.
        # But my python implementation used os.walk(absFolderPath).
        # root starts at absFolderPath.
        # I collect dirs and files in root.
        # So I collect everything INSIDE folderPath.

        # However, "Paths are relative to the PARENT directory of folderPath."
        # If I return "target/file1.txt", that is correct.

        # Let's check what I got.
        # fileList should contain:
        # 'target/file1.txt'
        # 'target/subdir'
        # 'target/subdir/file2.txt'

        # Wait, does it return 'target' (the folder itself)?
        # MATLAB: dir(fullfile(folderPath, '**', '*'))
        # If folderPath is /a/b.
        # It scans /a/b/**/*
        # It finds /a/b/c, /a/b/d.
        # It does NOT find /a/b itself usually unless explicitly included.

        # My python code:
        # for root, dirs, files in os.walk(absFolderPath):
        #   for d in dirs: ...
        #   for f in files: ...

        # The first iteration: root is absFolderPath.
        # dirs includes 'subdir'.
        # files includes 'file1.txt'.
        # So 'subdir' is added. 'file1.txt' is added.
        # Neither represents absFolderPath itself.

        # So 'target' is NOT in the list.
        # The paths returned are 'target/file1.txt', 'target/subdir', ...

        expected = [
            os.path.join('target', 'file1.txt'),
            os.path.join('target', 'subdir'),
            os.path.join('target', 'subdir', 'file2.txt')
        ]

        # Sort expected
        expected.sort()

        self.assertEqual(len(fileList), 3)
        self.assertEqual(sorted(fileList), expected)

        # Check isDir
        # file1.txt -> False
        # subdir -> True
        # subdir/file2.txt -> False

        idx_sub = fileList.index(os.path.join('target', 'subdir'))
        self.assertTrue(isDir[idx_sub])

        idx_f1 = fileList.index(os.path.join('target', 'file1.txt'))
        self.assertFalse(isDir[idx_f1])

    def test_findfilegroups(self):
        # Create structure
        # test_dir/
        #   g1/
        #     f_1.txt
        #     f_1.doc
        #     f_2.txt
        #     f_2.doc
        #   g2/
        #     orphan.txt

        g1 = os.path.join(self.test_dir, 'g1')
        g2 = os.path.join(self.test_dir, 'g2')
        os.makedirs(g1)
        os.makedirs(g2)

        with open(os.path.join(g1, 'f_1.txt'), 'w') as f: f.write('')
        with open(os.path.join(g1, 'f_1.doc'), 'w') as f: f.write('')
        with open(os.path.join(g1, 'f_2.txt'), 'w') as f: f.write('')
        with open(os.path.join(g1, 'f_2.doc'), 'w') as f: f.write('')
        with open(os.path.join(g2, 'orphan.txt'), 'w') as f: f.write('')

        # Test finding pairs f_#.txt and f_#.doc
        params = ['f_#.txt', 'f_#.doc']
        groups = vlt.file.findfilegroups(self.test_dir, params)

        self.assertEqual(len(groups), 2)

        # Sort groups by the first file in the pair to ensure order
        groups.sort(key=lambda x: x[0])

        # Expected
        # [g1/f_1.txt, g1/f_1.doc]
        # [g1/f_2.txt, g1/f_2.doc]

        self.assertTrue(os.path.join(g1, 'f_1.txt') in groups[0])
        self.assertTrue(os.path.join(g1, 'f_1.doc') in groups[0])
        self.assertTrue(os.path.join(g1, 'f_2.txt') in groups[1])
        self.assertTrue(os.path.join(g1, 'f_2.doc') in groups[1])

        # Test no match
        params2 = ['f_#.txt', 'f_#.missing']
        groups2 = vlt.file.findfilegroups(self.test_dir, params2)
        self.assertEqual(len(groups2), 0)

    def test_filenamesearchreplace(self):
        # Create
        # f1.txt
        # sub/f2.txt

        f1 = os.path.join(self.test_dir, 'f1.txt')
        d = os.path.join(self.test_dir, 'sub')
        os.makedirs(d)
        f2 = os.path.join(d, 'f2.txt')

        with open(f1, 'w') as f: f.write('1')
        with open(f2, 'w') as f: f.write('2')

        # Replace .txt with .doc
        vlt.file.filenamesearchreplace(self.test_dir, '.txt', '.doc', recursive=True, deleteOriginals=True)

        self.assertFalse(os.path.isfile(f1))
        self.assertFalse(os.path.isfile(f2))

        self.assertTrue(os.path.isfile(os.path.join(self.test_dir, 'f1.doc')))
        self.assertTrue(os.path.isfile(os.path.join(d, 'f2.doc')))

    def test_structArray(self):
        f = os.path.join(self.test_dir, 'struct.txt')

        data = [
            {'name': 'Alice', 'age': '30'},
            {'name': 'Bob', 'age': '25'}
        ]

        vlt.file.saveStructArray(f, data)

        loaded = vlt.file.loadStructArray(f)

        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0]['name'], 'Alice')
        self.assertEqual(loaded[0]['age'], '30')
        self.assertEqual(loaded[1]['name'], 'Bob')
        self.assertEqual(loaded[1]['age'], '25')

    def test_fileobj(self):
        f = os.path.join(self.test_dir, 'fileobj.bin')

        # Test write
        fo = vlt.file.fileobj()
        fo.fopen(filename=f, permission='w')
        count = fo.fwrite([65, 66, 67], 'uint8')
        self.assertEqual(count, 3)
        fo.fclose()

        self.assertTrue(os.path.isfile(f))

        # Test read
        fo = vlt.file.fileobj()
        fo.fopen(filename=f, permission='r')
        data, count = fo.fread(count=3, precision='uint8')
        self.assertEqual(count, 3)
        self.assertEqual(data, [65, 66, 67])
        fo.fclose()

        # Test char write/read
        f2 = os.path.join(self.test_dir, 'fileobj.txt')
        fo = vlt.file.fileobj()
        fo.fopen(filename=f2, permission='w')
        fo.fwrite('Hello', 'char')
        fo.fclose()

        fo = vlt.file.fileobj()
        fo.fopen(filename=f2, permission='r')
        data, count = fo.fread(count=5, precision='char')
        # Expect characters
        self.assertEqual(data, ['H', 'e', 'l', 'l', 'o'])
        fo.fclose()

    def test_dumbjsondb(self):
        db_path = os.path.join(self.test_dir, 'mydb.json')
        db = vlt.file.dumbjsondb('new', db_path)

        # Add entries
        for i in range(1, 6):
            doc = {'id': 2000 + i, 'value': i}
            db.add(doc)

        ids = db.alldocids()
        self.assertEqual(len(ids), 5)
        self.assertIn('2001', ids)

        # Read
        doc, ver = db.read(2001)
        self.assertEqual(doc['value'], 1)
        self.assertEqual(ver, 0)

        # Binary file
        fid, key, ver = db.openbinaryfile(2001)
        self.assertIsNotNone(fid)
        fid.write(b'binarydata')
        db.closebinaryfile(fid, key, 2001, ver)

        # Verify binary
        fid, key, ver = db.openbinaryfile(2001)
        fid.seek(0)
        data = fid.read()
        self.assertEqual(data, b'binarydata')
        db.closebinaryfile(fid, key, 2001, ver)

        # Remove
        db.remove(2002)
        ids = db.alldocids()
        self.assertEqual(len(ids), 4)
        self.assertNotIn('2002', ids)

        # Update version
        doc2 = {'id': 2005, 'value': 20}
        db.add(doc2, Overwrite=2)

        ver_list = db.docversions(2005)
        self.assertEqual(len(ver_list), 2)
        self.assertIn(0, ver_list)
        self.assertIn(1, ver_list)

        doc_v1, _ = db.read(2005, 1)
        self.assertEqual(doc_v1['value'], 20)

        # Search
        docs, _ = db.search({}, ['value', 20])
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0]['id'], 2005)

        docs2, _ = db.search({}, ['value', 999])
        self.assertEqual(len(docs2), 0)

        # Clear
        db.clear('yes')
        self.assertEqual(len(db.alldocids()), 0)

if __name__ == '__main__':
    unittest.main()
