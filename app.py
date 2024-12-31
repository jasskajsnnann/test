import matplotlib.pyplot as plt
import streamlit as st
import jieba
import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
import pandas as pd
from pyecharts.charts import WordCloud, Bar, Line, Pie, Scatter, Funnel
from pyecharts import options as opts
import streamlit.components.v1 as components
from PIL import Image
import numpy as np

# 1. 获取网页内容
def get_text_from_url(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        all_text = ' '.join([element.get_text() for element in soup.find_all(['p', 'div', 'span', 'h1', 'h2', 'li', 'a'])])
        return all_text
    except Exception as error:
        st.error(f"网页获取失败: {error}")
        return ""

# 2. 加载停用词文件
def load_stopwords(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        stopwords = {line.strip() for line in file}
    return stopwords

# 3. 清理HTML标签
def clean_html_tags(text):
    return re.sub(r'<.*?>', '', text)

# 4. 清除标点符号和空白字符
def remove_non_chinese(text):
    return re.sub(r'[^\w\u4e00-\u9fa5]+', '', text)

# 5. 进行分词和词频统计，并去除停用词
def calculate_word_frequency(text, stopwords):
    words = jieba.cut(text)
    words_list = [word for word in words if word not in stopwords and len(word) > 1]
    word_count = Counter(words_list)
    return word_count

# 6. 生成 PyeCharts 词云
def generate_pyecharts_wordcloud(word_counts, mask_image=None):
    filtered_words = [(word, count) for word, count in word_counts.items() if len(word) > 1]
    wordcloud = WordCloud()
    
    # 如果提供了自定义的掩模图像
    if mask_image:
        wordcloud.add("", filtered_words, word_size_range=[20, 100], shape=mask_image)
    else:
        wordcloud.add("", filtered_words, word_size_range=[20, 100])
        
    wordcloud.set_global_opts(title_opts=opts.TitleOpts(title="词云"))
    return wordcloud.render_embed()

# 7. 创建词频柱状图
def plot_bar_chart(word_freq_df):
    bar = Bar()
    bar.add_xaxis(word_freq_df['词语'].tolist())
    bar.add_yaxis("词频", word_freq_df['词频'].tolist())
    bar.set_global_opts(title_opts=opts.TitleOpts(title="词频柱状图"))
    return bar.render_embed()

# 8. 绘制词频折线图
def plot_line_chart(word_freq_df):
    line = Line()
    line.add_xaxis(word_freq_df['词语'].tolist())
    line.add_yaxis("词频", word_freq_df['词频'].tolist())
    line.set_global_opts(title_opts=opts.TitleOpts(title="词频折线图"))
    return line.render_embed()

# 9. 绘制词频饼图
def plot_pie_chart(word_freq_df):
    pie = Pie()
    pie.add("", [list(z) for z in zip(word_freq_df['词语'].tolist(), word_freq_df['词频'].tolist())])
    pie.set_global_opts(title_opts=opts.TitleOpts(title="词频饼图"))
    return pie.render_embed()

# 10. 创建词频散点图
def plot_scatter_chart(word_freq_df):
    scatter = Scatter()
    scatter.add_xaxis(word_freq_df['词语'].tolist())
    scatter.add_yaxis("词频", word_freq_df['词频'].tolist())
    scatter.set_global_opts(title_opts=opts.TitleOpts(title="词频散点图"))
    return scatter.render_embed()

# 11. 创建词频面积图
def plot_area_chart(word_freq_df):
    line = Line()
    word_freq_df_sorted = word_freq_df.sort_values(by='词语')
    line.add_xaxis(word_freq_df_sorted['词语'].tolist())
    line.add_yaxis("词频", word_freq_df_sorted['词频'].tolist(), areastyle_opts=opts.AreaStyleOpts(opacity=0.5))
    line.set_global_opts(
        title_opts=opts.TitleOpts(title="词频面积图"),
        xaxis_opts=opts.AxisOpts(type_="category"),  # 设置 x 轴为类别轴
        yaxis_opts=opts.AxisOpts(type_="value"),     # 设置 y 轴为数值轴
    )
    return line.render_embed()

# 12. 创建词频瀑布图
def plot_waterfall_chart(word_freq_df):
    funnel = Funnel()
    data = [list(z) for z in zip(word_freq_df['词语'].tolist(), word_freq_df['词频'].tolist())]
    funnel.add("", data)
    funnel.set_global_opts(
        title_opts=opts.TitleOpts(title="词频瀑布图"),
        yaxis_opts=opts.AxisOpts(type_="category", position="right")  # 设置 y 轴为类别轴，位于右侧
    )
    return funnel.render_embed()

# 主函数
def app():
    st.sidebar.title("图表选择与参数设置")
    url_input = st.text_input("请输入一个网址获取文本内容：")
    chart_type = st.sidebar.selectbox(
        '选择图表类型',
        ['词云', '条形图', '折线图', '饼图', '散点图', '面积图', '瀑布图']
    )
    min_freq = st.sidebar.slider("设置最小词频", 30, 200, 10)
    
    # 文件上传部分
    mask_file = st.sidebar.file_uploader("上传词云掩模图片 (PNG 格式)", type=["png"])
    stopwords_file = "stopwords.txt"  # 停用词文件路径
    stopwords = load_stopwords(stopwords_file)

    # 处理掩模图像
mask_image = None
if mask_file:
    try:
        # 确保上传的是 PNG 格式的图片
        image = Image.open(mask_file)
        if image.format != 'PNG':
            st.error("请上传 PNG 格式的图片文件作为掩模图像。")
        else:
            mask_image = np.array(image.convert("RGBA"))  # 转换为RGBA格式
    except Exception as e:
        st.error(f"图像处理失败: {e}")

# 确保掩模图像存在时才传递
if mask_image:
    chart = generate_pyecharts_wordcloud(filtered_word_counts, mask_image)
else:
    chart = generate_pyecharts_wordcloud(filtered_word_counts)


    if url_input:
        text = get_text_from_url(url_input)
        if text:
            clean_text = clean_html_tags(text)
            clean_text = remove_non_chinese(clean_text)
            word_counts = calculate_word_frequency(clean_text, stopwords)
            filtered_word_counts = {word: count for word, count in word_counts.items() if count >= min_freq}
            word_freq_df = pd.DataFrame(list(filtered_word_counts.items()), columns=["词语", "词频"]).sort_values(by="词频", ascending=False).reset_index(drop=True)

            # 显示词频排名前20的词汇
            st.subheader("词频排名前20的词汇：")
            st.dataframe(word_freq_df.head(20))

            # 根据用户选择的图表类型生成图表
            if chart_type == '词云':
                chart = generate_pyecharts_wordcloud(filtered_word_counts, mask_image)
            elif chart_type == '条形图':
                chart = plot_bar_chart(word_freq_df)
            elif chart_type == '折线图':
                chart = plot_line_chart(word_freq_df)
            elif chart_type == '饼图':
                chart = plot_pie_chart(word_freq_df)
            elif chart_type == '散点图':
                chart = plot_scatter_chart(word_freq_df)
            elif chart_type == '面积图':
                chart = plot_area_chart(word_freq_df)
            elif chart_type == '瀑布图':
                chart = plot_waterfall_chart(word_freq_df)

            # 显示选定的图表
            st.subheader(f"{chart_type}:")
            components.html(chart, height=600)
        else:
            st.error("未能从该网址获取到有效的文本内容，请检查网址是否有效。")

if __name__ == "__main__":
    app()
