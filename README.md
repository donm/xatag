xatag
=====

Xatag tags files by writing human readable text to the extended attributes
(xattr) of a file.  It relies on the excellent desktop search application
[Recoll](recoll.org) for indexing tags, and for integrating tags into desktop
search queries.

Xatag also provides a FUSE-based filesystem to search tagged files by browsing
a hierarchy of your tags.  The hierarchy is created dynamically as you
navigate.

Keeping tags in the extended attributes is a Good Thing because the metadata
can be transferred with the file when it is renamed, copied, or moved to
another system (if it supports xattrs).  Any database of tagged files can be
recreated using data stored in the files.

