# Python Guide For Our Project

## Python Style Guide

I'd like to use pep8 as our style guide, except with line lengths increased to at least 120 (maybe 140). To do this, you can just install pep8 or flake8 on your machine and then run it on your files. Later if we want I can just have a hook to check it for you if we want.

All indentation shall be made into spaces with a four space width.

## Tests

Write them.

Location is described below.

## Python File Structure

This will detail how to place your files, what to name them and how to invoke any tests or other things you need to get working.

I will add any information that people have questions about. It should also be updated when we make big changes to the structure. It will guide questions about the structure of the project in general and is a good piece of documentation.

### Basic Structure

```
$GIT_DIRECTORY/
|-- docs
|-- www
|-- etc.
|-- senseable_gym
    # All the python code goes in here
    #   And anything related to the python code.

    |-- sg_database
        # Anything with the database model goes here

    |-- sg_<object_name>
        # New additions (gui, view, etc.) get titled the same

    |-- test
        # Tests should be placed in this folder with descriptive names
```

Make sure to put your code in this format. This allows for a lot of really nice imports and testing features. These include:

### Importing

With this structure, importing different parts of our project becomes very easy. Whenever you want to import a different part of the project, you simply follow the directory structure. For example, to get the `DatabaseModel` from `database.py` in the `sg_database` folder, one can simply do this import:

```python
from senseable_gym.sg_database.database import DatabaseModel
```

This works for any of the folders or files we put in the project. This means no need for relative imports! This will solve a lot of problems for us down the road, so make sure to try and import like that for any other part of the project that you need.

### Testing

To run tests, on Linux you can say:

`$ make test`

or

`$ python3 -m unittest discover`

When invoking either of these commands, you will be able to automatically run the entire test suite that we've made.

However, if you're looking to only run a test script that you've been working on, this structure allows you to do it very easily. To invoke the test script, navigate to the `$GIT_DIRECTORY` directory and invoke the command:

`$ python3 -m senseable_gym.test.<test_script_name>`

and it will run your tests.

The structure is similar to what is shown below:

```python
# Built-in Imports
import unittest     # This is the package that lets us run automated unit tessts

# Local Imports
from senseable_gym.sg_module_to_test import class_to_test
from senseable_gym.sg_module_to_test import function_to_test


class Test_module_to_test(unittest.TestCase):
    def setUp(self):
        """
        This will run before every test begins.

        It should put the conditions in such a way that each test is independent of
            each other.
            It is not always required.
        """
        # Code here

    def test_testname_here(self):
        """
        This is a place to run the automated unit tests.
        """
        # Code here

if __name__ == '__main__':
    unittest.main()
```

### Writing Getters and Setters

So Python implements this **SUPER** awesome thing called a `property`. This may require some reading, but a basic idea is as follows:

```python
class ExampleModule():
    def __init__(self, parameter):
        # Going to set this parameter as a property of our module.
        #   This means the logic of getting and setting can be passed off
        #   Into different functions and always utilized
        self._squared = parameter

    # Here's where we tell python that our `p` value is a property
    @property
    def squared(self):
        return self._squared ** 2

    @squared.setter
    def squared(self, value):
        if not isinstance(value, int):
            raise ValueError('Value must be an int')

        self._squared = value
```

What this does is completely erase the need to write getters and setters. You can do everything with those now simply by accessing the property of the class.

For example, if you wanted to see what the `p` value was of an `ExampleModule` it would look like this:

```python
example = ExampleModule(5)

# This would print 25
print(example.squared)

# This would set the internal value to 10
example.squared = 10

# This would print 100
print(example.squared)

# This would give you an error
example.squared = 'THIS WILL BE AN ERROR'
```

This is a horrible example, but you see the point. You just interact with it like it is an attribute. You don't have to worry about getters and setters. But, when you do it, you still have the safety of the getters and setters that you would have had before.

### Logging

To view the currently logging setup, you can view the file in `team14/senseable_gym/__init__.py`. What this setup does is create the ability for all parts of the `senseable_gym` module to share a unified logger. This means we can send them to specific files, write them out in a similar way to the command line, etc.

At this point, you might say, "Wow, that sounds really nice, but how much setup do I have to do in each of my files to get it to work?" The answer is (of course, since this is Python) very nice, and even requires very little boilerplate code.

For your file, you should do something similar to this:

```python
# docstring and information

import logging

# other imports

# This name will get you the write logger
#   You can create sub loggers of this logger, by putting a period on the name
#   However, it is required that the first part of the name start with the global name
global_logger_name = 'senseable_logger'
file_logger_name = global_logger_name + '.my_file'

# Get the logger
my_logger = logging.getLogger(file_logger_name)

# Now you have the logger, so you can write statements to it.
#   This is pretty simple, and most of it you should be able to find online
#   But to write info or debug messages, you can use the following commands
my_logger.info('this is an informative statement')
my_logger.debug('this is a debug statement')
```

So there you go, it's a pretty simple idea about how you can set up the logger. The `__init__.py` file will be upgraded a few more times with configuration modifications, but your code should not have to change and you won't really have to worry about it. Ultimately, we'll have a logs folder that will print out pretty information to you about how your part of the project is working, and will help you debug any problems that are occuring. No more print statements for debugging, that have to disappear later! Yay!

#### Logging Levels

Currently, the only way to set the logger level is to modify the line in the `__init__.py` where it says `logger.setLevel(logging.LEVELNAME)`. At some point, this will be able to be specified at the command line level, but it's just not quite ready yet. Just try and change it back to whatever level name it was before you made the change (when you're going to commit) and everything should be just fine.

#### Logging Notes

IT IS IMPORTANT TO LOG. :)
