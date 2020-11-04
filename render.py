#!/usr/bin/env python3


import click
import jinja2
import os
import yaml
import re
from markupsafe import escape
from jinja2.utils import _word_split_re

rlm = re.compile(r'\{(rlm)\}\[(\d+)\]\((\w+)\)')

img = re.compile(r'\{(img)\}\[((\w+/?)+)\]\((\w+)\)')
md_link_regex = re.compile(r'\[([\w\s\d]+)\]\(((?:\/|https?:\/\/)?[\w\d./?=#]+)\)')


def rlm_img_filter(text):
    rlmed = re.sub(rlm, r'<a href="#rlm\2" target="_blank" class="accordionLink" id="rlm\2-ref">\3</a>', text)
    imged = re.sub(img, r"<a href=\"\2\" target=\"_blank\">\4</a>", rlmed)
    linked = re.sub(md_link_regex, r'<a href="../../images/\2">\1</a>', imged)
    return linked
    # words = _word_split_re.split(str(escape(text)))
    # for (i, word) in enumerate(words):
    #     match = rlmimg.match(words)
    #     if match:
    #         typ, path, _, display = match.groups()
    #         if typ == 'rlm':
    #             display = f'<a href="#rlm{path}" class="accordionLink" id="rlm{path}-ref">{display}</a>'
    #         else:
    #             display = f"<a href=\"{path}\">{display}</a>"
    #         words[i] = display
    # return ' '.join(words)


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
@click.argument('data', callback=validate_extension(['.yml', '.yaml']), required=True)
@click.option('--template', default='lesson.html.jinja2', callback=validate_extension(['.jinja2']))
def render_relpath(data, template):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(current_dir, data)) as f:
        lesson = yaml.load(f, Loader=yaml.FullLoader)
    template_loader = jinja2.FileSystemLoader(searchpath=current_dir)
    template_env = jinja2.Environment(loader=template_loader)
    template_env.filters['sanitize'] = rlm_img_filter
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
#