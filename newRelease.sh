#! /usr/bin/bash

#TODO: parameter check

VERSION_PART=$1

currentVersion=$(bump2version --dry-run --list $VERSION_PART --allow-dirty | grep current_version | sed -r s,"^.*=",,)
nextVersion=$(bump2version --dry-run --list $VERSION_PART --allow-dirty | grep new_version | sed -r s,"^.*=",,)
echo $nextVersion

# windows cp1252 has some trouble piping the output if we don't do this
PYTHONIOENCODING="UTF-8" BUMP_VERSION="v$nextVersion ($(date +%Y-%m-%d))" gitchangelog > CHANGELOG.rst
git add CHANGELOG.rst

bump2version --allow-dirty  $VERSION_PART

git push
git push origin v$nextVersion

# git commit -m "Bump $currentVersion -> $nextVersion"
# git tag v$nextVersion -m "Bump $currentVersion -> $nextVersion"
