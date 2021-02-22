#!/usr/bin/env python3

# Please be informed! This code is based on a code that was published by Gumtree Diff Team.
# Reference: https://github.com/GumTreeDiff/pythonparser/blob/master/pythonparser

# Imports represented here
from tree_sitter import Language, Parser
from xml.dom import minidom
import sys
import os

doc = minidom.Document()
positions = [0]


dummy_code = bytes("""
public class AddTwoIntegers {
    public static void main(String[] args) {
        
        int first = 10;
        int second = 20;

        System.out.println("Enter two numbers: " + first + " " + second);
        int sum = first + second;

        System.out.println("The sum is: " + sum);
    }
}
""", encoding='utf8')

# Debug only
# def main():


# Production only
def main(file):

    this_directory = os.path.dirname(__file__)
    # filename = os.path.join(this_directory, '/relative/path/to/file/you/want')
    # This code is used to configure parsing tool Tree Sitter
    Language.build_library(
        # Store the library in the `build` directory
        os.path.join(this_directory, 'build/my-languages.so'),

        # Include one or more languages
        [
            # 'vendor/tree-sitter-go',
            os.path.join(this_directory, 'vendor/tree-sitter-java')
            # 'vendor/tree-sitter-python'
        ]
    )
    java_lang = Language(os.path.join(this_directory, 'build/my-languages.so'), 'java')

    # Parsing algorithm starts here
    parser = Parser()
    parser.set_language(java_lang)

    # For debugging
    tree_sitter_tree = parser.parse(read_file(file))

    # For production
    # tree_sitter_tree = parser.parse(read_file(file))

    gumtree_ast = to_gumtree_node(tree_sitter_tree.root_node)

    # everything should be inside the tag
    root_node = doc.createElement('root')

    # in test case they have context tag, which is empty. Do not know why we need it
    context_node = doc.createElement('context')

    # We append our root node to document
    doc.appendChild(root_node)

    # Append context tag to root node (<root> </root)
    root_node.appendChild(context_node)

    # append data into <root> tag. At this stage we append parsed code structure.
    root_node.appendChild(gumtree_ast)

    # Recursively add children nodes (if exist)
    process_node(tree_sitter_tree.root_node, gumtree_ast)

    xml = doc.toprettyxml()
    print(xml)

    # type(tree_sitter_tree)
    # print(tree_sitter_tree.root_node.sexp())


def to_gumtree_node(tree_sitter_node):
    gumtree_node = doc.createElement('tree')

    if not tree_sitter_node.is_named:
        gumtree_node.setAttribute("type", tree_sitter_node.parent.type)
        gumtree_node.setAttribute("label", tree_sitter_node.type)
    else:
        gumtree_node.setAttribute("type", tree_sitter_node.type)

    # Calculation is done in bytes since we need to get accurate information about length of code structures.
    start_pos = tree_sitter_node.start_byte
    length = tree_sitter_node.end_byte - tree_sitter_node.start_byte

    gumtree_node.setAttribute("pos", str(start_pos))
    gumtree_node.setAttribute("length", str(length))
    return gumtree_node


def process_node(tree_sitter_node, gumtree_node):
    # TODO: Implement later error handling
    # if parsoNode.type == 'error_node':
    #    sys.exit(parsoNode)

    for tree_sitter_child in tree_sitter_node.children:
        gumtree_child = to_gumtree_node(tree_sitter_child)

        if gumtree_child is not None:
            gumtree_node.appendChild(gumtree_child)
            if tree_sitter_child.children is not None:
                process_node(tree_sitter_child, gumtree_child)


def read_file(file):
    with open(file, 'r') as file:
        data = file.read()
    index = 0
    for CHR in data:
        index += 1
        if CHR == '\n':
            positions.append(index)
    return bytes(data, encoding='utf8')


# Production
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main(sys.argv[1])

# Debugging
# Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#    main()
