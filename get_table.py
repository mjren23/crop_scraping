import requests
import json
from bs4 import BeautifulSoup

session = requests.Session()

# step 1: fetch html of home page, parse viewstate and set cookies
req_home = session.get("https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx")

home_html = req_home.text
home_soup = BeautifulSoup(home_html, 'html.parser')

# parse viewstate
view_state = None if home_soup.select("#__VIEWSTATE") is None else home_soup.select("#__VIEWSTATE")[0]['value']
view_state_gen = None if home_soup.select("#__VIEWSTATEGENERATOR") is None else \
    home_soup.select("#__VIEWSTATEGENERATOR")[0]['value']

if view_state_gen is None or view_state is None:
    print("unable to parse viewstate")
    exit()

# step 2: make post request to GetSession with information about form data
headers_json = {'Content-Type': "application/json; charset=utf-8"}
data_get_session = json.dumps({
    "value1": ["2000-01", "2000", "CROPPING PATTERN", "6b", "ALL SOCIAL GROUPS", "4", "ALL CROPS", "0", "DELHI", "26a",
               "NORTH", "1", "CIVIL LINES", "1"]})

req_get_session = session.post("https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx/GetSession",
                               headers=headers_json,
                               data=data_get_session)

# step 3: make post request to home page with viewstate info
headers_url = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:96.0) Gecko/20100101 Firefox/96.0",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
               "Accept-Language": "en-US,en;q=0.5",
               "Accept-Encoding": "gzip, deflate, br",
               "Content-Type": "application/x-www-form-urlencoded",
               "Connection": "keep-alive",
               }

data_post_taluk = {'__VIEWSTATE': view_state,
                   '__VIEWSTATEGENERATOR': view_state_gen,
                   '__VIEWSTATEENCRYPTED': "",
                   '_ctl0:ContentPlaceHolder1:ddlYear': '2000',
                   '_ctl0:ContentPlaceHolder1:ddlState': '26a',
                   '_ctl0:ContentPlaceHolder1:ddlDistrict': '1',
                   '_ctl0:ContentPlaceHolder1:ddlTehsil': '1',
                   '_ctl0:ContentPlaceHolder1:ddlTables': '6b',
                   '_ctl0:ContentPlaceHolder1:ddlSocialGroup': '4',
                   '_ctl0:ContentPlaceHolder1:ddlCrop': '0',
                   '_ctl0:ContentPlaceHolder1:btnSubmit': 'Submit'
                   }
print(data_post_taluk)

req_taluk_char = session.post("https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx",
                              data=data_post_taluk,
                              headers=headers_url, allow_redirects=False)
print(req_taluk_char.status_code)
print(req_taluk_char.text)

# step 4: make get request to tktabledisplay to obtain eventvalidation info
req_tk_table_get = session.get("https://agcensus.dacnet.nic.in/TL/tktabledisplay6b.aspx",
                               headers=headers_url)
print(req_tk_table_get.status_code)

tktable_get_soup = BeautifulSoup(req_tk_table_get.text, "html.parser")
event_validation = tktable_get_soup.select("#__EVENTVALIDATION")[0]['value']
new_view_state = tktable_get_soup.select("#__VIEWSTATE")[0]['value']
new_view_state_gen = tktable_get_soup.select("#__VIEWSTATEGENERATOR")[0]['value']
print("HEREHEREHERE")
print(event_validation)


# step 5: make post request to same endpoint as step 4, hopefully get back table html in response
tk_data = {"__EVENTTARGET": "ReportViewer1$_ctl9$Reserved_AsyncLoadTarget",
           '__EVENTARGUMENT': "",
           "__VIEWSTATE": new_view_state,
           '__VIEWSTATEGENERATOR': new_view_state_gen,
           '__VIEWSTATEENCRYPTED': "",
           "__EVENTVALIDATION": event_validation,
           "ReportViewer1:_ctl3:_ctl0": "",
           "ReportViewer1:_ctl3:_ctl1": "",
           "ReportViewer1:_ctl10": "ltr",
           "ReportViewer1:_ctl11": "standards",
           "ReportViewer1:AsyncWait:HiddenCancelField": "False",
           "ReportViewer1:ToggleParam:store": "",
           "ReportViewer1:ToggleParam:collapse": "false",
           "ReportViewer1:_ctl8:ClientClickedId": "",
           "ReportViewer1:_ctl7:store": "",
           "ReportViewer1:_ctl7:collapse": "false",
           "ReportViewer1:_ctl9:VisibilityState:_ctl0": "None",
           "ReportViewer1:_ctl9:ScrollPosition": "",
           "ReportViewer1:_ctl9:ReportControl:_ctl2": "",
           "ReportViewer1:_ctl9:ReportControl:_ctl3": "",
           "ReportViewer1:_ctl9:ReportControl:_ctl4": "100"
           }
req_tk_table_post = session.post("https://agcensus.dacnet.nic.in/TL/tktabledisplay6b.aspx",
                                 headers=headers_url,
                                 data=tk_data)
print(req_tk_table_post.status_code)
print(req_tk_table_post.text)
exit()
