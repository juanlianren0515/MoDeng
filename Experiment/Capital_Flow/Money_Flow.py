# encoding=utf-8import jsonfrom jqdatasdk import *from Global_Value.file_dir import rootPathimport pandas as pdimport numpy as np"""关于指数的资金出入的子函数字段名	                含义	                备注date	                日期	sec_code	            stk代码	change_pct	            涨跌幅(%)	net_amount_main	        主力净额(万)	        主力净额 = 超大单净额 + 大单净额net_pct_main	        主力净占比(%)	        主力净占比 = 主力净额 / 成交额net_amount_xl	        超大单净额(万)	        超大单：大于等于50万股或者100万元的成交单net_pct_xl	            超大单净占比(%)	        超大单净占比 = 超大单净额 / 成交额net_amount_l	        大单净额(万)	        大单：大于等于10万股或者20万元且小于50万股或者100万元的成交单net_pct_l	            大单净占比(%)	        大单净占比 = 大单净额 / 成交额net_amount_m	        中单净额(万)	        中单：大于等于2万股或者4万元且小于10万股或者20万元的成交单net_pct_m	            中单净占比(%)	        中单净占比 = 中单净额 / 成交额net_amount_s	        小单净额(万)	        小单：小于2万股或者4万元的成交单net_pct_s	            小单净占比(%)	        小单净占比 = 小单净额 / 成交额net_amount_main	        主力净额(万)net_amount_m	        中单净额(万)net_amount_s	        小单净额(万)"""def get_index_money_flow(index_code, start_date, end_date=None):    # 获取上证的成分股    sh_stks = get_index_stocks(index_code, date=None)    # 获取上证成分股的资金流    df_m_f = get_money_flow(sh_stks, start_date=start_date, end_date=end_date, fields=None, count=None)    # 按日期进行分类    df_m_f['date_str'] = df_m_f.apply(lambda x: str(x['date'])[:10], axis=1)    df_m_group = list(df_m_f.groupby(by='date_str'))    # 去掉相应的列之后，进行按列求和    df_m_group = [(x[0], x[1].loc[:, x[1].columns[[m not in ['date', 'date_str', 'sec_code'] for m in x[1].columns]]])                  for x in df_m_group]    # 按列求和    df_m_group = [(x[0], x[1].apply(lambda m: np.sum(m), axis=0)) for x in df_m_group]    # 加入日期    for srs in df_m_group:        srs[1]['date'] = srs[0]    df_m = pd.DataFrame([x[1] for x in df_m_group])    # 按日期排名，并将日期设置为索引    df_m = df_m.set_index(keys='date').sort_index(ascending=True)    return df_mdef get_stk_money_flow_pre(stk, start_date, end_date, c_max, c_min):    """    整理money_flow 并使用json中的极值进行归一化    :param stk:    :param start_date:    :param end_date:    :param max_min_json:    :param result_save_dir:    :return:    """    code = stk    if code in ['sh', 'sz', 'cyb']:        stk_code_normal = {            'sh': '000001.XSHG',            'sz': '399001.XSHE',            'cyb': '399006.XSHE'        }[code]        df = get_index_money_flow(normalize_code(stk_code_normal), start_date=start_date, end_date=end_date)    else:        df = get_money_flow(normalize_code(code), start_date=start_date, end_date=end_date)        df['date_str'] = df.apply(lambda x: str(x['date'])[:10], axis=1)        df = df.set_index(keys='date_str').sort_index(ascending=True)    # 获取主要的列    df_cols = df.loc[:, ['net_amount_main', 'net_amount_m', 'net_amount_s']]    # 对df中的值进行归一化    df_std = df_cols.applymap(lambda x: (x - c_min) / (c_max - c_min))    return df_stddef get_stk_money_flow(stk, start_date, end_date):    """    整理money_flow 并归一化    :param stk:    :param start_date:    :param end_date:    :param max_min_json:    :param result_save_dir:    :return:    """    code = stk    if code in ['sh', 'sz', 'cyb']:        stk_code_normal = {            'sh': '000001.XSHG',            'sz': '399001.XSHE',            'cyb': '399006.XSHE'        }[code]        df = get_index_money_flow(normalize_code(stk_code_normal), start_date=start_date, end_date=end_date)    else:        df = get_money_flow(normalize_code(code), start_date=start_date, end_date=end_date)        df['date_str'] = df.apply(lambda x: str(x['date'])[:10], axis=1)        df = df.set_index(keys='date_str').sort_index(ascending=True)    # 获取主要的列    df_cols = df.loc[:, ['net_amount_main', 'net_amount_m', 'net_amount_s']]    # 获取最大最小值    c_max, c_min = np.max(df_cols.values), np.min(df_cols.values)    # 对df中的值进行归一化    df_std = df_cols.applymap(lambda x: (x - c_min) / (c_max - c_min))    """    rootPath + '\Function\LSTM\AboutLSTM\stk_max_min.json'    """    # 将极值存入json记录中    record_json_url = rootPath + '\Function\LSTM\AboutLSTM\stk_max_min.json'    with open(record_json_url, 'r') as f:        json_max_min_info = json.load(f)    if code in json_max_min_info.keys():        json_max_min_info[code]['c_max'] = c_max        json_max_min_info[code]['c_min'] = c_min    else:        json_max_min_info[code] = {'c_max': c_max, 'c_min': c_min}    with open(record_json_url, 'w') as f:        json.dump(json_max_min_info, f)    return df_std, c_max, c_minif __name__ == '__main__':    code = 'sh'    df = get_stk_money_flow('sh', start_date='2019-05-12', end_date=None)    end = 0