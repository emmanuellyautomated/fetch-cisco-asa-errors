import requests
import unittest
import mock

from lxml import html
from pprint import pprint as pp
from helpers import pluck_children, content_from


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
template = syslog_template


#TODO:
#----> separate dicts with multiple ids
#----> handle unorthodox formats


def get_page_root(url):
    response = requests.get(url)
    page = response.content
    return html.fromstring(page)

def get_error_sections(url, div_root_id):
    errors_div_root = get_page_root(url).get_element_by_id(div_root_id)
    errors_section_root = errors_div_root.getchildren()[1]  # gets the section containing all error-sections
    return errors_section_root.findall('section')

def generate_error_dict(section, **template):
    for k, v in template.items():
        if 'selectors' in v:
            for selector in v['selectors']:
                template.update({k: [content_from(child, drop=v['replace']) for child in pluck_children(section, selector)]})
    return template

def map_section_to_dicts(url, div_root_id, template):
    error_sections = get_error_sections(url, div_root_id)
    cisco_error_list = []
    for section in error_sections:
        error_dict = generate_error_dict(section, **template)
        error_data = section.findall('p')  # auxiliary information is here in <p>, etc. tags
        cisco_error_list.append(error_dict)
    return cisco_error_list

def map_sections_to_dicts(urls, div_root_id, template):
    results = []
    for url in urls:
        cisco_error_list = map_section_to_dicts(url, div_root_id, template)
        results.extend(cisco_error_list)
    return results

cisco_errors_url = ['http://www.cisco.com/c/en/us/td/docs/security/asa/syslog-guide/syslogs/logmsgs1.html']
cisco_errors_urls = [
    'http://www.cisco.com/c/en/us/td/docs/security/asa/syslog-guide/syslogs/logmsgs1.html',
    'http://www.cisco.com/c/en/us/td/docs/security/asa/syslog-guide/syslogs/logmsgs2.html'
]

# msg.asa
# msg.firesight


class TestCiscoASAErrorsFetch(unittest.TestCase):
    def setUp(self):
        target = open('sample_asa_errors_page.html', 'r')
        self.sample_html = target.read()
        target.close()
        self.div_root_id = "chapterContent"

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
        self.assertEqual(type(get_error_sections(cisco_errors_url, self.div_root_id)).__name__, 'list')

    @mock.patch('requests.get')
    def test_that_all_error_sections_are_sections(self, mock_get):
        mock_get.return_value = self._stub_response_content_with(self.sample_html)
        sections = get_error_sections(cisco_errors_url, self.div_root_id)
        non_section_elements = [s for s in sections if 'section' not in s.__repr__()]
        self.assertTrue(len(non_section_elements) == 0)

    @mock.patch('requests.get')
    def test_that_sections_get_mapped_to_error_dicts(self, mock_get):
        mock_get.return_value = self._stub_response_content_with(self.sample_html)
        error_dicts = map_sections_to_dicts(cisco_errors_url, self.div_root_id, template)
        non_dicts = [d for d in error_dicts if type(d).__name__ != 'dict']
        self.assertTrue(len(non_dicts) == 0)

    @mock.patch('requests.get')
    def test_that_error_dicts_have_the_appropriate_keys(self, mock_get):
        expected_keys = sorted(['id', 'msg', 'exp', 'aux_exp', 'action'])
        mock_get.return_value = self._stub_response_content_with(self.sample_html)
        error_dicts = map_sections_to_dicts(cisco_errors_url, self.div_root_id, template)
        dict_keys = [e.keys() for e in error_dicts]
        keys_found = sorted(list(set([key for keys in dict_keys for key in keys])))
        pp(error_dicts[10:15])
        self.assertTrue(keys_found == expected_keys)

    @mock.patch('requests.get')
    def test_that_error_dicts_have_content_where_expected(self, mock_get):
        content_keys = ['id', 'msg', 'exp', 'action']
        mock_get.return_value = self._stub_response_content_with(self.sample_html)
        error_dicts = map_sections_to_dicts(cisco_errors_url, self.div_root_id, template)
        dict_values = [d[k] for k in content_keys for d in error_dicts]
        self.assertEqual(all(list(map(any, dict_values))), True)


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
