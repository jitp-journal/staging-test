# What is this repo?
A space in which to experiment with staging templates, scripts, and workflows

# How do I use this repo?
Clone (or fork, you be the judge) and set up a virtual Python 3 environment to minimize conflicts between local setups and versions; the few packages you'll need are listed in `requirements.txt`. With your own environment set up, you can quickly load these packages using `pip install -r requirements.txt`. 

NB: If you install more packages, please update the requirements using `pip freeze > requirements.txt`.

**To set up a virtual environment for Python**, see [https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/). 

# What's in the repo?

|filename | explanation |
|---------|-------------|
|jitp-staging-test.dotx | A template file for Microsoft Word. Opening this file will create a blank document with the appropriate styles. With an existing file, you can associate the template by following instructions [for Windows](https://support.microsoft.com/en-us/office/load-or-unload-a-template-or-add-in-program-2479fe53-f849-4394-88bb-2a6e2a39479d) or [for Mac](https://answers.microsoft.com/en-us/msoffice/forum/all/how-to-apply-a-template-to-an-existing-document-in/3e993b0c-01ed-4509-bfbe-5db77dbe4fdd). |
| jitp-staging-test.odt | A template file for LibreOffice. Click here for [documentation on loading these styles using the Styles and Formatting pane](https://documentation.libreoffice.org/assets/Uploads/Documentation/en/GS5.2/HTML/GS5203-StylesAndTemplates.html). |
| template as test file.docx | Either of the template files above, opened and then saved as a .docx file. Can be passed to to-html.py to test functionality over the range of article features. |
| to-html.py | A Python 3 script using the mammoth package to convert .docx files to .html files. We're working on automatically calling this file on new .docx files uploaded to the repo. |
|JITPtest.css |Greg's clean stylesheet for use on Manifold |

# What's next for the repo?

To-do list:
* [ ] Reconfigure `to-html.py` to automatically generate an output filename if none is given
* [ ] Test `to-html.py` on more real articles
* [ ] Set up GitHub Actions to call `to-html.py` on push, only on .docx files that have changed 
* [ ] Write documentation for stagers on how to upload/download using GitHub

