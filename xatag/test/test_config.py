#pylint: disable-all
import pytest
import os

from xatag.config import *
import xatag.constants as constants


@pytest.fixture
def confdir(tmpdir):
    os.environ[constants.CONFIG_DIR_VAR] = str(tmpdir)
    create_config_dir()
    fname = tmpdir.join('known_tags')
    with fname.open('a') as f:
        f.write("tags: tag1; tag2\n")
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


def test_get_config_dir(tmpdir):
    # TODO: mock the other possibilities
    os.environ[constants.CONFIG_DIR_VAR] = str(tmpdir)
    assert get_config_dir() == tmpdir
    os.environ[constants.CONFIG_DIR_VAR] = str(tmpdir) + 'this-does-not-exist'
    assert get_config_dir() == None


def test_get_known_tags_file(confdir):
    fname = confdir.join('known_tags')
    assert fname == get_known_tags_file()


def test_get_recoll_fields_file(tmpdir):
    os.environ[constants.CONFIG_DIR_VAR] = str(tmpdir)
    create_config_dir()
    assert get_recoll_fields_file() == tmpdir.join(
        constants.RECOLL_CONFIG_DIR, 'fields')


def test_load_known_tags(confdir):
    kt = load_known_tags()
    print kt
    assert kt == {
        '': ['tag1', 'tag2', 'tag3', 'tag4'],
        'key1': ['val1', 'val2']
        }


def test_add_known_tags(confdir):
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


def test_check_new_tags(capsys, confdir):
    tags = {'': [''], 'key': ['']}
    check_new_tags(tags)
    out, err = capsys.readouterr()
    print err
    assert err==''

    tags = {'': ['tag1', 'tag8', '', 'tag9'],
            'key1': ['val9', ''],
            'key9': ['newval']}
    check_new_tags(tags)
    out, err = capsys.readouterr()
    print out
    print err
    assert err=="""unknown keys: key9
unknown tags: tags:     tag8; tag9
unknown tags: key1:     val9
unknown tags: key9:     newval
"""

    check_new_tags(tags, add=True)
    out, err = capsys.readouterr()
    # kt = load_known_tags()
    print err
    assert err=="""adding new keys: key9
adding new tags: tags:     tag8; tag9
adding new tags: key1:     val9
adding new tags: key9:     newval
"""
    check_new_tags(tags)
    out, err = capsys.readouterr()
    assert err==''

    check_new_tags(tags, config_dir=str(confdir.join('this_doesnt-exist')))
    out, err = capsys.readouterr()
    assert err.startswith('xatag config dir cannot be found')


def test_update_recoll_fields(confdir, capsys):
    keys = ['newkey', 'newkey:with:punct']
    update_recoll_fields(keys)
    updated_file = (constants.RECOLL_FIELDS_HEAD +
                    constants.RECOLL_FIELDS_PREFIXES +
                    "xa:tags = XYXATAGS\n" +
                    "xa:newkey = XYXANEWKEY\n" +
                    "xa:newkey:with:punct = XYXANEWKEYWITHPUNCT\n\n" +
                    constants.RECOLL_FIELDS_STORED +
                    "xa:tags=\n" +
                    "xa:newkey=\n" +
                    "xa:newkey:with:punct=\n\n")

    with open(get_recoll_fields_file(), 'r') as f:
        assert f.read() == updated_file

    updated_file = (#constants.RECOLL_FIELDS_HEAD +
                    constants.RECOLL_FIELDS_PREFIXES +
                    "xa:tags = XYXATAGS\n" +
                    "xa:newkey = XYXANEWKEY\n" +
                    "xa:newkey:with:punct = XYXANEWKEYWITHPUNCT\n\n" +
                    constants.RECOLL_FIELDS_STORED +
                    "xa:tags=\n" +
                    "xa:newkey=\n" +
                    "xa:newkey:with:punct=\n\n")

    # remove the line that allows the file to be regenerated
    with open(get_recoll_fields_file(), 'w') as f:
        f.write(updated_file)

    keys = ['lots', 'of', 'new', 'stuff']
    update_recoll_fields(keys)

    with open(get_recoll_fields_file(), 'r') as f:
        assert f.read() == updated_file
