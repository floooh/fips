"""functions for generating source code documentation"""

import os, fnmatch, shutil, subprocess, re
from mod import log, util

def build(fips_dir, proj_dir):
    # target directory will be 'fips-deploy/[proj]-markdeep
    proj_name = util.get_project_name_from_dir(proj_dir)
    out_dir = util.get_workspace_dir(fips_dir)+'/fips-deploy/'+proj_name+'-markdeep'
    log.info('building to: {}...'.format(out_dir))
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)

    # check all .h files for embedded documentation
    hdrs = []
    for root, dirnames, filenames in os.walk(proj_dir):
        for filename in fnmatch.filter(filenames, '*.h'):
            hdrs.append(os.path.join(root, filename).replace('\\','/'))
    markdeep_files = []
    capture_begin = re.compile(r'/\*#\s')
    for hdr in hdrs:
        log.info('  parsing {}'.format(hdr))
        capturing = False
        markdeep_lines = []
        with open(hdr, 'r') as src:
            lines = src.readlines()
            for line in lines:
                if "#*/" in line and capturing:
                    capturing = False
                if capturing:
                    # remove trailing tab
                    if line.startswith('    '):
                        line = line[4:]
                    elif line.startswith('\t'):
                        line = line[1:]
                    markdeep_lines.append(line)
                if capture_begin.match(line) and not capturing:
                    capturing = True
        if markdeep_lines:
            markdeep_files.append(hdr)
            dst_path = out_dir + '/' + os.path.relpath(hdr,proj_dir) + '.html'
            log.info('    markdeep block(s) found, writing: {}'.format(dst_path))
            dst_dir = os.path.dirname(dst_path)
            if not os.path.isdir(dst_dir):
                os.makedirs(dst_dir)
            with open(dst_path, 'w') as dst:
                dst.write("<meta charset='utf-8' emacsmode='-*- markdown -*-'>\n")
                dst.write("<link rel='stylesheet' href='https://casual-effects.com/markdeep/latest/apidoc.css?'>\n")
                for line in markdeep_lines:
                    dst.write(line)
                dst.write("<script>markdeepOptions={tocStyle:'medium'};</script>")
                dst.write("<!-- Markdeep: --><script src='https://casual-effects.com/markdeep/latest/markdeep.min.js?'></script>")
    
    # write a toplevel index.html
    if markdeep_files:
        markdeep_files = sorted(markdeep_files)
        dst_path = out_dir + '/index.html'
        log.info('writing toc file: {}'.format(dst_path))
        with open(dst_path, 'w') as dst:
            dst.write("<meta charset='utf-8' emacsmode='-*- markdown -*-'>\n")
            dst.write("<link rel='stylesheet' href='https://casual-effects.com/markdeep/latest/apidoc.css?'>\n")
            dst.write('# {}\n'.format(proj_name))
            for hdr in markdeep_files:
                rel_path = os.path.relpath(hdr,proj_dir)
                dst.write('- [{}]({})\n'.format(rel_path, rel_path+'.html'))
            dst.write("<script>markdeepOptions={tocStyle:'medium'};</script>")
            dst.write("<!-- Markdeep: --><script src='https://casual-effects.com/markdeep/latest/markdeep.min.js?'></script>")
    else:
        log.error("no headers with embedded markdeep found in '{}'!".format(proj_dir))

# view generated markdeep in browser, we don't need a local http server for that
def view(fips_dir, proj_dir):
    proj_name = util.get_project_name_from_dir(proj_dir)
    out_dir = util.get_workspace_dir(fips_dir)+'/fips-deploy/'+proj_name+'-markdeep'
    if os.path.isfile(out_dir+'/index.html'):
        p = util.get_host_platform()
        if p == 'osx':
            subprocess.call('open index.html', cwd=out_dir, shell=True)
        elif p == 'win':
            subprocess.call('start index.html', cwd=out_dir, shell=True)
        elif p == 'linux':
            subprocess.call('xdg-open index.html', cwd=out_dir, shell=True)
    else:
        log.error('no generated index.html found: {}'.format(out_dir+'/index.html'))
