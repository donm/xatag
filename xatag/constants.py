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
XATTR_FIELD_SEPARATOR = ';'
DEFAULT_CONFIG_DIR = "~/.xatag/"
CONFIG_DIR_VAR='XATAG_DIR'
KNOWN_TAGS_FILE='known_tags'

DEFAULT_KNOWN_TAGS_FILE="""## xatag known_tags file
##
## Add tags to this file to prevent seeing warnings when unknown tags are
## added to a file with 'xatag -a' or 'xatag -s'.
##
## Tags are specified by starting the line with the tag key, followed by a
## colon.  You can add as many tags as you want on every line, separated by
## semicolons.
##
## If a line doesn't have a colon, then every thing on that line is given the
## default prexif "tags:".  For sorting purposes, you might consider prefixing
## lines with "tags:" even though you don't have to.
##
## Lines beginning with # are comments.
##
###########################################
## The next three lines are all equivalent.
# favorite; TODO; organize; summer vacation;
# : favorite; TODO; organize; summer vacation
# tags: favorite; TODO; organize; summer vacation
#
## You can specify tag values for a particular key on different lines, if you
## want:
# taxes: 2013; 2012; 2011
# taxes: 2010; 2009; 2008
# taxes: personal; business
"""

# This is the string that is actually used, both for parsing the command line
# and for testing.
XATAG_USAGE="""xatag - file tagging using extended attributes (xattr).

Usage:
  xatag [options] ([-a] | -s | -S | -d)      TAG FILE...
  xatag [options] ([-a] | -s | -S | -d | -l) FILE... -t TAG...
  xatag [options] ([-a] | -s | -S | -d | -l) TAG...  -f FILE...
  xatag [options] [-l] FILE...
  xatag [options] (-c | -C) SRC DEST... [-t TAG]...
  xatag [options] -D  FILE...
  xatag [options] -x  TAG... | QUERY_STRING
  xatag [options] -e  TAG...
  xatag [options] --new-config [PATH]
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
  -e --enter       Enter TAG(s) into the known tag list.  Adding a tag to the
                   list will prohibit the warning printed when using an
                   unknown tag.  Known tags are also used for shell completion.
     --new-config  Write xatag config directory at ~/.xatag, or at PATH if an
                   argument is given.

Argument Flags:
  -t TAG --tag=TAG     The following argument is a tag; when this flag is
                       used, all other positional arguments without the flag
                       will be considered files.
  -f FILE --file=FILE  The following argument is a file; when this flag is
                       used, all other positional arguments without the flag
                       will be considered tags.

General Options:
  -n --complement  Perform the specified command on the complement of the set
                   of TAG(s) that is specified.  The -n stands for "not".  Can
                   be used on -d, -l, and -c/-C.
  -q --quiet       Avoid writing to stdout.
  -T --terse       Only print values for tag keys that have been altered.
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
