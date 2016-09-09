import requests
import unittest
import mock

from lxml import html
from pprint import pprint as pp


def get_page_root(url):
    response = requests.get(url)
    page = response.content
    return html.fromstring(page)

def get_error_sections(url, div_root_id):
    errors_div_root = get_page_root(url).get_element_by_id(div_root_id)
    errors_section_root = errors_div_root.getchildren()[1]  # gets the section containing all error-sections
    return errors_section_root.findall('section')

    #section_copy.find('p[@class="pEE_ErrExp"]').getparent().remove(section_copy.find('p[@class="pEE_ErrExp"]'))
def pluck_children(parent, xpath, child=False):
    children = parent.findall(xpath)
    try:
        for child in children:
            parent.remove(child)
        return children
    except TypeError:
        return False

def content_from(element, split=None):
    formatted = element.text_content().strip()
    return formatted if not split else formatted.split(split)[-1]


def map_sections_to_dicts(url, div_root_id):
    error_sections = get_error_sections(url, div_root_id)
    cisco_error_list = []
    for section in error_sections:
        error_id = [content_from(child) for child in pluck_children(section, 'h3[@class="p_H_Head2"]')]
        msg = [content_from(child, split='Error Message ') for child in pluck_children(section, 'span[@class="pEM_ErrMsg"]')]
        exp = [content_from(child, split='Explanation ') for child in pluck_children(section, 'p[@class="pEE_ErrExp"]')]
        aux_exp = [content_from(child) for child in pluck_children(section, 'p[@class="pB2_Body2"]')]
        action = [content_from(child, split='Recommended Action ') for child in pluck_children(section, 'p[@class="pEA_ErrAct"]')]
        error_data = section.findall('p')  # auxiliary information is here in <p>, etc. tags
        cisco_error_list.append(
            {
                "id":       error_id,
                "msg":      msg,  # .split(':')[-1]
                "exp":      exp,
                "aux_exp":  aux_exp,
                "action":   action
            }
        )
    return cisco_error_list

cisco_errors_url = 'http://www.cisco.com/c/en/us/td/docs/security/asa/syslog-guide/syslogs/logmsgs1.html'
cisco_errors_urls = [
    'http://www.cisco.com/c/en/us/td/docs/security/asa/syslog-guide/syslogs/logmsgs1.html',
    'http://www.cisco.com/c/en/us/td/docs/security/asa/syslog-guide/syslogs/logmsgs2.html'
]

# msg.asa
# msg.firesight


class TestCiscoASAErrorsFetch(unittest.TestCase):
    #TODO:
    #----> handle list of urls
    #----> handle errors with multiple ids

    def setUp(self):
        target = open('sample_asa_errors_page.html', 'r')
        self.sample_html = target.read()
        target.close()

#-- PRIVATE ---------------------->
    def _stub_response_content_with(self, stub):
        mock_resp = mock.Mock()
        mock_resp.content = stub
        return mock_resp
#--------------------------------->

    @mock.patch('requests.get')
    def test_that_a_page_root_can_be_gotten(self, mock_get):
        mock_get.return_value = self._stub_response_content_with(self.sample_html)
        self.assertTrue('html' in get_page_root(cisco_errors_url).__repr__())

    @mock.patch('requests.get')
    def test_that_get_error_sections_returns_a_list(self, mock_get):
        mock_get.return_value = self._stub_response_content_with(self.sample_html)
        self.assertEqual(type(get_error_sections(cisco_errors_url, "chapterContent")).__name__, 'list')

    @mock.patch('requests.get')
    def test_that_all_error_sections_are_sections(self, mock_get):
        mock_get.return_value = self._stub_response_content_with(self.sample_html)
        sections = get_error_sections(cisco_errors_url, "chapterContent")
        non_section_elements = [s for s in sections if 'section' not in s.__repr__()]
        self.assertTrue(len(non_section_elements) == 0)

    @mock.patch('requests.get')
    def test_that_sections_get_mapped_to_error_dicts(self, mock_get):
        mock_get.return_value = self._stub_response_content_with(self.sample_html)
        error_dicts = map_sections_to_dicts(cisco_errors_url, 'chapterContent')
        non_dicts = [d for d in error_dicts if type(d).__name__ != 'dict']
        self.assertTrue(len(non_dicts) == 0)

    @mock.patch('requests.get')
    def test_that_error_dicts_have_the_appropriate_keys(self, mock_get):
        expected_keys = sorted(['id', 'msg', 'exp', 'aux_exp', 'action'])
        mock_get.return_value = self._stub_response_content_with(self.sample_html)
        error_dicts = map_sections_to_dicts(cisco_errors_url, 'chapterContent')
        dict_keys = [e.keys() for e in error_dicts]
        keys_found = sorted(list(set([key for keys in dict_keys for key in keys])))
        pp([d for d in error_dicts if any(d.get('aux_exp'))][:10])
        self.assertTrue(keys_found == expected_keys)


if __name__ == "__main__":
    unittest.main()

'''
IDEAL:
------
<section>
    <h3>
    <span>
    <p>
    <p>

NOT IDEAL:
----------
<section>
    <h3>
    <span>
    <p>
    <ul>
        <li>
        <...>
    <p>

<section>
    <h3>
    <span>
    <p>
    <ul>
        <li>
        <...>
    <p>
    <...>
    <p>

<section>
    <h3>
    <span>
    <p>
    <ul>
        <li>
        <...>
    <ul>
        <li>
        <...>
    <p>

<section>
    <h3>
    <span>
    <p>
    <ul>
        <li>
        <...>
    <p>
    <...>
    <ul>
        <li>
        <...>
    <p>

<section>
    <h3>
    <span>
    <p>
    <...>
    <ul>
        <li>
        <...>
    <p>

<section>
    <h3>
    <span>
    <p>
    <p>
    <table>
        <caption>
            <p>
        <tbody>
            <tr>
                <thead>
            <tr>
                <td>
                <td>
            <...>
'''
