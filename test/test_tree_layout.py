from src.map.map_state import MapState
from src.visualizations import tree_layout


def st(x, y=0):
    return MapState((x, y))


def test_tree_layout_depth_and_centered_parent():
    root, a, b, c, d = st(0), st(1), st(2), st(3), st(4)
    parent = {root: None, a: root, b: root, c: a, d: a}
    lay = tree_layout(parent)
    assert lay.depth == {root: 0, a: 1, b: 1, c: 2, d: 2}
    assert lay.max_depth == 2
    assert lay.slots == 3  # folhas: c, d, b
    assert lay.y[c] == 0 and lay.y[d] == 1 and lay.y[b] == 2
    assert lay.y[a] == 0.5            # entre c e d
    assert lay.y[root] == 1.25        # entre a (0.5) e b (2)


def test_tree_layout_single_node():
    root = st(0)
    lay = tree_layout({root: None})
    assert lay.max_depth == 0 and lay.slots == 1 and lay.y[root] == 0.0
