import os
import json
from .log import PypeLogger

log = PypeLogger().get_logger(__name__)


def collect_json_path(input_path):
    output = None
    if os.path.isdir(input_path):
        output = {}
        for file in os.listdir(input_path):
            full_path = os.path.sep.join([input_path, file])
            if os.path.isdir(full_path):
                loaded = collect_json_path(full_path)
                if loaded:
                    output[file] = loaded
            else:
                basename, ext = os.path.splitext(os.path.basename(file))
                if ext == '.json':
                    try:
                        with open(full_path, "r") as f:
                            output[basename] = json.load(f)
                    except json.decoder.JSONDecodeError:
                        log.warning(
                            'File "{}" has .json syntax error'.format(file)
                        )
                        output[basename] = {}
    else:
        basename, ext = os.path.splitext(os.path.basename(input_path))
        if ext == '.json':
            with open(input_path, "r") as f:
                output = json.load(f)

    return output


def get_presets(project_name=None):
    """ Loads preset files with usage of 'collect_json_from_path'
    Default preset path is set to: "{PYPE_STUDIO_CONFIG}/presets"
    Project preset path is set to: "{PYPE_PROJECT_CONFIGS}/*project_name*"
    - environment variable PYPE_STUDIO_CONFIG is required
    - PYPE_STUDIO_CONFIGS only if want to use overrides per project

    Return:
    - None
        - if default path does not exist
    - default presets (dict)
        - if project_name is not set
        - if project's presets folder does not exist
    - project presets (dict)
        - if project_name is set and include override data
    """
    # config_path should be set from environments?
    config_path = os.path.normpath(os.environ['PYPE_STUDIO_CONFIG'])
    preset_items = [config_path, 'presets']
    config_path = os.path.sep.join(preset_items)
    if not os.path.isdir(config_path):
        log.error('Preset path was not found: "{}"'.format(config_path))
        return None

    return collect_json_path(config_path)


def update_dict(main_dict, enhance_dict):
    """ Merges dictionaries by keys.
    Function call itself if value on key is again dictionary
        - does not overrides whole value on first found key
        but only values differences from enhance_dict
    """
    for key, value in enhance_dict.items():
        if key not in main_dict:
            main_dict[key] = value
        elif isinstance(value, dict):
            main_dict[key] = update_dict(main_dict[key], value)
        else:
            main_dict[key] = value
    return main_dict
