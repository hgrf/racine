from collections import namedtuple

from .sample import Sample
from .share import Share

sortkeys = {
    "id": lambda x: x.sample.id,
    "name": lambda x: x.sample.name,
    "last_modified": lambda x: x.sample.last_modified,
}


def is_indirectly_shared(sample, user):
    parent = sample.parent
    shares = []
    while parent:
        shares.append(parent.owner)
        shares.extend([s.user for s in parent.shares])
        parent = parent.parent
    return user in shares


def build_tree(user, order="id", callback=None):
    reverse = True if order == "last_modified" else False
    Node = namedtuple("Node", ["sample", "children", "indirectly_shared"])
    root = Node(None, [], False)
    nodes_to_explore = [root]
    while nodes_to_explore:
        current_node = nodes_to_explore.pop(0)
        current_id = current_node.sample.id if current_node.sample else 0
        kwargs = {"owner": user} if current_id == 0 else {}
        current_node.children.extend(
            [
                Node(sample, [], current_node.indirectly_shared or sample.owner != user)
                for sample in Sample.query.filter_by(
                    parent_id=current_id, isdeleted=False, **kwargs
                ).all()
            ]
        )
        current_node.children.extend(
            [
                Node(share.sample, [], current_node.indirectly_shared)
                for share in Share.query.filter_by(user=user, mountpoint_id=current_id).all()
                if not share.sample.isdeleted and not is_indirectly_shared(share.sample, user)
            ]
        )
        current_node.children.sort(key=sortkeys[order], reverse=reverse)
        nodes_to_explore.extend(current_node.children)

        if callback is not None and not callback(current_node.children):
            break

    return root


def list_tree(user, filter=None, limit=None):
    results = []

    def callback(nodes):
        results.extend([node.sample for node in nodes if filter is None or filter(node.sample)])
        if limit is not None and len(results) >= limit:
            return False
        return True

    build_tree(user, callback=callback)

    if limit is not None:
        return results[:limit]

    return results


def search_tree(user, query, limit=None):
    query = query.lower()

    def filter(sample):
        return sample.name is not None and query in sample.name.lower()

    return list_tree(user, filter=filter, limit=limit)
