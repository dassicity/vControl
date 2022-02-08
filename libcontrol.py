import argparse             # Helps in parsing command line arguments
import collections          # Helps in providing more container types like OrderedDict
import configparser         # Helps in reading and writing configuration files
import hashlib              # For SHA
import os
import re
import sys
import zlib                 # Compressing files

argparser = argparse.ArgumentParser(description="The stupid content tracker");

argsubparsers = argparser.add_subparsers(title="Commands", dest="command");
argsubparsers.required = True;

def main(argv=sys.argv[1:]):
    args=argparser.parse_args(argv);

    if args.command == "add"            : cmd_add(args);
    elif args.command == "cat-file"     : cmd_cat_file(args);
    elif args.command == "checkout"     : cmd_checkout(args);
    elif args.command == "commit"       : cmd_commit(args);
    elif args.command == "hash-object"  : cmd_cat_file(args);
    elif args.command == "int"          : cmd_init(args);
    elif args.command == "log"          : cmd_log(args);
    elif args.command == "ls-tree"      : cmd_ls_tree(args);
    elif args.command == "merge"        : cmd_merge(args);
    elif args.command == "rebase"       : cmd_rebase(args);
    elif args.command == "rev-parse"    : cmd_rev_parse(args);
    elif args.command == "rm"           : cmd_rm(args);
    elif args.command == "show-ref"     : cmd_show_ref(args);
    elif args.command == "tag"          : cmd_tag(args);
    
class GitRepository(object):

    worktree = none;
    gitdir = none;
    config = none;

    def __init__ (self, path, force=False):
        self.worktree = path;
        self.gitdir = os.path.join(path, ".git");

        if not (force or os.path.isdir(self.gitdir)):
            raise Exception("Not a git repository %s" % path);

        # Read configuration file in .git/config
        self.config - configparser.ConfigParser();
        cf  = repo_file(self , "config");

        if cf and os.path.exists(cf):
            self.config.read([cf]);
        elif not force:
            raise Exception("Configuration file is missing");

        if not force:
            vers = int(self.config.get("core" , "repositoryformatversion"));
            if vers != 0:
                raise Exception("Unsupported repository format version %s" % vers);