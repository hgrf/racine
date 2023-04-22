from collections import namedtuple

from .sample import Sample
from .share import Share

sortkeys = {
    "id": lambda x: x.sample.id,
    "name": lambda x: x.sample.name,
    "last_modified": lambda x: x.sample.last_modified,
}


def build_tree(user, order="id"):
    reverse = True if order == "last_modified" else False
    Node = namedtuple("Node", ["sample", "children"])
    root = Node(None, [])
    nodes_to_explore = [root]
    while nodes_to_explore:
        current_node = nodes_to_explore.pop(0)
        current_id = current_node.sample.id if current_node.sample else 0
        kwargs = {"owner": user} if current_id == 0 else {}
        current_node.children.extend(
            [
                Node(sample, [])
                for sample in Sample.query.filter_by(
                    parent_id=current_id, isdeleted=False, **kwargs
                ).all()
            ]
        )
        current_node.children.extend(
            [
                Node(share.sample, [])
                for share in Share.query.filter_by(user=user, mountpoint_id=current_id).all()
                if not share.sample.isdeleted
                and share.sample.is_accessible_for(user, direct_only=True)
            ]
        )
        current_node.children.sort(key=sortkeys[order], reverse=reverse)
        nodes_to_explore.extend(current_node.children)

    return root
