import os
from pdf2image import convert_from_path
from datetime import datetime, timedelta, timezone
import base64
from requests import post
from PIL import Image, ImageDraw
import re
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from collections import Counter
import time

def download_pdf(url, save_path):
    response = requests.get(url)
    with open(save_path, 'wb') as file:
        file.write(response.content)

def add_border_to_image(image_path, border_color, border_width, border_style):
    # 이미지 열기
    image = Image.open(image_path)

    # 이미지에 테두리 그리기
    draw = ImageDraw.Draw(image)
    width, height = image.size
    border_rectangle = [(0, 0), (width - 1, height - 1)]
    
    for _ in range(border_width):
        draw.rectangle(border_rectangle, outline=border_color, width=border_style)

    # 테두리가 그려진 이미지를 저장
    image.save(image_path)

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as pdf_file:
        pdf_reader = PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()  # PDF 페이지의 텍스트 추출
    return text

def extract_keywords_from_text(text, num_keywords=10):
    # 텍스트를 소문자로 변환하여 단어로 분할
    words = re.findall(r'\b(?![0-9]+\b)\w+\b', text.lower())
    
    # 빈도수 계산
    word_freq = Counter(words)
    
    # 가장 빈도가 높은 단어 10개 추출
    top_keywords = [word for word, freq in word_freq.most_common(num_keywords)]
    
    return top_keywords

def generate_markdown_image(image_path, alt_text):
    with open(image_path, 'rb') as img:
        img_data = img.read()
        base64_data = base64.b64encode(img_data).decode('utf-8')
        markdown_image = f'![{alt_text}](data:image/png;base64,{base64_data})'
    return markdown_image

def post_images_to_tistory(pdf_file_name, image_data_list, stock_name, stock_code, stock_title, sentences, keywords, published):
    # 티스토리 인증 정보 및 블로그 정보 설정
    api_token = "3d2f0835183bf774c20c43961399a0fc_bec5fdfb93ca5fee68f6058d14b9dabf"
    blog_name = "money-shower"
    categoryId = "1177849"

    # 글 제목 설정
    title = f"{today} {stock_name}({stock_code}) - {stock_title}"

    # 이미지 데이터 리스트에서 첫 번째 이미지를 대표 이미지로 설정
    first_image_data = image_data_list[0]
    image_data_list[0] = '<div class="representative-image">' + first_image_data + '</div>'

    # 글 내용 설정
    content =  '안녕하세요~<br>'
    content +=  f'<b><i>오늘은 {stock_name}({stock_code})에 대한 리포트가 발행되어 내용 전달해 드리겠습니다.</i></b><br><br>'
    content += '그 전에 금융 스타트업 중에 재무 설계를 무료로 진행하는 재테크 플라이(FLY)가 있어 소개해 드리니 관심있으신 분이라면 무료 설계 받아 보시기 바랍니다.<br>'
    content += '[##_Image|kage@nNvgJ/btstwIc9kEq/N6sAAJfCK5jkhdszAxk6nk/img.png|CDM|1.3|{"originWidth":539,"originHeight":621,"style":"alignCenter","width":172,"height":198,"link":"https://bjpleaders.co.kr/od6Qotq6","isLinkNewWindow":true,"title":"재테크플라이","caption":"재테크플라이 바로가기","filename":"재테크FLY.png"}_##]'
    content += '재테크 플라이는 재테크, 재무 설계를 필요로 하는 분들에게 전문 수석 재무 설계사를 연결해 주는 금융 전문가 매칭 플랫폼 서비스입니다. 1:1 개인 맞춤 포트폴리오를 제공하며 연령별 / 기간별 / 직업별 / 목적별 맞춤형 재테크 포트폴리오를 전문가가 직접 설계해 드리는 점이 재테크 플라이의 강점입니다. 상담을 통해 수석 재무 설계사가 무료로 재무 설계를 제공하고, 재테크 실행 및 성공을 위한 포트폴리오를 제공해 줍니다. 사용자는 상담받은 포트폴리오로 효율적인 재테크를 시작하실 수 있습니다.'
    content += "<blockquote data-ke-style='style1'><span style='font-family: \"Noto Serif KR\";'>이런 분들에게 추천 합니다.</span></blockquote><br>"
    content += '<p style="text-align: center;" data-ke-size="size16"><span style="font-family: \'Noto Serif KR\';">*&nbsp;사회&nbsp;초년생&nbsp;첫&nbsp;직장인&nbsp;급여&nbsp;재테크에&nbsp;고민이신&nbsp;분 <br />*&nbsp;재테크가&nbsp;꼭&nbsp;필요하다고&nbsp;느끼지만&nbsp;경제&nbsp;지식이&nbsp;부족한&nbsp;분 <br />*&nbsp;재테크에&nbsp;관심은&nbsp;많지만&nbsp;시간적&nbsp;여유가&nbsp;없는&nbsp;분 <br />*&nbsp;무분별한&nbsp;소비습관으로&nbsp;재테크로&nbsp;고민하시는&nbsp;분</span></p><br>'
    content += '<br><p style="text-align: center;" data-ke-size="size16"><u><span style="background-color: #ffffff; color: #444444; text-align: center;">* 해당 포스팅은 업체로부터 소정의 수수료를 받고 작성된 글입니다.</span></u></p><br><br>'

    content += "<br>".join(image_data_list)

    tag = ",".join([stock_name, stock_code,'주식리포트','종목리포트'])

    # 티스토리 API를 이용하여 글 작성 및 포스팅
    api_url = f'https://www.tistory.com/apis/post/write'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/xml',
    }

    data = {
        'access_token': api_token,
        'output': 'json',
        'blogName': blog_name,
        'title': title,
        'category': categoryId,
        'content': content,
        'visibility': 2,
        'published': published,
        'tag': tag
    }

    response = post(api_url, data=data)

    if response.status_code == 200:
        response_data = response.json()
        print("포스팅 예약이 완료되었습니다.")
        print(f"포스트 ID: {response_data['tistory']['postId']}")
    else:
        print("포스팅이 실패하였습니다. 상태 코드:", response.status_code)
        print(response.text)  # Print the response text (XML document)

# 예약 포스팅 간격 설정 (2시간)
interval = timedelta(hours=2)
scheduled_time = datetime.now()

while True:
    base_url = 'https://finance.naver.com/research/'
    list_url = base_url + "company_list.naver"
    response = requests.get(list_url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    
    # <a> 태그에서 링크 주소 추출
    pdf_links = soup.find_all('a')
    td_tags = soup.find_all('td', style="padding-left:10")
    pdf_stock_data = []

    # Get the current date in the desired format (e.g., "23.08.29")
    today = datetime.now().strftime('%y.%m.%d')

    # Counter to keep track of processed PDFs
    pdf_count = 0
    sentences = [] 

    # Loop through the PDF links and process each one
    for link in soup.select('a[href$=".pdf"]'):
        if pdf_count < 2:  # 총 3개의 PDF를 처리하면 종료
            break
        pdf_url = link['href']
        if pdf_url.endswith('.pdf'):
            pdf_file_name = os.path.splitext(os.path.basename(pdf_url))[0]  # PDF 파일명 추출

            # PDF 파일과 관련된 주식 정보를 찾기 위해 부모 <tr> 태그를 찾음
            tr_tag = link.find_parent('tr')

            # 주식 정보를 추출하기 위해 <td> 태그를 찾음
            td_tag = tr_tag.find('td', style="padding-left:10")

            if td_tag:
                stock_link = td_tag.find('a', class_="stock_item")
                # 'a' 태그를 찾았을 때만 정보를 추출합니다.
                if stock_link:
                    stock_name = stock_link.get_text(strip=True)
                    stock_code = stock_link['href'].split('=')[1]

                    # 텍스트 정보를 추출
                    stock_title = tr_tag.find_all('td')[1].text
                    report_link = tr_tag.find('a', string="리포트원문보기")
                    if report_link:
                        stock_summary_url = base_url + report_link['href']
                        stock_summary_response = requests.get(stock_summary_url)
                        stock_summary_html = stock_summary_response.text
                        stock_summary_soup = BeautifulSoup(stock_summary_html, 'html.parser')
                        stock_summary = stock_summary_soup.find('td', class_='view_cnt')
                        div_tags = stock_summary.find_all('div')
                        sentences = [div.get_text(strip=True) for div in div_tags]

                        # 여기서 sentences 리스트를 이용하여 리포트 내용을 가져와서 활용하면 됩니다.

                    # Generate a folder path based on the current date and PDF file name
                    datetime_utc = datetime.utcnow()
                    datetime_kst = datetime_utc + timedelta(hours=9)
                    
                    # 폴더 경로 생성
                    year = str(datetime_kst.year)
                    folder_path = os.path.join(year, pdf_file_name)

                    # Check if the folder already exists
                    if os.path.exists(folder_path):
                        continue

                    # Create a directory for each PDF file
                    os.makedirs(folder_path, exist_ok=True)

                    pdf_save_path = os.path.join(folder_path, f"{pdf_file_name}.pdf")

                    # Download the PDF file
                    download_pdf(pdf_url, pdf_save_path)
                    pdf_text = extract_text_from_pdf(pdf_save_path)

                    # 주요 키워드 추출
                    keywords = extract_keywords_from_text(pdf_text, num_keywords=10)   
                    tagName = ", ".join(keywords)

                    # Convert the downloaded PDF file to images
                    images = convert_from_path(pdf_save_path, dpi=300, size=(786, 1111), fmt='png')

                    # Process and collect image data
                    image_data_list = []  # Initialize the list for image data
                    for page_num, image in enumerate(images):
                        image_path = os.path.join(folder_path, f'page_{page_num + 1}.png')
                        image.save(image_path, 'PNG')

                        # Add borders to the image with a different border style
                        add_border_to_image(image_path, border_color='red', border_width=10, border_style=2)

                        # Prepare image data for posting
                        image_file_name = f'page_{page_num + 1}.png'
                        img_alt = image_file_name.replace(',', '_')  # Replace commas with underscores in alt attribute
                        with open(image_path, 'rb') as img:
                            img_data = img.read()
                            base64_data = base64.b64encode(img_data).decode('utf-8')
                            img_tag = f'<img src="data:image/png;base64,{base64_data}" alt="{img_alt}" /><br>'
                        
                        # Add the image data to the list
                        image_data_list.append(img_tag)

                    # Call a function to post all image data to Tistory
                    published = scheduled_time.strftime('%Y-%m-%d %H:%M:%S')
                    post_images_to_tistory(pdf_file_name, image_data_list, stock_name, stock_code, stock_title, sentences, keywords, published)

                    pdf_count += 1  # 처리한 PDF 개수 증가
                    print(f"Processing and posting for {pdf_file_name} is complete.")
    
    # 예약된 포스팅 간격을 기다림
    scheduled_time += interval
    print(f"Next scheduled posting at: {published}")
    time.sleep(2 * 60 * 60)  # 2시간 대기 (단위: 초)
