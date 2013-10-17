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
