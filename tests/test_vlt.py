import os
import shutil
import pytest
import numpy as np
import vlt.app.log
import vlt.data
import vlt.file

def test_vlt_app_log():
    if os.path.exists('test_logs'):
        shutil.rmtree('test_logs')
    os.makedirs('test_logs')

    sys_log = os.path.join('test_logs', 'sys.log')
    err_log = os.path.join('test_logs', 'error.log')
    debug_log = os.path.join('test_logs', 'debug.log')

    log = vlt.app.log.Log(system_logfile=sys_log, error_logfile=err_log, debug_logfile=debug_log, system_verbosity=1)

    assert os.path.exists(sys_log)

    log.msg('system', 1, 'test message')

    with open(sys_log, 'r') as f:
        content = f.read()
        assert 'test message' in content
        assert 'SYSTEM' in content

    shutil.rmtree('test_logs')

def test_vlt_data_assign():
    d = vlt.data.assign('a', 1, 'b', 2)
    assert d == {'a': 1, 'b': 2}

    d2 = vlt.data.assign({'a': 1, 'b': 2})
    assert d2 == {'a': 1, 'b': 2}

def test_vlt_data_cell2str():
    res = vlt.data.cell2str(['a', 1])
    assert res == "['a', 1]"
    assert vlt.data.cell2str([]) == '[]'

def test_vlt_data_cellarray2mat():
    c = [[1, 2, 3], [4, 5]]
    m = vlt.data.cellarray2mat(c)
    assert m.shape == (3, 2)
    assert m[0, 0] == 1
    assert m[1, 0] == 2
    assert m[2, 0] == 3
    assert m[0, 1] == 4
    assert m[1, 1] == 5
    assert np.isnan(m[2, 1])

def test_vlt_data_celloritem():
    l = [10, 20, 30]
    assert vlt.data.celloritem(l, 1) == 20
    assert vlt.data.celloritem(100) == 100

    # Check bounds
    with pytest.raises(IndexError):
        vlt.data.celloritem(l, 5)

def test_vlt_data_colvec():
    a = [[1, 2], [3, 4]]
    v = vlt.data.colvec(a)
    assert v.shape == (4, 1)
    # Default numpy flatten is row-major (C-style)
    # [1, 2, 3, 4]
    assert v[0, 0] == 1
    assert v[1, 0] == 2
    assert v[2, 0] == 3
    assert v[3, 0] == 4

def test_vlt_data_conditional():
    assert vlt.data.conditional(1, 'a', 'b') == 'a'
    assert vlt.data.conditional(0, 'a', 'b') == 'b'
    assert vlt.data.conditional(-1, 'a', 'b') == 'b'
