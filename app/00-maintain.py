#!/usr/bin/python3
#----------------------------------------------
# create index for JS files ...
#----------------------------------------------

# load basic modules and configuration
#----------------------------------------------

import time
import os
import glob


overall_index   = "00-maintain-index.js"
cache_manifest  = "cache.manifest"
text_to_replace = ""
text_to_insert  = ""
#text_to_replace = "appPrintMenu"
#text_to_insert  = "appPrint_menu"

# create index for JS files
#----------------------------------------------

def get_all_files():
    files = glob.glob("./*.*")
    return files

#----------------------------------------------

def get_js_files():
    files = glob.glob("./*.js")
    return files

#----------------------------------------------

def read_file(filename):
    file = open(filename,"r") 
    return file.read()

#----------------------------------------------

def create_file(filename,content):
    file = open(filename,"w+")
    file.write(content)
    file.close()

#----------------------------------------------

def write_file(filename,content):
    file = open(filename,"w")
    file.write(content)
    file.close()

#----------------------------------------------

def replace_in_file(content):
    global text_to_replace, text_to_insert
    
    if text_to_replace != "":
      content = content.replace(text_to_replace,text_to_insert)
    return content

#----------------------------------------------

def create_index_file(filename):
    '''
    create index index in file
    '''

    global overall_index

    content = read_file(filename)
    index   = read_file(overall_index)

    new_lines_header = []
    new_lines_index  = []
    new_lines_body   = []
    length           = -1
    new_content      = ""

    start     = False
    end       = False

    if "/* INDEX" in content:

       content = replace_in_file(content)
       lines       = content.split("\n")    
       length      = len(lines)
       
       for line in lines:
       
          if  "*/" in line and start == True:      end   = True
          if start == False and end == False:      new_lines_header.append( line )
          if start == True  and end == True:       new_lines_body.append( line )
          if "/* INDEX" in line and start == False:      start = True

       for line in new_lines_body:
         if "function " in line or "function	" in line:
           parts = line.split(")")
           new_lines_index.append( parts[0]+")" )

       for line in new_lines_header:  new_content += line + "\n"
       for line in new_lines_index:   new_content += line + "\n"
       for line in new_lines_body:    new_content += line + "\n"
       
    index += "----------------------------\n"
    index += filename + " (" + str(length) + ")\n"
    index += "----------------------------\n"

    for line in new_lines_index:    index += line + "\n"

    write_file(overall_index,index)
    
    if start and end:
      #create_file(filename+".test",new_content)
      write_file(filename,new_content)

#----------------------------------------------

create_file(overall_index,"")

files = get_js_files()
for file in files: create_index_file(file)

content = ""
files   = get_all_files()

content += "CACHE MANIFEST\n"
content += "# 2018-09-26 Version 1.6\n"
content += "\nCACHE:\n"
content += "\n".join(files)
content += "\n"
content += "\nNETWORK:\n"
content += "\nFALLBACK:\n"

#create_file(cache_manifest+".test",content)
