from mod import log, util, markdeep

def run(fips_dir, proj_dir, args):
    if len(args) > 0:
        if len(args) > 1:
            proj_name = args[1]
            proj_dir = util.get_project_dir(fips_dir, proj_name)
        if not util.is_valid_project_dir(proj_dir):
            log.error('{} is not a valid fips project!'.format(proj_name))
        if args[0] == 'build':
            markdeep.build(fips_dir, proj_dir)
        elif args[0] == 'view':
            # view also build the markdown docs first
            markdeep.build(fips_dir, proj_dir)
            markdeep.view(fips_dir, proj_dir)
        else:
            log.error("expected 'build' or 'view' arg")
    else:
        log.error("expected 'build' or 'view' arg")

def help():
    log.info(log.YELLOW +
        "fips markdeep build [proj]\n"
        "fips markdeep view [proj]\n"+log.DEF+
        "    Generate or view Markdeep documentation webpage.\n"
        "    Parses all *.h files in a project, searches for special\n"
        "    /*# #*/ comment blocks, and extracts them into Markdeep\n"
        "    HTML files.")