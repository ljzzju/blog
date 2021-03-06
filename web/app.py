#
#
# Author: Cheng-Lai Huang
# Author: Dan Wang
# Author: Lei Li (leili@cs.berkeley.edu)
# Since: 2012-02
# Last modified: 2013-12-25

import web
import time
import os
import subprocess
import re

BLOG_EXTENSION = ".blog"
USER_STORE = "static/user_query/"
DEFAULT_GRAPH = "static/images/BerkeleyLogo.png"
EXAMPLE_BLOG_PATH = 'example.blog'

urls = ('/', 'blog_web_ui')
render = web.template.render('templates/')

app = web.application(urls, globals())

with open(EXAMPLE_BLOG_PATH) as f:
    example_blog_code = f.read()

def run_process(script_name):
    command = ["../blog", "--displaycbn", script_name]
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = os.linesep.join(p.communicate())
    return output

def ensure_dir(d):
    """ make sure the corresponding directory exists"""
    if not os.path.exists(d):
        os.makedirs(d)

def store_script(prefix, script):
    #Check if directory exist
    ensure_dir(USER_STORE)

    #Write input into local file
    script_name = prefix+BLOG_EXTENSION
    input_handler = open(script_name, 'w')
    input_handler.write(script)
    input_handler.close()
    return script_name

def execute_script(script):
    #Define name of the script
    current = str(time.time())
    filename = "tmp_%s" % current

    prefix = USER_STORE + filename

    script_name = store_script(prefix, script)
    return run_process(script_name)

class blog_web_ui:
    def GET(self):
        return render.index(example_blog_code)

    def POST(self):
        s = web.input().textfield
        raw_data = execute_script(s)
        parsed_results = parse_query_results(raw_data)
        return render.data(raw_data, parsed_results)

def parse_query_results(s):
    results = []
    regex = re.compile(r'Query Results\s*=*\n(([^=].*\n)*)\s*=*\s*Done\s*=*')
    for match in regex.finditer(s):
        lines = match.groups()[0].split('\n')
        match = re.match('Number of samples: (\d+)', lines[0])
        if match:
            samples = match.group(1)
            results.append({
                'samples': samples,
                'queries': []
            })
        for line in lines[1:]:
            query_match = re.match('Distribution of values for (.*)', line)
            result_match = re.match(r'\s*(\S*)\s+([0-9]*\.?[0-9]+[eE]?[-+]?[0-9]*)', line)
            if query_match:
                query = query_match.group(1)
                results[-1]['queries'].append({
                    'query': query,
                    'distribution': []
                })
            elif result_match:
                value, probability = result_match.groups()
                results[-1]['queries'][-1]['distribution'].append({
                    'value': value,
                    'probability': 100 * float(probability)
                })
    return results


if __name__ == '__main__':
    app.run()
