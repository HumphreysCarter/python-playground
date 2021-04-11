from os import walk, path, remove
from time import time

base_dir    = '/home/admin/www/html/bin/models/'
file_types  = ('png', 'pdf', 'jpg')
max_age_hrs = 36

# Get current epoch time
epoch_now = time()

# Find all files matching file extentions in path
for root, dirs, files in walk(base_dir):
    for file in files:
        if file.endswith(file_types):
            # Get file path
            file_path = path.join(root, file)

            # Get file epoch
            epoch_file = path.getmtime(file_path)

            # Check if updated since max_age_hrs, delete if false
            max_age = max_age_hrs * 3600
            if (epoch_now-epoch_file) >= max_age:
                remove(file_path)
                print(f'Deleted {file_path}')
