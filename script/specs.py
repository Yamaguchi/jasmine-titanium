#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, re, shutil
from optparse import OptionParser

def project_dir():
    return resource_dir().replace("/Resources", "")

def resource_dir():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    sep = os.sep
    return re.sub("%(sep)sResources%(sep)s.+" % locals(), "%(sep)sResources" % locals(), script_dir)

def sdk_version():
    setting_path = os.path.join(project_dir(), ".settings", "com.appcelerator.titanium.mobile.prefs")
    version = ''
    version_constant_name = "MOBILE_PROJECT_SDK_VERSION"
    for line in open(setting_path, 'r'):
        if line.startswith(version_constant_name):
            version = re.sub(version_constant_name + "=", "", line.strip())
        
    return version

def options_temporary_path():
    return os.path.join(resource_dir(), 'temp_runner_options.js')

def app_js_path():
    return os.path.join(resource_dir(), 'app.js')

def app_js_backup_path():
    return app_js_path() + ".backup"

def jasmine_titanium_app_js_path():
    return os.path.join(resource_dir(), 'vendor', 'jasmine-titanium', 'lib', 'jasmine-titanium-app.js')

def save_options_to_temporary(options, args):
    class_name = options.class_name
    verbose = options.is_verbose

    f = open(options_temporary_path(), "w")
    f.write("var runner_options = { classname:'%(class_name)s', verbose:'%(verbose)s' };" % locals())
    f.close()

def remove_temporary():
    os.remove(options_temporary_path())

def setup_jasmine_titanium_app_js():
    shutil.copyfile(app_js_path(), app_js_backup_path())
    shutil.copyfile(jasmine_titanium_app_js_path(), app_js_path())

def restore_app_js():
    shutil.copyfile(app_js_backup_path(), app_js_path())
    os.remove(app_js_backup_path())

def create_option_parser():
    parser = OptionParser(usage = "Usage: specs.py [options] [files or directories]")

    parser.add_option("-v", "--verbose", dest="is_verbose", 
            help="print spec detail.", action="store_true", default='')

    parser.add_option("-s", "--spec", dest="class_name", 
            help="specify class name", default="", metavar="CLASS_NAME")

    parser.add_option("-o", "--out", dest="output", 
            help="Write output to a file instead of STDOUT.", default="", metavar="FILE")

    return parser

def run_iphone_simulator():
    command = "/Library/Application\ Support/Titanium/mobilesdk/osx/" + sdk_version() + "/iphone/builder.py run " + project_dir()
    os.system(command)

def main(argv):
    parser = create_option_parser()
    (options, args) = parser.parse_args(argv)

    save_options_to_temporary(options, args)
    setup_jasmine_titanium_app_js()

    if options.output:
        log = os.open(options.output, os.O_WRONLY|os.O_CREAT)
        os.dup2(log, sys.stdout.fileno())

    run_iphone_simulator()

    restore_app_js()
    remove_temporary()

if __name__ == "__main__":
    main(sys.argv)
    sys.exit(0)
