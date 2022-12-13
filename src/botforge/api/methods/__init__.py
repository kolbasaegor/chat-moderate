from abc import abstractmethod

import requests

from botforge.api.objects import JsonSerializable


class APIProxy(object):
    def _request(self, url, method='get', **kwargs):
        return requests.request(method, url, **kwargs)

    @abstractmethod
    def request(self, *args, **kwargs):
        pass

    @abstractmethod
    def report_api_error(self, text, *args, **kwargs):
        print('API ERROR: %s' % text)


def dictify(list_or_object):
    if isinstance(list_or_object, JsonSerializable):
        return list_or_object.to_dict()
    elif isinstance(list_or_object, [tuple, list]):
        result = []

        for elem in list_or_object:
            if isinstance(elem, JsonSerializable):
                result.append(elem.to_dict())
            elif isinstance(elem, [tuple, list]):
                result.append(dictify(elem))

        return result

    return None
