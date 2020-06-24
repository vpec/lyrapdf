# Lyrapdf: convert a PDF to JSON or MarkDown

Lyrapdf is a project based on [PDFMiner.Six](https://github.com/pdfminer/pdfminer.six),
which extracts text from a PDF document and processes it so the original
structure from the text is reconstructed.

The output format can be MarkDown or JSON.

## Getting started

Download the repository or clone it:
```
git clone https://github.com/vpec/lyrapdf.git
```

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

To convert PDFs inside a directory to JSON (more information in [Usage examples](#usage-examples)) use:
```
python3 -m lyrapdf folder/with/pdfs
```

This repository also includes a Natural Lenguage Understanding proof of concept
in *docbot* directory, which uses the following dependencies:

```
pip install snips-nlu
```

## How it works

The original document is processed by a pipeline composed by multiple
processing steps until reaching the final output format: JSON. It's also
possible to get the output file in MarkDown format.

![Pipeline diagram](https://ibb.co/N9YVBX8)

Almost all processing is based on the use of regular expressions. More details can
be found looking at the code, as each small step is contained inside a method.

## Features

### Keep only the content you actually need

It removes unnecessary elements as page numbers. This is made thanks to the position
inside the page provided by the HTML format.

![Document before page number removal](https://ibb.co/mDMMKcL)

![Document after page number removal](https://ibb.co/VvGYCh6)


### Smart text relevance

The whole text does not have the same relevance. Some words are titles, others are just... text.

A classification has been made based on the size of each text block.
All text that is contained within 95% of the cumulative character size 
within the document is considered standard. Larger sizes are considered titles.

For relevance of each title, several intervals have been established,
thanks to a deterministic and optimal version of the K-means algorithm.

The result of this process is a MarkDown document.

![Document after conversion to MarkDown](https://ibb.co/JzbCWBJ)


### Paragraph debugging

Text is debugged in order to get paragraphs merged into one line.
Some other small processing is done to remove defects from the text.

![Debugged MarkDown text](https://ibb.co/JHtPwrc)

### Structured format

It is possible to obtain an output in JSON structured format, from a
conversion from MarkDown, where the level of relevance of the text
is indicated (1 is the most important, 7 is the standard text).

![JSON output file](https://ibb.co/b6Qmbh1)

## Usage examples

I want to extract, process and convert to JSON text from PDFs inside a directory.
From git root directory, run:
```
python3 -m lyrapdf folder/with/pdfs
```

I want to extract, process and convert to JSON text from PDFs inside a directory, using 4 CPU threads.
From git root directory, run:
```
python3 -m lyrapdf folder/with/pdfs --threads 4
```

I want to extract, process and convert to JSON text from PDFs inside a directory, using 4 CPU threads.
From git root directory, run:
```
python3 -m lyrapdf folder/with/pdfs --threads 4
```

I want to extract, process and convert to JSON text from PDFs inside a directory, using 4 CPU threads.
From git root directory, run:
```
python3 -m lyrapdf folder/with/pdfs --threads 4
```

I want to extract, process and convert to MARKDOWN text from PDFs inside a directory, using 4 CPU threads.
From git root directory, run:
```
python3 -m lyrapdf folder/with/pdfs --format md --threads 4
```
or
```
python3 -m lyrapdf folder/with/pdfs --format markdown --threads 4
```

I want to print information about command line arguments.
From git root directory, run:
```
python3 -m lyrapdf --help
```

## About

This tool was made as a Bachelor’s Degree Final Project in 
Computer Science at Universidad de Zaragoza.
