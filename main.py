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


def get_total_pages(query, location, start):
    params = {
        'q': query,
        'l': location,
        'start': start,
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


def get_all_items(query, location, start, page):
    company_url = 'https://id.indeed.com'
    params = {
        'q': query,
        'l': location,
        'start': start,
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

        company_get_location = item.find('div', 'companyLocation')
        company_location = company_get_location.text

        try:
            company_get_salary = item.find('div', 'metadata salary-snippet-container')
            company_salary = company_get_salary.text
        except:
            company_salary = 'Gaji tidak disebutkan'

        data_dict = {
            'title': title,
            'company name': company_name,
            'company link': link,
            'company location': company_location,
            'salary': company_salary,
        }
        joblist.append(data_dict)

    # create json
    try:
        os.mkdir('json_result')
    except FileExistsError:
        pass

    # export ke json
    with open(f'json_result/{query}_in_{location}_page_{page}.json', 'w+') as json_data:
        json.dump(joblist, json_data)
    print(f'json page {page} berhasil dibuat')
    return joblist


def create_document(data_frame, file_name, page):
    try:
        os.mkdir('data_result')
    except FileExistsError:
        pass

    # export ke csv dan excel
    df = pd.DataFrame(data_frame)
    df.to_csv(f'data_result/{file_name}.csv', index=False)
    print(f'Data {file_name} di page {page} berhasil di Export ke Csv')
    df.to_excel(f'data_result/{file_name}.xlsx', index=False)
    print(f'Data {file_name} di page {page} berhasil di Export ke Excel')


def run():
    query = input('Masukan kata kunci: ')
    location = input('Masukan lokasi: ')

    counter = 0
    total = get_total_pages(query, location, counter)
    final_result = []
    for page in range(total):
        page += 1
        counter += 10
        final_result += get_all_items(query, location, counter, page)

        # formating data
        try:
            os.mkdir('reports')
        except FileExistsError:
            pass

        with open('reports/{}.json'.format(query), 'w+') as final_data:
            json.dump(final_result, final_data)

        print('Report Json berhasil dibuat\n')
        create_document(final_result, query, page)


if __name__ == '__main__':
    run()
