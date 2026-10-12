# Compatibility status

## Declared target

The intended support target is CPython 3.10–3.13 on Windows, Linux, and macOS.
The library uses standard Python packaging and is independent of VS Code,
PyCharm, Jupyter, or another editor once the same interpreter/environment is
selected.

## Actually validated in private L1

- Windows 11;
- CPython 3.12.10;
- core import with NumPy and pandas;
- full local test suite;
- Ruff lint and format checks;
- wheel and source distribution build/metadata checks;
- isolated local wheel smoke tests.
- portable asset and notebook JSON validation;
- synthetic notebook execution in the existing local Jupyter environment.

The final validation report is the authority for completed checks. The
presence of a CI matrix is preparation, not evidence that remote jobs ran.

## Prepared but not yet executed

- Ubuntu and macOS;
- Python 3.10, 3.11, and 3.13;
- dependency-minimum and dependency-latest matrices;
- Conda and Google Colab runtime execution;
- bit-for-bit container reproduction.

Do not claim these surfaces as supported until their jobs execute successfully
and the evidence is retained.

## Numerical reproducibility

Functional decisions should be deterministic for the same ordered input,
configuration, and dependency contract. Floating-point results may vary within
documented tolerances across BLAS implementations, architectures, and library
versions. Bit-for-bit reproduction requires a separately frozen runtime.
