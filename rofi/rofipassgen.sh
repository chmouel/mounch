#!/usr/bin/env bash
COMPLEXITY=15
SWITCH=MNCLS
set -eux


if [[ ${ROFI_RETV} == 1 ]];then
   if [[ ${XDG_SESSION_TYPE} == "wayland" ]];then
      echo "$@"|wl-copy
   else
      echo "$@" | xclip -i -selection clipboard
   fi
   exit
elif [[ ${ROFI_RETV} == 2 ]];then
    COMPLEXITY=${1:-${COMPLEXITY}}
    SWITCH=${2:-${SWITCH}}
fi

apg -${SWITCH} -a1 -m${COMPLEXITY}
