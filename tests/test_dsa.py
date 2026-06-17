import pytest
from dsa import PositionBuffer, PositionBufferError, PointByPointBuffer, Point


class TestPositionBuffer:
    def test_init_valid_capacity(self):
        buf = PositionBuffer(4)
        assert len(buf) == 0
        assert buf._capacity == 4

    def test_init_invalid_capacity(self):
        with pytest.raises(PositionBufferError):
            PositionBuffer(0)
        with pytest.raises(PositionBufferError):
            PositionBuffer(-1)

    def test_push_and_len(self):
        buf = PositionBuffer(2)
        buf.push(10)
        buf.push(20)
        assert len(buf) == 2
        buf.push(30)
        assert len(buf) == 3

    def test_grow_doubles_capacity(self):
        buf = PositionBuffer(2)
        for i in range(5):
            buf.push(i)
        assert len(buf) == 5
        assert buf._capacity >= 8

    def test_pop_order(self):
        buf = PositionBuffer(4)
        buf.push("a")
        buf.push("b")
        assert buf.pop() == "b"
        assert buf.pop() == "a"
        assert len(buf) == 0

    def test_pop_empty_raises(self):
        buf = PositionBuffer(4)
        with pytest.raises(PositionBufferError):
            buf.pop()

    def test_get_valid(self):
        buf = PositionBuffer(4)
        buf.push(100)
        buf.push(200)
        assert buf.get(0) == 100
        assert buf.get(1) == 200

    def test_get_out_of_range(self):
        buf = PositionBuffer(4)
        buf.push(1)
        with pytest.raises(PositionBufferError):
            buf.get(5)
        with pytest.raises(PositionBufferError):
            buf.get(-1)

    def test_iter(self):
        buf = PositionBuffer(4)
        buf.push(1)
        buf.push(2)
        buf.push(3)
        assert list(buf) == [1, 2, 3]

    def test_negative_grow_from_one(self):
        buf = PositionBuffer(1)
        buf.push("x")
        buf.push("y")
        assert len(buf) == 2
        assert buf._capacity >= 2
