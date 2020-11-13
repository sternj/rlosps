#!/usr/bin/env python3


import click
import jinja2
import os
import yaml
import re
import shutil

rlm = re.compile(r'\{(rlm)\}\[(\d+)\]\((\w+)\)')

img = re.compile(r'\{(img)\}\[((\w+/?)+)\]\((\w+)\)')
md_link_regex = re.compile(r'\[([\w\s\d]+)\]\(((?:\/|https?:\/\/)?[\w\d./?=#]+)\)')

special_templates = {
    '_index.yml': 'index',
    '_mod.yml': 'mod',
    '_grade.yml': 'grade'
}
SPECIAL_TEMPLATE_TYPE = 'builtin'
DIR_TYPE = 'dir'
LESSON_TYPE = 'lesson'


def load_yml_files(base_dir):
    """

    """
    ret = {}
    for root, dirs, files in os.walk(base_dir):
        tmp = {'type': DIR_TYPE}
        # Iterates over special templates, if there's a file corresponding to a builtin
        # adds it as a builtin dict item
        for path, name in special_templates.items():
            if path in files:
                with open(os.path.join(root, path)) as f:
                    tmp[name] = yaml.load(f, Loader=yaml.FullLoader)
                    # tmp[name]['name'] = name
                    tmp[name]['type'] = SPECIAL_TEMPLATE_TYPE
        # If file doesn't correspond to a builtin and is a yml file, enters it with its name
        for file in files:
            if (file.endswith('.yml') or file.endswith('.yaml')) and file not in special_templates.keys():
                with open(os.path.join(root, file)) as f:
                    tmp[file] = yaml.load(f, Loader=yaml.FullLoader)
                    tmp[file]['type'] = LESSON_TYPE
                    tmp[file]['name'] = file.split('.')[0]
        # If we're at the base directory, just enters in all the entries automatically
        if root == base_dir:
            ret.update(tmp)
        else:
            # Enters the dict into the correct location in the tree.
            # Since a parent directory will always be processed before its children,
            # this will always work
            paths = root.split(os.path.sep)
            # Remove the root directory and the current directory
            paths = paths[1:-1]
            diter = ret
            for path in paths:
                diter = diter[path]
            diter[os.path.basename(root)] = tmp
    return ret


def rlm_img_filter(text):
    rlmed = re.sub(rlm, r'<a href="#rlm\2" target="_blank" class="accordionLink" id="rlm\2-ref">\3</a>', text)
    imged = re.sub(img, r"<a href=\"\2\" target=\"_blank\">\4</a>", rlmed)
    linked = re.sub(md_link_regex, r'<a href="../../images/\2">\1</a>', imged)
    return linked


template_loader = jinja2.FileSystemLoader(searchpath='templates')
template_env = jinja2.Environment(loader=template_loader)
template_env.filters['sanitize'] = rlm_img_filter


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


# def render_directory(base_path, dest_root, directory_dict: dict, index: dict):
#     os.mkdir(os.path.join(dest_root, base_path))
#     for key, value in directory_dict.items():
#         if not isinstance(value, dict):
#             continue
#         val_type = value['type']
#         if val_type == SPECIAL_TEMPLATE_TYPE:
#             template = template_env.get_template(f'{key}.html.jinja2')
#         elif val_type == DIR_TYPE:
#             render_directory(os.path.join(base_path, key), dest_root, value, index)
#         elif val_type == LESSON_TYPE:
#
#             template = template_env.get_template('lesson.html.jinja2')
#             output_text = template.render(
#                 grades=index,
#                 dlcs=value['DLCS'],
#                 plan_for_instruction=value['plan_for_instruction'],
#                 rlms=value['rlms']
#             )
#             output_filename = os.path.join(dest_root, value['name']) + '.html'
#             with open(output_filename, 'w+') as f:
#                 f.write(output_text)


def render_template(template_name, template_params, output_file):
    template = template_env.get_template(template_name)
    output_text = template.render(**template_params)
    with open(output_file, 'w+') as f:
        f.write(output_text)


def render(base_dir, dest_dir):
    with open('config.yml', 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    os.mkdir(dest_dir)
    yml_base = load_yml_files(base_dir)
    index = gen_index(yml_base)
    index['base_path'] = config['base_path']
    # render_directory(base_dir, dest_dir, index)
    render_template('index.html.jinja2', {'index': index}, os.path.join(dest_dir, 'index.html'))
    for grade in index['grades']:
        os.mkdir(os.path.join(dest_dir, grade['name']))
        for module in grade['modules']:
            os.mkdir(os.path.join(dest_dir, grade['name'], module['name']))
            render_template('mod.html.jinja2',
                            {
                                'index': index,
                                'module': module['module'],
                                'lessons': module['lessons']
                            },
                            os.path.join(dest_dir, grade['name'], module['name'], 'index.html')
                            )
            for lesson in module['lessons']:
                render_template('lesson.html.jinja2',
                                {
                                    'index': index,
                                    'lesson': lesson
                                },
                                os.path.join(dest_dir, grade['name'], module['name'], f'{lesson["name"]}.html'))


def gen_index(structure_dict: dict):
    builtin_vals = set(special_templates.values())
    builtin_vals.add("type")
    return {
        "grades": [
            {
                "name": grade_dict['grade']['name'],
                "grade": grade_dict['grade'],
                "modules": [
                    {
                        "name": module_dict['mod']['name'],
                        "module": module_dict["mod"],
                        "link": f"{grade_name}/{module_name}/index.html",
                        "lessons": [
                            lesson_dict
                            for lesson, lesson_dict in module_dict.items()
                            if lesson not in builtin_vals
                        ],
                    }
                    for module_name, module_dict, in grade_dict.items()
                    if isinstance(module_dict, dict) and module_dict["type"] == DIR_TYPE
                ],
            }
            for grade_name, grade_dict in structure_dict.items()
            if isinstance(grade_dict, dict) and grade_dict["type"] == DIR_TYPE
        ]
    }


# @click.command()
# @click.argument('data', callback=validate_extension(['.yml', '.yaml']), required=True)
# @click.option('--template', default='lesson.html.jinja2', callback=validate_extension(['.jinja2']))
# def render_relpath(data, template):
#     current_dir = os.path.dirname(os.path.realpath(__file__))
#     with open(os.path.join(current_dir, data)) as f:
#         lesson = yaml.load(f, Loader=yaml.FullLoader)
#
#     template = template_env.get_template(template)
#     output_text = template.render(
#         dlcs=lesson['DLCS'],
#         plan_for_instruction=lesson['plan_for_instruction'],
#         rlms=lesson['rlms']
#     )
#     output_filename = os.path.join(current_dir, os.path.splitext(data)[0]) + '.html'
#     with open(output_filename, 'w+') as f:
#         f.write(output_text)


# if __name__ == '__main__':
#     render_relpath()

# print(gen_index(load_yml_files('structure')))
if __name__ == '__main__':
    render('structure', 'docs')