        #Delta savings for staircasing 
        if df.at[0, 'AZ'] == 1:
            df.at[0, 'BG'] = df.at[0, 'M']
        else:
            df.at[i, 'BG'] = df.at[i, 'BF'] * (df.at[i, 'I'] - df.at[i, 'J'] - df.at[i, 'F'] * service_charge - staircase_admin - df.at[i, 'BE'] * (1 - 0) - 0* mortgage_rate)
        #Total share owned
        df.at[0, 'BH'] = min(0+(df.at[0, 'BG']+df.at[0, 'BL'])/df.at[0, 'F'] , 1)
        df.at[0, 'BJ'] = min(df.at[0, 'BF'] * loan_ratio * df.at[0, 'I'] - 0,  (1 - 0) * df.at[0, 'F'] - df.at[0, 'BG'])
        df.at[0, 'BK'] = (LTV/(1-LTV))*(df.at[0,'BG']+ 0*df.at[0,'F'] - 0)
        df.at[0, 'BM'] = df.at[0, 'BL'] * df.at[0, 'BF'] if df.at[0, 'BH'] < 1 else 0 + min(df.at[0, 'BL'], df.at[0, 'F'] - df.at[0, 'BG']) if df.at[0, 'BH'] == 1 and 0 < 1 else 0



        for i in range(1, len(df)):
            if df.at[i, 'AZ'] == 1:
                df.at[i, 'BG'] = df.at[i, 'M']
            else:
                df.at[i, 'BG'] = df.at[i, 'BF'] * (df.at[i, 'I'] - df.at[i, 'J'] - df.at[i, 'F'] * service_charge - staircase_admin - df.at[i, 'BE'] * (1 - df.at[i-1, 'BH']) - (df.at[i-1, 'BL']* mortgage_rate))

        #Total share owned
   #     df.at[0, 'BH'] = min(0+(df.at[0, 'BG']+df.at[0, 'BL'])/df.at[0, 'F'] , 1)
        for i in range(1, len(df)):
            if df.at[i, 'BH'] == 1:
                df.at[i, 'BH'] = 1
            else:
                df.at[i, 'BH'] = min(df.at[i-1, 'BH'] +(df.at[i, 'BG']+df.at[i, 'BL'])/df.at[i, 'F'] , 1)
    #Full staircase
    for i in range(len(df)):
        if df.at[i, 'BH'] == 1:
            df.at[i, 'BI'] = 1 
        else:
            df.at[i, 'BI'] = 0
    
    #A Delta Loan constraint A (LTI)
    #df.at[0, 'BJ'] = min(df.at[0, 'BF'] * loan_ratio * df.at[0, 'I'] - 0,  (1 - 0) * df.at[0, 'F'] - df.at[0, 'BG'])
    for i in range(1, len(df)):
        if 1 - df.at[i, 'BH'] > 0:
            df.at[i, 'BJ'] = min((df.at[i, 'BF'] * loan_ratio * df.at[i, 'I'] - df.at[i-1, 'BM']),
            (1 - df.at[i-1, 'BH']) * df.at[i, 'F'] - df.at[i, 'BG'])
        else:
            df.at[i, 'BJ'] = df.at[0, 'BF'] * loan_ratio * df.at[i, 'I'] - df.at[i-1, 'BM']
    
    #B Delta Loan constraint B (LTV)
#    df.at[0, 'BK'] = (LTV/(1-LTV))*(df.at[0,'BG']+ 0*df.at[0,'F'] - 0)
    for i in range(1, len(df)):
        df.at[i, 'BK'] = (LTV/(1-LTV))*(df.at[i,'BG']+ df.at[i-1,'BH']*df.at[0,'F'] - df.at[i-1,'BM'])
    for i in range(len(df)):
        df.at[i, 'BL'] = min(df.at[i, 'BJ'], df.at[i, 'BK'])

    #Total loan
#    df.at[0, 'BM'] = df.at[0, 'BL'] * df.at[0, 'BF'] if df.at[0, 'BH'] < 1 else 0 + min(df.at[0, 'BL'], df.at[0, 'F'] - df.at[0, 'BG']) if df.at[0, 'BH'] == 1 and 0 < 1 else 0
    for i in range(1, len(df)):
        # Previous row values
        BM_previous = df.at[i-1, 'BM']
        BH_previous = df.at[i-1, 'BH']
        
        # Calculation for current row based on the formula logic
        if df.at[i, 'BH'] < 1:
            df.at[i, 'BM'] = BM_previous + df.at[i, 'BL'] * df.at[i, 'BF']
        elif df.at[i, 'BH'] == 1 and BH_previous < 1:
            df.at[i, 'BM'] = BM_previous + min(df.at[i, 'BL'], df.at[i, 'F'] - df.at[i, 'BG'])
        else:
            df.at[i, 'BM'] = BM_previous
        
