#!/usr/bin/python3

# Command line usage: ./to-html.py inputfile outputfile

import mammoth
import sys
import re

style_map = """
p[style-name='Byline'] => p.byline:fresh
p[style-name='Abstract'] => section.abstract > p:fresh
p[style-name='Authorbio'] => section.authorbio > p:fresh
p[style-name='Blockquote'] => blockquote > p:fresh
p[style-name='Figure'] => figure
r[style-name='figcaption'] => figcaption
r[style-name='author-name'] => span.author-name
p[style-name='Reference'] => section.bibliography > p:fresh
p[style-name='Preformatted Text'] => pre:fresh
r[style-name='code'] => code
"""

input_file=str(sys.argv[1])
output_file=str(sys.argv[2])

# print ("input file: " + input_file)
# print ("output file: " +  output_file)

with open(input_file, "rb") as docx_file:
    result = mammoth.convert_to_html(docx_file, style_map=style_map)

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


    with open(output_file, "w") as html_file:
        html_file.write(interim_html)
