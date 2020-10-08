#!/usr/bin/env python3

import click
import jinja2
import os
import yaml


def validate_extension(extensions):
    def callback(ctx, param, value):
        valid_extension = False
        for extension in extensions:
            if os.path.splitext(value)[1] == extension:
                valid_extension = True
        if not valid_extension:
            raise click.BadParameter(f'{param} must end with one of {extensions}')
        return value
    return callback


@click.command()
@click.option('--template', default='lesson.html.jinja2', callback=validate_extension(['.jinja2']))
@click.option('--data', '--yml-file',  callback=validate_extension(['.yml', '.yaml']), required=True)
def render_relpath(data, template):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(current_dir, data)) as f:
        lesson = yaml.load(f, Loader=yaml.FullLoader)
    template_loader = jinja2.FileSystemLoader(searchpath=current_dir)
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(template)
    output_text = template.render(
        dlcs=lesson['DLCS'],
        plan_for_instruction=lesson['plan_for_instruction'],
        rlms=lesson['rlms']
    )
    output_filename = os.path.join(current_dir, os.path.splitext(data)[0]) + '.html'
    with open(output_filename, 'w+') as f:
        f.write(output_text)


if __name__ == '__main__':
    render_relpath()