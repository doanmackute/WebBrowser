import json, sys

# Load language text and audio for web browser
def load_sweb_config_json():
    # Exit when error occurs and print notification to log
    try:
        with open("../sconf/SWEB_config.json", "r",encoding='utf-8') as f:
            langDB = json.load(f)
        f.close()
        return langDB
    except FileNotFoundError:
        print(f"Configuration file not found /sconf/SWEB_config.json")
    except json.JSONDecodeError:
        print(f"Error parsing JSON file: /sconf/SWEB_config.json")

def load_config_in_same_directory(file_name):
    # Exit when error occurs and print notification to log
    try:
        with open(file_name, 'r',encoding='utf-8') as f:
            data = json.load(f)
        f.close
        return data
    except FileNotFoundError:
        print(f"Configuration file not found: {file_name}")
    except json.JSONDecodeError:
        print(f"Error parsing JSON file: {file_name}")