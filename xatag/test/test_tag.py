#pylint: disable-all
from xatag.tag import *

class TestTag():
    def test___init__(self):
        t = Tag('genre', 'classical')
        assert t.key == 'genre'
        assert t.value == 'classical'
        t = Tag('', 'favorite')
        assert t.key == 'tags'
        t = Tag('tags', 'favorite')
        assert t.key == 'tags'

    def test_from_string(self):
        t = Tag.from_string('simple-tag')[0]
        assert t.key == 'tags'
        assert t.value == 'simple-tag'
        t = Tag.from_string('tags:simple-tag')[0]
        assert t.key == 'tags'
        t = Tag.from_string('genre:classical')[0]
        assert t.key == 'genre'
        assert t.value == 'classical'
        # Nigel Kennedy?
        ts = Tag.from_string('genre:classical;   rock;\n bluegrass\tstuff')
        assert len(ts) == 3
        assert ts[0].key == 'genre'
        assert ts[0].value == 'classical'
        assert ts[1].key == 'genre'
        assert ts[1].value == 'rock'
        assert ts[2].key == 'genre'
        assert ts[2].value == 'bluegrass stuff'
        t = Tag.from_string('multi:part:key')[0]
        assert t.key == 'multi:part'
        assert t.value == 'key'

    def test_to_string(self):
        t = Tag('', 'simple-tag')
        assert t.to_string() == 'simple-tag'
        t = Tag('genre', 'classical')
        assert t.to_string() == 'genre:classical'

    def test___eq__(self):
        t1 = Tag('', 'tag')
        t2 = Tag('', 'tag')
        t3 = Tag('key', 'val')
        t4 = Tag('key', 'val')
        assert t1 == t2
        assert t3 == t4
        assert t2 != t3
