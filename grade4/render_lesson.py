import yaml
import jinja2
import os
with open('lesson1.yml') as f:
    lesson = yaml.load(f, Loader=yaml.FullLoader)
templateLoader = jinja2.FileSystemLoader(searchpath="./")
templateEnv = jinja2.Environment(loader=templateLoader)
template = templateEnv.get_template('lesson1.html.jinja2')
outputText = template.render(
    dlcs=lesson['DLCS'],
    plan_for_instruction=lesson['plan_for_instruction'],
    rlms=lesson['rlms']
)

with open('lesson1.html', 'w+') as f:
    f.write(outputText)
