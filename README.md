# What is this repo?
A space in which to experiment with staging templates, scripts, and workflows

<div class="alert alert-warning"><a href="STAGE.md"><strong>Looking for stager instructions?</strong> Click here.</a></div>

# How do I use this repo?
Clone (or fork, you be the judge) and set up a virtual Python 3 environment to minimize conflicts between local setups and versions; the few packages you'll need are listed in `requirements.txt`. With your own environment set up, you can quickly load these packages using `pip install -r requirements.txt`.

NB: If you install more packages, please update the requirements using `pip freeze > requirements.txt`.

**To set up a virtual environment for Python**, see [https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/).

# What's in the repo?

|filename | explanation |
|---------|-------------|
|jitp-staging-test.dotx | A template file for Microsoft Word. Opening this file will create a blank .docx document with the appropriate styles. With an existing file, you can associate the template by following instructions [for Windows](https://support.microsoft.com/en-us/office/load-or-unload-a-template-or-add-in-program-2479fe53-f849-4394-88bb-2a6e2a39479d) or [for Mac](https://answers.microsoft.com/en-us/msoffice/forum/all/how-to-apply-a-template-to-an-existing-document-in/3e993b0c-01ed-4509-bfbe-5db77dbe4fdd). To edit the template itself, open Word first and use File > Open rather than double-clicking the filename, and be sure to File > Save as \*.dotx. |
| jitp-staging-test.odt | A template file for LibreOffice. Click here for [documentation on loading these styles using the Styles and Formatting pane](https://documentation.libreoffice.org/assets/Uploads/Documentation/en/GS5.2/HTML/GS5203-StylesAndTemplates.html). |
| template as test file.docx | Either of the template files above, opened and then saved as a .docx file. Can be passed to to-html.py to test functionality over the range of article features. |
| to-html.py | A Python 3 script using the mammoth package to convert .docx files to .html files, saved in a new folder along with any embedded image files. We're working on automatically calling this file on new .docx files uploaded to the repo. To run, first set up a Python environment as described above. Then call using the syntax `./to-html.py %sourcefile% %outputdirectory%`, where `%sourcefile%` is in .docx format and `%outputdirectory%` is the relative path (e.g. the first author name) of a directory to be created. |
|JITPtest.css |[Gregory](https://github.com/palermog)'s clean stylesheet for use on Manifold, plus a few tweaks based on Mammoth output |

# What's next for the repo?

To-do list:
* [ ] Reconfigure `to-html.py` to automatically generate an output filename if none is given
* [X] Test `to-html.py` on more real articles
* [ ] Investigate automation:
  * [ ] Github path
    - [ ] Set up GitHub Actions to call `to-html.py` on push, only on .docx files that have changed
    - [ ] Write documentation for stagers on how to upload/download using GitHub
  * [ ] Shiny path
    - [X] Set up R Shiny app to call Python functions via `reticulate` package ([Thanks again](https://github.com/jitp-journal/jitp-converter), @palermog!)
    - [ ] Update app with latest versions of `to-html.py` and CSS
    - [ ] Add download functionality
* [X] Update documentation for stagers
