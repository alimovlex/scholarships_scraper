# Web Scrapping Scholarships
from bs4 import BeautifulSoup

import requests
from datetime import datetime, date


url = 'https://scholarshipamerica.org/students/browse-scholarships/'
html = requests.get(url)

# Beautiful soup object
soup = BeautifulSoup(html.text, 'lxml')
scholarships = soup.find_all('article', class_ = 'scholarship')

# Define your keywords
keywords = ['STEM', 'first-generation', 'undergraduate', 'graduate', 'Latino', 'Hispanic', 'Engineer', 'Texas', 'National']

# List to hold scholarships that match the keywords
filtered_scholarships = []

# # Iterate over each scholarship
for scholarship in scholarships:
    # Get the 'more' section or description
    description = scholarship.find('div', class_ = 'info')  # P tag holds the description
    # print(description)
    if description:
        description_text = description.get_text().lower()  # Convert to lowercase for case-insensitive search
        # Check if any of the keywords are in the description
        if any(keyword.lower() in description_text for keyword in keywords):
            filtered_scholarships.append(scholarship)

# Now from those filtered scholarships we want to get the info
# Iterate over each filtered scholarship
matching_scholarships = []
for scholarship in filtered_scholarships:

    scholarship_name = scholarship.find('h3', class_ = '').text.replace(' ', ' ')

    # Extracting status, deadline, and location
    p_text = scholarship.find('p').get_text(strip=True)
    status, deadline, location = p_text.split('|')

    # Cleaning up the deadline to remove extra spaces and the 'Deadline:' part
    deadline = deadline.replace('Deadline:', '').strip()
 
    scholarship_url = scholarship.find('a', {'class':'text-btn'}).get('href')

    # Create a dictionary with the scholarship info
    scholarship_info = {
        'Name': scholarship_name,
        'Deadline': deadline,
        'URL': scholarship_url
    }

    # Append the dictionary to the list
    matching_scholarships.append(scholarship_info)

'''
Date Sorting Logic
'''
# Convert deadline strings to datetime objects and sort
def convert_to_datetime(date_str):
    try:
        # Adjust the format if necessary
        # Creates Date to Numerical Value Ex. June 6th, 2023 -> 6,6,2023
        return datetime.strptime(date_str, '%B %d, %Y')
    except ValueError:
        # Return a default date if the parsing fails
        return datetime.max
    
# Present date    
today = date.today()

# Sort the scholarships by date
matching_scholarships.sort(key=lambda x: convert_to_datetime(x['Deadline']))

# Implementing stack using list
scholarship_stack = []

# Push scholarships onto stack (latest first, so they are popped earliest first)
for scholarship in reversed(matching_scholarships):
    scholarship_deadline = convert_to_datetime(scholarship['Deadline'])
    # Check if the scholarship's deadline is after today's date
    if scholarship_deadline.date() >= today:
        scholarship_stack.append(scholarship)

# Pop scholarships from stack to list them by earliest date
while scholarship_stack:
    scholarship = scholarship_stack.pop()
    print(f"Name: {scholarship['Name']}, Deadline: {scholarship['Deadline']}, URL: {scholarship['URL']}")

'''
Text File with constant updating
'''

