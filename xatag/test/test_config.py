#pylint: disable-all
import pytest
import os

from xatag.config import *
import xatag.constants as constants
from xatag.constants import DEFAULT_TAG_KEY

@pytest.fixture
def confdir(tmpdir):
    os.environ[constants.CONFIG_DIR_VAR] = str(tmpdir)
    create_config_dir()
    fname = tmpdir.join('known_tags')
    with fname.open('a') as f:
        f.write(DEFAULT_TAG_KEY + ": tag1; tag2\n")
        f.write("tag3 ; tag4\n")
        f.write("  key1  : val1   ;  val2  \n")
    return tmpdir


def test_create_config_dir(tmpdir, capsys):
    os.environ[constants.CONFIG_DIR_VAR] = str(tmpdir)
    create_config_dir()
    fname = tmpdir.join('known_tags')
    with fname.open('r') as f:
        known_tags_file = f.read()
    assert known_tags_file == constants.DEFAULT_KNOWN_TAGS_FILE
    capsys.readouterr()
    create_config_dir()
    out, err = capsys.readouterr()
    print err
    assert err.startswith('xatag config dir already exists:')

def test_guess_confid_dir(tmpdir):
    assert guess_config_dir("whatever_is_passed") == "whatever_is_passed"
    os.environ[constants.CONFIG_DIR_VAR] = '~/.something-else'
    assert guess_config_dir() == os.path.expanduser("~/.something-else")
    os.environ[constants.CONFIG_DIR_VAR] = ''
    assert guess_config_dir() == os.path.expanduser(constants.DEFAULT_CONFIG_DIR)


def test_find_config_dir(tmpdir):
    # TODO: mock the other possibilities
    os.environ[constants.CONFIG_DIR_VAR] = str(tmpdir)
    assert find_config_dir() == tmpdir
    os.environ[constants.CONFIG_DIR_VAR] = str(tmpdir) + 'this-does-not-exist'
    assert find_config_dir() == None


def test_find_known_tags_file(confdir):
    fname = confdir.join('known_tags')
    assert fname == find_known_tags_file()


def test_find_recoll_fields_file(tmpdir):
    os.environ[constants.CONFIG_DIR_VAR] = str(tmpdir)
    create_config_dir()
    assert find_recoll_fields_file() == tmpdir.join(
        constants.RECOLL_CONFIG_DIR, 'fields')


def test_load_known_tags(confdir):
    kt = load_known_tags()
    print kt
    assert kt == {
        DEFAULT_TAG_KEY: ['tag1', 'tag2', 'tag3', 'tag4'],
        'key1': ['val1', 'val2']
        }


def test_add_known_tags(confdir):
    new_tags = {DEFAULT_TAG_KEY: ['tag5'], 'key1': ['val3'], 'key2': ['newval']}
    add_known_tags(new_tags)
    kt = load_known_tags()
    assert kt == {
        DEFAULT_TAG_KEY: ['tag1', 'tag2', 'tag3', 'tag4', 'tag5'],
        'key1': ['val1', 'val2', 'val3'],
        'key2': ['newval']
        }


def test_make_known_tags_string():
    new_tags = {DEFAULT_TAG_KEY: ['tag5'], 'key1': ['val3'], 'key2': ['newval']}
    tagstr = make_known_tags_string(new_tags)
    assert    tagstr == DEFAULT_TAG_KEY+""":  tag5
key1: val3
key2: newval
"""


def test_update_recoll_fields(confdir, capsys):
    keys = ['newkey', 'new,key:with.punct']
    update_recoll_fields(keys)
    updated_file = (constants.RECOLL_FIELDS_HEAD +
                    constants.RECOLL_FIELDS_PREFIXES +
                    "xa:new:key:with:punct = XYXANEWKEYWITHPUNCT\n" +
                    "xa:newkey = XYXANEWKEY\n" +
                    "xa:tag = XYXATAG\n\n" +
                    constants.RECOLL_FIELDS_STORED +
                    "xa:new:key:with:punct=\n" +
                    "xa:newkey=\n" +
                    "xa:tag=\n\n")

    with open(find_recoll_fields_file(), 'r') as f:
        assert f.read() == updated_file

    # Test that the file won't be overwritten without the HEAD
    updated_file = (#constants.RECOLL_FIELDS_HEAD +
                    constants.RECOLL_FIELDS_PREFIXES +
                    "xa:newkey = XYXANEWKEY\n" +
                    "xa:new:key:with:punct = XYXANEWKEYWITHPUNCT\n" +
                    "xa:tag = XYXATAG\n\n" +
                    constants.RECOLL_FIELDS_STORED +
                    "xa:newkey=\n" +
                    "xa:new:key:with:punct=\n" +
                    "xa:tag=\n\n")


    # remove the line that allows the file to be regenerated
    with open(find_recoll_fields_file(), 'w') as f:
        f.write(updated_file)

    keys = ['lots', 'of', 'new', 'stuff']
    update_recoll_fields(keys)

    with open(find_recoll_fields_file(), 'r') as f:
        assert f.read() == updated_file
