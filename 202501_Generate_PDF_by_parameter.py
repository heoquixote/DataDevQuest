import os
import io
import PyPDF2  # ✅ PyPDF 사용
import tableauserverclient as TSC

# Tableau Server 정보
my_server_url = 'https://10ax.online.tableau.com/'
my_token_name = os.getenv("my_token_name")
my_token_secret = os.getenv("my_token_secret")
my_site_id = os.getenv("my_site_id")
my_workbook = "Let's Play A Game"

# 'SelectedPublisher' 매개변수 목록
publishers = [
    "Activision",
    "Electronic Arts",
    "Konami Digital Entertainment",
    "Namco Bandai Games",
    "Nintendo",
    "Sega",
    "Sony Computer Entertainment",
    "Take-Two Interactive",
    "THQ",
    "Ubisoft"
]

# Tableau 인증
tableau_auth = TSC.PersonalAccessTokenAuth(
    token_name=my_token_name,
    personal_access_token=my_token_secret,
    site_id=my_site_id
)
server = TSC.Server(my_server_url, use_server_version=True)

# PDF 저장 폴더
pdf_folder = "output"
os.makedirs(pdf_folder, exist_ok=True)

# 병합된 PDF 파일 경로
merged_pdf_path = os.path.join(pdf_folder, "merged_publisher_views.pdf")
merged_pdf_writer = PyPDF2.PdfWriter()  # ✅ PyPDF2 PdfWriter 사용

# Tableau 로그인
with server.auth.sign_in_with_personal_access_token(tableau_auth):
    print(f'[Logged in successfully to {my_server_url}]')

    # Workbook 가져오기
    req_option = TSC.RequestOptions()
    req_option.filter.add(
        TSC.Filter(
            TSC.RequestOptions.Field.Name,
            TSC.RequestOptions.Operator.Equals,
            my_workbook
        )
    )

    workbooks, pagination_item = server.workbooks.get(req_options=req_option)

    if workbooks:
        workbook = workbooks[0]
        print(f"Workbook found: {workbook.name} (ID: {workbook.id})")

        # Workbook 내 View 가져오기
        server.workbooks.populate_views(workbook)
        view = workbook.views[0]  # 첫 번째 View 사용
        print(f"Using view: {view.name} (ID: {view.id})")

        for publisher in publishers:
            print(f"Generating PDF for: {publisher}")

            # 🆕 새로운 view 객체 가져오기
            selected_view = server.views.get_by_id(view.id)

            # 🆕 필터 적용 후 PDF 변환
            pdf_req_option = TSC.PDFRequestOptions()
            pdf_req_option.vf("SelectedPublisher", publisher)  # ✅ 필터 적용

            server.views.populate_pdf(selected_view, pdf_req_option)

            # ✅ selected_view.pdf를 BytesIO 객체로 변환
            pdf_stream = io.BytesIO(selected_view.pdf)

            # ✅ PyPDF2로 PDF 읽기
            temp_pdf_reader = PyPDF2.PdfReader(pdf_stream)

            # ✅ 기존 PDF 페이지를 그대로 추가 (회전 없음)
            for page in temp_pdf_reader.pages:
                merged_pdf_writer.add_page(page)

        print("All PDFs merged successfully.")

        # 병합된 PDF 저장
        with open(merged_pdf_path, "wb") as output_pdf:
            merged_pdf_writer.write(output_pdf)

        print(f"Final merged PDF saved: {merged_pdf_path}")