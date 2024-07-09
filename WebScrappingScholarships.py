import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, date

def get_scholarships(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, verify=False)  # Disable SSL verification
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None

def parse_scholarships(html):
    soup = BeautifulSoup(html, 'lxml')
    return soup.find_all('article', class_='scholarship')

def filter_scholarships(scholarships, keywords):
    filtered_scholarships = []
    for scholarship in scholarships:
        description = scholarship.find('div', class_='info')
        if description:
            description_text = description.get_text().lower()
            if any(keyword.lower() in description_text for keyword in keywords):
                filtered_scholarships.append(scholarship)
    return filtered_scholarships

def extract_scholarship_info(scholarship):
    try:
        scholarship_name = scholarship.find('h3').get_text(strip=True)
        p_text = scholarship.find('p').get_text(strip=True)
        status, deadline, location = map(str.strip, p_text.split('|'))
        deadline = deadline.replace('Deadline:', '').strip()
        scholarship_url = scholarship.find('a', class_='text-btn').get('href')
        return {
            'Name': scholarship_name,
            'Deadline': deadline,
            'URL': scholarship_url
        }
    except Exception as e:
        print(f"Error extracting scholarship info: {e}")
        return None

def convert_to_datetime(date_str):
    try:
        return datetime.strptime(date_str, '%B %d, %Y')
    except ValueError:
        return datetime.max

def save_scholarships_to_file(scholarships, filename='scholarships.txt'):
    with open(filename, 'w') as f:
        for scholarship in scholarships:
            f.write(f"Name: {scholarship['Name']}, Deadline: {scholarship['Deadline']}, URL: {scholarship['URL']}\n")

def main():
    url = 'https://scholarshipamerica.org/students/browse-scholarships/'
    keywords = ['STEM', 'first-generation', 'undergraduate', 'graduate', 'Latino', 'Hispanic', 'Engineer', 'Texas', 'National']
    today = date.today()

    html = get_scholarships(url)
    if not html:
        return

    scholarships = parse_scholarships(html)
    filtered_scholarships = filter_scholarships(scholarships, keywords)
    matching_scholarships = [extract_scholarship_info(sch) for sch in filtered_scholarships]
    matching_scholarships = [sch for sch in matching_scholarships if sch]

    matching_scholarships.sort(key=lambda x: convert_to_datetime(x['Deadline']))

    scholarship_stack = [sch for sch in reversed(matching_scholarships) if convert_to_datetime(sch['Deadline']).date() >= today]

    while scholarship_stack:
        scholarship = scholarship_stack.pop()
        print(f"Name: {scholarship['Name']}, Deadline: {scholarship['Deadline']}, URL: {scholarship['URL']}")

    save_scholarships_to_file(matching_scholarships)

if __name__ == '__main__':
    main()
