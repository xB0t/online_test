import shutil
import os
import zipfile
import tempfile
import csv
from django.template import Context, Template


def copy_files(file_paths):
    """ Copy Files to current directory, takes
    tuple with file paths and extract status"""

    files = []
    for src in file_paths:
        file_path, extract = src
        file_name = os.path.basename(file_path)
        files.append(file_name)
        shutil.copy(file_path, os.getcwd())
        if extract:
            z_files, path = extract_files(file_name, os.getcwd())
            for file in z_files:
                files.append(file)
    return files


def delete_files(files, file_path=None):
    """ Delete Files from directory """
    for file_name in files:
        if file_path:
            file = os.path.join(file_path, file_name)
        else:
            file = file_name
        if os.path.exists(file):
            if os.path.isfile(file):
                os.remove(file)
            else:
                shutil.rmtree(file)


def extract_files(zip_file, path=None):
    """ extract files from zip """
    zfiles = []
    if zipfile.is_zipfile(zip_file):
        zip_file = zipfile.ZipFile(zip_file, 'r')
        for z_file in zip_file.namelist():
            zfiles.append(z_file)
        if path:
            extract_path = path
        else:
            extract_path = tempfile.gettempdir()
        zip_file.extractall(extract_path)
        zip_file.close()
        return zfiles, extract_path


def is_csv(document):
    ''' Check if document is csv with ',' as the delimiter'''
    try:
        try:
            content = document.read(1024).decode('utf-8')
        except AttributeError:
            document.seek(0)
            content = document.read(1024)
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(content, delimiters=',')
        document.seek(0)
    except (csv.Error, UnicodeDecodeError):
        return False, None
    return True, dialect


def write_static_files_to_zip(zipfile, course_name, current_dir):
    static_files = {"js": ["bootstrap.js", "bootstrap.min.js",
                           "jquery-1.9.1.min.js", "video.js"],
                    "css": ["bootstrap.css", "bootstrap.min.css",
                            "video-js.css", "offline.css"],
                    "images": ["yaksh_banner.png"]}
    for folder in static_files.keys():
        folder_path = os.sep.join((current_dir, "static", "yaksh", folder))
        for file in static_files[folder]:
            file_path = os.sep.join((folder_path, file))
            with open(file_path, "rb") as f:
                zipfile.writestr(
                    os.sep.join((course_name, "static", folder, file)),
                    f.read()
                    )


def write_templates_to_zip(zipfile, template_path, data, filename, filepath):
    with open(template_path) as f:
        template_data = f.read()
        template = Template(template_data)
        context = Context(data)
        render = template.render(context)
        zipfile.writestr(os.sep.join((filepath, "{0}.html".format(filename))),
                         str(render))
