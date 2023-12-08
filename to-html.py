#!/usr/bin/python3

# Command line usage: ./to-html.py input_file output_dir

# NB: before passing the Word file to mammoth, you may want to run a search-and-replace for " with " and ' with ' (to convert any straggling straight quotes to curly; Word is better at this).

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

    ## Now mammoth is done!

    # add line breaks to make it more human-readable
    interim_html = re.sub(r"<p", "\n"+r"<p", interim_html)
    interim_html = re.sub(r"<h", "\n\n"+r"<h", interim_html)
    interim_html = re.sub("\n\n"+r"<h1", "\n"+r"<h1", interim_html)
    interim_html = re.sub(r"<blockquote>", "\n"+r"<blockquote>", interim_html)
    interim_html = re.sub(r"<section", "\n\n"+r"<section", interim_html)
    interim_html = re.sub(r"</section>", r"\n</section>"+"\n", interim_html)

    # fix anchors that break figcaptions
    interim_html = re.sub(r"</figcaption><a "+"(.*?)"+r"</a><figcaption>", r"<a "+"\1"+r"</a>", interim_html)

    # fix figcaptions that fall just after the </figure>
    interim_html = re.sub(r"</figure>\n<p>(<figcaption>.*?</figcaption>)</p>", r"\1</figure>", interim_html)

    # fix failure of :separator for pre
    interim_html = re.sub(r"</pre>"+"\n"+r"<pre>", "\n", interim_html)

    # fix footnote references
    interim_html = re.sub(r'<sup><sup>(.*?)</sup></sup>', r'<sup>\1</sup>', interim_html)

    interim_html = re.sub(r'<sup>(<a href="#footnote.*?)>\[(\d?)\]</a></sup>', r'\1 class="ftnref">\2</a>', interim_html)

    # tuck table captions into the actual table
    interim_html = re.sub(r"<p>"+"(<caption>.*?</caption>)"+r"</p><table>", r"<table>"+r"\1", interim_html)

    # tuck abstract h2 inside the abstract section; add matching id for consistency
    interim_html = re.sub(r'(<h2>.*Abstract</h2>\n)(\n)(<section class="abstract">\n)', r'\2\3\1', interim_html)

    interim_html = re.sub(r'(class="abstract")', r'id="abstract" \1', interim_html)

    # tuck bibliography h2 inside the bibliography section
    interim_html = re.sub(r'(<h2>.*References</h2>\n)(\n)(<section class="bibliography">\n)', r'\2\3\1', interim_html)

    interim_html = re.sub(r'(class="bibliography")', r'id="bibliography" \1', interim_html)

    # tuck authorbio h2 inside the authorbio section
    interim_html = re.sub(r'(<h2>.*About the Author[s]*</h2>\n)(\n)(<section class="authorbio">\n)', r'\2\3\1', interim_html)

    interim_html = re.sub(r'(class="authorbio")', r'id="authorbio" \1', interim_html)

    # add section + h2 for footnotes, move footnotes to just before references
    interim_html = re.sub(r'(?s)(<section id="bibliography".*?</section>)(\n*)(<section id="authorbio".*?</section>\n)(<ol><li id="footnote.*?</ol>)', r'<section class="footnoteblock">\n<h2>Notes</h2>\n\4\n</section> <!-- end footnoteblock -->\n\n\1\n\n\3', interim_html)

    ### save time on copyediting
    # Convert double spaces to single spaces
    interim_html = re.sub(r'  ', r' ', interim_html)

    # Convert hyphens to en-dashes when they appear between numbers
    interim_html = re.sub(r'(\d)-(\d)', r'\1–\2', interim_html)

    # Convert endash between spaces to emdash without spaces
    interim_html = re.sub(r'(\w) – (\w)', r'\1—\2', interim_html)

    # Don't trap trailing spaces inside html tags
    interim_html = re.sub(r' (</.*?>)', r'\1 ', interim_html)


    ### big wraparound html chunks
    # wrap everything after abstract and before footnotes in div#article-body
    interim_html = re.sub(r'(?s)(<section id="abstract".*?</section>)(\n*)(.*?)(<section)', r'\1 <!-- end abstract -->\n\n<section id="article-body">\n\3</section> <!-- end article-body -->\n\n\4', interim_html)

    # wrap article-body + everything to end in div#text-column
    # (back compatibility from WordPress, sigh)
    interim_html = re.sub(r'(<section id="article-body")', r'<div id="text-column">\n\1', interim_html)
    interim_html = interim_html + '\n</div> <!-- end text-column -->\n'

    # add Creative Commons license block
    cc_html = '''
<div class="entry-meta entry-meta-creative-commons">

	<a data-logo="1" href="https://creativecommons.org/licenses/by-nc-sa/4.0/" rel="license" target="_blank"><img alt="Attribution-NonCommercial-ShareAlike 4.0 International" data-license="by-nc-sa" data-size="normal" src="https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png" style="border-width:0"/></a>
	<p>This entry is licensed under a Creative Commons <a data-logo="0" href="https://creativecommons.org/licenses/by-nc-sa/4.0/" rel="license" target="_blank">Attribution-NonCommercial-ShareAlike 4.0 International</a> license.</p>

</div>
'''
    interim_html = re.sub(r'(\n</div> <!-- end text-column -->\n)', cc_html + r'\1', interim_html)

    # wrap whole thing in necessary html document declarations
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
    title = re.findall(r'<h1>(.*?)</h1>', interim_html)
    if(title):
        title = re.sub(r'<a.*?></a>', '', title[0])
        title = html.escape(title)
        title_html = '<meta name="citation_title" content="' + title + '">' + '\n\t<title>' + title + '</title>'
        interim_html = re.sub(r'</head>', '\t' + title_html + '\n</head>', interim_html)

    # TO DO: add author last name to <title> instead of just the article title, to make it easier to find in Manifold after uploading.
    # OR NOT: It would help us in Manifold, but would be a problem for citation software if Manifold ever decides to include our <head> data.


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
