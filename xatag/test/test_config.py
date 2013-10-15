#pylint: disable-all
import pytest
import os

from xatag.config import *
import xatag.constants as constants

@pytest.fixture
def tmp_known_tags(tmpdir):
    os.environ[constants.CONFIG_DIR_VAR] = str(tmpdir)
    fname = tmpdir.join('known_tags')
    with fname.open('a') as f:
        f.write("tags: tag1; tag2\n")
        f.write("tag3 ; tag4\n")
        f.write("  key1  : val1   ;  val2  \n")
    return fname


def test_get_config_dir(tmpdir):
    # TODO: mock the other possibilities
    os.environ[constants.CONFIG_DIR_VAR] = str(tmpdir)
    assert get_config_dir() == tmpdir
    os.environ[constants.CONFIG_DIR_VAR] = str(tmpdir) + 'this-does-not-exist'
    assert get_config_dir() == None


def test_get_known_tags(tmp_known_tags):
    assert tmp_known_tags == get_known_tags_file()


def test_load_known_tags(tmp_known_tags):
    kt = load_known_tags()
    print kt
    assert kt == {
        '': ['tag1', 'tag2', 'tag3', 'tag4'],
        'key1': ['val1', 'val2']
        }

def test_add_known_tags(tmp_known_tags):
    new_tags = {'': ['tag5'], 'key1': ['val3'], 'key2': ['newval']}
    add_known_tags(new_tags)
    kt = load_known_tags()
    assert kt == {
        '': ['tag1', 'tag2', 'tag3', 'tag4', 'tag5'],
        'key1': ['val1', 'val2', 'val3'],
        'key2': ['newval']
        }

def test_make_known_tags_string():
    new_tags = {'': ['tag5'], 'key1': ['val3'], 'key2': ['newval']}
    tagstr = make_known_tags_string(new_tags)
    assert    tagstr == """tags:     tag5
key1:     val3
key2:     newval
"""

def test_warn_new_tags(capsys):
    tags = {'': ['tag1', 'tag8', 'tag9'], 'key1': ['val9'], 'key9': ['newval']}
    warn_new_tags(tags)
    out, err = capsys.readouterr()
    assert err=="""unknown keys: key9
unknown tags: tags:     tag8; tag9
unknown tags: key1:     val9
unknown tags: key9:     newval
"""

    warn_new_tags(tags, add=True)
    out, err = capsys.readouterr()
    # kt = load_known_tags()
    print err
    assert err=="""adding new keys: key9
adding new tags: tags:     tag8; tag9
adding new tags: key1:     val9
adding new tags: key9:     newval
"""
    warn_new_tags(tags)
    out, err = capsys.readouterr()
    assert err==''
