def pluck_children(parent, xpath, single=False):
    children = parent.findall(xpath)
    if len(children) is not None:
        map(lambda child: parent.remove(child), children)
    return children

def content_from(element, drop=[]):
    if type(element).__name__ == "HtmlElement":
        formatted = element.text_content().strip()
        return formatted if not drop else formatted.replace(*drop)
