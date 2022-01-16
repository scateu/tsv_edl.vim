#!/bin/bash
sed -E -n '/^[0-9]+$/{N;d;}; /./p;' 
