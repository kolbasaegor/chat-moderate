import json


class JsonSerializable(object):
    def __init__(self, json_str=None, **kwargs):
        """
        Any object that can be transformed to JSON and backwards
        :param json_str: in case of json string representation of json
        :param kwargs: the actual json to build object of
        """
        if json_str is not None:
            kwargs = json.loads(json_str, encoding='utf-8')

        for attr_name, attr_value in kwargs.items():
            setattr(self, attr_name, attr_value)

    def to_dict(self):
        out = {}

        def parse_list(lst):
            res = []

            for x in lst:
                if isinstance(x, JsonSerializable):
                    res.append(x.to_dict())
                elif isinstance(x, list):
                    res.append(parse_list(x))
                else:
                    res.append(x)

            return res

        for key, value in self.__dict__.items():
            if value is None:
                continue

            if isinstance(value, JsonSerializable):
                out[key] = value.to_dict()
            elif isinstance(value, list):
                out[key] = parse_list(value)
            else:
                out[key] = value

        return out

    def to_json(self):
        return json.dumps(self.to_dict())
