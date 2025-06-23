import streamlit as st
import pandas as pd
import os

# 设置页面标题
st.title("Schwab RSU 数据分析工具")
# 提示用户输入美元汇率，缺省为7.1884
st.subheader("美元汇率")
default_exchange_rate = 7.1884
exchange_rate = st.number_input("请输入美元汇率（缺省为7.1884）", min_value=0.00000, value=default_exchange_rate, step=0.00001, format="%.5f")
# st.subheader("股票交易所得税率")
# tax_rate = 0.2 
# tax_exchange_rate = st.number_input("请输入股票盈利所得税率（缺省为0.2）", min_value=0.00000, value=tax_rate, step=0.00001, format="%.2f")
# st.subheader("股息所得税率")
# tax_intreast_rate =  0.1 
# tax_intreast_rate = st.number_input("请输入股息所得（缺省为0.1）", min_value=0.00000, value=tax_intreast_rate, step=0.00001, format="%.2f")
# 提示用户上传 CSV 文件
st.subheader("上传从Schwab导出的Stock年度CSV 文件")
st.write("请选择CSV 文件")
uploaded_file = st.file_uploader("选择 CSV 文件", type=["csv"], accept_multiple_files=False)

non_negtive_rsu_profit_summary = 0.0
non_negtive_espp_profit_summary = 0.0
include_negative_rsu_profit_summary = 0.0
include_negative_espp_profit_summary = 0.0
divedend_summary = 0.0


# 如果文件已上传
if uploaded_file is not None:
    # 读取 CSV 文件
    try:
        df = pd.read_csv(uploaded_file)
        st.success("文件上传成功！")



        st.write("原始数据预览：")
        st.dataframe(df)

        # 获取所有列名
        columns = df.columns.tolist()

        # ---------------------RSU部分---------------------
        # 提示用户选择需要过滤的列
        st.subheader("选择RSU数据进行过滤")
        default_index = columns.index('Type') if 'Type' in columns else 0
        selected_column = st.selectbox("选择要过滤的列(缺省为'Type')", options=columns, index=default_index)
        # 获取选中列的唯一值
        unique_values = df[selected_column].dropna().unique().tolist()

        # 允许用户选择多个值进行过滤
        selected_values = st.multiselect(
            f"选择 {selected_column} 列的过滤值,可以选择多个值,缺省为‘RS’",
            options=unique_values,
            default=['RS']  # 默认不选中任何值
        )

        # 如果用户选择了值，则进行过滤
        if selected_values:
            filtered_df = df[df[selected_column].isin(selected_values)]
            st.write(f"过滤后的数据（基于 {selected_column} = {selected_values}）：")
            st.dataframe(filtered_df)
            # 显示过滤后的数据统计信息
            st.write(f"过滤后数据行数：{len(filtered_df)}")
        else:
            st.warning("请至少选择一个过滤值！")
        
        # 计算rsu的盈利值
        # 给出提示，选择销售价格的列和成本价格的列，以及销售股数的列
        st.subheader("计算盈利值")
        default_index = columns.index('SalePrice') if 'SalePrice' in columns else 0
        sales_price_column = st.selectbox("选择销售价格的列, 缺省为'SalePrice'", options=columns, index=default_index)
        default_index = columns.index('VestFairMarketValue') if 'VestFairMarketValue' in columns else 0
        cost_price_column = st.selectbox("VestFairMarketValue, '缺省为VestFairMarketValue‘", options=columns, index=default_index)
        default_index = columns.index('Shares') if 'Shares' in columns else 0
        shares_column = st.selectbox("选择销售股数的列, 缺省为'Shares", options=columns, index=default_index) 
        if sales_price_column and cost_price_column and shares_column:
            # st.write("原始列：")
            # st.dataframe(filtered_df[[sales_price_column, cost_price_column, shares_column]])
            # st.write(f"过滤后数据行数：{len(filtered_df)}")
            # 计算盈利值
            # 销售价格、成本价格和销售股数的列为字符串类型，去除字符串中的非数值字符，如美元符号等
            df[sales_price_column] = df[sales_price_column].replace(r'[\$,]', '', regex=True)
            df[cost_price_column] = df[cost_price_column].replace(r'[\$,]', '', regex=True)
            df[shares_column] = df[shares_column].replace(r'[\$,]', '', regex=True)
            # st.write("去除$后的值：")
            # st.dataframe(filtered_df[[sales_price_column, cost_price_column, shares_column]])
            # st.write(f"过滤后数据行数：{len(filtered_df)}")
            # # 将销售价格、成本价格和销售股数的列转换为数值类型
            df[sales_price_column] = pd.to_numeric(df[sales_price_column], errors='coerce')
            df[cost_price_column] = pd.to_numeric(df[cost_price_column], errors='coerce')
            df[shares_column] = pd.to_numeric(df[shares_column], errors='coerce')
            # 计算盈利值
            df['Profit'] = (df[sales_price_column] - df[cost_price_column]) * df[shares_column]
            # st.write("计算后的数据预览：")
            # st.dataframe(filtered_df[[sales_price_column, cost_price_column, shares_column]])
            # st.write(f"过滤后数据行数：{len(filtered_df)}")
            st.warning("盈利值统计(计入亏损交易)：")
            st.write(f"总盈利值($): {df['Profit'].sum():.2f}")
            st.write(f"总盈利值(¥): {df['Profit'].sum()*exchange_rate:.2f}")
            include_negative_rsu_profit_summary = df['Profit'].sum()
            st.warning("盈利值统计(不计入亏损交易)：")
            st.write(f"总盈利值($): {df[df['Profit'] > 0]['Profit'].sum():.2f}")
            st.write(f"总盈利值(¥): {df[df['Profit'] > 0]['Profit'].sum()*exchange_rate:.2f}")
            non_negtive_rsu_profit_summary = df[df['Profit'] > 0]['Profit'].sum()
        
        # ---------------------ESPP部分---------------------
        # 提示用户选择需要过滤的列
        st.subheader("选择ESPP数据进行过滤")
        # 允许用户选择多个值进行过滤
        selected_values = st.multiselect(
            f"选择 {selected_column} 列的过滤值,可以选择多个值,缺省为‘ESPP’",
            options=unique_values,
            default=['ESPP']  # 默认不选中任何值
        )

        # 如果用户选择了值，则进行过滤
        if selected_values:
            filtered_df = df[df[selected_column].isin(selected_values)]
            st.write(f"过滤后的数据（基于 {selected_column} = {selected_values}）：")
            st.dataframe(filtered_df)
            # 显示过滤后的数据统计信息
            st.write(f"过滤后数据行数：{len(filtered_df)}")
        else:
            st.warning("请至少选择一个过滤值！")
        
        # 计算rsu的盈利值
        # 给出提示，选择销售价格的列和成本价格的列，以及销售股数的列
        st.subheader("计算盈利值")
        default_index = columns.index('SalePrice') if 'SalePrice' in columns else 0
        sales_price_column = st.selectbox("选择销ESPP售价格的列, 缺省为'SalePrice'", options=columns, index=default_index)
        default_index = columns.index('PurchaseFairMarketValue') if 'PurchaseFairMarketValue' in columns else 0
        cost_price_column = st.selectbox("ESPP PurchaseFairMarketValue, '缺省为PurchaseFairMarketValue‘", options=columns, index=default_index)
        default_index = columns.index('Shares') if 'Shares' in columns else 0
        shares_column = st.selectbox("选择销售ESPP股数的列, 缺省为'Shares", options=columns, index=default_index) 
        if sales_price_column and cost_price_column and shares_column:
            # st.write("原始列：")
            # st.dataframe(filtered_df[[sales_price_column, cost_price_column, shares_column]])
            # st.write(f"过滤后数据行数：{len(filtered_df)}")
            # 计算盈利值
            # 销售价格、成本价格和销售股数的列为字符串类型，去除字符串中的非数值字符，如美元符号等
            df[sales_price_column] = df[sales_price_column].replace(r'[\$,]', '', regex=True)
            df[cost_price_column] = df[cost_price_column].replace(r'[\$,]', '', regex=True)
            df[shares_column] = df[shares_column].replace(r'[\$,]', '', regex=True)
            # st.write("去除$后的值：")
            # st.dataframe(filtered_df[[sales_price_column, cost_price_column, shares_column]])
            # st.write(f"过滤后数据行数：{len(filtered_df)}")
            # # 将销售价格、成本价格和销售股数的列转换为数值类型
            df[sales_price_column] = pd.to_numeric(df[sales_price_column], errors='coerce')
            df[cost_price_column] = pd.to_numeric(df[cost_price_column], errors='coerce')
            df[shares_column] = pd.to_numeric(df[shares_column], errors='coerce')
            # 计算盈利值
            df['Profit'] = (df[sales_price_column] - df[cost_price_column]) * df[shares_column]
            # st.write("计算后的数据预览：")
            # st.dataframe(filtered_df[[sales_price_column, cost_price_column, shares_column]])
            # st.write(f"过滤后数据行数：{len(filtered_df)}")
            st.warning("盈利值统计(计入亏损交易)：")
            st.write(f"总盈利值($): {df['Profit'].sum():.2f}")
            st.write(f"总盈利值(¥): {df['Profit'].sum()*exchange_rate:.2f}")
            include_negative_espp_profit_summary = df['Profit'].sum()
            st.warning("盈利值统计(不计入亏损交易)：")
            st.write(f"总盈利值($): {df[df['Profit'] > 0]['Profit'].sum():.2f}")
            st.write(f"总盈利值(¥): {df[df['Profit'] > 0]['Profit'].sum()*exchange_rate:.2f}")
            non_negtive_espp_profit_summary = df[df['Profit'] > 0]['Profit'].sum()
        
# ---------------------股息部分---------------------
        # 提示用户选择需要过滤的列
        st.subheader("选择Dividen所在列数据进行过滤")
        default_index = columns.index('Action') if 'Action' in columns else 0
        selected_column = st.selectbox("选择要过滤的列(缺省为'Action)", options=columns, index=default_index)

        unique_values = df[selected_column].dropna().unique().tolist()
        # 允许用户选择多个值进行过滤
        selected_values = st.multiselect(
            f"选择 {selected_column} 列的过滤值,可以选择多个值,缺省为‘Dividend’",
            options=unique_values,
            default=['Dividend']  # 默认不选中任何值
        )

        # 如果用户选择了值，则进行过滤
        if selected_values:
            filtered_df = df[df[selected_column].isin(selected_values)]
            st.write(f"过滤后的数据（基于 {selected_column} = {selected_values}）：")
            st.dataframe(filtered_df)
            # 显示过滤后的数据统计信息
            st.write(f"过滤后数据行数：{len(filtered_df)}")
        else:
            st.warning("请至少选择一个过滤值！")
        
        # 计算的盈利值
        st.subheader("计算Dividen总值")
        default_index = columns.index('Amount') if 'Amount' in columns else 0
        sales_price_column = st.selectbox("选择销Dividend值所在列, 缺省为'Amount'", options=columns, index=default_index)
        if sales_price_column:
            filtered_df[sales_price_column] = filtered_df[sales_price_column].replace(r'[\$,]', '', regex=True)
            filtered_df[sales_price_column] = pd.to_numeric(filtered_df[sales_price_column], errors='coerce')
            # 计算盈利值
            filtered_df['Profit'] = filtered_df[sales_price_column]
            st.write(f"总股息值($): {filtered_df['Profit'].sum():.2f}")
            st.write(f"总股息值(¥): {filtered_df['Profit'].sum()*exchange_rate:.2f}")
            divedend_summary = filtered_df['Profit'].sum()
        else:
            st.warning("请确保选择了正确的列！")

    except Exception as e:
        st.error(f"读取文件时发生错误：{str(e)}")
else:
    st.info("请上传一个 CSV 文件以开始过滤。")

# 写入分隔符
st.markdown("---")
st.info("计算美元数据如下：")
st.write(f"计入亏损交易的股票盈利值：RSU {include_negative_rsu_profit_summary:.2f} (USD) + ESPP {include_negative_espp_profit_summary:.2f} (USD) = {include_negative_rsu_profit_summary + include_negative_espp_profit_summary:.2f} (USD)")
st.write(f"不计入亏损交易的股票盈利值：RSU {non_negtive_rsu_profit_summary:.2f} (USD) + ESPP {non_negtive_espp_profit_summary:.2f} (USD) = {non_negtive_rsu_profit_summary + non_negtive_espp_profit_summary:.2f} (USD)")
st.write(f"股息所得：{divedend_summary:.2f} (USD)")
st.markdown("---")
st.info("计算人民币数据如下：")
st.write(f"计入亏损交易的股票盈利值：RSU  {include_negative_rsu_profit_summary * exchange_rate:.2f} (CNY) + {include_negative_espp_profit_summary * exchange_rate:.2f} (CNY) = {(include_negative_rsu_profit_summary + include_negative_espp_profit_summary) * exchange_rate:.2f} (CNY)")
st.write(f"不计入亏损交易的股票盈利值：RSU {non_negtive_rsu_profit_summary * exchange_rate:.2f} (CNY) + ESPP {non_negtive_espp_profit_summary * exchange_rate:.2f} (CNY) = {(non_negtive_rsu_profit_summary + non_negtive_espp_profit_summary) * exchange_rate:.2f} (CNY)")
st.write(f"股息所得：{divedend_summary * exchange_rate:.2f} (CNY)")
st.markdown("---")