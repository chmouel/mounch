#!/usr/bin/env bash
set -euf
current=$(git describe --tags $(git rev-list --tags --max-count=1))
VERSION=${1-""}
[[ -z ${VERSION} ]] && { 
   echo "Current version is ${current}"
   read -p "Would you like to bump [M]ajor, Mi[n]or or [P]atch: " ANSWER
   if [[ ${ANSWER,,} == "m" ]];then
       mode=major
   elif [[ ${ANSWER,,} == "n" ]];then
       mode=minor
   elif [[ ${ANSWER,,} == "p" ]];then
       mode=patch
   else
       print "no or bad reply??"
       exit
   fi
   VERSION=$(python3 -c "import semver,sys;print(str(semver.VersionInfo.parse(sys.argv[1]).bump_${mode}()))" ${current})
   [[ -z ${VERSION} ]] && {
       echo "could not bump version automatically"
       exit
   }
   echo "Releasing ${VERSION}"
}
set -x

git tag -s ${VERSION} -m "Releasing version ${VERSION}"
git push --tags origin ${VERSION}

./hack/aur/build.sh ${VERSION}
