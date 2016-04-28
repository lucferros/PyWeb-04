"""
For your homework this week, you'll be creating a new WSGI application.

The MEMEORIZER acquires a phrase from one of two sources, and applies it
to one of two meme images.

The two possible sources are:

  1. A fact from http://unkno.com
  2. One of the 'Top Stories' headlines from http://www.cnn.com

For the CNN headline you can use either the current FIRST headline, or
a random headline from the list. I suggest starting by serving the FIRST
headline and then modifying it later if you want to.

The two possible meme images are:

  1. The Buzz/Woody X, X Everywhere meme
  2. The Ancient Aliens meme (eg https://memegenerator.net/instance/11837275)

To begin, you will need to collect some information. Go to the Ancient
Aliens meme linked above. Open your browser's network inspector; in Chrome
this is Ctrl-Shift-J and then click on the network tab. Try typing in some
new 'Bottom Text' and observe the network requests being made, and note
the imageID for the Ancient Aliens meme.

TODO #1:
The imageID for the Ancient Aliens meme is:

You will also need a way to identify headlines on the CNN page using
BeautifulSoup. On the 'Unnecessary Knowledge Page', our fact was
wrapped like so:

```
<div id="content">
  Penguins look like they're wearing tuxedos.
</div>
```

So our facts were identified by the tag having
* name: div
* attribute name: id
* attribute value: content.

We used the following BeautifulSoup call to isolate that element:

```
element = parsed.find('div', id='content')
```

Now we have to figure out how to isolate CNN headlines. Go to cnn.com and
'inspect' one of the 'Top Stories' headlines. In Chrome, you can right
click on a headline and click 'Inspect'. If an element has a rightward
pointing arrow, then you can click on it to see its contents.

TODO #2:
Each 'Top Stories' headline is wrapped in a tag that has:
* name:
* attribute name:
* attribute value:

NOTE: We used the `find` method to find our fact element from unkno.com.
The `find` method WILL ALSO work for finding a headline element from cnn.com,
although it will return exactly one headline element. That's enough to
complete the assignment, but if you want to isolate more than one headline
element you can use the `find_all` method instead.


TODO #3:
You will need to support the following four requests:

```
  http://localhost:8080/fact/buzz
  http://localhost:8080/fact/aliens
  http://localhost:8080/news/buzz
  http://localhost:8080/news/aliens
```

You can accomplish this by modifying the memefacter.py that we created
in class.

There are multiple ways to architect this assignment! You will probably
have to either change existing functions to take more arguments or create
entirely new functions.

I have started the assignment off by passing `path` into `process` and
breaking it apart using `strip` and `split` on lines 136, 118, and 120.

To submit your homework:

  * Fork this repository (PyWeb-04).
  * Edit this file to meet the homework requirements.
  * Your script should be runnable using `$ python memeorizer.py`
  * When the script is running, I should be able to view your
    application in my browser.
  * Commit and push your changes to your fork.
  * Submit a link to your PyWeb-04 fork repository!

"""

from bs4 import BeautifulSoup
import requests

def get_image(message, image_name):
    """
    Determines which image we wish to have our text overlayed on

    :param message: This is the text that will overlay onto our image
    :type message: String
    :param image_name: This is the second param offered in the url which determines which image we are going to overlay
    our text on
    :type image_name: String

    :return: Returns the image with text overlaid on top of it.
    """

    image = {
        'buzz': 2097248,
        'aliens': 627067
    }
    url = 'http://cdn.meme.am/Instance/Preview'
    params = {
        'imageID': image[image_name],
        'text1': message
    }

    response = requests.get(url, params)

    return response.content


def parse(body, message):
    """
    Parses the source of the website for the message we are going to overlay onto our image
    :param body: This is the raw source html of a website
    :type body: String
    :param message: This determines which tags and content we need to parse the raw html.
    :type message: String

    :return: Returns the text that we wish to overlay onto our image
    """
    parsed = BeautifulSoup(body, 'html5lib')
    tag = {
        'fact': parsed.find('div', id='content'),
        'news': parsed.find('h2', class_='banner-text banner-text--natural')
    }
    content = tag[message]
    return content.text.strip()


def get_response(content):
    """
    Gets the source of the website specified
    :param content: This will be the first parameter in the url entered, either 'fact' or 'news'
    :type content: String

    :return: Returns the Fact or News Headline based on the content value provided to the function
    """
    options = {
        'fact': 'http://unkno.com',
        'news': 'http://cnn.com'
    }
    response = requests.get(options[content])
    return parse(response.text, content)


def process(path):
    args = path.strip("/").split("/")
    message = get_response(args[0])
    meme = get_image(message, args[1])

    return meme


def application(environ, start_response):
    headers = [('Content-type', 'image/jpeg')]
    try:
        path = environ.get('PATH_INFO', None)
        if path is None:
            raise NameError

        body = process(path)
        status = "200 OK"
    except NameError:
        headers = [('Content-type', 'text/plain')]
        status = "404 Not Found"
        body = "<h1>Not Found</h1>"
    except Exception as e:
        headers = [('Content-type', 'text/plain')]
        status = "500 Internal Server Error"
        body = """<html>
    <head><h1>Memeorizer</h1></head>
    <h2> You screwed up: {}</h2>
    <p> To use this page, use the URL to decide the output.</p>
    <p> The first item in the path represents the content of the meme. </p>
    <ul>
        <li> /fact </li>
        <li> /news </li>
    </ul>
    <p> The second item in the path represents the image the message will be displayed upon </p>
    <p></p>
    <h2> Example: </h2>
    <ul>
        <li>http://localhost:8080/fact/buzz</li>
        <li>http://localhost:8080/fact/aliens</li>
        <li>http://localhost:8080/news/buzz</li>
        <li>http://localhost:8080/news/aliens</li>
    </ul>
    <p>If you have any further questions, you should find a new line of work</p>
    </html>
    """.format(e)
    finally:
        headers.append(('Content-length', str(len(body))))
        start_response(status, headers)
        return [body]

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    srv = make_server('localhost', 8080, application)
    srv.serve_forever()
