import re
import math


def on_page_markdown(markdown, page, **kwargs):
    """auto calc read time based on word count"""

    # if 'read_time' in page.meta:
    #     return markdown

    text_without_images = re.sub(r'!\[.*?]\(.*?\)', '', markdown)
    text_without_html = re.sub(r'<[^>]*>', '', text_without_images)
    text_without_space = re.sub(r'\s+', ' ', text_without_html)
    text_without_chinese = re.sub(r'[\u4e00-\u9fff]', '', text_without_space)

    chinese_words = re.findall(r'[\u4e00-\u9fff]', text_without_space)
    english_words = re.findall(r'\w+', text_without_chinese)
    images = re.findall(r'!\[.*?]\(.*?\)', markdown)

    chinese_time = len(chinese_words) / 210
    english_time = len(english_words) / 140
    image_time = len(images) * 0.5

    minutes = math.ceil(chinese_time + english_time + image_time)

    if minutes == 0:
        read_time = '< 1 min'
    elif minutes == 1:
        read_time = '1 min'
    else:
        read_time = f'{minutes} min'

    page.meta['read_time'] = read_time

    return markdown
