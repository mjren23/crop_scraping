# Notes on scraping 
##### URL: https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx

## Using the script 

Right now, get_table.py prints out the HTML of the table for a specific combination of form values (Delhi, North, All Crops or something like that).

draft.py contains code from the development of get_table. The HTML files are example outputs from different calls to the website. 
## Networking calls
- getTehsil: POST
  - information about what tehsils match
  - full URL: https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx/getTehsil 
  - example payload: {'value':'15','Text':'DIBRUGARH','CallFor':'District','stcdu':'2a','year':'2000'} 
- GetSession: POST 
  - send information about form data 
  - full URL: https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx/GetSession
  - example payload: {"value1":["2000-01","2000","CROPPING PATTERN","6b","ALL SOCIAL GROUPS","4","ALL CROPS","0","ASSAM","2a","DIBRUGARH","15","CHABUA","3"]}
- TalukCharacteristics: POST (HTML document initiated)
  - send ViewState information 
  - full URL: https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx 
  - example payload: __VIEWSTATE=r3or53TSk...NXMtAP4YwYU6Hny90kQDCP4iKSgMtcfVOpnw%3D%3D&__VIEWSTATEGENERATOR=4ABB07E7&__VIEWSTATEENCRYPTED=&_ctl0%3AContentPlaceHolder1%3AddlYear=2000&_ctl0%3AContentPlaceHolder1%3AddlState=2a&_ctl0%3AContentPlaceHolder1%3AddlDistrict=15&_ctl0%3AContentPlaceHolder1%3AddlTehsil=3&_ctl0%3AContentPlaceHolder1%3AddlTables=6b&_ctl0%3AContentPlaceHolder1%3AddlSocialGroup=4&_ctl0%3AContentPlaceHolder1%3AddlCrop=0&_ctl0%3AContentPlaceHolder1%3AbtnSubmit=Submit
- tktabledisplay6b.aspx: POST 
  - get table information as requested
  - full URL: https://agcensus.dacnet.nic.in/TL/tktabledisplay6b.aspx
  - example payload: __EVENTTARGET=ReportViewer1%24_ctl9%24Reserved_AsyncLoadTarget&__EVENTARGUMENT=&__VIEWSTATE=2MOQp4jpyfsh5QBzKKTC8hPudXod09%...8wY6dVXFhufBvk3bA%3D%3D&ReportViewer1%3A_ctl3%3A_ctl0=&ReportViewer1%3A_ctl3%3A_ctl1=&ReportViewer1%3A_ctl10=ltr&ReportViewer1%3A_ctl11=standards&ReportViewer1%3AAsyncWait%3AHiddenCancelField=False&ReportViewer1%3AToggleParam%3Astore=&ReportViewer1%3AToggleParam%3Acollapse=false&ReportViewer1%3A_ctl8%3AClientClickedId=&ReportViewer1%3A_ctl7%3Astore=&ReportViewer1%3A_ctl7%3Acollapse=false&ReportViewer1%3A_ctl9%3AVisibilityState%3A_ctl0=None&ReportViewer1%3A_ctl9%3AScrollPosition=&ReportViewer1%3A_ctl9%3AReportControl%3A_ctl2=&ReportViewer1%3A_ctl9%3AReportControl%3A_ctl3=&ReportViewer1%3A_ctl9%3AReportControl%3A_ctl4=100

## Miscellaneous 
- Use requests.Session() to pass required cookies between calls 
- Certain calls need the ViewState and/or EventValidation to work properly 
- There are two calls to tktabledisplay6b - first one is a GET, needed for the new ViewState values and the EventValidation value
- Use Mozilla Firefox over Google Chrome - its dev tools are nicer (specifically, it doesn't delete the response information of a networking call after navigation away from the page)


