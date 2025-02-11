import atexit
import os
import platform
import re
from typing import *

import pkg_resources

from .process_wrapper import ProcessWrapper, safe_string

HTML_ITEM_HEADER = r'''<html><head>
<!-- /* A font by Jos Buivenga (exljbris) -> www.exljbris.com */ -->
<link href="https://web.poecdn.com/css/font.css" media="screen" rel="stylesheet" type="text/css">
<style>
html {
    text-align: center;
    background: black;
    color: antiquewhite;
    font-family: "FontinSmallCaps",Verdana,Arial,Helvetica,sans-serif;
    line-height: 1.3;
    font-size: 13.5px;
    font-weight: 400;
}
.results {
    font-family: sans-serif;
}
.option > .hdr1 {
    padding-top: 1em;
    display: block;
}
</style>
</head><body>
'''


class ExternalError(Exception):
    def __init__(self, status):
        self.status = status
        super().__init__()


def _num_string(value):
    return f'{value:.10g}'


def _pob_line_to_html(line):
    line = re.sub(r'\^8', r'^x888888', line)  # ^8 is grey
    line = re.sub(r'\^1', r'^xFF0000', line)  # ^1 is red
    line = re.sub(r'\^x([0-9A-F]{6})(.*?)(?=\Z|\^)', r'<span style="color:#\1">\2</span>', line,
                  flags=re.MULTILINE | re.DOTALL)
    line = re.sub(r'\^7', r'', line)  # ^7 resets to default
    if line == '----':
        line = '<hr/>'
    else:
        line = f'<div>{line}</div>'
    return line


def _mark_item_groups(output):
    hr_pos = output.rfind('<hr/>')
    output = f'<div class="item">\n{output[:hr_pos]}</div>\n<hr/>\n<div class="results">\n{output[hr_pos + 6:]}\n</div>'
    output = re.sub(r'\n(?:<div>)((?:Equipping|Removing) this item.+:)\n(\(.+\))</div>((?:\n.*</div>)+)',
                    r'<div class="option">\n<div class="hdr1">\1</div>\n<div class="hdr2">\2</div>\3\n</div>\n',
                    output)
    output = re.sub(r'\n<hr/>\n<hr/>', r'\n<hr/>', output)
    return output


def _calculate_diff(base_values, new_values):
    fields = set(base_values.keys()) | set(new_values.keys())
    changes = dict()
    for field in fields:
        base_value = base_values.get(field, 0)
        new_value = new_values.get(field, 0)
        if not isinstance(base_value, int) and not isinstance(base_value, float):
            continue
        if base_value == new_value:  # exactly the same
            continue
        if _num_string(base_value) == _num_string(new_value):  # the same to 10 significant figures
            continue
        changes[field] = float(_num_string(new_value - base_value))
    return changes


class PathOfBuilding:
    def __init__(self, pob_path, pob_install, verbose=False):
        self.verbose = verbose and True
        data_dir = pkg_resources.resource_filename('pob_wrapper', 'data')

        os.environ['PATH'] = f'{pob_install};{os.environ["PATH"]}'
        os.environ['LUA_PATH'] = f'{data_dir}/?.lua;{pob_path}/lua/?.lua;{pob_install}/lua/?.lua'
        os.environ['LUA_CPATH'] = f'{pob_install}/?.dll'

        os.environ['POB_SCRIPTPATH'] = pob_path
        os.environ['POB_RUNTIMEPATH'] = pob_install

        self.pob = ProcessWrapper(debug=self.verbose)
        if platform.system() == 'Windows':
            self.pob.start([f'{data_dir}/luajit.exe', f'{data_dir}/cli.lua'], cwd=pob_path)
        else:
            self.pob.start([f'luajit', f'{data_dir}/cli.lua'], cwd=pob_path)
        atexit.register(self.kill)

    def require(self, module):
        '''Load the specified Lua module.'''
        module = safe_string(module)
        self._send(f'require("{module}")', ignore_result=True)

    def get_builds_dir(self):
        return self._send('getBuildsDir()')

    def load_build(self, path: str):
        path = safe_string(path)
        self._send(f'loadBuild("{path}")', ignore_result=True)

    def update_build(self):
        self._send(f'updateBuild()', ignore_result=True)

    def get_build_info(self):
        result = self._send(f'getBuildInfo()')
        return result

    def item_as_html(self, item_text):
        '''Run the item through the tester, returning an HTML representation of the effects.'''
        item_text = safe_string(item_text)
        lines = self._send(f'testItemForDisplay("{item_text}")')

        if not lines:
            return None
        # Convert the output to HTML
        lines = [_pob_line_to_html(line) for line in lines]
        output = '\n'.join(lines)
        output = _mark_item_groups(output)
        regex = r'\n<hr/>\n</div>\n<hr/>\n<div class="results">.*$'
        result = re.sub(regex, '', output, flags=re.S)
        regex = r'\n<hr/>\n<div class="results">.*$'
        result = re.sub(regex, '', result, flags=re.S)
        regex = r'(<hr/>|\n)+$'
        result = re.sub(regex, '', result, flags=re.S)

        return result + '</div>'

    def import_build_as_xml(self, account_name, char_name):
        lines = self._send(f'importBuild("{account_name}", "{char_name}")')
        return lines

    # # Not currently possible without evaluating all possible slots
    # def test_item_effect(self, item_text):
    #     '''Run the item through the tester, returning the stat diffs.'''
    #     item_text = safe_string(item_text)
    #     result = self._send(f'testItemStats("{item_text}")')
    #     changes = _calculate_diff(result['base'], result['new'])
    #     return changes

    def test_mod_effect(self, mod_line):
        '''Evaluate the effect of the given mod line, returning the stat diffs.'''
        mod_line = safe_string(mod_line)
        result = self._send(f'findModEffect("{mod_line}")')
        changes = _calculate_diff(result['base'], result['new'])
        return changes

    def echo(self, msg: str):
        msg = safe_string(msg)
        self._send(f'echo_message("{msg}")')

    def error(self, msg: str):
        msg = safe_string(msg)
        self._send(f'echo_error("{msg}")')

    def fetch(self, msg: str):
        '''Warning: msg must be valid Lua format'''
        result = self._send(f'echo_result({msg})')
        return result

    def _send(self, line, ignore_result=False) -> Any:
        result = self.pob.send(line, ignore_result=ignore_result)
        if ignore_result:
            return True
        if not result or result['status'] != 'success':
            raise ExternalError(result)
        return result.get('result', None)

    direct_send = _send

    def kill(self):
        if self.pob:
            self.pob.kill()
            self.pob = None

        atexit.unregister(self.kill)
