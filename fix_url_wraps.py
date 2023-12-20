# This breaks in weird ways, when I try to put it in to-html.py –  it doubles at the beginning and end – and I'm not sure why. It also drove me NUTS trying to get BeautifulSoup to stop escaping brackets. But at least the functions seem to work when you pass them *only* the html that you want to parse.

# load the library (note: if you get an error, try `pip3 install bs4`
from bs4 import BeautifulSoup

# Define a function to do the cleanup
def fix_url_wraps(html_content):

    # And then define a string reformatter function *within* the function
    def break_lines_on_punctuation(html_string):
        ## IMPORTANT: we only apply this to anchor strings between <a> and </a>, never to the href value
        # Insert a word break opportunity after a colon
        html_string = re.sub(r':', r':<wbr>', html_string)
        # Before a single slash, tilde, period, comma, underline, question mark, number sign, percent symbol, equals sign, or ampersand
        html_string = re.sub(r'([/~.,\_?#%=&])', r'<wbr>\1', html_string)
        # Fix the double-slash situation
        html_string = re.sub(r'<wbr>/<wbr>/', r'//<wbr>', html_string)
        html_string = re.sub(r':<wbr>//', r'://', html_string)
        # Remove any double word break opportunities
        html_string = re.sub(r'<wbr><wbr>', r'<wbr>', html_string)

        # print(text_string) # for debugging
        return html_string

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html_content.string, 'html.parser')

    # Find all anchor tags (hyperlinks) in the HTML content
    for a_tag in soup.find_all('a', href=True):
        # Apply the format_url_string function to the *text content* of each anchor tag, if it exists
        if a_tag.string:
            a_tag.string.replace_with(break_lines_on_punctuation(a_tag.string))

    # Return the modified HTML content
    return(soup.decode(formatter=None))

# Now apply that function to just the bibliography section
### Pretty sure this regex is where the breakage happens. Just apply the function above manually in a python shell or Jupyter notebook or something ###

# interim_html = re.sub(r'(?s)<section id="bibliography".*?</section>', fix_url_wraps, interim_html)
