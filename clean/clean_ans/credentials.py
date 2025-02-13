import os
from jinja2 import Environment, FileSystemLoader

def render_template_to_yaml(template_file, output_file, env_vars):
    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader('.'))
    
    # Load the Jinja2 template
    template = env.get_template(template_file)
    
    # Render the template with environment variables
    rendered_content = template.render(env_vars)
    print(rendered_content)
    
    # Write the rendered content to the output YAML file
    with open(output_file, 'w') as file:
        file.write(rendered_content)
    
    print(f"YAML file generated and saved as: {output_file}")

env_vars = {
    "NXOS_USERNAME": os.getenv("NXOS_USERNAME"),
    "NXOS_PASSWORD": os.getenv("NXOS_PASSWORD"),
}

# Render the template and save to testbed.yml
render_template_to_yaml("testbed_template.j2", "testbed.yml", env_vars)
