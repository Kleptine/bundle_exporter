def traverse_tree(t, exclude_parent=False):
    if not exclude_parent:
        yield t
    for child in t.children:
        if exclude_parent:
            yield child
        yield from traverse_tree(child, exclude_parent)


def traverse_tree_from_iteration(iterator):
    for obj in iterator:
        yield obj
        for child in obj.children:
            yield from traverse_tree(child, exclude_parent=False)
