import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()
import tableauserverclient as TSC


my_server_url = 'https://10ax.online.tableau.com/'
my_token_name = os.getenv("my_token_name")
my_token_secret = os.getenv("my_token_secret")
my_site_id = os.getenv("my_site_id")

tableau_auth = TSC.PersonalAccessTokenAuth( token_name=my_token_name
                                           ,personal_access_token=my_token_secret
                                           ,site_id=my_site_id)
server = TSC.Server(my_server_url, use_server_version=True)

with server.auth.sign_in_with_personal_access_token(tableau_auth):
    print('[Logged in successfully to {}]'.format(my_server_url))

    req_option = TSC.RequestOptions()
    req_option.filter.add(TSC.Filter(TSC.RequestOptions.Field.ContentUrl
                                    ,TSC.RequestOptions.Operator.Equals
                                    ,my_content_url))

    workbooks, pagination_item = server.workbooks.get(req_options=req_option)
    if workbooks:

        wb = workbooks[0]
        print(f"=== Workbook ===")
        print(f"Name:{wb.name}")
        print(f"luid:{wb.id}")
        print(f"URL:{wb.webpage_url}")
        print(f"View:{wb.content_url}")

        pdf_options = TSC.PDFRequestOptions(page_type='unspecified', orientation='landscape')

        server.workbooks.populate_pdf(wb, pdf_options)

        print(f'Path:{os.getcwd()}')
        with open(pdf_file_name, 'wb') as f:
            f.write(wb.pdf)
            print('[PDF Generated]')