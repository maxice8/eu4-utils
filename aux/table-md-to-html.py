#!/usr/bin/env python3
#
# Original
# https://gist.github.com/jiffyclub/5015986
#
# Changed <style></style>

import argparse
import sys

import jinja2
import markdown

TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <style>
        table {
            border: solid 1px #DDEEEE;
            border-collapse: collapse;
            border-spacing: 0;
            font: normal 13px Arial, sans-serif;
            margin-left: auto;
            margin-right: auto;
        }
        table thead th {
            background-color: #DDEFEF;
            border: solid 1px #DDEEEE;
            color: #336B6B;
            padding: 10px;
            text-align: left;
            text-shadow: 1px 1px 1px #fff;
        }
        {{first_child}}
        table tbody td {
            border: solid 1px #DDEEEE;
            color: #333;
            padding: 10px;
            text-shadow: 1px 1px 1px #fff;
        }
    </style>
</head>
<body>
<div class="container">
{{content}}
</div>
</body>
</html>
"""


def parse_args(args=None):
    d = "Make a complete, styled HTML document from a Markdown file."
    parser = argparse.ArgumentParser(description=d)
    parser.add_argument(
        "mdfile",
        type=argparse.FileType("r"),
        nargs="?",
        default=sys.stdin,
        help="File to convert. Defaults to stdin.",
    )
    parser.add_argument(
        "-o",
        "--out",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="Output file name. Defaults to stdout.",
    )
    parser.add_argument(
        "--highlight-first-row",
        default=False,
        action="store_true",
        help="Highlight the first row on the left",
    )
    return parser.parse_args(args)


def main(args=None):
    args = parse_args(args)
    md = args.mdfile.read()
    extensions = ["extra", "smarty"]
    html = markdown.markdown(md, extensions=extensions, output_format="html5")
    if args.highlight_first_row:
        first_child = """
        table tbody tr td:first-child {
            background-color: #DDEFEF;
            border: solid 1px #DDEEEE;
            color: #336B6B;
            padding: 10px;
            text-align: left;
            text-shadow: 1px 1px 1px #fff;
            font-weight: bold
        }
        """
    else:
        first_child = ""
    doc = jinja2.Template(TEMPLATE).render(content=html, first_child=first_child)
    args.out.write(doc)


if __name__ == "__main__":
    sys.exit(main())
