"""
For your homework this week, you'll be creating a wsgi application of
your own.

You'll create an online calculator that can perform several operations.

You'll need to support:

  * Addition
  * Subtractions
  * Multiplication
  * Division

Your users should be able to send appropriate requests and get back
proper responses. For example, if I open a browser to your wsgi
application at `http://localhost:8080/multiple/3/5' then the response
body in my browser should be `15`.

Consider the following URL/Response body pairs as tests:

```
  http://localhost:8080/multiply/3/5   => 15
  http://localhost:8080/add/23/42      => 65
  http://localhost:8080/subtract/23/42 => -19
  http://localhost:8080/divide/22/11   => 2
  http://localhost:8080/divide/6/0     => HTTP "400 Bad Request"
  http://localhost:8080/               => <html>Here's how to use this page...</html>
```

To submit your homework:

  * Fork this repository (Session03).
  * Edit this file to meet the homework requirements.
  * Your script should be runnable using `$ python calculator.py`
  * When the script is running, I should be able to view your
    application in my browser.
  * I should also be able to see a home page (http://localhost:8080/)
    that explains how to perform calculations.
  * Commit and push your changes to your fork.
  * Submit a link to your Session03 fork repository!


"""

import re


class CalculatorBadRequestURLExc(Exception):
    """ A simple class that can be thrown as an exception when
        a URL that can't be processed is encountered.
    """
    pass

class CalculatorBadRequestDivBy0Exc(Exception):
    """ A simple class that can be thrown as an exception when
        a divide-by-0 situation is encountered.
    """
    pass


def usage(*args):
    """ Returns a usage string for how to use this web calculator

    :param args: Unused
    :return: A string of HTML to indicate how to use the calculator
    """
    body = "<h1>Welcome to the Calculator<br></h1>"
    body += "<h2>So, you want to do some math huh. Well, here is how to use this web app to do it!<br></h2>"
    body += "Usage:<br>"
    body += "    http://localhost:8080/opr/op1/op2<br>"
    body += "<br>"
    body += "Where:<br>"
    body += "    'opr' can be one of add, subtract, multiply or divide<br>"
    body += "    'op1/op2' are the signed floating point operands you want evaluated<br>"
    return body


def resolve_path(path):
    """
    Resolves the WSGI path into the function to call and the arguments
    to call the function with.
    """
    # First, trap for the special case of getting the usage informatoin
    if len(path) == 1 and path[0] == "/":
        func = usage
        args = []
    else:
        # Lets get the re module to do the work of parsing out the
        # items of interest from the path by using capturing groups.
        match = re.match(r"/(?P<opr>add|subtract|multiply|divide)/(?P<op1>[0-9\.\+\-]+)/(?P<op2>[0-9\.\+\-]+)",
                         path,
                         re.IGNORECASE)

        # Validate what was passed in to make sure it is legal.
        if match is None:
            # An invalid query was specified by the user.
            raise CalculatorBadRequestURLExc()
        elif (match.groupdict()['opr'].lower() in "divide") and float(match.groupdict()['op2']) == 0:
            # Invalid request to divide-by-0
            raise CalculatorBadRequestDivBy0Exc()

        # Why reinvent the wheel, just use the math operators provided by the
        # float class instead of writing our own. As a side effect, the
        # calculator can then also do floating point math.
        fn_dict = {'add'     : float.__add__,
                   'subtract': float.__sub__,
                   'multiply': float.__mul__,
                   'divide'  : float.__truediv__}

        # Return the function to call from the fn_dict based on the operator supplied.
        func = fn_dict[match.groupdict()['opr'].lower()]
        args = [float(match.groupdict()['op1']), float(match.groupdict()['op2'])]

    return func, args

def application(environ, start_response):
    headers = [('Content-type', 'text/html')]

    try:

        path = environ.get('PATH_INFO', None)
        if path is None:
            raise NameError

        func, args = resolve_path(path)
        body = str(func(*args))
        status = "200 OK"

    except CalculatorBadRequestURLExc:
        status = "400 Bad Request"
        body  = "<h1>HTTP 400 Bad Request</h1>"
        body += "<h2>Unable to parse out the URL<br></h2>"
        body += "<h2>Go to <a href='http://localhost:8080/'> http://localhost:8080/</a> for usage instructions</h2>"
    except CalculatorBadRequestDivBy0Exc:
        status = "400 Bad Request"
        body  = "<h1>HTTP 400 Bad Request</h1>"
        body += "<h2>Can't divide-by-0<br></h2>"
        body += "<h2>Go to <a href='http://localhost:8080/'> http://localhost:8080/</a> for usage instructions</h2>"
    except NameError:
        status = "404 Not Found"
        body = "<h1>HTTP 404 Not Found</h1>"
    except Exception:
        status = "500 Internal Server Error"
        body = "<h1>HTTP 500 Internal Server Error</h1>"
    finally:
        headers.append(('Content-Length', str(len(body))))
        start_response(status, headers)
        return [body.encode('utf8')]

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    srv = make_server('localhost', 8080, application)
    srv.serve_forever()

