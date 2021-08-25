import requests
from bs4 import BeautifulSoup
from argparse import ArgumentParser
import csv
import os.path
import re

# https://www.olx.com.pk/karachi/mobile-phones/?page=2
base_url = 'https://www.olx.com.pk'
loc = 'karachi'
category = 'mobile-phones'
current_page = 10
page = 1
till_page = 100
acc_saved = 0

parser = ArgumentParser(prog="olx_scraper")
parser.add_argument('-l', '--location', type=str)
parser.add_argument('-c', '--category', type=str)
parser.add_argument('-f', '--from_page', type=int)
parser.add_argument('-t', '--till_page', type=int)

args = parser.parse_args()

loc = args.location
category = args.category
page = args.from_page
till_page = args.till_page


def get_length(file_path):
	with open(file_path) as csvfile:
		reader = csv.reader(csvfile)
		reader_list = list(reader)
		return len(reader_list)

def append_data(file_path, n, ph, pro, city, area):
	fieldnames = ['id', 'name', 'phone', 'province', 'city', 'area']
	#the number of rows?
	next_id = get_length(file_path)
	with open(file_path, "a", newline='') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		if next_id == 0:
			writer.writeheader()
			next_id += 1
		writer.writerow({
				"id": next_id,
				"name": n,
				"phone": ph,
				"province": pro,
				"city": city,
				"area": area,
			})

def get_cleaned_add(address):
	area, city, pro = address.strip().split(',')
	return area.strip(), city.strip(), pro.strip()
		
# print(olx_soup.prettify())
print("----------------------------------\nGreet from M4N1 | pym4n1@gmail.com\n----------------------------------")
file_path = 'olx_contacts_{loc}_{category}.csv'.format(loc=loc, category=category)
if not os.path.isfile(file_path):
	with open(file_path, 'w') as create:
		print('New file created! {}'.format(file_path))

while page < till_page:
	url = base_url + '/' + loc + '/' + category + '/' + '?page=' + str(page)
	try:
		olx_r = requests.get(url)
	except:
		print('Can\'t access this url: {}\nCheck your arguments.'.format(url))
		exit(1)

	olx_soup = BeautifulSoup(olx_r.text, 'html.parser')
	for ad in olx_soup.findAll('li', {'data-aut-id': r'itemBox'}):
		itemBox = ad.a['href']
		ad_link = base_url+itemBox
		try:
			ad_r = requests.get(ad_link)
			ad_soup = BeautifulSoup(ad_r.text, 'html.parser')
			all_js = ad_soup.findAll('script', {'type': r'text/javascript'})
			for js in all_js:
				if 'window.__APP' in str(js):
					p = re.compile('formatted_value":"[+]92[0-9]*')
					s1 = re.search(p, str(js)).group()
					ph = re.search('[+][0-9]*', s1).group()



			name = ad_soup.findAll('div', {'class': '_3oOe9'})
			address = ad_soup.findAll('span', {'class': '_2FRXm'})
			area, city, pro = get_cleaned_add(address[0].text)


			try:
				n = str(name[0].text)
				append_data(file_path, n, ph, pro, city, area)

				print(n, ' > ', ph)
				print(area, city, pro)
				acc_saved += 1
			except:
				print("Error! Please close the csv file, if it's open")
		except:
			print('could\'nt get the ad link!')
	page += 1


print('-------DONE :)--------')
print(acc_saved, "accounts saved.")