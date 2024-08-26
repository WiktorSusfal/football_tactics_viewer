import os 


STYLES_REL_PATH = r'./resources/styles'
STYLE_FILE_EXTENSION = '.qss'


def get_styles_code() -> str:
    style_code = str()
    
    for file_name in os.listdir(STYLES_REL_PATH):
        if file_name.endswith(STYLE_FILE_EXTENSION):
            file_full_path = os.path.join(STYLES_REL_PATH, file_name)
            with open(file_full_path, 'r') as style_file:
                style_code = '\n'.join([style_code, style_file.read()])

    return style_code