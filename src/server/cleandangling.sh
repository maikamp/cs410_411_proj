#!/bin/sh
echo Clean up of dangling containers to remove orphans.
docker volume rm $(docker volume ls -qf dangling=true)