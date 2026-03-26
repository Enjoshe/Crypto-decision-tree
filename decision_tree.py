# decision_tree.py

import math
from collections import Counter


class Node:
    def __init__(self, feature=None, branches=None, result=None):
        self.feature = feature
        self.branches = branches or {}
        self.result = result

    def is_leaf(self):
        return self.result is not None


def entropy(rows):
    total = len(rows)
    counts = Counter(row["Scheme"] for row in rows)

    ent = 0
    for count in counts.values():
        p = count / total
        ent -= p * math.log2(p)

    return ent


def information_gain(rows, feature):
    total_entropy = entropy(rows)
    total = len(rows)

    partitions = {}
    for row in rows:
        value = row[feature]
        partitions.setdefault(value, []).append(row)

    weighted = 0
    for subset in partitions.values():
        weighted += (len(subset) / total) * entropy(subset)

    return total_entropy - weighted


def best_feature(rows, features):
    best = None
    best_gain = -1

    for f in features:
        gain = information_gain(rows, f)
        if gain > best_gain:
            best_gain = gain
            best = f

    return best


def build_tree(rows, features):
    schemes = set(row["Scheme"] for row in rows)

    # Leaf
    if len(schemes) == 1:
        return Node(result=rows[0]["Scheme"])

    if not features:
        # fallback
        return Node(result=rows[0]["Scheme"])

    best = best_feature(rows, features)

    node = Node(feature=best)
    values = set(row[best] for row in rows)

    remaining = [f for f in features if f != best]

    for value in values:
        subset = [r for r in rows if r[best] == value]

        if not subset:
            node.branches[value] = Node(result=rows[0]["Scheme"])
        else:
            node.branches[value] = build_tree(subset, remaining)

    return node
