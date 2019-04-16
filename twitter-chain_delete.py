import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter import filedialog
import numpy as np
import warnings, shutil, sys, os, csv, time, re#, networkx

warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from bs4 import BeautifulSoup
from lxml import etree
from lxml import html

htmlparser = etree.HTMLParser()
driver = webdriver.Firefox()

class get_Login:
	global usrname, pwd
	def __init__(self):
		self.root = Tk()
		self.label = Label(self.root, text="Enter your Twitter login")
		self.label.pack(side=TOP)
		self.usrlabel = Label(self.root, text="Phone, email, or username:")
		self.usrlabel.pack()
		self.f = Entry(self.root)
		self.f.pack()
		self.pwdlabel = Label(self.root, text="Password:")
		self.pwdlabel.pack()
		self.e=Entry(self.root, show="*")
		self.e.pack()
		self.button = Button(self.root, text="Go", command=self.get_creds)
		self.button.pack()
		self.root.attributes("-topmost", True)
		self.root.mainloop()

	def get_creds(self):
		globals()["username"] = self.f.get()
		globals()["password"] = self.e.get()

		driver.get("https://twitter.com/login")
		time.sleep(2)
		username_field = driver.find_element_by_class_name("js-username-field")
		password_field = driver.find_element_by_class_name("js-password-field")

		username_field.send_keys(username)
		driver.implicitly_wait(1)

		password_field.send_keys(password)
		driver.implicitly_wait(1)

		driver.find_element_by_class_name("EdgeButtom--medium").click() #log in

		self.root.destroy()

app = get_Login()

class verification_code:
	def __init__(self):
		self.root = Tk()
		self.label = Label(self.root, text="Enter the verification code")
		self.label.pack(side=TOP)
		self.label.pack()
		self.g = Entry(self.root)
		self.g.pack()
		self.button = Button(self.root, text="Go", command=self.enter_verification)
		self.button.pack()
		self.root.mainloop()

	def enter_verification(self):
		verif_code = self.g.get()
		driver.find_element_by_name("challenge_response").send_keys(verif_code)
		driver.implicitly_wait(1)
		driver.find_element_by_xpath('//*[@id="email_challenge_submit"]').click()
		self.root.destroy()

app = verification_code()

class go_to_account:
	def __init__(self):
		self.root = Tk()
		self.label = Label(self.root, text="Enter the screenname you want to scrape followers from:")
		self.label.pack(side=TOP)
		self.label.pack()
		self.f = Label(self.root, text="@")
		self.f.pack(side="left")
		self.g = Entry(self.root)
		self.g.pack(side="left")
		self.button = Button(self.root, text="Go", command=self.enter_verification)
		self.button.pack(side="right")
		self.root.mainloop()

	def enter_verification(self):
		global TOTAL_FOLLOWERS
		screenname = self.g.get()
		driver.get(f"https://twitter.com/{screenname.strip()}/followers")
		driver.implicitly_wait(1)

		response = driver.page_source
		tree = html.fromstring(response)
		xpath = tree.xpath('//*[@id="page-container"]/div[1]/div/div[2]/div/div/div[2]/div/div/ul/li[3]/a/span[3]')
		soup = BeautifulSoup(etree.tostring(xpath[0], xml_declaration=True))
		TOTAL_FOLLOWERS = int(soup.span.attrs['data-count'])
		# driver.find_element_by_xpath('//*[@id="email_challenge_submit"]').click()

		self.root.destroy()

app = go_to_account()

class Check_names(tk.Tk):
	def __init__(self, *args, **kwargs):
		global TOTAL_FOLLOWERS
		############################################
		############Initialize the GUI#############
		###########################################
		tk.Tk.__init__(self, *args, **kwargs)

		progressvar = IntVar()
		progressvar.set(0)
		self.progress = ttk.Progressbar(self, orient="horizontal", variable=progressvar, length=200, mode="determinate")
		self.progress.pack()

		self.bytes = 0.
		self.maxbytes = TOTAL_FOLLOWERS
		self.progressvar=0
		self.progress["maximum"] = self.maxbytes
		self.label = Label(self, text="Starting up...")
		self.label.pack()
		self.update()
		############################################

		def twitter_login(self):#name_search(self):
			global TOTAL_FOLLOWERS
			#############################
			#some stuff got deleted here#
			#############################
			screen = 1
			last_height = driver.execute_script("return document.body.scrollHeight")
			screennames = []
			with open('followers.csv', mode='w') as csv_file:
				csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
				while True:
					print(screen)
					response = driver.page_source
					tree = html.fromstring(response)
					for prof in np.arange(6)+1:
						xpath = tree.xpath("/html/body/div[2]/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div[2]/div[2]/div["+str(screen)+"]/div["+str(prof)+"]/div/div")
						soup = BeautifulSoup(etree.tostring(xpath[0], xml_declaration=True))
						usr_id = soup.div['data-user-id']
						screenname = soup.div['data-screen-name']
						# except IndexError:
						# 	usr_id = ""
						print(screenname, usr_id)
						screennames.append([screenname, usr_id])
						csv_writer.writerow([usr_id])
						profs_so_far = int(progressvar.get())
						progressvar.set(progressvar.get()+1)
						self.label.configure(text = "{} of {} ({:.3%}): {}".format(profs_so_far, TOTAL_FOLLOWERS, profs_so_far/TOTAL_FOLLOWERS, screenname)) #update the text in self.label
						self.update()
					driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
					progressvar.set(len(screennames))
					self.update()
					self.lift()
					time.sleep(2)
					wait = WebDriverWait(driver, 100)
					men_menu = wait.until(ec.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div[2]/div[2]/div["+str(screen)+"]/div[1]/div/div/div/div[2]/span/a")))
					new_height = driver.execute_script("return document.body.scrollHeight")
					if new_height == last_height: break
					else: last_height = new_height
					screen += 1
					continue
							# self.label.configure(text = "Page "+pagenum+" of 67: Checking "+personname) #update the text in self.label
							# progressvar.set(progressvar.get()+1)
							# self.update()
							# self.lift()

			# self.label.configure(text = "Done!") #update the text in self.label
			# progressvar.set(self.maxbytes)
			# self.update()

			self.destroy()

		twitter_login(self)
		self.mainloop()


app = Check_names()
# app.mainloop()
print(globals()["names"])
