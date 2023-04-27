#!/usr/bin/python3

# Command line usage: ./to-html.py input_file output_dir

import mammoth
import sys
import re
import os
import shutil
import datetime
import html

# Define mapping between Word styles and html elements or classes
style_map = """
p[style-name='Byline'] => p.byline:fresh
p[style-name='Abstract'] => section.abstract > p:fresh
p[style-name='Authorbio'] => section.authorbio > p:fresh
p[style-name='Blockquote'] => blockquote > p:fresh
p[style-name='Figure'] => figure
r[style-name='figcaption'] => figcaption
r[style-name='caption'] => caption
r[style-name='author-name'] => span.author-name
p[style-name='Reference'] => section.bibliography > p:fresh
p[style-name='Preformatted Text'] => pre:fresh
r[style-name='code'] => code
p[style-name='TableHeader] => th
"""

input_file=str(sys.argv[1])
output_dir=str(sys.argv[2])

# make sure we have a place to output
os.mkdir(output_dir)
output_file=os.path.join(output_dir, str(sys.argv[2]) + ".html")

# print ("input file: " + input_file)
# print ("output dir: " + output_dir)
# print ("output file: " +  output_file)


# Copy default image handler from mammoth command-line app; it should then copy images from the source file into an output directory alongside the html
class ImageWriter(object):
    def __init__(self, output_dir):
        self._output_dir = output_dir
        self._image_number = 1

    def __call__(self, element):
        extension = element.content_type.partition("/")[2]
        image_filename = output_dir + "_fig_{0}.{1}".format(self._image_number, extension)
        with open(os.path.join(self._output_dir, image_filename), "wb") as image_dest:
            with element.open() as image_source:
                shutil.copyfileobj(image_source, image_dest)

        self._image_number += 1

        return {"src": image_filename}



# convert input file
with open(input_file, "rb") as docx_file:
    result = mammoth.convert_to_html(docx_file, style_map=style_map, convert_image = mammoth.images.inline(ImageWriter(output_dir)))

    interim_html = result.value

    # add line breaks to make it more human-readable
    interim_html = re.sub(r"<p", "\n"+r"<p", interim_html)
    interim_html = re.sub(r"<h", "\n\n"+r"<h", interim_html)
    interim_html = re.sub("\n\n"+r"<h1", "\n"+r"<h1", interim_html)
    interim_html = re.sub(r"<blockquote>", "\n"+r"<blockquote>", interim_html)
    interim_html = re.sub(r"<section", "\n\n"+r"<section", interim_html)
    interim_html = re.sub(r"</section>", r"</section>"+"\n", interim_html)

    # fix anchors that break figcaptions
    interim_html = re.sub(r"</figcaption><a"+"(.*?)"+r"</a><figcaption>", r"<a"+r"\1"+r"</a>", interim_html)

    # fix failure of :separator for pre
    interim_html = re.sub(r"</pre>"+"\n"+"<pre>", "\n", interim_html)
    
    # tuck table captions into the actual table
    interim_html = re.sub(r"<p>"+"(<caption>.*?</caption>)"+r"</p><table>", r"<table>"+r"\1", interim_html) 

    # tuck abstract h2 inside the abstract section; add matching id for consistency
    interim_html = re.sub(r'(<h2>.*Abstract</h2>\n)(\n)(<section class="abstract">\n)', r'\2\3\1', interim_html)

    interim_html = re.sub(r'(class="abstract")', r'id="abstract" \1', interim_html)



    # same for bibliography and authorbio sections
    interim_html = re.sub(r'(<h2>.*References</h2>\n)(\n)(<section class="bibliography">\n)', r'\2\3\1', interim_html)

    interim_html = re.sub(r'(class="bibliography")', r'id="bibliography" \1', interim_html)

    interim_html = re.sub(r'(<h2>.*About the Author[s]*</h2>\n)(\n)(<section class="authorbio">\n)', r'\2\3\1', interim_html)

    interim_html = re.sub(r'(class="authorbio")', r'id="authorbio" \1', interim_html)


    # wrap in necessary html document declarations
    ## NB: change language if the article isn't in English
    interim_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
''' + interim_html + '''
</body>
</html>
'''

    # add standard journal info to head
    journal_html = '''
    <meta name="citation_journal_title" content="Journal of Interactive Technology and Pedagogy">
    <meta name="citation_journal_abbrev" content="JITP">
    <meta name="citation_year" content="%s">
''' % datetime.date.today().year

    interim_html = re.sub(r'</head>', journal_html + '\n</head>', interim_html)


    # extract author names from bio section and insert into head
    authors = re.findall(r'<span class="author-name">(.*?)</span>', interim_html)
    author_html = '<meta name="citation_authors" content="' + "; ".join(authors) + '">'

    interim_html = re.sub(r'</head>', '\t' + author_html + '\n</head>', interim_html)


    # extract article title and add that to head, too
    title_html = re.findall(r'<h1>(.*?)</h1>', interim_html)
    if(title_html):
        title_html = re.sub(r'<a.*?></a>', '', title_html[0])
        title_html = html.escape(title_html)
        title_html = '<meta name="citation_title" content="' + title_html + '">'
        interim_html = re.sub(r'</head>', '\t' + title_html + '\n</head>', interim_html)


    # can we also prepopulate the abstract field? multiparagraph is tricky, but let's try a substitution.
    abstract_html = re.findall(r'(?s)<h2>Abstract</h2>\n(.*?)</section>', interim_html)
    if(abstract_html):
        abstract_html = re.sub(r'</p>\n<p>', ' || ', abstract_html[0])
        abstract_html = re.sub(r'<p>', "", abstract_html)
        abstract_html = re.sub(r'</p>', "", abstract_html)
        abstract_html = '<meta name="citation_abstract" content="' + html.escape(abstract_html) + '">'
        interim_html = re.sub(r'</head>', '\t' + abstract_html + '\n</head>', interim_html)



    # write to output directory
    with open(output_file, "w") as html_file:
        html_file.write(interim_html)
