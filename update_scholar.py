import re
import urllib.request
import ssl
from bs4 import BeautifulSoup

# Your Google Scholar ID
SCHOLAR_ID = "g4RBaCQAAAAJ"
URL = f"https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en"

def fetch_publications(): #fetches the publications
    print(f"Fetching publications for Google Scholar ID: {SCHOLAR_ID}...") #prints that the publications are being fetched
    
    # Create an unverified SSL context to avoid certificate errors on Windows
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    # Google Scholar blocks basic requests, so we spoof a standard web browser user-agent
    req = urllib.request.Request(
        URL, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    )
    
    try:
        html = urllib.request.urlopen(req, context=ctx).read() #reads the HTML content
    except Exception as e:
        print("Error fetching Google Scholar profile. Google might be blocking the request.") #prints that the publications are being fetched
        print(f"Details: {e}") #prints the details of the error
        return []

    soup = BeautifulSoup(html, 'html.parser')
    publications = []
    
    # Google Scholar uses class "gsc_a_tr" for publication rows
    for row in soup.find_all('tr', class_='gsc_a_tr'):
        title_tag = row.find('a', class_='gsc_a_at')
        if not title_tag:
            continue
            
        title = title_tag.text
        authors = row.find('div', class_='gs_gray').text
        journal_info = row.find_all('div', class_='gs_gray')[1].text
        
        # Link to the specific paper page
        link = "https://scholar.google.com" + title_tag['href']
        
        publications.append({
            'title': title,
            'authors': authors,
            'journal': journal_info,
            'link': link
        })
        
    return publications

def update_html(publications):
    if not publications:
        print("No publications found or unable to fetch. Skipping HTML update.")
        return
        
    print(f"Successfully fetched {len(publications)} publications. Updating research.html...")
    
    with open('research.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    # Create the new HTML list items
    new_html = "<!-- PUBLICATIONS START -->\n"
    for pub in publications:
        new_html += f"                        <li><a href='{pub['link']}' target='_blank'><strong>{pub['title']}</strong></a><br>\n"
        new_html += f"                        <em>{pub['authors']}</em><br>\n"
        new_html += f"                        {pub['journal']}<br></li>\n"
    new_html += "                        <!-- PUBLICATIONS END -->"
    
    # Replace the old list with the new one
    updated_content = re.sub(
        r'<!-- PUBLICATIONS START -->.*?<!-- PUBLICATIONS END -->',
        new_html,
        html_content,
        flags=re.DOTALL
    )
    
    with open('research.html', 'w', encoding='utf-8') as f:
        f.write(updated_content)
        
    print("research.html has been successfully updated with your latest publications!")

if __name__ == "__main__":
    pubs = fetch_publications()
    update_html(pubs)
