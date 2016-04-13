#!/bin/bash

# setup tools path

declare -r TOOL_DIR=${PWD}
declare BASHRC=~/.bashrc

# add the current directory to the bashrc path
echo "" >> ${BASHRC}
echo "# custom tools" >> ${BASHRC}
echo "TOOL_PATH=${TOOL_DIR}" >> ${BASHRC}
echo "export PATH=\$PATH:\$TOOL_PATH" >> ${BASHRC}
