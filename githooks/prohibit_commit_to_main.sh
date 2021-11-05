#!/bin/sh

branch="$(git rev-parse --abbrev-ref HEAD)"

if [ "$branch" = "main" ] || [ "$branch" = "master" ]; then
  echo "You can't commit directly to main/master branch"
  exit 1
fi
