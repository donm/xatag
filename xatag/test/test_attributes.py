import pytest

from xatag.tag import Tag
from xatag.attributes import *

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

def test_read_tag_keys(file_with_tags):
    keys = read_tag_keys(file_with_tags)  
    assert set(keys) == set(['', 'genre', 'artist'])

def test_read_tags_as_dict(file_with_tags):
    tags = read_tags_as_dict(file_with_tags)  
    assert tags == {'': ['tag1','tag2','tag3','tag4','tag5'],
                    'genre': ['indie','pop'],
                    'artist': ['The XX']
                    }

def test_is_xatag_xattr_key():
    assert is_xatag_xattr_key('user.org.xatag.tags')
    assert is_xatag_xattr_key('user.org.xatag.tags.whatever')
    assert is_xatag_xattr_key('org.xatag.tags')
    assert is_xatag_xattr_key('org.xatag.tags.whatever')
    assert not is_xatag_xattr_key('anything else')

def test_xatag_to_xattr_key():
    assert xatag_to_xattr_key('') == 'user.org.xatag.tags'
    assert xatag_to_xattr_key('tags') == 'user.org.xatag.tags'
    assert xatag_to_xattr_key('other') == 'user.org.xatag.tags.other'
    tag = Tag('genre', 'classical')
    assert xatag_to_xattr_key(tag) == 'user.org.xatag.tags.genre'

def test_xattr_value_to_list():
    assert xattr_value_to_list('') == []
    assert xattr_value_to_list(' \n \t') == []
    assert xattr_value_to_list('one') == ['one']
    assert xattr_value_to_list('one tag') == ['one tag']
    assert xattr_value_to_list('one;two;three') == ['one', 'two', 'three']
    assert (xattr_value_to_list('one;two words;three') ==
            ['one', 'two words', 'three'])
    assert (xattr_value_to_list('one; two words   ;\nthree\t') 
            == ['one', 'two words', 'three'])

def test_list_to_xattr_value():
    assert list_to_xattr_value([]) == ''
    assert list_to_xattr_value(["one", "   two words\n"]) == 'one;two words'

def test_remove_tag_values_from_xattr_value():
    assert remove_tag_values_from_xattr_value('one', 'one') == ''
    assert remove_tag_values_from_xattr_value('one;two;three;four',
                                              ['two','four']) == 'one;three'
    assert remove_tag_values_from_xattr_value('', ['notfound']) == ''

    assert remove_tag_values_from_xattr_value('one', 'one', True) == 'one'
    assert remove_tag_values_from_xattr_value('one;two;three;four',
                                              ['two','five'], True) == 'two'
    assert remove_tag_values_from_xattr_value('one;two', [''], True) == 'one;two'
    assert remove_tag_values_from_xattr_value('', ['notfound'], True) == ''



