import re
import requests
from bs4 import BeautifulSoup


# This function returns a list of the casts' names.
def get_cast_names(imdb_id):
    url = "https://www.imdb.com/title/" + imdb_id
    names = []
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    out = soup.find_all('div', class_='credit_summary_item')
    directors = out[0].text.split()
    director = directors[1] + ' ' + directors[2]
    names.append(director)
    writers = out[1].text.split()
    writer = writers[1] + ' ' + writers[2]
    names.append(writer)
    stars = out[2].text.split('|')[0].split('\n')[2].split(',')
    for i in stars:
        if i not in names:
            names.append(i)
    return names
#print(get_cast_names('tt0360717'))


# This function returns a list of lists each containing the cast and their role ID.
def scrape_cast(imdb_id):
    #url = "https://www.imdb.com/title/" + "imdb_id"
    casts = []
    names = get_cast_names(imdb_id)
    check = 0
    stop = len(names)
    while check < stop:
        if check == 0 or check == 1:
            casts.append([imdb_id, check, names[check]])
            check += 1
        else:
            casts.append([imdb_id, 2, names[check]])
            check += 1
    return casts
#print(scrape_cast('tt0360717'))


# This function returns a list of lists each containing the cast and their award.
def scrape_awards(imdb_id, important):
    results = []
    url = "https://www.imdb.com/title/" + imdb_id
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    out = soup.find('a', class_='btn-full').attrs['href']
    awd_url = "https://www.imdb.com/" + out
    awd_r = requests.get(awd_url)
    awd_soup = BeautifulSoup(awd_r.text, 'html.parser')
    awd_out = awd_soup.find_all('table', class_='awards')
    #print(len(awd_out))
    awards = {}
    for block in awd_out:
        text = block.text.split(' '*6)
        text = [i for i in text if i !='']
        #print(text)
        prefix = [i for i in text[0].split('\n') if i != '']
        prefix = ' '.join([str(elem) for elem in prefix[::-1]])
        for i in text[1:]:
            record = [j for j in i.split('\n') if j != '']
            if len(record) > 0:
                suffix = record[0]
                award = prefix + ': ' + suffix
                people = tuple(record[1:])
                awards[people] = award
    #print(awards)
    results = []
    for p in important:
        if len(results) == 3:
            return results
        for k,v in awards.items():
            if p in k:
                results.append([imdb_id, p, v])
                break
#print(scrape_awards('tt0360717', get_cast_names('tt0360717')))



#This function finds additional movie links from a given HTML text.
def link_finder(HTML_to_parse):
    import re
    import requests
    from bs4 import BeautifulSoup
    
    movie_ids = []
    soup  =  BeautifulSoup(HTML_to_parse, 'html.parser')
    recs  =  soup.find_all('div', class_='rec_item')


    reg = '(?<=data-tconst=").{9}'
    for i in recs:
        text = str(i)
        x = re.findall(reg, text)
        if x not in movie_ids: 
            movie_ids.append(x)
    return movie_ids
#print(link_finder(HTML_to_parse))



#This function finds additional (n^site) number of recommended movie links recursively.  
def recursive_link_scraper(site, n, level): 
    
    # list to return 
    urls=[] 

    r = requests.get(site) 
    s = BeautifulSoup(r.text,"html.parser")
    
    if n>12:
        return 'At most 12 recommendations for one movie'

    #Using Chrome Inspect I found that there are 12 <div class='rec_poster"> tags, and each contains one url for one movie. 
    #The format of the following code is based on this assumption    
    while level:
        for i in s.find_all(class_='rec_poster')[0:n]:      
            url = i.attrs['href'] 
           
            if url.startswith("/"): 
                site = "https://www.imdb.com/title/" + url 
               
                if site not in urls: 
                    urls.append(site)  
                    print(site)
                    #recursive call
                    recursive_link_scraper(site, n, level-1) 
    return urls