import json
import pandas as pd
import numpy as np
import re

# Update the categorization function
def categorize_path_final(path):
    if "//Document/P" in path:
        return "Paragraph"
    elif "//Document/Figure" in path:
        return "Figure"
    elif "//Document/Table" in path:
        return "Table Content"
    elif "//Document/H1" in path:
        return "Heading 1"
    elif "//Document/H2" in path:
        return "Heading 2"
    elif "//Document/H3" in path:
        return "Heading 3"
    elif "//Document/H4" in path:
        return "Heading 4"
    elif "//Document/H5" in path:
        return "Heading 5"
    elif "//Document/H6" in path:
        return "Heading 6"
    elif "//Document/TOC" in path:
        return "Table of Contents"
    elif "//Document/L" in path and "/LI" in path and "/Lbl" in path:
        return "List Label"
    elif "//Document/L" in path and "/LI" in path and "/LBody" in path:
        return "List Body"
    elif "//Document/L" in path and "/LI" in path and "/LBody" in path and "/Lbl" in path:
        return "Bullet Label"
    elif "//Document/Aside" in path:
        return "Aside Paragraph"
    elif "//Document/Footnote" in path:
        return "Footnote"
    else:
        return "Unknown"

def create_elements(data):

    # Extracting text, text size, page, and path into lists
    texts = []
    text_sizes = []
    pages = []
    paths = []
    
    for element in data['elements']:
        if 'Text' in element and 'TextSize' in element and 'Page' in element:
            texts.append(element['Text'])
            text_sizes.append(element['TextSize'])
            pages.append(element['Page'])
            paths.append(element['Path'])
    
    # Creating the DataFrame
    df = pd.DataFrame({'Text': texts, 'TextSize': text_sizes, 'Page': pages, 'Path': paths})
    
    df['Type'] = df['Path'].apply(categorize_path_final)

    return df


def initial_document(df):
    # Initialize a new DataFrame with desired columns, including a new column for List Labels
    result = pd.DataFrame(columns=['heading_1', 'heading_2', 'heading_3', 'heading_4', 'heading_5', 
                                   'heading_6', 'list_label', 'body_of_the_text', 'is_footnote', 
                                   'page_number', 'path'])
    
    # Initialise variables
    new_rows_v4 = []
    current_list_label = None
    current_headings = {'heading_1': None, 
                        'heading_2': None, 
                        'heading_3': None, 
                        'heading_4': None, 
                        'heading_5': None, 
                        'heading_6': None}

    
    # Loop through each row in the original DataFrame
    for idx, row in df.iterrows():
        # Determine the type of content
        content_type = categorize_path_final(row['Path'])
        
        # Initialize a new row for df_new_filtered_v4
        new_row = {'page_number': row['Page'], 'is_footnote': 0}  # Initialize 'is_footnote' as 0 (False)
        
        # Include relevant rows (i.e., headings, paragraphs, list bodies, list labels, or footnotes)
        if "Heading" in content_type or content_type in ["Paragraph", "List Body", "List Label", "Footnote"]:
            # Populate the new row based on the content type
            if "Heading" in content_type:
                # Update the current heading of the respective level
                heading_level = int(content_type.split(" ")[-1])
                current_headings[f'heading_{heading_level}'] = row['Text']
                
                # Reset the sub-headings under this heading level
                for i in range(heading_level + 1, 7):
                    current_headings[f'heading_{i}'] = None

                continue
                    
                # Populate the new row with the current headings
                # for key, value in current_headings.items():
                #     new_row[key] = value
    
                # new_row['body_of_the_text'] = None  # No body text for heading rows
                
            elif content_type in ["Paragraph", "List Body"]:
                # Populate the new row with the current headings and list label
                for key, value in current_headings.items():
                    new_row[key] = value
    
                new_row['list_label'] = current_list_label  # Set the list label
                new_row['body_of_the_text'] = row['Text']  # Set the body text
                
            elif content_type == "List Label":
                current_list_label = row['Text']  # Update the current list label
                continue  # Skip appending List Label rows, as they are saved for future List Body rows
                
            elif content_type == "Footnote":
                # Populate the new row with the current headings
                for key, value in current_headings.items():
                    new_row[key] = value
                
                new_row['body_of_the_text'] = row['Text']  # Set the body text
                new_row['is_footnote'] = 1  # Update 'is_footnote' to 1 (True)
       
    
            new_row['path'] = row['Path']
            
            # Append the new row to list
            new_rows_v4.append(new_row)
    
    # Convert list of new rows to a DataFrame and concatenate it with df_new_filtered_v4
    result = pd.concat([result, pd.DataFrame(new_rows_v4)], ignore_index=True)
    # result['merge_id'] = result['path'].str.extract(r'//Document/(.*?)/LBody')
    result['merge_id'] = result['path'].apply(generate_merge_id)
   
    return result

def generate_merge_id(path):
    """
    Generate a merge ID based on the path. Handles a variety of cases.
    """
    # Case 1: For List Body
    if '/LBody' in path:
        return path.split('/LBody')[0]
    
    # Case 2: For Footnotes
    elif '/Footnote[' in path:
        # Extract the footnote number
        footnote_number = path.split('/Footnote[')[1].split(']')[0]
        return f"//Document/Footnote[{footnote_number}]"

    # Case 3: For Paragraphs with ParagraphSpan
    elif '/P[' in path:
        # Extract the paragraph number
        paragraph_number = path.split('/P[')[1].split(']')[0]
        return f"//Document/P[{paragraph_number}]"
    
    # Add more cases as needed
    
    return None

def create_merge_flag(df):
    # Loop through DataFrame rows to set the boolean flag
    df['span_section'] = 0

    counter = 1
    
    for i in range(len(df) - 1):
        current_text = df.loc[i, 'body_of_the_text']
        # print(2, current_text)
        current_text = current_text.strip()
        
        # Check if the current row ends with ':'
        if current_text.endswith(':'):
            df.loc[i, 'span_section'] = counter
    
            # print(3, current_text)
            # Inner loop to check up to the next 10 rows
            for j in range(1, min(11, len(df) - i)):
                next_text = df.loc[i + j, 'body_of_the_text']
                
                # Check if the next row starts with a lowercase letter
                if not re.match(r'^[A-Z]', next_text):
                    df.loc[i + j, 'span_section'] = counter
                else:
                    # Break the inner loop if a row starts with a capital letter
                    break

            counter += 1
            
    return df


def merge_rows(df):

    # Initialize variables
    merged_rows = []
    current_text = None
    current_index_counter = None
    last_row = None
    
    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        # If index_counter is zero, save the row immediately
    
        if (row['index_counter'] == 0) and (current_text is not None):
            first_row['body_of_the_text'] = current_text
            merged_rows.append(first_row)
            current_text = None  # Reset current_text
            current_index_counter = None
    
            merged_rows.append(row.copy())
    
        elif row['index_counter'] == 0:
            merged_rows.append(row.copy())
    
        elif current_index_counter is None:
            current_index_counter = row['index_counter']
            current_text = row['body_of_the_text']
            first_row = row.copy()
    
        elif current_index_counter == row['index_counter']:
            current_text += row['body_of_the_text']
    
        elif current_index_counter != row['index_counter']:
            first_row['body_of_the_text'] = current_text
            merged_rows.append(first_row)
    
            current_index_counter = row['index_counter']
            current_text = row['body_of_the_text']
            first_row = row.copy()
    
    # Handle the last group
    if current_text is not None:
        first_row['body_of_the_text'] = current_text
        merged_rows.append(first_row)
                           
    return pd.DataFrame(merged_rows).reset_index(drop=True)

def create_merge_index(df):
    # Initialize variables
    unique_counter = 0
    prev_merge_id = None
    prev_span_section = None
    
    # Create a new column for the index
    df['index_counter'] = 0
    
    # Iterate through the DataFrame rows
    for idx, row in df.iterrows():
        # Check if either merge_id or span_section is the same as the previous row
        if row['merge_id'] == prev_merge_id or (row['span_section'] == prev_span_section and prev_span_section != 0):
            # Set the index_counter for these rows to the current unique counter value
            df.loc[idx, 'index_counter'] = unique_counter
            df.loc[idx - 1, 'index_counter'] = unique_counter
            
        else:
            # Increment the unique counter only if the row should be merged (either 'merge_id' or 'span_section' is non-zero)
            if (row['merge_id'] or row['span_section']): # and row['span_section'] != 0:
                unique_counter += 1
                df.loc[idx, 'index_counter'] = 0
                
            else:
                df.loc[idx, 'index_counter'] = 0  # Reset to 0 for rows that shouldn't be merged
    
        # Update previous merge_id and span_section for the next iteration
        prev_merge_id = row['merge_id']
        prev_span_section = row['span_section']

    return df
    

                           
# Define a function to count words with more than 3 letters
def count_words(text):
    words = text.split()
    count = 0
    for word in words:
        if len(word) > 2:
            count += 1
    return count

                           
def enrich_dataset(df):                             
    df['body_of_the_text'] = df['body_of_the_text'].str.strip().astype(str)
    # df['correct_format'] = df['body_of_the_text'].apply(lambda x:  str(x)[0].isupper() and  str(x).endswith('.'))
    df['correct_format'] = df['body_of_the_text'].apply(
        lambda x: (str(x)[0].isupper() or str(x)[0].isdigit()) and str(x).endswith('.')
        )
    df['word_count'] = df['body_of_the_text'].apply(count_words)
    df['extracted_numbers'] = df['body_of_the_text'].apply(
            lambda x: [int(tup[1]) for tup in re.findall(r'([a-zA-Z,;.:])(\d+)', x)]
        )
    df['extracted_numbers'] = np.where(df['is_footnote'] == 1, '[]', df['extracted_numbers'])

    heads = ['heading_1', 'heading_2', 'heading_3', 'heading_4', 'heading_5']
    df['source'] = df[heads].apply(lambda row: ' > '.join([str(x) for x in row if x is not None]), axis=1)

    df['footnote_number'] = np.where(
        df['is_footnote'] == 1,
        df['body_of_the_text'].str.extract(r'(\d+)')[0],
        np.nan
    )

    return df
