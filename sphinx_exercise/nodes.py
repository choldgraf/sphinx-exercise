"""
sphinx_exercise.nodes
~~~~~~~~~~~~~~~~~~~~~

Enumerable and unenumerable nodes

:copyright: Copyright 2020 by the QuantEcon team, see AUTHORS
:licences: see LICENSE for details
"""
from sphinx.builders.html import HTMLTranslator
from docutils.nodes import Node

from sphinx.util import logging
from docutils import nodes


logger = logging.getLogger(__name__)


class enumerable_node(nodes.Admonition, nodes.Element):
    pass


def visit_enumerable_node(self, node: Node) -> None:
    self.visit_admonition(node)


def depart_enumerable_node(self, node: Node) -> None:
    self.depart_admonition(node)


class unenumerable_node(nodes.Admonition, nodes.Element):
    pass


def visit_unenumerable_node(self, node: Node) -> None:
    self.visit_admonition(node)


def depart_unenumerable_node(self, node: Node) -> None:
    self.depart_admonition(node)


class linked_node(nodes.Admonition, nodes.Element):
    pass


def visit_linked_node(self, node: Node) -> None:
    env = self.builder.env
    linked_node_label = node.attributes.get("title", "")
    node_type = node.attributes.get("type", "")

    self.body.append(self.starttag(node, "div", CLASS="admonition"))
    self.body.append('<p class="admonition-title">')

    # Check to see if linked node label exists
    if linked_node_label in env.exercise_list.keys():
        linked_node_typ = env.exercise_list[linked_node_label].get("type", "")

        # Check to see if linked node has nonumber
        if env.exercise_list[linked_node_label].get("nonumber", bool):
            # Check if title string in linked node is nonempty
            linked_node_title = env.exercise_list[linked_node_label].get("title", "")
            if linked_node_title == "":
                title = f'<a href="#{linked_node_label}">'
                title += f"{node_type.title()} to {linked_node_typ.title()}</a>"
                self.body.append(f"<span>{title}</span>")
            else:
                # Retrieve linked node title
                atts = {}
                linked_node_title = env.exercise_list[linked_node_label].get("node")[0]
                atts["href"] = "#" + linked_node_label

                self.body.append(
                    self.starttag(
                        linked_node_title, "a", f"{node_type.title()} to ", **atts
                    )
                )

                for item in linked_node_title:
                    if type(item) == nodes.math:
                        # https://fossies.org/linux/Sphinx/sphinx/ext/mathjax.py
                        self.body.append(
                            self.starttag(
                                item,
                                "span",
                                "",
                                CLASS="math notranslate nohighlight",
                            )
                        )
                        self.body.append(
                            self.builder.config.mathjax_inline[0]
                            + self.encode(item.astext())
                            + self.builder.config.mathjax_inline[1]
                            + "</span>"
                        )
                    else:
                        self.body.append(item.astext())
                self.body.append("</a>")
        else:
            # Linked node is an enumerable node
            number = get_node_number(self, linked_node_label)
            ref_node_title = f"{linked_node_typ.title()} {number}"
            title = f'<a href="#{linked_node_label}">'
            title += f"{node_type.title()} to {ref_node_title}</a>"
            self.body.append(f"<span>{title}</span>")
    else:
        # If label of linked node referenced in current node not found
        docpath = env.doc2path(self.builder.current_docname)
        path = docpath[: docpath.rfind(".")]
        msg = f"label '{linked_node_label}' not found"
        logger.warning(msg, location=path, color="red")
        title = f"{node_type.title()} to {linked_node_label}"
        self.body.append(f"<span>{title}</span>")

    self.body.append("</p>")


def depart_linked_node(self, node: Node) -> None:
    self.body.append("</div>")


def get_node_number(self: HTMLTranslator, attr: str) -> str:
    key = "exercise"
    number = self.builder.fignumbers.get(key, {}).get(attr, ())
    return ".".join(map(str, number))