# Embedded Sass in Python

This package doesn't have a good name yet.

The [embedded Sass protocol](https://github.com/sass/sass/blob/main/spec/embedded-protocol.md), implemented for python.

Existing Sass libraries for python use [libsass](https://sass-lang.com/libsass). Libsass is now
deprecated, and the only way to use either run the dart sass binary in a subprocess (subprocess
overhead every time the binary is executed), or to use the
embedded Sass protocol (which doesn't have many implementations). So, here's an attempt at the
protocol for python.

It's extremely early in development, currently only supporting the VersionRequest command. The goal
is to eventually provide a not-quite-drop-in replacement for
[libsass-python](https://sass.github.io/libsass-python).

## License

Except for the `embedded_sass_python/varint.py` file, the code in this repository is public domain
software. To avoid confusion about the copyright status of this code, a "license" is provided via
the [Unlicense](https://unlicense.org). The unlicense disclaims copyright interest in the software,
and explicitly places it in the public domain.

The `embedded_sass_python/varint.py` file was adapted from
<https://github.com/fmoo/python-varint/>, and is licensed under the MIT license. Please read the
`embedded_sass_python/varint.py` file for the full license text.

This project also uses the [embedded Sass protobuf schema](https://github.com/sass/sass/blob/main/spec/embedded_sass.proto). This schema is copyright Google Inc., and licensed under the MIT license. Please read that file for the full copyright header.
