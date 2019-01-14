#!/bin/bash

# The directory containint this script (all paths are then relative to this)
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# This is needed by pylint to find imports
export PYTHONPATH="$PYTHONPATH:$PROJECT_DIR/polyshaper/test:$PROJECT_DIR/polyshaper/plugin"

RUN_PYLINT="y"
RUN_TESTS="y"
if [ "$1" = "pylint" ]; then
    RUN_TESTS="n"
elif [ "$1" = "tests" ]; then
    RUN_PYLINT="n"
fi

# First launch pylint on all source and test files, if present
PYLINT_EXEC=$(which pylint)
if [ $? != 0 ]; then
    echo
    echo "=== pylint not found, skipping"
    echo
elif [ "$RUN_PYLINT" = "y" ]; then
    echo
    echo "=== Running pylint"
    echo
    # --additional-builtins is to avoid warning when using the _() function for localization
    "${PYLINT_EXEC}" --output-format=colorized --additional-builtins=_ polyshaper
fi

# Now run all tests
if [ "$RUN_TESTS" = "y" ]; then
    echo
    echo "=== Running tests"
    echo
    "${PROJECT_DIR}/polyshaper/test/testall.py"
fi
