import streamlit as st
import jieba
import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pyecharts.charts import WordCloud, Bar, Line, Pie, Scatter, Funnel
from pyecharts import options as opts
import streamlit.components.v1 as components

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
def generate_pyecharts_wordcloud(word_counts):
    filtered_words = [(word, count) for word, count in word_counts.items() if len(word) > 1]
    wordcloud = WordCloud()
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

# 13. 创建 Seaborn 热力图
def plot_heatmap(word_freq_df):
    plt.figure(figsize=(10, 8))
    heatmap_data = word_freq_df.pivot("词语", "词频", "词频")
    sns.heatmap(heatmap_data, annot=True, cmap="YlGnBu")
    st.pyplot()

# 14. 创建 Seaborn 箱线图
def plot_boxplot(word_freq_df):
    plt.figure(figsize=(10, 6))
    sns.boxplot(x=word_freq_df['词频'])
    plt.title("词频箱线图")
    st.pyplot()

# 主函数
def app():
    st.sidebar.title("图表选择与参数设置")
    url_input = st.text_input("请输入一个网址获取文本内容：")
    chart_type = st.sidebar.selectbox(
        '选择图表类型',
        ['词云', '条形图', '折线图', '饼图', '散点图', '面积图', '瀑布图', '热力图', '箱线图']
    )
    min_freq = st.sidebar.slider("最小词频", 1, 20, 5)
    
    if url_input:
        text = get_text_from_url(url_input)
        if text:
            stopwords = load_stopwords("stopwords.txt")
            cleaned_text = clean_html_tags(text)
            cleaned_text = remove_non_chinese(cleaned_text)
            word_count = calculate_word_frequency(cleaned_text, stopwords)
            word_freq_df = pd.DataFrame(word_count.items(), columns=['词语', '词频'])
            word_freq_df = word_freq_df[word_freq_df['词频'] >= min_freq]
            word_freq_df = word_freq_df.sort_values(by='词频', ascending=False)
            
            if chart_type == "词云":
                chart = generate_pyecharts_wordcloud(word_count)
                components.html(chart)
            elif chart_type == "条形图":
                chart = plot_bar_chart(word_freq_df)
                components.html(chart)
            elif chart_type == "折线图":
                chart = plot_line_chart(word_freq_df)
                components.html(chart)
            elif chart_type == "饼图":
                chart = plot_pie_chart(word_freq_df)
                components.html(chart)
            elif chart_type == "散点图":
                chart = plot_scatter_chart(word_freq_df)
                components.html(chart)
            elif chart_type == "面积图":
                chart = plot_area_chart(word_freq_df)
                components.html(chart)
            elif chart_type == "瀑布图":
                chart = plot_waterfall_chart(word_freq_df)
                components.html(chart)
            elif chart_type == "热力图":
                plot_heatmap(word_freq_df)
            elif chart_type == "箱线图":
                plot_boxplot(word_freq_df)

# 运行 Streamlit 应用
if __name__ == "__main__":
    app()
