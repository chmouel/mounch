#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Chmouel Boudjnah <chmouel@chmouel.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# Rofi menu to jump to my preferred app, config is stored in
# ~/.config/mounch/mounch.yaml that look like this :
#
# emacs:
#   description: "Emacs"
#   binary: emacs
#   icon: emacs27
# suspend:
#   args: suspend
#   binary: systemctl
#   description: "Suspend"
#   icon: system-suspend-hibernate
# ssh:
#   args: ["-show", "ssh", "-theme",  "mounch"]
#   binary: rofi
#   description: "SSH"
#   icon: ssh
# calculate:
#   args: ["-modi", "calc:qalc +u8",
#           "-show", "calc", "-theme", "mounch", "-theme-str", '* { width: 640; height: 400;}']
#   binary: rofi
#   description: "Calculate"
#   icon: calc
#
#
# Binaries will be look in the path. Make sure your
# path is imported in your session.
# Icons will be looked up from your icon path theme or in
# ~/.local/share/icons/{iconname}.png
#
# There is a cache of the application sorted in ~/.cache/mounch/cache, it is
# used to sort the last one, so the last used appears at the top of the list.
import argparse
import collections
import os
import pathlib
import shutil
import subprocess
import sys

import yaml

DEFAULT_ARGS = ["-dmenu", "-p", "🤓 Choose your mounchie:"]

ROFI_CMD = "rofi"
ROFI_THEME = "mounch"
ROFI_ARGS = ["-i", "-p", "-show-icons", "-no-custom", "-theme", ROFI_THEME]

WOFI_CMD = "wofi"
WOFI_ARGS = [
    "-d",
    "-G",
    "-I",
    "--alow-images",
    "--allow-markup",
    "-W",
    "500",
    "-H",
    "500",
    "-i",
]


# maybe we should just import gi to be able get from the theme and not care about all of this? 🤔
# https://stackoverflow.com/a/65433574
def get_icon_path(icon: str) -> str:
    if os.path.exists(icon):
        return icon
    for path in [
            os.path.expanduser("~/.local/share/icons/"),
            os.path.expanduser("~/.local/share/icons/hicolor/scalable/apps"),
            os.path.expanduser("~/.local/share/icons/hicolor/48x48/apps"),
            os.path.expanduser("~/.local/share/icons/hicolor/64x64/apps"),
            "/usr/share/icons", "/usr/share/pixmaps",
            "/usr/share/icons/hicolor/scalable/apps",
            "/usr/share/icons/hicolor/64x64/apps",
            "/usr/share/icons/hicolor/48x48/apps",
            "/usr/share/icons/Adwaita/scalable/apps",
            "/usr/share/icons/Adwaita/64x64/apps",
            "/usr/share/icons/Adwaita/48x48/apps"
            "/usr/share/icons/Yaru/scalable/apps",
            "/usr/share/icons/Yaru/64x64/apps",
            "/usr/share/icons/Yaru/48x48/apps",
            "/usr/share/icons/Humanity/apps/48",
            "/usr/share/icons/Humanity/actions/48",
            "/usr/share/icons/Humanity-Dark/apps/48"
            "/usr/share/icons/Humanity-Dark/actions/48"
    ]:
        for icontype in ["svg", "png"]:
            tpath = pathlib.Path(f"{path}/{icon}.{icontype}")
            if tpath.exists():
                return str(tpath)
    return ""



def get_command(cmd: str, args: list, argp: argparse.Namespace) -> list:
    ret = [cmd] + DEFAULT_ARGS
    if not argp.no_defaults:
        if cmd == "rofi" and argp.rofi_theme:
            modified = []
            for x in args:
                if x == ROFI_THEME:
                    modified.append(argp.rofi_theme)
                else:
                    modified.append(x)
            args = modified
        ret += args
    return ret

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Mounchie - A simple Wofi/Rofi launcher on yaml')
    parser.add_argument(
        '--no-defaults',
        "-N",
        action='store_true',
        help=
        "No default arguments for launcher, let you configure it via the launcher config file"
    )
    parser.add_argument('--rofi-theme',
                        help="rofi theme to use")

    parser.add_argument('--use-rofi',
                        "-r",
                        dest='use_rofi',
                        action='store_true',
                        help="always use rofi")
    parser.add_argument('--use-wofi',
                        "-w",
                        dest='use_wofi',
                        action='store_true',
                        help="always use wofi")
    parser.add_argument(
        '--print-only',
        "-p",
        dest='print_only',
        action='store_true',
        help=
        "don't try to execute just print the command, usually would play nicely with \"swaymsg exec\""
    )

    return parser.parse_args()


def main():
    argp = parse_arguments()
    if not argp.use_rofi and not argp.use_wofi:
        if "WAYLAND_DISPLAY" in os.environ:
            argp.use_wofi = True
        else:
            argp.use_rofi = True
    if argp.use_rofi and argp.use_wofi:
        print("we can't have both rofi and wofi")
        sys.exit(1)

    cache_file = pathlib.Path("~/.cache/mounch/cache").expanduser()
    configfile = pathlib.Path("~/.config/mounch/mounch.yaml").expanduser()
    cached_entries = {}

    if not configfile.exists():
        print("I could not find config file: ", configfile)
        sys.exit(1)
    application_config = yaml.safe_load(configfile.open('r', encoding="utf-8"))

    if cache_file.exists():
        # Machine learning, big data at work!!!!!
        # Sort the application_config by frequency in the
        # cache first. It will first do a collection ordering if the element is
        # not an empty string when stripped. Sort the cached_entries as list
        # sorted by its frequency number and then merge in order as it appears
        # in the config (py3.7+) to the one who didn't appear with the other
        # application_config dict.
        for entry in cache_file.read_text(encoding="utf-8").split('\n'):
            try:
                id_, freq_str = entry.strip().split()
                if id_ not in application_config:
                    continue
                cached_entries[id_] = int(freq_str)
            except (IndexError, ValueError):
                continue

        application_config = {
            **dict(
                collections.OrderedDict([(el, application_config[el]) for el in dict(
                                             reversed(
                                                 sorted(cached_entries.items(),
                                                        key=lambda item: item[1]))).keys(
                                         ) if el.strip()])),
            **application_config
        }

    cmd = get_command(ROFI_CMD, ROFI_ARGS, argp)
    if argp.use_wofi:
        cmd = get_command(WOFI_CMD, WOFI_ARGS, argp)

    if "launcher" in application_config:
        cmd = [application_config["launcher"]["binary"]
               ] + application_config["launcher"]["args"]
        del application_config["launcher"]

    ret = []
    for app in application_config:
        icon = application_config[app].get('icon', 'default')
        iconpath = get_icon_path(icon)
        if "if" in application_config[app]:
            # pylint: disable=eval-used
            if not eval(application_config[app]["if"]):
                continue
        if argp.use_wofi:
            ret.append(
                f"img:{iconpath}:text:{application_config[app]['description']}"
            )
        else:
            ret.append(
                f"{application_config[app]['description']}\0icon\x1f{iconpath}"
            )

    with subprocess.Popen(cmd,
                          stdout=subprocess.PIPE,
                          stdin=subprocess.PIPE,
                          stderr=subprocess.PIPE) as popo:
        stringto = "\n".join(ret).encode()
        stdout = popo.communicate(input=stringto)[0]
        output = stdout.decode().strip()
        if not output:
            return

    if argp.use_wofi:
        output = output.rsplit(":", maxsplit=1)[-1]

    chosen_id = [
        x for x in application_config
        if application_config[x]['description'] == output
    ][0]
    chosen = application_config[chosen_id]

    if not cache_file.parent.exists():
        cache_file.parent.mkdir(0o755)

    if chosen_id not in cached_entries:
        cached_entries[chosen_id] = 0
    else:
        cached_entries[chosen_id] += 1
    cache_file.write_text('\n'.join(
        [f'{entry} {freq}' for entry, freq in cached_entries.items()]),
                          encoding="utf-8")

    binarypath = pathlib.Path(chosen['binary']).expanduser()
    binary = shutil.which(binarypath)
    if not binary:
        print(f"Cannot find executable \"{chosen['binary']}\"")
        sys.exit(1)

    args = chosen.get('args')

    if args is None:
        if argp.print_only:
            print(binary)
            return
        os.execv(binary, [binary])
    else:
        if isinstance(args, str):
            args = [args]
        if argp.print_only:
            print(" ".join([binary, *args]))
            return

        os.execv(binary, [
            binary,
            *args,
        ])


if __name__ == '__main__':
    main()
