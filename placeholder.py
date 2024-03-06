    if df.at[0, 'BI'] > 0:
        df.at[0, 'BN'] = 1
    else:
        df.at[0, 'BN'] = 0
    for i in range(1, len(df)):
        if df.at[i, 'BI'] > df.at[i-1, 'BI']:
            df.at[i, 'BN'] = 1
        else:
            df.at[i, 'BN'] = 0
    #Loan adjusted + STLT
    for i in range(len(df)):
        df.at[i, 'BO'] = (df.at[i, 'BM']+df.at[i, 'P'])*df.at[i, 'BN'] 
    
    #Savings after full staircasing indicator
        df['BP'] = (df['BN'].cumsum()).astype(int)
    #Savings 
        df.at[i, 'BQ'] = df.at[i, 'BP']*(df.at[i, 'I']-df.at[i, 'J'] - (service_charge*df.at[i, 'F']))
    df.at[0, 'BR'] = df.at[0, 'BO'] - df.at[0, 'BQ']
    for i in range(1, len(df)):
        df.at[i, 'BR'] = (df.at[i-1, 'BR']* (1 + mortgage_rate)) + df.at[i, 'BO'] - df.at[i, 'BQ']
    
    #mortgage loan indicator 
    for i in range(len(df)):
        df.at[i, 'BO']=  df.at[i, 'BN'] +  df.at[i, 'BP']
    #mortgage loan
        df.at[i, 'BT'] = (1 - df.at[i, 'BS']) * df.at[i, 'BM'] + (1 if df.at[i, 'BR'] > 0 else 0) * df.at[i, 'BR']
    #mortgage repayment
    df.at[0, 'BU'] = 0
     
    for i in range(1, len(df)):
        if df.at[i, 'BR'] <= 0 and df.at[i-1, 'BR'] > 0:
           df.at[i, 'BU'] = 1
        else: 
            df.at[i, 'BU'] = 0 
    #savings indicator
    for i in range(len(df)):
        df['BV'] = (df['BU'].cumsum() >= 1).astype(int)
    #first savings
        df.at[i, 'BW'] = -df.at[i, 'BU']*df.at[i, 'BR']*((1+savings_rate)/(1+mortgage_rate))
    #savings 
    df.at[0, 'BX'] = df.at[0, 'BU']*df.at[0, 'BW']+df.at[0, 'BV']*df.at[0, 'BQ']
    for i in range(1, len(df)):
        df.at[i, 'BX'] = df.at[i, 'BU']*df.at[i, 'BW']+df.at[i, 'BV']*df.at[i, 'BQ']
    #Liquid wealth 
    for i in range(len(df)):
        df.at[i, 'BY'] = df.at[i, 'M']*(1-df.at[i, 'BF']) + df.at[i, 'BX']
    #Housing wealth 
        df.at[i, 'BZ'] =df.at[i, 'BH']*df.at[i, 'F'] - df.at[i, 'BT']

        df.at[i, 'CA'] = df.at[i, 'AI'] 
        df.at[i, 'CB'] = df.at[i, 'D']
        df.at[i, 'CC'] = df.at[i, 'BY']/df.at[i, 'CA'] 
        df.at[i, 'CD'] = df.at[i, 'BZ']/df.at[i, 'CA']
