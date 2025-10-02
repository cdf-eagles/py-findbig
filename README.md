[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Lint Python Code](https://github.com/cdf-eagles/py-findbig/actions/workflows/pylint.yaml/badge.svg)](https://github.com/cdf-eagles/py-findbig/actions/workflows/pylint.yaml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=cdf-eagles_py-findbig&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=cdf-eagles_py-findbig)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=cdf-eagles_py-findbig&metric=bugs)](https://sonarcloud.io/summary/new_code?id=cdf-eagles_py-findbig)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=cdf-eagles_py-findbig&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=cdf-eagles_py-findbig)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=cdf-eagles_py-findbig&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=cdf-eagles_py-findbig)
[![main](https://img.shields.io/badge/main-stable-green.svg?maxAge=2592000)]('')

# Python Implementation of 'findbig'

This is a Python3 implementation of [Jason Fesler's](https://github.com/jfesler) Perl5 'findbig' script.

It has only been tested on macOS and FreeBSD, but it should work on on a variety of UNIX/Linux distributions as long as Python3 is installed.

## Example Usage

### Help
The default number of lines to print is determined by your terminal size. A standard 80x24 terminal will output 19 lines of output.

```
# ./findbig.py -h
usage: findbig.py [-h] [-n NUMPRINT] [searchPath]

This script recursively finds the largest files/directories in the current
working directory (default) or the specified directory.

positional arguments:
  searchPath          If provided, program will search the provided path
                      instead of the current working directory. (default: ./)

options:
  -h, --help          show this help message and exit
  -n, --num NUMPRINT  The number of lines to display. (default: 19)

Example: ./findbig.py -n 10 /tmp
```

### Default use and output
```
# ./findbig.py
 Directory/File  |   Created    |   Modified   |    Size
-----------------|--------------|--------------|-----------
./               |  5.62 (min)  |  5.62 (min)  |     160.0M
./a              |  4.55 (min)  |  4.55 (min)  |      94.0M
./a/1            |  3.93 (min)  |  3.93 (min)  |      84.0M
./b              |  4.55 (min)  |  4.55 (min)  |      56.0M
./a/1/file1      |  3.93 (min)  |  3.93 (min)  |      52.0M
./b/2            |  3.42 (min)  |  3.42 (min)  |      46.0M
./b/2/file2      |  3.42 (min)  |  3.42 (min)  |      43.0M
./a/1/z          |  3.62 (min)  |  3.62 (min)  |      32.0M
./a/1/z/filez    |  3.62 (min)  |  3.62 (min)  |      32.0M
./c              |  4.55 (min)  |  4.55 (min)  |      10.0M
./a/filea        |  4.55 (min)  |  4.55 (min)  |      10.0M
./c/filec        |  4.55 (min)  |  4.55 (min)  |      10.0M
./b/fileb        |  4.55 (min)  |  4.55 (min)  |      10.0M
./b/2/y          |  3.27 (min)  |  3.27 (min)  |       3.0M
./b/2/y/filey    |  3.27 (min)  |  3.27 (min)  |       3.0M
./c/3            |  5.62 (min)  |  5.62 (min)  |       160B
./c/3/x          |  5.62 (min)  |  5.62 (min)  |        64B
```

### Limit number of lines of output
```
# ./findbig.py -n 4
 Directory/File  |   Created    |   Modified   |    Size
-----------------|--------------|--------------|-----------
./               |  6.52 (min)  |  6.52 (min)  |     160.0M
./a              |  5.44 (min)  |  5.44 (min)  |      94.0M
./a/1            |  4.82 (min)  |  4.82 (min)  |      84.0M
./b              |  5.44 (min)  |  5.44 (min)  |      56.0M
```

### Limit number of lines of output and specify directory to evaluate
```
# ./findbig.py -n 4 ./a
 Directory/File  |   Created    |   Modified   |    Size
-----------------|--------------|--------------|-----------
./a              |  6.16 (min)  |  6.16 (min)  |      94.0M
./a/1            |  5.54 (min)  |  5.54 (min)  |      84.0M
./a/1/file1      |  5.54 (min)  |  5.54 (min)  |      52.0M
./a/1/z          |  5.23 (min)  |  5.23 (min)  |      32.0M
```
