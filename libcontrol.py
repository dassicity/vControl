import argparse             # Helps in parsing command line arguments
import collections          # Helps in providing more container types like OrderedDict
import configparser         # Helps in reading and writing configuration files
import hashlib              # For SHA
import os
import re
import sys
import zlib                 # Compressing files

argparser = argparse.ArgumentParser(description="The stupid content tracker");

"""The CLI command for this program will be verc <command>. So to accept the command part, we will need argument sub parsers.
Because argument parser is used to parse verc."""

argsubparsers = argparser.add_subparsers(title="Commands", dest="command");
argsubparsers.required = True;

def main(argv=sys.argv[1:]):
    args=argparser.parse_args(argv);

    if args.command == "add"            : cmd_add(args);
    elif args.command == "cat-file"     : cmd_cat_file(args);       # Done
    elif args.command == "checkout"     : cmd_checkout(args);
    elif args.command == "commit"       : cmd_commit(args);
    elif args.command == "hash-object"  : cmd_hash_object(args);    # Done
    elif args.command == "init"         : cmd_init(args);           # Done
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
        self.config= configparser.ConfigParser();
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


def repo_create(path):
    """Creating a git repository"""

    repo = GitRepository(path, True);

    if os.path.exists(repo.worktree):
        if not os.path.isdir(repo.worktree):
            raise Exception("%s is not a directory!" % path);
        if os.listdir(repo.worktree):
            raise Exception("%s is not empty!" % path);
    else:
        os.makedirs(repo.worktree);

    assert(repo_dir(repo, "branches", mkdir=True));
    assert(repo_dir(repo, "objects", mkdir=True));
    assert(repo_dir(repo, "refs", "tags", mkdir=True));
    assert(repo_dir(repo, "refs", "heads", mkdir=True));

    #.git/description
    with open(repo_file(repo, "description"), "w") as f:
        f.write("Unnamed repository: Edit this file to name it.\n");

    # .git/HEAD
    with open(repo_file(repo, "HEAD"), "w") as f:
        f.write("ref: refs/heads/master\n");

    with open(repo_file(repo, "config"), "w") as f:
        config=repo_default_config();
        config.write(f);

def repo_default_config():
    ret=configparser.ConfigParser();

    ret.add_section("core");
    ret.set("core", "repositoryformatversion" , "0");
    ret.set("core", "bare" , "false");
    ret.set("core", "filemode" , "false");

    return ret;

""" Implementing INIT command"""
argsp = argsubparsers.add_parser("init" , help="Initialize a new, empty repository");
argsp.add_argument("path", metavar="directory", nargs="?", default=".", help="Where to create the repository");

def cmd_init(args):
    repo_create(args.path);

def repo_find(path=".", required=True):

    if os.path.isdir(os.path.join(path, ".git")):
        return GitRepository(path);

    parent = os.path.realpath(os.path.join(path, ".."));

    if parent == path:
        if required:
            raise Exception("Not a Git repository");
        else:
            return None;

    return repo_find(parent, required);


class Gitobject(object):

    def __init__(self, repo, data=None):
        self.repo = repo;

        if data != None:
            self.deserialize(data);

        def serialize(self):
            raise Exception("Unimplemented");

        def deserialize(self, data):
            raise Exception("Unimplemented")


def object_read(repo, sha):

    path = repo_file(repo, "objects", sha[0:2], sha[2:]);

    with open(path, "rb") as f:
        raw = zlib.decompress(f.read());

        # Read object type
        x = raw.find(b' ');
        fmt = raw[0:x];

        # Read and validate object size
        y = raw.find(b'\x00', x);
        size = int(raw[x:y].decode("ascii"));
        if size != len(raw)-y-1:
            raise Exception("Malformed object {0}: bad length".format(sha));

        # Pick constructor
        if      fmt == b'commit':   c=GitCommit;
        elif    fmt == b'tree':     c=GitTree;
        elif    fmt == b'tag':      c=GitTag;
        elif    fmt == b'blob':     c=GitBlob;
        else:
            raise Exception("Unknown type {0} for object {1}".format(fmt.decode('ascii'), sha));

        # Call constructor and return object
        return c(repo, raw[y+1:]);

def object_find(repo, name, fmt=None, follow=True):
    return name;

def object_write(obj, actually_write=True):
    # Serialize object data
    data = obj.serialize();
    # Add header
    result = obj.fmt+ b' '+ str(len(data)).encode() + b'\x00' + data;
    # Compute hash
    sha = hashlib.sha1(result).hexdigest();

    if actually_write:
        # Compute path of the file where the data is to be written
        path = repo_file(obj.repo, "objects", sha[0:2], sha[2:], mkdir=actually_write);

        with open(path, "wb") as f:
            f.write(zlib.compress(result));
        
    return sha;

class GitBlob(Gitobject):
    fmt = b'blob';

    def serialize(self):
        return self.blobdata;

    def deserialize(self, data):
        self.blobdata = data;

""" Impplementing CAT-FILE command"""

argsp = argsubparsers.add_parser("cat-file", help="Provide the actual data of repository objects");

argsp.add_argument("type", metavar="type", choices=["blob", "commit", "tag", "tree"], help="Specify the type");
argsp.add_argument("object", metavar="object", help="Object to display");

def cmd_cat_file(args):
    repo = repo_find();
    cat_file(repo, args.object, fmt=args.type.encode());

def cat_file(repo, obj, fmt=None):
    obj = object_read(repo, object_find(repo, obj, fmt=fmt));
    sys.stdout.buffer.write(obj.serialize());

"""Hash object command"""

argsp = argsubparsers.add_parser("hash-object" , help="Compute hash of a file and either store it or print its hash");

argsp.add_argument("-t" , metavar="type" , dest="type" , choices=["blob" , "commit" , "tag" , "tree"], default="blob" , help="Specify the type");
argsp.add_argument("-w" , dest="write" , action="store_true" , help="Actually write the object into the database");
argsp.add_argument("path" , help="Read object from <file>");

def cmd_hash_object(args):
    if args.write:
        repo = GitRepository(".");
    else:
        repo = None;

    with open(args.path, "rb") as fd:
        sha = object_hash(fd, args.type.encode(), repo);
        print(sha);

def object_hash(fd, fmt, repo=None):
    data=fd.read();

    if fmt==b'commit' : obj=GitCommit(repo, data)
    elif fmt==b'tree' : obj=GitTree(repo, data)
    if fmt==b'tag' : obj=GitTag(repo, data)
    if fmt==b'blob' : obj=GitBlob(repo, data)
    else:
        raise Exception("Unknown type %s!" % fmt)
    
    return object_write(obj , repo)

"""Key value list with meesage"""

