# Import dependencies
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    browser = Browser('chrome', executable_path='chromedriver', headless=True)
    
    thumbnail, article_date, news_title, news_paragraph = mars_news(browser)
    
    # Run all scraping functions and store results in dictionary
    data = {
        "thumbnail": thumbnail,
        "article_date": article_date,
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": mars_hemispheres(browser),
        "last_modified": dt.datetime.now()
    }
    
    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object
    html = browser.html
    news_soup = soup(html, 'html.parser')
    
    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')

        # Use the parent element to get the thumbnail URL
        thumbnail = 'https://mars.nasa.gov' + slide_elem.select_one('div.list_image img')['src']

        # Use the parent element to find div.list_date
        article_date = slide_elem.find('div', class_='list_date').get_text()

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()
    
    except AttributeError:
        return None, None

    return thumbnail, article_date, news_title, news_p

# Featured Images

def featured_image(browser):
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info     ', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')
    
    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")
    
    except AttributeError:
        return None
    
    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'
    
    return img_url

# Mars Planet Profile

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a DataFrame
        df = pd.read_html('http://space-facts.com/mars/')[0]
    
    except BaseException:
        return None
        
    # Convert DataFrame into HTML format, add bootstrap
    return df.to_html(header=False, index=False, classes='table table-striped')

# Mars Hemispheres

def mars_hemispheres(browser):
    # Use browser to visit the URL 
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # Create a list to hold the images and titles
    hemisphere_image_urls = []

    # Retrieve the image urls and titles for each hemisphere
    for x in range(4):
        attributes = browser.find_by_tag('a')
        links = [attributes[4].find_by_tag('img'), attributes[6].find_by_tag('img'), 
            attributes[8].find_by_tag('img'), attributes[10].find_by_tag('img')]
        browser.is_element_present_by_xpath('/html/body/div/div/div[2]/section/div/div[2]', wait_time=1)
        links[x].click()
        hemisphere_soup = soup(browser.html, 'html.parser')
        
        # Add try/except for error handling
        try:
            url = hemisphere_soup.select_one('div.downloads ul li a')['href']
            content = hemisphere_soup.find('div', class_='content')
            metadata = content.find('section', class_='block metadata')
            title = metadata.find('h2').text
        except AttributeError:
            return None 

        hemisphere_image_urls.append({'img_url': url, 'title': title})
        browser.back()

    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())
