# xatag #

Xatag tags files by writing human readable text to the extended attributes
(xattr) of a file.  It relies on the excellent desktop search application
[Recoll](http://recoll.org) for indexing tags, and for integrating tags into
desktop search queries.

Xatag will also provide a FUSE-based filesystem to search tagged files by
browsing a hierarchy of your tags.  The hierarchy is created dynamically as
you navigate.

Keeping tags in the extended attributes is a Good Thing because the metadata
can be transferred with the file when it is renamed, copied, or moved to
another system (if it supports xattrs).  Any database of tagged files can be
recreated using data stored in the files.

## setup ##

### Recoll ###

For now, it is necessary to use the development version of Recoll and compile
the source.  This is a relatively easy procedure, at least on Debian and Ubuntu.

#### Installation ####

```
> sudo apt-get remove recoll # if it's already installed
> sudo apt-get install mercurial
> sudo apt-get install make g++ libxapian-dev libqt4-dev libqtwebkit-dev zlib1g-dev
> hg clone https://bitbucket.org/medoc/recoll
> cd recoll/src
> ./configure --prefix=/usr/local
> make
> sudo make install
```

#### Configuration ####

Aside from the many Recoll configuration options that you'll want to
investigate, xatag needs to inform Recoll to read and index tags from the
extended attributes.  Tell Recoll to read the xatag config files for Recoll by
setting either of the environment varibles `RECOLL_CONFTOP` or
`RECOLL_CONFMID` to the `recoll` folder inside your xatag config directory
(`~/.xatag/recoll`, by default).

##### Short version #####

Put the following line in your `~/.xsessionrc` file and in your shell startup
file (e.g., `~/.bash_profile`):

```bash
export RECOLL_CONFMID="$HOME/.xatag/recoll"
```

##### Long version #####

You can add one of these lines to your shell startup file (`~/.bash_profile`, or
whatever).  But since you'll most likely want to launch the Recoll GUI from
outside of your shell, you'll need to also set up the environment variables
for your session, using `~/.xsessionrc`, `~/.pam_environment` or something
similar.

```bash
# Edit paths if you choose to set up your xatag config directory somewhere
# else.
#
# Pick one:
export RECOLL_CONFTOP="$HOME/.xatag/recoll"
export RECOLL_CONFMID="$HOME/.xatag/recoll"
```

The values set in the xatag-specific recoll directory will overwrite the
global Recoll options if you set `RECOLL_CONFMID`.  If you instead set
`RECOLL_CONFTOP` then these options will overwrite the default config profile
(typically found in `~/.recoll`).

Currently, the xatag-specific Recoll directory does not overwrite settings
that most Recoll users will already have configured.
