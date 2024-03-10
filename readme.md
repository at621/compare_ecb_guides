# Comparing Two Documents Using Language Models

## Introduction

This document outlines various methods for comparing two documents using language models (LLMs).

## PDF to Text Conversion

To inspect the contents of two documents, it's beneficial to convert PDF files into text files. The most effective tool for this task is Adobe's toolkit, which allows for the conversion and subsequent afterprocessing of the JSON file. An example of this process is detailed in a notebook prepare_dataset.ipynb. It's important to note that the quality of automatic PDF to TXT conversion by LLMs is currently not up to standard, particularly with respect to heading numbering and the presence of low-quality elements.

## Document Comparison Techniques

When comparing two high-quality text files, the following methods can be considered:

1. **Full Comparison**: Present both documents to an LLM and request it to highlight differences. This approach is currently effective for smaller documents. For documents exceeding 10 pages, especially regulatory texts where single sentences are critical, the quality diminishes. Prose documents allow for a greater number of pages to be compared with acceptable quality.

2. **Segmented LLM Comparison**: A more refined approach involves showing the LLM logical parts of the document (e.g., specific sections like Credit Risk or Market Risk) and asking to analyse the differences. This method is limited when structural changes between documents prevent direct comparison (e.g., changes in the Definition of Default section).

3. **Paragraph Tokenization**: This method involves tokenizing individual paragraphs and comparing each paragraph from one document to all paragraphs in the other document. This technique makes it easier to identify paragraphs that are unique to one document. For accurate comparison, it's essential to compare the new document to the old document and vice versa. Further details and examples are available in a notebook compare_docs.ipynb.


## Conclusion

Currently, there is no straightforward method for comparing two documents comprehensively. While existing techniques offer partial solutions, the ideal scenario - a seamless comparison of two PDF documents resulting in a detailed summary of differences — may become a reality by 2025.
