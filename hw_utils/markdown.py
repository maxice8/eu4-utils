def make_markdown_table(array: list[Any]) -> str:
    """Generates a Markdown table from a Python list

    Taken from:
    https://gist.github.com/m0neysha/219bad4b02d2008e0154?permalink_comment_id=4201220#gistcomment-4201220

    Made minor change to centralize text by default.

    Args:
        array (list[Any]): a python list.

    Returns:
        str: a string representation of the generated markdown table
    """

    nl = "\n"

    markdown = nl
    markdown += f"| {' | '.join(array[0])} |"

    markdown += nl
    markdown += f"| {' | '.join([':-:']*len(array[0]))} |"

    markdown += nl
    for entry in array[1:]:
        markdown += f"| {' | '.join(entry)} |{nl}"

    markdown += nl

    return markdown
