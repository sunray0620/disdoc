import os
import subprocess


def read_file(file_path):
  with open(file_path) as f:
    content = f.read()
  return content


def write_file(file_path, file_content):
  with open(file_path, 'w') as f:
    f.write(file_content)

