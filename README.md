# Selfection (an RTS tool for TizenRT)

Selfection is an RTS tool for projects written in C that compiles to
Arm binary. Selfection uses the `arm-none-eabi-objdump` and
`arm-none-eabi-readelf` tools to statically build a dependency graph
of functions from binaries and detect modified code elements.

### Requirements

`arm-none-eabi-objdump` and `arm-none-eabi-readelf` should be in
`PATH` environment variable. You can download GNU Arm Embedded
Toolchain from
[here](https://developer.arm.com/open-source/gnu-toolchain/gnu-rm/downloads).

### Usage
`python -m selfection.callgraph rts -h`
```
usage: TOOL rts [-h] [--dir DIR] [--skip SKIP] [--debug] [--syms] BINARY

positional arguments:
  BINARY       binary file

optional arguments:
  -h, --help   show this help message and exit
  --dir DIR    cache directory for dependencies
  --skip SKIP  file path of skipped functions
  --debug      Enable debug output
  --syms       Enable tracking of symbols
```

### Citing

If you use our tool in your publication, please cite it.
```
@inproceedings{CelikETAL18Selfection,
  title={Regression test selection for TizenRT},
  author={Celik, Ahmet and Lee, Young Chul and Gligoric, Milos},
  booktitle={Proceedings of the 2018 26th ACM Joint Meeting on European Software Engineering Conference and Symposium on the Foundations of Software Engineering},
  pages={845--850},
  year={2018},
  organization={ACM}
}
```
### Limitations

Only supports binaries of `armv7-m` and `armv7-r`.

### Disclaimer

All trademarks, servicemarks, registered trademarks, and registered
servicemarks (including Arm and TizenRT) are the
property of their respective owners.
