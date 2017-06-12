
"""
The MIT License (MIT)

Copyright (c) 2016 Emil Stenström

https://github.com/EmilStenstrom/json-traverse

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
SOFTWARE.
"""

from __future__ import unicode_literals
import re
import json

# This ensures that we use 'str' in Python 3, and 'unicode' in Python 2
PythonString = "".__class__


class JsonTraverseParser:
    def __init__(self, raw_data, custom_json_impl=None):
        if raw_data and not isinstance(raw_data, PythonString):
            raise TypeError("the 'raw_data' argument must be {}, not '{}'"
                            .format(PythonString, type(raw_data)))

        json_impl = custom_json_impl or json
        self.data = json_impl.loads(raw_data) if raw_data else None

    def traverse(self, path, force_list=False):
        if not isinstance(path, PythonString):
            raise TypeError("the 'path' argument must be {}, not '{}'"
                            .format(PythonString, type(path)))

        reduced = []

        if self.data:
            reduced.append(self.data)

        if path:
            for item in path.split("."):
                list_reduced = list(reduced)
                if self.is_valid_index(item):
                    list_reduced = self.reduce_list(reduced, item)

                dict_reduced = self.flatten(reduced)
                if not list_reduced or list_reduced == reduced:
                    dict_reduced = self.reduce_dict(dict_reduced, item)

                if list_reduced and list_reduced != reduced:
                    reduced = list_reduced
                elif dict_reduced and dict_reduced != self.flatten(reduced):
                    reduced = dict_reduced
                else:
                    reduced = []

        if isinstance(reduced, list) and len(reduced) == 1:
            reduced = reduced[0]

        if isinstance(reduced, list) and len(reduced) == 0:
            reduced = None

        if force_list and not isinstance(reduced, list):
            if reduced is None:
                reduced = []
            else:
                reduced = [reduced]

        return reduced

    def reduce_list(self, reduced, item):
        outputs = []

        for value in reduced:
            try:
                outputs.append(value[int(item)])
            except (ValueError, IndexError, KeyError, TypeError):
                pass

        return outputs

    def reduce_dict(self, reduced, item):
        outputs = []

        for value in reduced:
            try:
                outputs.append(value[item])
            except (KeyError, TypeError):
                pass

        return outputs

    def flatten(self, reduced):
        flattened = []
        for value_or_sublist in reduced:
            if isinstance(value_or_sublist, list):
                flattened += value_or_sublist
            else:
                flattened.append(value_or_sublist)
        return flattened

    def is_valid_index(self, string):
        return re.match(r"^(0|[1-9][0-9]*)$", string)