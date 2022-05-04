import os
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import openpyxl


# Definisi Parameter
url = "https://id.indeed.com/jobs?q="
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/100.0.4896.127 Safari/537.36'}


def get_total_pages():
    params = {
        'q': 'Laravel Developer',
        'l': 'Indonesia',
        'vjk': '177b29f46a3befe1',
    }
    res = requests.get(url, params=params, headers=headers)
    # Pembuatan Temporary Folder untuk menampung hasil Scrapping
    try:
        os.mkdir('temp')
    except FileExistsError:
        pass

    with open('temp/res.html', 'w+') as outfile:
        outfile.write(res.text)
        outfile.close()

    # Proses Scrapping
    soup = BeautifulSoup(res.text, 'html.parser')
    pagination = soup.find('ul', 'pagination-list')
    pages = pagination.findAll('li')
    total_pages = []
    for page in pages:
        total_pages.append(page.text)

    total = int(max(total_pages))
    return total


def get_all_items():
    company_url = 'https://id.indeed.com'
    params = {
        'q': 'Laravel Developer',
        'l': 'Indonesia',
        'vjk': '177b29f46a3befe1',
    }
    res = requests.get(url, params=params, headers=headers)

    # Proses Scrapping
    soup = BeautifulSoup(res.text, 'html.parser')
    contents = soup.find_all('table', 'jobCard_mainContent big6_visualChanges')
    joblist = []
    for item in contents:
        title = item.find('h2', 'jobTitle').text
        company = item.find('span', 'companyName')
        company_name = company.text
        try:
            link = company_url + company.find('a')['href']
        except:
            link = 'Link is not available'

        data_dict = {
            'title': title,
            'company name': company_name,
            'company link': link,
        }
        joblist.append(data_dict)

    # create json
    try:
        os.mkdir('json_result')
    except FileExistsError:
        pass

    with open('json_result/indeed_joblist.json', 'w+') as json_data:
        json.dump(joblist, json_data)
    print('json created')

    # create csv and excel
    df = pd.DataFrame(joblist)
    df.to_csv('indeed_joblist.csv', index=False)
    print('data csv created')
    df.to_excel('indeed_joblist.xlsx', index=False)
    print('data excel created')


if __name__ == '__main__':
    get_all_items()
