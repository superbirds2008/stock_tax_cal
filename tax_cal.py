import streamlit as st
import pandas as pd
import os
from version import version

# 设置页面标题
st.title(f"Schwab Stock Equity Award\n 数据分析工具 V-{version}")
st.info(
'''
本工具用于分析Schwab导出的RSU和ESPP数据，计算盈利值和税务信息 \n
请上传从Schwab导出的Stock年度CSV文件，并根据需要进行数据过滤和计算 \n
注意：本工具仅供参考，具体税务信息请咨询专业人士 \n
导出方法：\n
1. 登录Schwab账户，进入“Transaction History” \n
2. 在页面左侧选择“Equity Awards” \n
3. Data Range选择“Previous Year” \n
4. 点击"Search"按钮 \n
5. 在页面右上角选择“Export” \n
6. 选择“CSV”格式导出 \n
7. 下载CSV文件并上传到本工具 \n
8. 设置美元汇率（默认7.1884）\n
9. 选择RSU、ESPP以及Dividend数据进行过滤，除非有变化，本工具已经设置好相应的字段和过滤关键字 \n
'''
)
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

profit_summary = {
    "RSU": {"non_negative": 0.0, "include_negative": 0.0},
    "ESPP": {"non_negative": 0.0, "include_negative": 0.0},
    "Dividend": {"total": 0.0}
}


# 如果文件已上传
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("文件上传成功！")
        st.write("原始数据预览：")
        st.dataframe(df)
        columns = df.columns.tolist()

        # 定义配置字典
        configs = {
            "RSU": {
                "filter_column": "Type",
                "filter_default": ["RS"],
                "cost_column": "VestFairMarketValue",
                "sale_column": "SalePrice",
                "shares_column": "Shares",
                "profit_func": lambda fdf, sale, cost, shares: (fdf[sale] - fdf[cost]) * fdf[shares],
                "profit_label": "盈利值"
            },
            "ESPP": {
                "filter_column": "Type",
                "filter_default": ["ESPP"],
                "cost_column": "PurchaseFairMarketValue",
                "sale_column": "SalePrice",
                "shares_column": "Shares",
                "profit_func": lambda fdf, sale, cost, shares: (fdf[sale] - fdf[cost]) * fdf[shares],
                "profit_label": "盈利值"
            },
            "Dividend": {
                "filter_column": "Action",
                "filter_default": ["Dividend"],
                "amount_column": "Amount",
                "profit_func": lambda fdf, amount: fdf[amount],
                "profit_label": "股息值"
            }
        }

        for key, cfg in configs.items():
            st.markdown(f"---\n### {key} 部分")
            filter_col = cfg["filter_column"]
            filter_default = cfg["filter_default"]
            default_index = columns.index(filter_col) if filter_col in columns else 0
            selected_column = st.selectbox(f"{key}: 选择要过滤的列(缺省为'{filter_col}')", options=columns, index=default_index, key=f"{key}_filter_col")
            unique_values = df[selected_column].dropna().unique().tolist()
            selected_values = st.multiselect(
                f"{key}: 选择 {selected_column} 列的过滤值,可以选择多个值,缺省为{filter_default}",
                options=unique_values,
                default=filter_default,
                key=f"{key}_filter_val"
            )
            if selected_values:
                filtered_df = df[df[selected_column].isin(selected_values)].copy()
                st.write(f"{key}: 过滤后的数据（基于 {selected_column} = {selected_values}）：")
                st.dataframe(filtered_df)
                st.write(f"{key}: 过滤后数据行数：{len(filtered_df)}")
            else:
                st.warning(f"{key}: 请至少选择一个过滤值！")
                continue

            if key in ["RSU", "ESPP"]:
                sale_col = cfg["sale_column"]
                cost_col = cfg["cost_column"]
                shares_col = cfg["shares_column"]
                # 选择列
                sale_index = columns.index(sale_col) if sale_col in columns else 0
                cost_index = columns.index(cost_col) if cost_col in columns else 0
                shares_index = columns.index(shares_col) if shares_col in columns else 0
                sales_price_column = st.selectbox(f"{key}: 选择销售价格的列, 缺省为'{sale_col}'", options=columns, index=sale_index, key=f"{key}_sale_col")
                cost_price_column = st.selectbox(f"{key}: 选择成本价格的列, 缺省为'{cost_col}'", options=columns, index=cost_index, key=f"{key}_cost_col")
                shares_column = st.selectbox(f"{key}: 选择销售股数的列, 缺省为'{shares_col}'", options=columns, index=shares_index, key=f"{key}_shares_col")
                if sales_price_column and cost_price_column and shares_column:
                    for col in [sales_price_column, cost_price_column, shares_column]:
                        filtered_df[col] = filtered_df[col].replace(r'[\$,]', '', regex=True)
                        filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce')
                    filtered_df['Profit'] = cfg["profit_func"](filtered_df, sales_price_column, cost_price_column, shares_column)
                    st.warning(f"{key} {cfg['profit_label']}统计(计入亏损交易)：")
                    st.write(f"总{cfg['profit_label']}($): {filtered_df['Profit'].sum():.2f}")
                    st.write(f"总{cfg['profit_label']}(¥): {filtered_df['Profit'].sum()*exchange_rate:.2f}")
                    profit_summary[key]["include_negative"] = filtered_df['Profit'].sum()
                    st.warning(f"{key} {cfg['profit_label']}统计(不计入亏损交易)：")
                    st.write(f"总{cfg['profit_label']}($): {filtered_df[filtered_df['Profit'] > 0]['Profit'].sum():.2f}")
                    st.write(f"总{cfg['profit_label']}(¥): {filtered_df[filtered_df['Profit'] > 0]['Profit'].sum()*exchange_rate:.2f}")
                    profit_summary[key]["non_negative"] = filtered_df[filtered_df['Profit'] > 0]['Profit'].sum()
            elif key == "Dividend":
                amount_col = cfg["amount_column"]
                amount_index = columns.index(amount_col) if amount_col in columns else 0
                sales_price_column = st.selectbox(f"{key}: 选择{cfg['profit_label']}所在列, 缺省为'{amount_col}'", options=columns, index=amount_index, key=f"{key}_amount_col")
                if sales_price_column:
                    filtered_df[sales_price_column] = filtered_df[sales_price_column].replace(r'[\$,]', '', regex=True)
                    filtered_df[sales_price_column] = pd.to_numeric(filtered_df[sales_price_column], errors='coerce')
                    filtered_df['Profit'] = cfg["profit_func"](filtered_df, sales_price_column)
                    st.write(f"总{cfg['profit_label']}($): {filtered_df['Profit'].sum():.2f}")
                    st.write(f"总{cfg['profit_label']}(¥): {filtered_df['Profit'].sum()*exchange_rate:.2f}")
                    profit_summary[key]["total"] = filtered_df['Profit'].sum()
                else:
                    st.warning(f"{key}: 请确保选择了正确的列！")
    except Exception as e:
        st.error(f"读取文件时发生错误：{str(e)}")
else:
    st.info("请上传一个 CSV 文件以开始过滤。")

# 写入分隔符
st.markdown("---")
st.info("股票相关美元总值如：")
st.write(f"计入亏损交易的股票盈利值：RSU {profit_summary['RSU']['include_negative']:.2f} (USD) + ESPP {profit_summary['ESPP']['include_negative']:.2f} (USD) = {profit_summary['RSU']['include_negative'] + profit_summary['ESPP']['include_negative']:.2f} (USD)")
st.write(f"不计入亏损交易的股票盈利值：RSU {profit_summary['RSU']['non_negative']:.2f} (USD) + ESPP {profit_summary['ESPP']['non_negative']:.2f} (USD) = {profit_summary['RSU']['non_negative'] + profit_summary['ESPP']['non_negative']:.2f} (USD)")
st.write(f"股息所得：{profit_summary['Dividend']['total']:.2f} (USD)")
st.markdown("---")
st.info("股票相关人民币数据如下：")
st.write(f"计入亏损交易的股票盈利值：RSU  {profit_summary['RSU']['include_negative'] * exchange_rate:.2f} (CNY) + {profit_summary['ESPP']['include_negative'] * exchange_rate:.2f} (CNY) = {(profit_summary['RSU']['include_negative'] + profit_summary['ESPP']['include_negative']) * exchange_rate:.2f} (CNY)")
st.write(f"不计入亏损交易的股票盈利值：RSU {profit_summary['RSU']['non_negative'] * exchange_rate:.2f} (CNY) + ESPP {profit_summary['ESPP']['non_negative'] * exchange_rate:.2f} (CNY) = {(profit_summary['RSU']['non_negative'] + profit_summary['ESPP']['non_negative']) * exchange_rate:.2f} (CNY)")
st.write(f"股息所得：{profit_summary['Dividend']['total'] * exchange_rate:.2f} (CNY)")
st.markdown("---")# 写入分隔符