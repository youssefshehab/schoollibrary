#!/bin/bash

# A script to backup the database of the school library system.
#
# Notes:
#     - The relative backups dir is a mounted usb, which is used for 
#       storing backups of database and book covers/thumbnails.
#     - Directories are relative to the location of this script so that 
#	this script is included within in the application directory
#       and called from anywhere.	


# source files
DATABASE=`dirname $0`/bpslibrary/bpslibrary.db
THUMBNAILDIR=`dirname $0`/bpslibrary/static/img/thumbnails

# general opt
BACKUPDIR=`dirname $0`/backups
BACKUPDAYS=5

# run vars
TIMESTAMP=$(date +'%Y%m%d%H%M%S')
DATABASEBACKUP=$BACKUPDIR/database/bpslibrary_$TIMESTAMP.db
THUMBNAILBACKUP=$BACKUPDIR/thumbnails_$TIMESTAMP

sqlite3 $DATABASE <<EOSQL
.backup $DATABASEBACKUP
.quit
EOSQL

# Backup thumbnails
mkdir $THUMBNAILBACKUP
cp -f $THUMBNAILDIR/* $THUMBNAILBACKUP/

# Delete old database backups
find $BACKUPDIR/database -type f -iname '*.db' -mtime +$BACKUPDAYS -exec rm -f {} \;

# Detele old thumbnails
find $BACKUPDIR -type d -iname 'thumbnails*' -mtime +$BACKUPDAYS -exec rm -Rf {} \;

