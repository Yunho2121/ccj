import os
import re
import html
from urllib.parse import urlparse
from bs4 import BeautifulSoup

def load_mapping(txt_file):
    """
    탭으로 구분된 '파일명<tab>드라이브링크' 형식의 텍스트를 읽어
    {파일명: 드라이브링크} 형태의 딕셔너리를 반환.
    """
    mapping_dict = {}
    with open(txt_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # 탭(\t) 기준으로 분할
            parts = line.split("\t")
            if len(parts) == 2:
                filename, drive_link = parts
                mapping_dict[filename] = drive_link
    return mapping_dict

def replace_with_drive_links(html_file, output_file, mapping_dict):
    """
    1) html_file에서 <img src="...">, style="background-image:url(...)"를 찾아
    2) 파일명을 추출하여, mapping_dict에 있으면 드라이브 링크로 교체
    3) 수정된 결과를 output_file에 저장
    """
    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # (1) <img src> 교체
    for img in soup.find_all("img", src=True):
        old_src = img["src"]
        filename = os.path.basename(urlparse(old_src).path)
        if filename in mapping_dict:
            img["src"] = mapping_dict[filename]

    # (2) style="background-image: url(...)" 교체
    pattern = re.compile(r"(background-image\s*:\s*url$$['\"]?)([^)'\"]+)(['\"]?$$)")
    for tag in soup.find_all(style=True):
        style_str = html.unescape(tag["style"])

        def repl(m):
            prefix, old_url, suffix = m.groups()
            fname = os.path.basename(urlparse(old_url).path)
            if fname in mapping_dict:
                return f"{prefix}{mapping_dict[fname]}{suffix}"
            else:
                return m.group(0)

        new_style = pattern.sub(repl, style_str)
        tag["style"] = new_style

    # (3) 결과 저장
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(soup.prettify())

    print(f"[완료] '{output_file}'에 구글 드라이브 링크로 경로를 교체했습니다.")

if __name__ == "__main__":
    # ① 매핑파일(탭 구분) 예: mapping.txt
    mapping_file = "mapping.txt"

    # ② 수정 대상 HTML
    input_html = "index.html"

    # ③ 수정된 결과를 저장할 HTML
    output_html = "index_drive.html"

    # (A) 매핑 로드
    mapping = load_mapping(mapping_file)

    # (B) HTML 수정
    replace_with_drive_links(input_html, output_html, mapping)