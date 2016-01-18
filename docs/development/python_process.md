# Python Guide For Our Project

## Python Style Guide

I'd like to use pep8 as our style guide, except with line lengths increased to at least 120 (maybe 140). To do this, you can just install pep8 or flake8 on your machine and then run it on your files. Later if we want I can just have a hook to check it for you if we want.

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

To run tests, soon you should be able to just say:

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
