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
