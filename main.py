#!/usr/bin/env python3

# Imports represented here
from tree_sitter import Language, Parser
from xml.dom import minidom
import sys

doc = minidom.Document()
positions = [0]


def main(file):
    # This code is used to configure parsing tool Tree Sitter.
    Language.build_library(
        # Store the library in the `build` directory
        'build/my-languages.so',

        # Include one or more languages
        [
            # 'vendor/tree-sitter-go',
            'vendor/tree-sitter-java'
            # 'vendor/tree-sitter-python'
        ]
    )
    java_lang = Language('build/my-languages.so', 'java')

    # Parsing algorithm starts here
    parser = Parser()
    parser.set_language(java_lang)
    tree_sitter_tree = parser.parse(read_file(file))
    gumtree_ast = to_gumtree_node(tree_sitter_tree.root_node)
    doc.appendChild(gumtree_ast)
    process_node(tree_sitter_tree.root_node, gumtree_ast)
    xml = doc.toprettyxml()
    print(xml)

    # type(tree_sitter_tree)
    # print(tree_sitter_tree.root_node.sexp())


def to_gumtree_node(tree_sitter_node):
    gumtree_node = doc.createElement('tree')
    gumtree_node.setAttribute("type", tree_sitter_node.type)

    start_pos = (tree_sitter_node.start_point[0] - 1) + tree_sitter_node.start_point[1]
    end_pos = (tree_sitter_node.end_point[0] - 1) + tree_sitter_node.end_point[1]
    length = end_pos - start_pos

    gumtree_node.setAttribute("pos", str(start_pos))
    gumtree_node.setAttribute("length", str(length))
    return gumtree_node


def process_node(tree_sitter_node, gumtree_node):
    # TODO: Implement later error handling
    # if parsoNode.type == 'error_node':
    #    sys.exit(parsoNode)

    for tree_sitter_child in tree_sitter_node.children:
        gumtree_child = to_gumtree_node(tree_sitter_child)

        if gumtree_child != None:
            gumtree_node.appendChild(gumtree_child)
            if tree_sitter_child.children != None:
                process_node(tree_sitter_child, gumtree_child)


def read_file(file):
    with open(file, 'r') as file:
        data = file.read()
    index = 0
    for chr in data:
        index += 1
        if chr == '\n':
            positions.append(index)
    return bytes(data, encoding='utf8')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main(sys.argv[1])
