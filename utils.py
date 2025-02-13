import json
import os
from jinja2 import Environment, FileSystemLoader

def load_json_data(input_json_path):
    with open(input_json_path, 'r') as file:
        data = json.load(file)
    return data

def setup_jinja2_environment(template_dir):
    env = Environment(loader=FileSystemLoader(template_dir))
    return env

def render_template(env, template_name, context):
    template = env.get_template(template_name)
    content = template.render(context)
    return content

def write_output_file(output_dir, filename, content):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, filename)
    with open(output_path, 'w') as file:
        file.write(content)