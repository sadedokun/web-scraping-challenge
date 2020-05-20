from splinter import Browser
from bs4 import BeautifulSoup as bs
import time
import pandas as pd
from selenium import webdriver
import requests as req


def init_browser():
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=True)


def scrape_info():
    browser = init_browser()

    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    html = browser.html
    soup = bs(html, "html.parser")

    news_title = soup.find("div", class_="content_title").text
    paragraph_text = soup.find("div", class_="rollover_description_inner").text

    # executable_path = {'executable_path': 'chromedriver'}
    # browser = Browser('chrome', **executable_path, headless=True)
    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)

    html = browser.html
    soup = bs(html, "html.parser")

    browser.click_link_by_partial_text('FULL IMAGE')

    time.sleep(5)
    browser.click_link_by_partial_text('more info')

    new_html = browser.html
    new_soup = bs(new_html, 'html.parser')
    temp_img_url = new_soup.find('img', class_='main_image')
    back_half_img_url = temp_img_url.get('src')

    recent_mars_image_url = "https://www.jpl.nasa.gov" + back_half_img_url

    twitter_response = req.get("https://twitter.com/marswxreport?lang=en")
    twitter_soup = bs(twitter_response.text, 'html.parser')

    tweet_containers = twitter_soup.find_all(
        'div', class_="js-tweet-text-container")
    for i in range(10):
        tweets = tweet_containers[i].text
        if "Sol " in tweets:
            mars_weather = tweets
            break

    request_mars_space_facts = req.get("https://space-facts.com/mars/")

    mars_space_table_read = pd.read_html(request_mars_space_facts.text)
    df = mars_space_table_read[0]

    df.set_index(0, inplace=True)
    mars_data_df = df

    mars_data_html = mars_data_df.to_html()
    mars_data_html.replace('\n', '')
    mars_data_df.to_html('mars_table.html')

    usgs_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    usgs_req = req.get(usgs_url)

    soup = bs(usgs_req.text, "html.parser")
    hemi_attributes_list = soup.find_all('a', class_="item product-item")

    hemisphere_image_urls = []
    for hemi_img in hemi_attributes_list:
        # get the img title
        img_title = hemi_img.find('h3').text
        # print(img_title)
        # get the link to stir another soup, this is the page with the actual image url
        link_to_img = "https://astrogeology.usgs.gov/" + hemi_img['href']
        # print(link_to_img)
        img_request = req.get(link_to_img)
        soup = bs(img_request.text, 'lxml')
        img_tag = soup.find('div', class_='downloads')
        img_url = img_tag.find('a')['href']
        hemisphere_image_urls.append(
            {"Title": img_title, "Image_Url": img_url})

    twit_url = ('https://twitter.com/marswxreport?lang=en')

    response = req.get(twit_url)
    soup = bs(response.text, 'html.parser')
    # soup = bs(response.text, 'html5lib')

    # print(soup.prettify())
    content = soup.find_all('div', class_="content")
    # print(content)
    print(content[0].text)

    mars_weather = []
    for content in content:
        tweet = content.find("div", class_="js-tweet-text-container").text
        mars_weather.append(tweet)
    # print(mars_weather)

    mars_weather = mars_weather[8]
    print(mars_weather)

    mars_data = {
        "News_Title": news_title,
        "Paragraph_Text": paragraph_text,
        "Most_Recent_Mars_Image": recent_mars_image_url,
        "Mars_Weather": mars_weather,
        "mars_h": hemisphere_image_urls
    }

    return mars_data


def scrape():
    init_browser()
    return scrape_info()
