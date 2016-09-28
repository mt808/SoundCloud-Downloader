from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from PIL import Image
import re
import eyed3
import urllib
import time
import os.path
import shutil
import sys
import imagehash


name = raw_input("Link to the artist's profile: ").strip(':').split('/')
name = name[-1]
artistName = unicode(raw_input("Artist's Name: "), 'utf-8')
pages = raw_input('Have they uploaded more than ~17 tracks? (y/n) ')
musicPath = '/Users/michaeltassone/Downloads/Music/' + name + '/'
items = 0

if not os.path.exists(musicPath):
    os.makedirs(musicPath)

artPath = musicPath + "albumArt/"
url = 'https://soundcloud.com/' + name
songNameList = list()
list1 = list()
artList = list()
driver = webdriver.Chrome("/Users/michaeltassone/Downloads/chromedriver")
driver.get(url)
end = 0

if pages == 'n':
    end = 9

while end < 10:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    end += 1

elems = driver.find_elements_by_xpath("//a[@href]")
for link in elems:
    href = link.get_attribute("href")

    if (href.startswith(url + '/') and (href not in list1) and href.split("/")[-2] == name and
                href.endswith('/tracks') == False and
                href.endswith('/albums') == False and
                href.endswith('/reposts') == False and
                href.endswith('/following') == False and
                href.endswith('/followers') == False and
                href.endswith('/likes') == False and
                href.endswith('/comments') == False and
                href.endswith('/sets') == False):
        list1.append(href)

count = 0
for pictures in list1:
    driver.get(pictures)
    time.sleep(2)
    try:
        arts = driver.find_element_by_xpath(
            '//*[@id="content"]/div/div[2]/div/div[2]/div[1]/div/div/div/span').value_of_css_property("background-image")
        songName = driver.find_element_by_xpath(
            '//*[@id="content"]/div/div[2]/div/div[2]/div[2]/div/div/div[2]/span/span').text
    except:
        time.sleep(3)
        arts = driver.find_element_by_xpath(
            '//*[@id="content"]/div/div[2]/div/div[2]/div[1]/div/div/div/span').value_of_css_property(
            "background-image")
        songName = driver.find_element_by_xpath(
            '//*[@id="content"]/div/div[2]/div/div[2]/div[2]/div/div/div[2]/span/span').text

    if not os.path.exists(musicPath + "albumArt"):
        os.makedirs(musicPath + "albumArt")

    arts = arts.strip(")").strip("(").strip('"')
    arts = re.search("(?P<url>https?://[^\s]+)", arts).group("url")
    save = urllib.urlretrieve(str(arts), artPath + str(count) + ".jpg")
    artList.append(artPath + str(count) + ".jpg")
    songNameList.append(songName)
    count += 1
count = 0
items = len(artList)
for songs in list1:
    if not os.path.isfile(musicPath + songNameList[count] + ".mp3"):
        driver.get('http://offliberty.com/')
        time.sleep(2)
        toEnter = driver.find_element_by_id("track").send_keys(songs)
        submit = driver.find_element_by_id("button")
        submit.click()
        try:
            wait = WebDriverWait(driver, 60)
            con = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "download")))
            dlLink = driver.find_element_by_class_name("download").get_attribute('href')
        except:
            driver.get('http://offliberty.com/')
            time.sleep(2)
            toEnter = driver.find_element_by_id("track").send_keys(songs)
            submit = driver.find_element_by_id("button")
            submit.click()
            try:
                wait = WebDriverWait(driver, 60)
                con = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "download")))
                dlLink = driver.find_element_by_class_name("download").get_attribute('href')
            except:
                driver.get('http://offliberty.com/')
                time.sleep(2)
                toEnter = driver.find_element_by_id("track").send_keys(songs)
                submit = driver.find_element_by_id("button")
                submit.click()
                try:
                    wait = WebDriverWait(driver, 60)
                    con = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "download")))
                    dlLink = driver.find_element_by_class_name("download").get_attribute('href')
                except:
                     print("One of the downloads failed, run me again.")
                     shutil.rmtree(artPath)
                     driver.close()
                     sys.exit()

        success = urllib.urlretrieve(dlLink, musicPath + songNameList[count] + ".mp3")

        audioFile = eyed3.load(musicPath + songNameList[count] + ".mp3")
        audioFile.initTag()
        audioFile.tag.artist = artistName

        audioFile.tag.title = songNameList[count]
        imageData = open(artList[count], "rb").read()
        audioFile.tag.images.set(3, imageData, "image/jpg")
        imgHashList = list()
        for images in artList:
            imgHashList.append(imagehash.average_hash(Image.open(images)))

        if imgHashList.count(imgHashList[count]) == 1:
            audioFile.tag.album = unicode(songNameList[count]) + u" - Single"
            audioFile.tag.track_num = 1
        else:
            audioFile.tag.album = unicode(imgHashList[count])

        audioFile.tag.save()
    count += 1

shutil.rmtree(artPath)
driver.close()
