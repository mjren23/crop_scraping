import requests
import json
from bs4 import BeautifulSoup

session = requests.Session()


page = session.get("https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx")
print(page.headers)
print(page.request.headers)
print(page.cookies)


headers_json = {'Content-Type': "application/json; charset=utf-8"}
headers_url = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:96.0) Gecko/20100101 Firefox/96.0",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
               "Accept-Language": "en-US,en;q=0.5",
               "Accept-Encoding": "gzip, deflate, br",
               "Content-Type": "application/x-www-form-urlencoded"}
data_get_session = json.dumps({
    "value1": ["2000-01", "2000", "CROPPING PATTERN", "6b", "ALL SOCIAL GROUPS", "4", "ALL CROPS", "0", "DELHI", "26a",
               "NORTH", "1", "CIVIL LINES", "1"]})


req_get_session = session.post("https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx/GetSession",
                               headers=headers_json,
                               data=data_get_session)
print(req_get_session.request.headers)

print(req_get_session.status_code)
print(req_get_session.text)
session_id = req_get_session.cookies.get("ASP.NET_SessionId")
cookies = {"ASP.NET_SessionId": session_id}
print(session_id)

home_html = page.text
home_soup = BeautifulSoup(home_html, 'html.parser')

# parse viewstate
print(home_soup.select("#__VIEWSTATE"))
view_state = None if home_soup.select("#__VIEWSTATE") is None else home_soup.select("#__VIEWSTATE")[0]['value']
view_state_gen = None if home_soup.select("#__VIEWSTATEGENERATOR") is None else \
    home_soup.select("#__VIEWSTATEGENERATOR")[0]['value']

if view_state_gen is None or view_state is None:
    print("bad view state get")
    exit()

form_data_col = {'__VIEWSTATE': view_state,
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

taluk_char = session.post("https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx",
                          data=form_data_col, headers=headers_url)

print(taluk_char.request.body)
print(taluk_char.request.headers)

tktable_get = session.get("https://agcensus.dacnet.nic.in/TL/tktabledisplay6b.aspx", headers=headers_url)
print("status code: " + str(tktable_get.status_code))
print("cookies: " + str(tktable_get.request.headers))
# print(tktable_get.text)
exit()

tk_data = {"__EVENTTARGET": "ReportViewer1$_ctl9$Reserved_AsyncLoadTarget",
           '__EVENTARGUMENT': "",
           "__VIEWSTATE": view_state,
           '__VIEWSTATEGENERATOR': view_state_gen,
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

taluk_char = requests.post("https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx",
                           data=form_data_col, headers=headers_url)
print(taluk_char.status_code)
print(taluk_char.text)
# print(taluk_char.text)

tktable_get = requests.get("https://agcensus.dacnet.nic.in/TL/tktabledisplay6b.aspx", headers=headers_url)
print("status code: " + str(tktable_get.status_code))
print(tktable_get.text)

event_validation = home_soup.select("#__EVENTVALIDATION")[0]['value']

req_display_table = requests.post("https://agcensus.dacnet.nic.in/TL/tktabledisplay6b.aspx",
                                  data=tk_data, headers=headers_url)

# _ctl0%3AContentPlaceHolder1%3AddlYear=2000&_ctl0%3AContentPlaceHolder1%3AddlState=2a&_ctl0%3AContentPlaceHolder1%3AddlDistrict=15&_ctl0%3AContentPlaceHolder1%3AddlTehsil=3&_ctl0%3AContentPlaceHolder1%3AddlTables=6b&_ctl0%3AContentPlaceHolder1%3AddlSocialGroup=4&_ctl0%3AContentPlaceHolder1%3AddlCrop=0&_ctl0%3AContentPlaceHolder1%3AbtnSubmit=Submit

# # data = json.dumps({'value':'1','Text':'ANDAMANS','CallFor':'District','stcdu':'23a','year':'2000'})
# data_arr = json.dumps({"value1":["2000-01","2000","CROPPING PATTERN","6b","ALL SOCIAL GROUPS","4","ALL CROPS","0","DELHI","26a","NORTH","1","CIVIL LINES","1"]})
# # r2 = requests.post("https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx/getTehsil", headers=h,
# #                    data=data)
# r3 = requests.post("https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx/GetSession", headers=h,
#                    data=data_arr)
# print(r3.status_code)
# # get = requests.get("https://agcensus.dacnet.nic.in/TL/tktabledisplay6b.aspx")
#
# display_table = requests.post("https://agcensus.dacnet.nic.in/TL/tktabledisplay6b.aspx", headers=h,
#                               data=data_arr)
#
# print(display_table.status_code)
# print(display_table.text)


# print(get.status_code)
# print(get.text)
# print(r3.status_code)
# print(r3.text)
# print(r2.status_code)
# print(r2.json())
