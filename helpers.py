from pprint import pprint as pp


syslog_template = {
    "id":       {
        "selectors": ['h3[@class="p_H_Head2"]'],
        "replace":  ['', '']
    },
    "msg":      {
        "selectors": ['span[@class="pEM_ErrMsg"]'],
        "replace":  ['Error Message ', '']
    },
    "exp":      {
        "selectors": ['p[@class="pEE_ErrExp"]'],
        "replace":  ['Explanation', '']
    },
    "aux_exp":  {
        "selectors": ['p[@class="pB2_Body2"]', 'ul/li[@class="pBuS_BulletStepsub"]'],
        "replace":  ['Explanation', '']
    },
    "action":   {
        "selectors": ['p[@class="pEA_ErrAct"]'],
        "replace":  ['Recommended Action ', '']
    }
}

def pluck_children(parent, xpath, single=False):
    children = parent.findall(xpath)
    if len(children) is not None:
        map(lambda child: parent.remove(child), children)
    return children

def content_from(element, drop=[]):
    if type(element).__name__ == "HtmlElement":
        formatted = element.text_content().strip()
        return formatted if not drop else formatted.replace(*drop)
