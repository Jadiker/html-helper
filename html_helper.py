'''
Copyright 2018 London Lowmanstone

MIT License:
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

'''
The goal of this file is to make it so I can import HTML files inside HTML files.
It bothered be from a coding perspective to have to copy/paste HTML,
...and have to remember all the references in case I wanted to change something.
So, this is a solution that allows me to generate HTML files from HTML files that import other HTML files.
'''

import re
import os

def import_html_files(file_path, output_path=None, verbosity=2):
    '''
    Takes in the path to a file, and looks for lines in the file that have:
    <div data-include="name_of_html.html"></div>
    
    in them.
    
    It then takes those lines in the file, replaces them with the data from the appropriate html file,
    ...and saves it to a new file.
    
    It also works recursively, so you can include ".htmlt.html" files,
    ...and it will do all the substitutions in that (without saving that inner file)
    '''
    def default_output_path(input_path):
        '''Take something that ends in ".htmlt.html" and return it so it ends in just ".html"'''
        return input_path[:-6]
        
    # a special file ending so that it doesn't run on everything
    # it was going to just be ".htmlt" for "HTML Template", but then my editor didn't recognize that as an HTML file,
    # ...so I made it the longer ".htmlt.html" so it was both special, but still recognized as an HTML file.
    file_ending = ".htmlt.html"
    assert file_path.endswith(file_ending)
    
    # get the absolute path
    file_path = os.path.abspath(file_path)
    file_folder, file_name = os.path.split(file_path)
    
    if output_path is None:
        # replace the ".htmlt.html" with just ".html"
        output_path = default_output_path(file_path)
        
    if verbosity > 0:
        display_file_name = file_path
        if not verbosity > 2:
            # don't use the full path, use the shorter name
            display_file_name = file_name
            
        print("Starting to import html files into '{}'".format(display_file_name))
        
        
    if output_path != -1:
        output_path = os.path.abspath(output_path)
        output_display_name = output_path
        if not verbosity > 2:
            # don't use the full path, use the shorter name
            output_display_name = os.path.split(output_path)[1]
        print("The output file will be saved as '{}'".format(output_display_name))
    else:
        if verbosity > 0:
            print("The output will not be saved.")
        

    # regex to match something like <div data-include="name_of_html.html"></div> and get the level of spacing
    div_regex = r'(\s*)<div\ data\-include\=\"(.*)\"\>\<\/div\>'
    with open(file_path, "r") as f:
        lines = f.readlines()

    for line_index, line in enumerate(lines):
        # see if it matches the form:
        match = re.match(div_regex, line)
        if match:
            import_file_name = match.group(2)
            import_file_path = os.path.relpath(import_file_name, start=file_folder)
            if verbosity > 1:
                if verbosity > 2:
                    print("Adding in data from the file '{}'".format(import_file_path))
                else:
                    print("Adding in data from the file '{}'".format(import_file_name))

            # check for recursivity and get the lines from the correct file
            if import_file_path.endswith(file_ending):
                # recursive
                try:
                    import_verbosity = 0
                    if verbosity > 4:
                        import_verbosity = verbosity
                    import_lines = import_html_files(import_file_path, output_path=-1, verbosity=import_verbosity).split("\n")
                    # add back in the new lines that were split out
                    import_lines = [import_line + "\n" for import_line in import_lines]
                except Exception as e:
                    raise RuntimeError("Failed to convert necessary file '{}'".format(import_file_name)) from e
            else:
                with open(import_file_name, "r") as import_f:
                    import_lines = import_f.readlines()
                    
            # actually do the substitution
            spacing = match.group(1)
            import_lines = [spacing + import_line for import_line in import_lines]
            # check to see if this should be the end of the file or not, and make the imported lines mimic the ones in the file
            if line.endswith("\n"):
                if not import_lines[-1].endswith("\n"):
                    import_lines[-1] += "\n"
            else:
                if import_lines[-1].endswith("\n"):
                    import_lines[-1] = import_lines[-1][:-1]

            lines[line_index] = "".join(import_lines)

    # create the final text for the file
    ans = "".join(lines) # short for 'answer'
    
    if output_path == -1:
        return ans
    else:
        with open(output_path, "w") as new_f:
            new_f.write(ans)


if __name__ == "__main__":
    '''
    This is my usual workflow.
    I create a directory called "internal_code" or something like that inside the root for my project.
    The internal directory contains this script, and all of the ".htmlt.html" files as well as normal ".html" files.
    My ".css" (and ".js") files go in the root folder itself, since that's where everything will be run from.
    Then, I label the files that I actually want to display with the extension ".f.htmlt.html" where the ".f" stands for "final".
    This script then looks for all of those files, performs the imports on them, and then saves them to the root folder.
    This keeps the other imported ".htmlt.html" and ".html" files from cluttering up the root folder.
    '''
    
    import traceback
    for file_name in os.listdir("."):
        # look particularly for ".htmlt.html" files that start with ".f" for "final"
        final_extension = ".f.htmlt.html"
        if file_name.endswith(final_extension):
            try:
                output_path = "../" + file_name[:-len(final_extension)] + ".html"
                import_html_files(file_name, output_path, verbosity=2)
            except Exception:
                traceback.print_exc()
                print("Failed to convert '{}' into html file".format(file_name))
