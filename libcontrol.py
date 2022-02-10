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

    worktree = None;
    gitdir = None;
    config = None;

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
    
def repo_path(repo, *path):
    """A function to basically compute a repo's gitdir path"""
    return os.path.join(repo.gitdir, *path);


def repo_file(repo, *path, mkdir=False):
    
    """This method is essentially like repo_path but here it is checking whether a dir at *path is present or not.
    If a dir is not present, it is creating a dir by providing mkdir=mkdir and then returning repo_path(path)"""
    
    if repo_dir(repo, *path[:-1], mkdir=mkdir):
        return repo_path(repo , *path); 


def repo_dir(repo, *path, mkdir=False):
    path = repo_path(repo, *path);

    """Here it is checking if the path and the dir exists. If not it will create a dir in the next portion"""

    if os.path.exists(path):
        if os.path.isdir(path):
            return path;
        else:
            raise Exception("Not a directory %s" % path);
    
    if mkdir:
        os.makedirs(path);
        return path;
    else:
        return None;