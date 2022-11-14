def has_mapping(tree: tuple, mapping: tuple, in_not: bool = False) -> bool:
    """check if a tuple is present in the given tree

    Args:
        tree (tuple): the tree to be checked
        mapping (tuple): the tuple that needs to be checked, example: ("tag", "FRA")
        in_not (bool, optional): whether we are inside a NOT = { }, which negates any matches and is used internally. Defaults to False.

    Returns:
        bool: whether the mapping is present in the tree
    """
    for elem in tree:
        if elem == mapping and in_not is False:
            return True
        elif elem[0].upper() == "NOT":
            if has_mapping(elem[1], mapping, in_not=not in_not):
                return True
        elif any(x == elem[0].upper() for x in ["AND", "OR"]):
            if has_mapping(elem[1], mapping, in_not=in_not):
                return True

    return False
