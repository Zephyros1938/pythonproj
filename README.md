# pythonproj

A project made by [Zephyros](https://github.com/Zephyros1938) and [PiffleV](https://github.com/PiffleV) for our CS1 EOY class

## About

This project is developed primarily on Linux systems (specifically Arch-based distributions). As a result, **we do not guarantee full compatibility or stability on Windows or macOS**.

If you encounter any issues/bugs, please [open an issue](https://github.com/Zephyros1938/pythonproj/issues/new/choose).

## How to Run

Due to platform-specific differences in Python environments and terminal behavior, we provide platform-specific setup instructions below.

### Linux

A simple setup script is provided for Linux users:
```
./setup.sh
./run.sh
```
### Windows

We currently do not provide a Windows-specific setup script. However, you can manually set up and run the project using PowerShell:
```
mkdir .venv
python -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/python main.py
```

# Documentation

See the [Documentation page](docs/documentation.md)

# License

This project is licensed under the Apache 2.0 License.

To see our terms, see [LICENSE](LICENSE)
