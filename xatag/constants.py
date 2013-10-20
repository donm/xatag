# Copyright (c) 2013 Don March <don@ohspite.net>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


XATTR_PREFIX = 'org.xatag.tags'
DEFAULT_TAG_KEY = 'tag'
XATTR_FIELD_SEPARATOR = ';'
DEFAULT_CONFIG_DIR = "~/.xatag/"
CONFIG_DIR_VAR='XATAG_DIR'
KNOWN_TAGS_FILE='known_tags'
IGNORED_KEYS_FILE='ignored_keys'
RECOLL_CONFIG_DIR='recoll' # relative to xatag config dir

RECOLL_BASE_CONFIG_DIR_VAR='XATAG_DIR'
DEFAULT_RECOLL_BASE_CONFIG_DIR='~/.recoll/'

RECOLL_TAG_PREFIX='xa:'
RECOLL_XAPIAN_PREFIX='XYXA'

DEFAULT_KNOWN_TAGS_FILE="""## xatag known_tags file
##
## Add tags to this file to prevent seeing warnings when unknown tags are
## added to a file with 'xatag -a' or 'xatag -s'.
##
## Lines beginning with # are comments.
##
## Tags are specified by starting the line with the tag key, followed by a
## colon.  You can add as many tags as you want on every line, separated by
## semicolons.
##
## If a line doesn't have a colon, then every thing on that line is given the
## default prefix "tag:".
##
## For sorting purposes, you might consider prefixing lines with "tag:" even
## though you don't have to.  Then you can sort the file using something like:
##      > grep '^#' known_tags ; grep -v '^#' known_tags | sort ; } > kt
##      > cat kt   # check that the output is what you want
##      > mv kt known_tags
##
## Removing all instances of a tag key from this file will cause the key to be
## dropped from the Recoll fields file the next time it is generated.  Adding
## a new key will cause the key to be added to the fields file.
#################################################################
## The next three lines are all equivalent.
# favorite; TODO; organize; summer vacation;
# : favorite; TODO; organize; summer vacation
# tag: favorite; TODO; organize; summer vacation
#
## You can specify tag values for a particular key on different lines, if you
## want:
# taxes: 2013; 2012; 2011
# taxes: 2010; 2009; 2008
# taxes: personal; business
"""

DEFAULT_IGNORED_KEYS_FILE="""## xatag ignored_keys file
##
## Add tag keys to this file to prevent them from being automatically added to
## the recoll/fields file, so they won't be indexed by Recoll.
##
## Lines beginning with # are comments.
##
## Write one key per line in this file, without a trailing colon (unless for
## some reason the trailing colon is actually part of the tag key).
##
#################################################################
## You probably don't want to do this:
# tag
## You might want something like this:
# publication-date
"""

DEFAULT_RECOLL_CONF="""# xatag-specific recoll config
#
# To tell Recoll to load this file, set one of the environment variables
# RECOLL_CONFTOP or RECOLL_CONFMID to the parent directory of this file.
#
# The values set in this file will overwrite the global Recoll options if you
# set RECOLL_CONFMID to look at this directory.  If you set RECOLL_CONFTOP
# instead, then these options will overwrite the default config profile
# (typically at ~/.recoll) as well as the global Recoll options.
#
# The default line below asks recoll to look for tags on any file that it
# already indexes.  If you want Recoll to look for xatag tags in only part of
# your file system, then edit and uncomment the line above it.
#
# [~/docs]
metadatacmds = ; rclmultixatag = xatag --recoll-tags %f
"""

RECOLL_FIELDS_UPDATE_RE = ".*XATAG WILL REGENERATE THIS FILE"

RECOLL_FIELDS_HEAD="""# xatag-specific Recoll fields config
#
# XATAG WILL REGENERATE THIS FILE
#
# As long as one of the first 5 lines of this file contains the string
#
#     "XATAG WILL REGENERATE THIS FILE"
#
# then this file will be overwritten every time a new tag key is added to the
# known_tags file.  This way Recoll will index the key in its database.
#
# When xatag regenerates this file, it includes all keys found in the
# known_tags file except for those found in the ignored_tags file.
#
# If you want to keep this file up to date manually, delete the aforementioned
# line or move it below the fifth line of this file.  You might want to do
# this if, for instance, you plan on using a fairly stable set of tag keys
# that you want Recoll to index, and also use some other set of tag keys that
# you don't want indexed.
#
# However, if you have a relatively stable set of keys that you don't want
# indexed, then add them to the 'ignored_keys' file, and let this file be
# automatically updated.
"""

RECOLL_FIELDS_PREFIXES="""
# By convention, xatag keys in the [prefixes] section have "xa:" prepended to
# the name, and the part after the equals sign (the key name for Xapian)
# should be in all caps.  Xatag adds new entries in the form
#
#     xa:keyname = XYXAKEYNAME
#
[prefixes]
"""

RECOLL_FIELDS_STORED="""
# In the [stored] section, add the same tag prefixes as before followed by an
# equals sign, unless you have specific requirements,
#
[stored]
"""

# This is the string that is actually used, both for parsing the command line
# and for testing.
XATAG_USAGE="""xatag - file tagging using extended attributes (xattr).

Usage:
  xatag [options] (-a | -s | -S | -d)           TAG       FILE...
  xatag [options] (-a | -s | -S | -d | [-l]) -t TAG...    FILE...
  xatag [options] (-a | -s | -S | -d | [-l])    TAG... -f FILE...
  xatag [options] [-l] FILE...
  xatag [options] (-c | -C) SRC DEST... [-t TAG]...
  xatag [options] -D FILE...
  xatag [options] -x TAG... | QUERY
  xatag [options] -u TAG...
  xatag [options] -U [TAG]...
  xatag [options] --new-config [CONFIG_DIR]
  xatag [options] --recoll-tags FILE
  xatag [options] --regenerate
  xatag  -h | --help
  xatag  -v | --version

File Tagging Commands:
  -a --add         Add the TAG(s) to each of the FILE(s).  This is the default
                   command if you provide more than one argument.
  -c --copy        Copy xatag fields from SRC to DEST(s)
  -C --copy-over   Copy xatag fields from SRC to DEST(s), erasing all previous
                   xatag data in the extended attributes of DEST(s).
                   Equivalent to "xatag -D FILE...; xatag -c TAG FILE..."
  -d --delete      Remove all of the given TAG(s) from the given FILE(s).
  -D --delete-all  Remove all xatag tags from the FILE(s)
  -l --list        List the tags currently written on FILE(s).  If TAG(s) are
                   given as well, list only the TAG(s) that are set on the
                   FILE(s).
  -s --set         Set the tags of the FILE(s) to the TAG(s) given, erasing
                   any previous xatag data in the extended attributes in the
                   same keys mentioned in the new TAG(s).
  -S --set-all     Set the tags of the given FILE(s) exactly to the TAG(s)
                   given erasing any previous xatag data in the extended
                   attributes.  Equivalent to "xatag -D FILE...; xatag -a TAG
                   FILE..."
  -x --execute     Execute a query.

Management Commands:
     --new-config   Write xatag config directory at ~/.xatag, or at CONFIG_DIR
                    if an argument is given.
     --recoll-tags  List the tags of FILE in a format appropriate for Recoll's
                    metadatacmds field.
  -R --regenerate   Recreate all of the files that are generated by xatag.
                    Right now, this is only the fields file in the xatag
                    recoll config directory.
  -u --use          Enter TAG(s) into the known tag list.  Adding a tag to the
                    list will prohibit the warning printed when using an
                    unknown tag.  Known tags are also used for shell completion.
  -U --used-tags    Print list of known tags.

Argument Flags:
  -t TAG --tag=TAG     The following argument is a tag; when this flag is
                       used, all other positional arguments without the flag
                       will be considered files.
  -f FILE --file=FILE  The following argument is a file; when this flag is
                       used, all other positional arguments without the flag
                       will be considered tags.

General Options:
     --config-dir=CONFIG-DIR  Use CONFIG-DIR as the xatag configuration,
                              instead of checking in the default path or
                              environment variable.
  -n --complement  Perform the specified command on the complement of the set
                   of TAG(s) that is specified.  The -n stands for "not".  Can
                   be used on -d, -l, and -c/-C.
     --no-index    Do not attempt to update the Recoll index for altered files.
  -q --quiet       Avoid writing to stdout.
  -T --terse       Only print values for tag keys that have been altered.
                   Also, don't print the names of files unless tags will be
                   printed as well.
  -w --no-warn     Do not warn when adding or setting tag values that are not
                   in the known_tags config file.
  -W --warn-once   Print a warning when adding or setting tag values that are
                   not in the known_tags config file, but then add them to the
                   file to prevent future messages.
  -v --version     Print version and exit.
  -h --help        You managed to find this just fine already.

Tag Printing Options:
  -k --key-val-pairs  Print key:val style tag separately, instead of printing
                      all values with the same key together.  Probably easier
                      to grep.  Compatible with --one-line.
  -o --one-line       Print all tags on one line.  Possibly easier to grep.
                      Compatible with --key-val-pairs.
  -F <fsep> --file-separator=<fsep>  Set character(s) used to separate the file
                                     name from the tags for that
                                     file. [default: :] (a colon)
  -K <ksep> --key-separator=<ksep>   Set character(s) used to separate the tag
                                     key from the tag value.  This only
                                     affects printing, not parsing tags passed
                                     as arguments.  [default: :] (a colon)
  -V <vsep> --val-separator=<vsep>   Set character(s) used to separate tag
                                     values.  This only affects printing, not
                                     parsing tags passed as arguments.
                                     [default:  ] (a space)

When reading and writing extended attributes, symlinks are followed by default.
"""
