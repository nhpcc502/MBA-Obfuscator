# MBA-Obfuscator Code and Dataset for ICICS'21

MBA-Obfuscator is a tool for generating Non-linear Mixed Boolean-Arithmetic Expressions.


## Prerequisties:
### Python 3.6
1. Z3 solver: `pip3 install z3-solver`
2. sympy: `pip3 install sympy`
2. numpy: `pip3 install numpy`


# Structure
MBA-Obfuscator's code is in mba_obfuscator,
MBA-Obfuscator's output samples are in samples.

### samples
The files storing non-linear MBA expressions.
1. Polynomial MBA expressions are in ground.linear.poly.txt
2. Non-Polynomial MBA expressions are in ground.linear.nonpoly.txt

### mba-obfuscator
MBA expression generation's code are in "mba_obfuscator" folder.
