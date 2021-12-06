# Tap
![build status](https://img.shields.io/drone/build/hwittenborn/tap/main?logo=drone&server=https%3A%2F%2Fdrone.hunterwittenborn.com)

## Overview
Tap is a feature-rich MPR helper that aims to be a drop-in replacement for APT. Tap provides access to almost every command accessible by `apt`, with MPR functionality integrated directly into said commands.

## Installation
If you have an existing MPR helper, you can simply install Tap from there via the `tap` package.

Otherwise, you can install Tap manually from the MPR:

```sh
git clone 'https://mpr.hunterwittenborn.com/tap'
cd tap/
makedeb -si
```

## Usage
Users of the APT commandline tools will find most options readily available to them. All available commands can be found via `tap --help` after installation.

Several commands have specific options available to them, those can be seen by running `tap *command* --help`.

## Support
Issues with using Tap should be made inside of the project's [issue tracker](/hwittenborn/tap/issues).

If a package fails to build with Tap, you should try building the package with makedeb before posting issues to the package maintainer or the makedeb issue tracker, as the issue may be rooted in Tap itself.

If you prefer a chatroom for obtaining support or just want to chat, Tap has a Matrix room located at [#tap:hunterwittenborn.com](https://matrix.to/#/#tap:hunterwittenborn.com).
