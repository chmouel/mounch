#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

VERSION=${1:-""}
[[ -z ${VERSION} ]] && { echo "need a version!";exit 1 ;}
AUTHOR_EMAIL="chmouel@chmouel.com"
AUTHOR_NAME="Chmouel Boudjnah"
RELEASE=1
PKGNAME=mounch
image_name=${PKGNAME}-aur-builder
finalaction="git push origin master"
gitdir=$(git rev-parse --show-toplevel)
cd "${gitdir}"

while getopts "n" o; do
    case "${o}" in
        n)
            finalaction="echo done"
            ;;
        *)
            echo "Invalid option"; exit 1;
            ;;
    esac
done
shift $((OPTIND-1))

sudo docker build -f ./packaging/aur/Dockerfile -t ${image_name} .

sudo docker run --rm \
           -v "${gitdir}":/src \
           -v $SSH_AUTH_SOCK:/ssh-agent --env SSH_AUTH_SOCK=/ssh-agent \
           --name ${PKGNAME}-builder \
           -it ${image_name} \
           /bin/bash -c "set -x;mkdir -p ~/.ssh/;chmod 0700 ~/.ssh && \
                         ssh-keyscan aur.archlinux.org >> ~/.ssh/known_hosts && \
                         git clone --depth=1 ssh://aur@aur.archlinux.org/${PKGNAME} /tmp/${PKGNAME} && \
                         cd /tmp/${PKGNAME} && \
                         git config --global user.email '${AUTHOR_EMAIL}' && \
                         git config --global user.name '${AUTHOR_NAME}' && \
                         sed -E 's#(pkgver=).*#\1$VERSION#' -i PKGBUILD && \
                         updpkgsums && \
                         makepkg --printsrcinfo > .SRCINFO && \
                         git clean -f && \
                         git commit -v -m 'Update to ${VERSION}' .SRCINFO PKGBUILD && \
                         ${finalaction}"
