"""initialize fips project directory from template"""

import os
from string import Template

from mod import log, util

#-------------------------------------------------------------------------------
def write_git_ignore(proj_dir, entries) :
    """modify or create the .gitignore file with fips-specific
    entries. fips entries will go into a special section marked with:
        #>fips
        #<fips

    :param entries: array of fips .gitignore strings
    """
    path = proj_dir + '/.gitignore'
    out_lines = []
    if os.path.isfile(path) :
        # .gitignore already exists, read into lines array,
        # but drop everything between #>fips and #<fips
        with open(path, 'r') as f :
            in_lines = f.readlines()
        copy_line = True
        for l in in_lines :
            if '#>fips' in l :
                copy_line = False
            if copy_line :
                out_lines.append(l)
            if '#<fips' in l :
                copy_line = True
    
    # append the fips .gitignore entries
    out_lines.append('#>fips\n')
    out_lines.append('# this area is managed by fips, do not edit\n')
    out_lines.extend('\n'.join(entries) + '\n')
    out_lines.append('#<fips\n')

    # write back .gitignore file
    with open(path, 'w') as f :
        f.writelines(out_lines)

    log.info("wrote '{}'".format(path))
    
#-------------------------------------------------------------------------------
def copy_template_file(fips_dir, proj_dir, filename, values, silent=False) :
    """copy a template file from fips/templates to the project 
    directory and replace template values (e.g. the project name),
    ask for user permission if files exist

    :param fips_dir:    absolute fips directory
    :param proj_dir:    absolute project directory
    :param filename:    filename to copy from fips/templates
    :param values:      template key/value dictionary
    :param silent:      if True, overwrite existing file and don't print status
    :returns:           True file overwritten, False on not overwritten
    """
    
    src_path = fips_dir + '/templates/' + filename
    dst_path = proj_dir + '/' + filename

    if not os.path.isfile(src_path) :
        log.error("template src file '{}' doesn't exist".format(src_path))
    
    if not silent :
        if os.path.isfile(dst_path) :
            if not util.confirm("overwrite '{}'?".format(dst_path)) :
                log.info("skipping '{}'".format(dst_path))
                return False

    content = None
    with open(src_path, 'r') as f :
        content = f.read()
    content = Template(content).substitute(values)
    with open(dst_path, 'w') as f :
        f.write(content)

    if not silent :
        log.info("wrote '{}'".format(dst_path))
    return True







