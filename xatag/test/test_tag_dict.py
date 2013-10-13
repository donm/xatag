#pylint: disable-all
import pytest
import xattr

from xatag.tag_dict import *

NON_XATAG_TAGS = {'user.other.tag':  'something'}
XATAG_TAGS = {
    'user.org.xatag.tags': 'tag1;tag2;tag3;tag4;tag5',
    'user.org.xatag.tags.genre': 'indie;pop',
    'user.org.xatag.tags.artist': 'The XX'
    }

@pytest.fixture
def file_with_tags(tmpdir):
    f = tmpdir.join('test.txt')
    path = str(f.dirpath() + '/test.txt')
    f.open('a').close
    x = xattr.xattr(path)
    for k, v in NON_XATAG_TAGS.items():
        x[k] = v
    for k, v in XATAG_TAGS.items():
        x[k] = v
    return path

@pytest.fixture
def tag_dict1():
    return {'': ['some', 'simple', 'tags'],
            'scope': ['home', 'work'],
            'first': ['one', 'tag'],
            'third': ['a', 'b']
            }

@pytest.fixture
def tag_dict2():
    return {'': ['some', 'other', 'tags'],
            'scope': ['hacking', 'programming'],
            'second': ['another', 'tag']
            }

@pytest.fixture
def tag_dict_with_empty_vals():
    return {'': ['some', 'simple', 'other'],
            'scope': [''],
            'second': ['another'],
            'third': ['a', 'b']
            }

# TODO
from StringIO import StringIO
def test_print_file_tags(file_with_tags):
    out = StringIO()
    # print_file_tags(file_with_tags, out=out)
    output = out.getvalue().strip()
    pass

def test_merge_tags(tag_dict1, tag_dict2):
    m = merge_tags(tag_dict1, tag_dict2)
    assert set(m['']) == set(['some', 'other', 'simple', 'tags'])
    assert set(m['scope']) == set(['home', 'work', 'hacking', 'programming'])
    assert set(m['first']) == set(['one', 'tag'])
    assert set(m['second']) == set(['another', 'tag'])

def test_subtract_tags(tag_dict1, tag_dict_with_empty_vals):
    s = subtract_tags(tag_dict1, tag_dict_with_empty_vals)
    assert set(s['']) == set(['tags'])
    assert 'scope' not in s.keys()
    assert s['first'] == tag_dict1['first']
    assert 'second' not in s.keys()
    assert 'third' not in s.keys()

def test_select_tags(tag_dict1, tag_dict_with_empty_vals):
    s = select_tags(tag_dict1, tag_dict_with_empty_vals)
    assert set(s['']) == set(['some', 'simple'])
    assert set(s['scope']) == set(tag_dict1['scope'])
    assert 'first' not in s.keys()
    assert 'second' not in s.keys()
    
