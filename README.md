# Lyrapdf: convert a PDF to JSON or MarkDown

Lyrapdf is a project based on [PDFMiner.Six](https://github.com/pdfminer/pdfminer.six),
which extracts text from a PDF document and processes it so the original
structure from the text is reconstructed.

The output format can be MarkDown or JSON.

## Getting started

In order to execute this project, **python3** is needed.
```
sudo apt install python3
sudo apt install python3-pip
```
Also, some libraries must be installed:

```
pip install pdfminer.six
pip install sspipe
```

This repository also includes a Natural Lenguage Understanding proof of concept
in *docbot* directory, which uses the following dependencies:

```
pip install snips-nlu
```

## Usage

From git root directory, run:
```
python3 -m lyrapdf folder/with/pdfs
```

## About

This tool was made as a Bachelor’s Degree Final Project in 
Computer Science at Universidad de Zaragoza.
