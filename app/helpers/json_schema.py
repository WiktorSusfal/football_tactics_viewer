import os
import json
from typing import Any


CURRENT_SCRIPT_PATH = os.path.realpath(os.path.dirname(__file__))
JSON_BASE_REL_PATH  = '../../resources/tactics_data'
GENERATED_SCHEMES_REL_PATH  = '../../resources/generated/json_schemes'


def _extract_schema(data: Any) -> Any:
    if isinstance(data, dict):
        schema = {}
        for key, value in data.items():
            schema[key] = _extract_schema(value)
        return schema
    elif isinstance(data, list):
        if len(data) > 0:
            return [_extract_schema(data[0])]
        else:
            return []
    else:
        return type(data).__name__

def get_json_schema(json_file_path: str) -> Any:
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    data = data[0] if isinstance(data, list) and len(data) > 0 else data
    return _extract_schema(data)


if __name__ == '__main__':
    JSON_BASE_ABS_PATH = os.path.join(CURRENT_SCRIPT_PATH, JSON_BASE_REL_PATH)

    e_schema_obj = get_json_schema(os.path.join(JSON_BASE_ABS_PATH, '3788757 - events.json'))
    f_schema_obj = get_json_schema(os.path.join(JSON_BASE_ABS_PATH, '3788757 - frames.json'))
    l_schema_obj = get_json_schema(os.path.join(JSON_BASE_ABS_PATH, '3788757 - lineups.json'))

    e_schema = json.dumps(e_schema_obj, indent=4)
    f_schema = json.dumps(f_schema_obj, indent=4)
    l_schema = json.dumps(l_schema_obj, indent=4)

    GENERATED_SCHEMES_ABS_PATH =  os.path.join(CURRENT_SCRIPT_PATH, GENERATED_SCHEMES_REL_PATH)

    with open(os.path.join(GENERATED_SCHEMES_ABS_PATH, 'README.md'), 'w') as f:
        f.write(f'JSON scheme files generated using {os.path.relpath(__file__, start=os.path.curdir)}')

    with open(os.path.join(GENERATED_SCHEMES_ABS_PATH, 'events_scheme.json'), 'w') as f:
        f.write(e_schema)

    with open(os.path.join(GENERATED_SCHEMES_ABS_PATH, 'frames_scheme.json'), 'w') as f:
        f.write(f_schema)

    with open(os.path.join(GENERATED_SCHEMES_ABS_PATH, 'lineups_scheme.json'), 'w') as f:
        f.write(l_schema)