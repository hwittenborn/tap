# Contributing
Tap doesn't enforce many rules for contributors to the project, with only a few things such as some code linters being enforced.

# Setting up your system
You'll first need to have forked and cloned this repository to your local system. Various guides are present online on how to do such, which should get you in the right direction.

We use Flake8 and Black to format and validate all Python files. Black is used as a base for formatting files, and then Flake8 is utilized to ensure things like matching syntax and unused imports aren't present in files.

Flake8 should be installable via the `flake8` package in your Linux distribution's repositories. If Black can't be found on your system, you can install the `black-bin` package from the MPR.

# Running linters
After modifying files, you should run the linters before pushing your changes.

Black linting can be done by running the following from the root of the cloned repository:

```sh
black ./
```

Likewise, you can run the Flake8 linter with the following:

```sh
flake8 ./
```

After both commands run cleanly with no changes/errors, you're good to go to push your changes.
