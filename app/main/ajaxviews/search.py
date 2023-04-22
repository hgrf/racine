from flask import request, render_template, jsonify
from flask_login import current_user

from . import ajaxviews
from ...models import search_tree


@ajaxviews.route("/search", methods=["GET"])
def search():
    keyword = request.args.get("term")
    if keyword is None or keyword == "":
        return jsonify(error="Please specify a search term")

    results = [
        {
            "name": sample.name,
            "id": sample.id,
            "ownername": sample.owner.username,
            "mysample": (sample.owner == current_user),
            "parentname": sample.parent.name if sample.parent_id else "",
        }
        for sample in search_tree(
            user=current_user,
            query=keyword,
            limit=10,
        )
    ]

    if request.args.get("autocomplete") is not None:
        return jsonify(results=results)
    return render_template("main/searchresults.html", results=results, term=keyword)
