import os

# List of folder names
folders = ['level_0', 'level_1', 'level_2', 'level_3', 'level_4', 'level_5']

# Output file name
output_file = 'merged_texts.txt'

# Open the output file in write mode
with open(output_file, 'w', encoding='utf-8') as outfile:
    # Iterate through each folder
    for folder in folders:
        file_path = os.path.join(folder, 'texts.txt')
        # Check if the file exists
        if os.path.exists(file_path):
            # Open the texts.txt file in read mode
            with open(file_path, 'r', encoding='utf-8') as infile:
                # Read the contents and write to the output file
                outfile.write(infile.read())
                outfile.write("\n\n")  # Add a newline to separate contents from different files
        else:
            print(f"File {file_path} does not exist")


