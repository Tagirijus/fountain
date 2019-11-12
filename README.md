# Fountain parser

## About

This python script is a fountain script parser, which converts .fountain files to python object. It is ported to Python 3 by Colton J. Provias - cj@coltonprovias.com - [original code here](https://gist.github.com/ColtonProvias/8232624), based on `Fountain` by Nima Yousefi & John August; original code for Objective-C at https://github.com/nyousefi/Fountain.

I did just some little tweaks to Coltons code, since I ran into some issues.

## Install

1. Make a pull request of this repo
3. Go into the repo-dir on your machine
2. `sudo python3 setup.py install`

## Usage

```
from fountain import fountain

F = fountain.Fountain(STRING)
```

This will make `F` to a fountain object.
