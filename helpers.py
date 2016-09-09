kwargs = {
    "id":       {
        "selector": 'h3[@class="p_H_Head2"]',
        "replace":  ['', '']
    },
    "msg":      {
        "selector": 'span[@class="pEM_ErrMsg"]',
        "replace":  ['Error Message ', '']
    },
    "exp":      {
        "selector": 'p[@class="pEE_ErrExp"]',
        "replace":  ['Explanation', '']
    },
    "aux_exp":  {
        "selector": 'p[@class="pB2_Body2"]',
        "replace":  ['Explanation', '']
    },
    "action":   {
        "selector": 'p[@class="pEA_ErrAct"]',
        "replace":  ['Recommended Action ', '']
    }
}

def pluck_children(parent, xpath, child=False):
    children = parent.findall(xpath)
    try:
        for child in children:
            parent.remove(child)
        return children
    except TypeError:
        return False

def content_from(element, drop=None):
    formatted = element.text_content().strip()
    return formatted if not drop else formatted.replace(*drop)
