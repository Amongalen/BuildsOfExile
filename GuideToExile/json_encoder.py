import json

import jsonpickle

from GuideToExile.data_classes import PobDetails


class BuildDetailsJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, PobDetails):
            obj_str = jsonpickle.encode(obj)
            obj_dict = json.loads(obj_str)
            return obj_dict

        return json.JSONEncoder.default(self, obj)


class BuildDetailsJsonDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    @staticmethod
    def object_hook(obj):
        if "py/object" in obj.keys() and obj["py/object"] == "GuideToExile.data_classes.PobDetails":
            test = json.dumps(obj)
            return jsonpickle.decode(test)
        return obj
