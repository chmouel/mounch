#!/usr/bin/env bash
set -euf
VERSION=${1-""}
PKGNAME=$(basename $(git rev-parse --show-toplevel))

docker ps -q >/dev/null || exit 1

bumpversion() {
	current=$(git tag -l | sort -Vr | head -1)
	echo "Current version is ${current}"

	major=$(python3 -c "import semver,sys;print(str(semver.VersionInfo.parse(sys.argv[1]).bump_major()))" ${current})
	minor=$(python3 -c "import semver,sys;print(str(semver.VersionInfo.parse(sys.argv[1]).bump_minor()))" ${current})
	patch=$(python3 -c "import semver,sys;print(str(semver.VersionInfo.parse(sys.argv[1]).bump_patch()))" ${current})

	echo "If we bump we get, Major: ${major} Minor: ${minor} Patch: ${patch}"
	read -p "To which version you would like to bump [M]ajor, Mi[n]or, [P]atch or Manua[l]: " ANSWER
	if [[ ${ANSWER,,} == "m" ]]; then
		mode="major"
	elif [[ ${ANSWER,,} == "n" ]]; then
		mode="minor"
	elif [[ ${ANSWER,,} == "p" ]]; then
		mode="patch"
	elif [[ ${ANSWER,,} == "l" ]]; then
		read -p "Enter version: " -e VERSION
		return
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

[[ $(git rev-parse --abbrev-ref HEAD) != main ]] && {
	echo "you need to be on the main branch"
	exit 1
}
[[ -z ${VERSION} ]] && bumpversion
git tag ${VERSION}
git push origin ${VERSION}
mkdir -p dist
tar czf ./dist/${PKGNAME}-${VERSION}.tar.gz LICENSE mounch.py README.md helpers/ rofi/
gh release create ${VERSION} ./dist/${PKGNAME}-${VERSION}.tar.gz

./packaging/aur/build.sh ${VERSION}
