#! /bin/bash
mkdir -p ./ucSession
echo "Making chrome ram session"
mkdir -p /dev/shm/capfamucsession
echo "Ram session cost was $(du -sh /dev/shm/capfamucsession)"
echo "Purging"
rm -r /dev/shm/capfamucsession/*
echo "Copying $(du -sh ./ucSession) worth of cost"
cp -rp ./ucSession/. /dev/shm/capfamucsession
echo "Following program will start with configured chrome session in ram shown above"
echo "Taking over ctrl+c"
trap ' ' SIGINT
pipenv run python ./main.py --session-dir /dev/shm/capfamucsession
echo "Program has finished, restoring ctrl+c"
trap - SIGINT
echo "Ram session currently worth of $(du -sh /dev/shm/capfamucsession)"
echo "Stored session at current directory currently worth of $(du -sh ./ucSession)"
echo "Copying changed files over to original session directory"
rsync --delete -a /dev/shm/capfamucsession/ ./ucSession
echo "Synced saved session at current directory now worth $(du -sh ./ucSession)"
echo "Purging ram session"
rm -rd /dev/shm/capfamucsession
echo "Finished"
