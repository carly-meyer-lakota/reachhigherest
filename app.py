import pandas as pd
import streamlit as st
from fuzzywuzzy import process
import spacy

# Load the Excel file
file_path = 'rh3A-6B .xlsx'
df = pd.read_excel(file_path, engine='openpyxl')

# Load spaCy model
spacy.cli.download('en_core_web_sm')
nlp = spacy.load('en_core_web_sm')

# Streamlit app
st.title('Unit Part Search App')

# Search filter
keyword = st.text_input('Enter Keyword')

# Function to perform fuzzy search
def fuzzy_search(keyword, choices, limit=5):
    results = process.extract(keyword, choices, limit=limit)
    return [result[0] for result in results]

# Function to find semantically similar words
def get_similar_words(keyword, choices, limit=5):
    keyword_vec = nlp(keyword)
    similarities = [(choice, keyword_vec.similarity(nlp(choice))) for choice in choices]
    similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
    return [similarity[0] for similarity in similarities[:limit]]

# Get all content as a single string for each row
df['combined'] = df.apply(lambda row: ' '.join(row.values.astype(str)), axis=1)

# Perform fuzzy search on the skill columns (columns 7-13)
skill_columns = df.columns[6:13]
df['skills_combined'] = df[skill_columns].apply(lambda row: ' '.join(row.values.astype(str)), axis=1)

if keyword:
    choices = df['skills_combined'].tolist()
    matched_rows = fuzzy_search(keyword, choices)
    similar_words = get_similar_words(keyword, choices)
    matched_rows.extend(similar_words)
    filtered_df = df[df['skills_combined'].isin(matched_rows)].head(5)
else:
    filtered_df = df.head(5)

# Highlight the matched words in the dataframe
def highlight_keywords(s, keywords):
    for keyword in keywords:
        s = s.str.replace(f'({keyword})', r'<mark>\1</mark>', case=False, regex=True)
    return s

if keyword:
    keywords = [keyword] + get_similar_words(keyword, df['skills_combined'].tolist())
    filtered_df[skill_columns] = filtered_df[skill_columns].apply(lambda row: highlight_keywords(row, keywords), axis=1)

# Display the filtered results with highlighted keywords
st.write('Filtered Results:')
st.write(filtered_df.drop(columns=['combined', 'skills_combined']).to_html(escape=False), unsafe_allow_html=True)

# Save the filtered results to a new Excel file
filtered_df.drop(columns=['combined', 'skills_combined']).to_excel('filtered_results.xlsx', index=False)

st.write('Filtered results have been saved to filtered_results.xlsx')
