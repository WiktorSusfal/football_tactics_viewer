# Example list of floats
float_list = []

paired_list = [list(pair) for pair in zip(float_list[::2], float_list[1::2])]

print(paired_list)
        
        
#$#if __name__ == '__main__':
#$#    med = MdlEventsData()
#$#    med.set_json_filepath(r'C:\Users\wikto\Rzeczy\Projekty\Python\FootballTacticsViewer\resources\tactics_data\3788757 - events.json')
#$#    med.get_result_frames()
#$
#$import pandas as pd 
#$
#$# Example DataFrame with a column that we'll expand into multiple rows
#$df = pd.DataFrame({
#$    'id': [1, 2],
#$    'items': [['apple', 'banana'], ['carrot', 'date', 'eggplant']]
#$})
#$
#$print("Original DataFrame:")
#$print(df)
#$
#$# Apply a function to expand the 'items' column into multiple rows
#$#df['items'] = df['items'].apply(lambda x: x)  # Identity function for clarity
#$#print(df)
#$
#$# Use explode to turn lists into multiple rows
#$df_expanded = df.explode('items').reset_index(drop=True)
#$
#$print("\nDataFrame after expanding 'items' into multiple rows using explode:")
#$print(df_expanded)