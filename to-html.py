#!/usr/bin/python3

# Command line usage: ./to-html.py input_file output_dir

import mammoth
import sys
import re
import os
import shutil

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


    # write to output directory
    with open(output_file, "w") as html_file:
        html_file.write(interim_html)
