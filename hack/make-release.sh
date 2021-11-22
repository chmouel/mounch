#!/usr/bin/env bash
set -eufx

VERSION=${1-""}
[[ -z ${VERSION} ]] && { echo "need a version"; exit 1 ;}

git tag -s ${VERSION} -m "Releasing version ${VERSION}"
git push --tags origin ${VERSION}

./hack/aur/build.sh ${VERSION}
