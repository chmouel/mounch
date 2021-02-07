#!/usr/bin/env bash
COMPLEXITY=15
SWITCH=MNCLS
set -eux


if [[ ${ROFI_RETV} == 1 ]];then
    echo "$@" | xclip -i -selection clipboard
    exit
elif [[ ${ROFI_RETV} == 2 ]];then
    COMPLEXITY=${1:-${COMPLEXITY}}
    SWITCH=${2:-${SWITCH}}
fi

apg -${SWITCH} -a1 -m${COMPLEXITY}
