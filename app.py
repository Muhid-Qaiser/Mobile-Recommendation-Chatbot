from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import numpy as np

import re
import pandas as pd


reviews_df = pd.read_csv('Reviews.csv')
products_df = pd.read_csv('Product_Detail.csv')

merged_df = pd.merge(reviews_df, products_df, on='ID')


# Define a simple chatbot function
def chatbot(user_query):
    # Extract information from the user query using regular expressions

    brands = ['Samsung', 'Redmi', 'Realme', 'itel', 'tecno', 'Xiaomi', 'Infinix', 'iPhone', 'Oppo']
    colors = ['white', 'gray', 'silver', 'red ', 'green', 'blue', 'black', 'gold', 'rose gold', 'purple', 'orange', 'yellow', 'cyan', 'navy blue']
    rams = [0,2,4,6,8,12,16,32]
    roms = [0,64,128,256,512]
    megapixels = [2, 3, 5, 8, 10, 12, 16, 20, 24, 32, 48, 50, 64, 108]
    brand = ''
    color = ''


    for b in brands:
        if b.lower() in user_query.lower():
            brand = b

    for c in colors:
        if c.lower() in user_query.lower():
            color = c
   
    # ! Two Price given
    # * Considers any Number as price
    # price_match = re.search(r'\$?(\d+) to \$?(\d+)', user_query)

    # number = -2
    number = 2
    # * Number proceeding $ will be price. Numbers proceeding nothing will be quantity of results.

    price_match = re.search(r'\$(\d+) to \$(\d+)', user_query)

    if not price_match:
        price_match = re.search(r'\$(\d+) and \$(\d+)', user_query)

    # number = re.search(r'(?<!\$)(\d+)', user_query)
    number = re.search(r'(?<= )(?<!\$)(\d+)', user_query)
    flag = False
    try:
        number = int(number.group(1))
    except AttributeError:
        flag = True
        # number = -2
        number = 2
    if not flag and number == None:
        # number = -2
        number = 2


    # * Check if a range for RAM is mentioned
    ram_range_input = []

    ram_range_match = re.search(r' (\d+) to (\d+)\s?gb ram', user_query.lower())
    if ram_range_match == None:
        ram_range_input.append('\0')
    else:
        start_ram = int(ram_range_match.group(1))
        end_ram = int(ram_range_match.group(2))
        ram_range_input = [f' {value}gb' for value in rams if start_ram <= value <= end_ram]
        

    # * Check if RAM is mentioned
    ram_match = re.search(r' (\d+)\s?gb ram', user_query.lower())
    if ram_match == None:
        ram_input = ''
        ram_input2 = ''
    else:
        ram_input = ' ' + ram_match.group(1) + 'gb'
        ram_input2 = '(' + ram_match.group(1) + 'gb'


    # * Check if ROM is mentioned
    rom_match = re.search(r' (\d+)\s?gb rom', user_query.lower())
    if rom_match == None:
        rom_input = ''
        rom_input2 = ''
    else:
        rom_input = ' ' + rom_match.group(1) + 'gb'
        rom_input2 = ')' + rom_match.group(1) + 'gb'


    # * Check if above Camera MP is mentioned
    camera_match = re.search(r' > (\d+)\s?mp', user_query.lower())
    if camera_match == None:
        mp_above_input = ['\0']
        mp_above_input2 = ['\0']
    else:
        end_mp = int(camera_match.group(1))
        mp_above_input = [f' {value}mp' for value in megapixels if value >= end_mp]
        mp_above_input2 = [f' {value} mp' for value in megapixels if value >= end_mp]
        camera_flag = True

    # * Check if below Camera MP is mentioned
    camera_match = re.search(r' < (\d+)\s?mp', user_query.lower())
    if camera_match == None:
        mp_below_input = ['\0']
        mp_below_input2 = ['\0']
    else:
        end_mp = int(camera_match.group(1))
        mp_below_input = [f' {value}mp' for value in megapixels if value <= end_mp]
        mp_below_input2 = [f' {value} mp' for value in megapixels if value <= end_mp]
        camera_flag = True


    # * Check if Camera MP is mentioned
    camera_match = re.search(r'(\d+)\s?mp', user_query.lower())
    if camera_match == None:
        mp_input = ''
        mp_input2 = ''
    else:
        mp_input =' ' + camera_match.group(1) + 'mp'
        mp_input2 =' ' + camera_match.group(1) + ' mp'


    
    # * Check if Specific Phone name is mentioned
    for b in brands:
        # name_match = re.search(rf'{b.lower()} (\S+(\s\d+)?)', user_query.lower())
        name_match = re.search(rf'{b.lower()} ((?!phone|phones|products|product|,)\S+(\s\d+)?)', user_query.lower())

        if name_match == None:
            name_input = ''
        else:
            name_input = f'{b.lower()} ' + name_match.group(1)
            break
            
    # * Check if 'greater than rating' value is given
    overRating_match = re.search(r'rating > (\d+(\.\d+)?)\s?', user_query.lower())
    if overRating_match == None:
        overRating = -1
    else:
        overRating = float(overRating_match.group(1))

    # * Check if 'less than rating' value is given
    underRating_match = re.search(r'rating < (\d+(\.\d+)?)\s?', user_query.lower())
    if underRating_match == None:
        underRating = 6
    else:
        underRating = float(underRating_match.group(1))

    # * Check if 'equal to rating' value is given
    equalRating_match = re.search(r'rating = (\d+(\.\d+)?)\s?', user_query.lower())
    if equalRating_match == None:
        equalRating = -1
    else:
        equalRating = float(equalRating_match.group(1))
    

    if price_match:
        min_price = int(price_match.group(1))
        max_price = int(price_match.group(2))
        relevant_products = merged_df[(merged_df['Price'] >= min_price) & (merged_df['Price'] <= max_price)]
    
        if not relevant_products.empty:

            # Sort products by seller score
            if 'seller wise' in user_query.lower() or 'seller score' in user_query.lower():
                if 'worst' in user_query.lower() or 'bad' in user_query.lower() or 'not good' in user_query.lower() or 'terrible' in user_query.lower():
                    relevant_products = relevant_products.sort_values(by='Seller Score', ascending=True)
                else:
                    relevant_products = relevant_products.sort_values(by='Seller Score', ascending=False)

            # Sort products by review count
            elif 'review count' in user_query.lower():
                if 'worst' in user_query.lower() or 'bad' in user_query.lower() or 'not good' in user_query.lower() or 'terrible' in user_query.lower() or 'least' in user_query.lower() or 'minimum' in user_query.lower() or 'less' in user_query.lower():
                    relevant_products = relevant_products.sort_values(by='Total Reviews', ascending=True)
                else:
                    relevant_products = relevant_products.sort_values(by='Total Reviews', ascending=False)

             # Sort products by price
            elif 'sort by price' in user_query.lower() or 'based on price' in user_query.lower() or 'sorted by price' in user_query.lower():
                if 'worst' in user_query.lower() or 'bad' in user_query.lower() or 'not good' in user_query.lower() or 'terrible' in user_query.lower() or 'least' in user_query.lower() or 'minimum' in user_query.lower() or 'less' in user_query.lower() or 'ascending' in user_query.lower() or 'low to high' in user_query.lower():
                    relevant_products = relevant_products.sort_values(by='Price', ascending=True)
                else:
                    relevant_products = relevant_products.sort_values(by='Price', ascending=False)
            
            # Sort products by product score 
            else:
                # relevant_products = relevant_products.sort_values(by='Score', ascending=False)
                if 'worst' in user_query.lower() or 'bad' in user_query.lower() or 'not good' in user_query.lower() or 'terrible' in user_query.lower():
                    relevant_products = relevant_products.sort_values(by='Score', ascending=True)
                else:
                    relevant_products = relevant_products.sort_values(by='Score', ascending=False)
        
            # product_names = relevant_products['Name'].tolist()
            # product_names = [name for name in relevant_products['Name'].tolist() if brand.lower() in name.lower() and color.lower() in name.lower()]

            # product_names = [(row['Name'], row['Url']) for index, row in relevant_products.iterrows() if brand.lower() in row['Name'].lower() and color.lower() in row['Name'].lower() and ( ram_input.lower() in row['Name'].lower() or ram_input.lower() in row['Specs'].lower()  or  ram_input2.lower() in row['Name'].lower() or ram_input2.lower() in row['Specs'].lower() )]

            if equalRating == -1:
                product_names = [(row['Name'], row['Url']) for index, row in relevant_products.iterrows() if brand.lower() in row['Name'].lower() and color.lower() in row['Name'].lower() and ( ram_input.lower() in row['Name'].lower() or ram_input.lower() in row['Specs'].lower()  or  ram_input2.lower() in row['Name'].lower() or ram_input2.lower() in row['Specs'].lower() or any(element in row['Name'] for element in ram_range_input) or any(element in row['Specs'] for element in ram_range_input) )
                                and ( rom_input.lower() in row['Name'].lower() or rom_input.lower() in row['Specs'].lower()  or  rom_input2.lower() in row['Name'].lower() or rom_input2.lower() in row['Specs'].lower() )
                                and ( mp_input in row['Name'].lower() or mp_input in row['Specs'].lower() or mp_input2 in row['Name'].lower() or mp_input2 in row['Specs'].lower() or any(element in row['Name'].lower() for element in mp_above_input) or any(element in row['Specs'].lower() for element in mp_above_input) or any(element in row['Name'].lower() for element in mp_above_input2) or any(element in row['Specs'].lower() for element in mp_above_input2)   or   any(element in row['Name'].lower() for element in mp_below_input) or any(element in row['Specs'].lower() for element in mp_below_input) or any(element in row['Name'].lower() for element in mp_below_input2) or any(element in row['Specs'].lower() for element in mp_below_input2)  ) 
                                #   and ( mp_input in row['Name'].lower() or mp_input in row['Specs'].lower() or mp_input2 in row['Name'].lower() or mp_input2 in row['Specs'].lower() ) 
                                and overRating < row['Score'] and underRating > row['Score']  and name_input in row['Name'].lower() ]
            else:
                product_names = [(row['Name'], row['Url']) for index, row in relevant_products.iterrows() if brand.lower() in row['Name'].lower() and color.lower() in row['Name'].lower() and ( ram_input.lower() in row['Name'].lower() or ram_input.lower() in row['Specs'].lower()  or  ram_input2.lower() in row['Name'].lower() or ram_input2.lower() in row['Specs'].lower() or any(element in row['Name'] for element in ram_range_input) or any(element in row['Specs'] for element in ram_range_input) )
                                and ( rom_input.lower() in row['Name'].lower() or rom_input.lower() in row['Specs'].lower()  or  rom_input2.lower() in row['Name'].lower() or rom_input2.lower() in row['Specs'].lower() )
                                and ( mp_input in row['Name'].lower() or mp_input in row['Specs'].lower() or mp_input2 in row['Name'].lower() or mp_input2 in row['Specs'].lower() or any(element in row['Name'].lower() for element in mp_above_input) or any(element in row['Specs'].lower() for element in mp_above_input) or any(element in row['Name'].lower() for element in mp_above_input2) or any(element in row['Specs'].lower() for element in mp_above_input2)   or   any(element in row['Name'].lower() for element in mp_below_input) or any(element in row['Specs'].lower() for element in mp_below_input) or any(element in row['Name'].lower() for element in mp_below_input2) or any(element in row['Specs'].lower() for element in mp_below_input2)  ) 
                                #   and ( mp_input in row['Name'].lower() or mp_input in row['Specs'].lower() or mp_input2 in row['Name'].lower() or mp_input2 in row['Specs'].lower() ) 
                                and overRating < row['Score'] and underRating > row['Score']  and name_input in row['Name'].lower() and equalRating == row['Score'] ]


            if product_names != []:

            # product_names_str = ' \n '.join(product_names)

                product_names_str = ''
                for index, name in enumerate(product_names):
                    if index == number:
                        break
                    # product_names_str += f'<br /> {index+1} : {name}.\n '
                    # product_names_str += f'<br /> {index+1} : <a href="{name}">{name}.</a>\n '
                    product_names_str += f'<br /> {index+1} : <a href="{name[1]}">{name[0]}.</a>\n '

                # return f"Based on user ratings and price, the best phones from ${min_price} to ${max_price} are {', '.join(product_names)}."
                return f"Based on user ratings and price, the best phones from ${min_price} to ${max_price} are : \n {(product_names_str)}"
            
            else:
                return f"No {color} {brand} products found from ${min_price} to ${max_price}."
        else:
            return f"No {color} {brand} products found from ${min_price} to ${max_price}."

    # ! One Price given
    else:
        # * Any Number will be considered price
        # price_match = re.search(r'\$?(\d+)', user_query)
        
        # number = -2
        number = 2

        # * Number proceeding $ will be price. Numbers proceeding nothing will be quantity of results.
        price_match = re.search(r'\$(\d+)', user_query)
        # number = re.search(r'(?<!\$)(\d+)', user_query)
        number = re.search(r'(?<= )(?<!\$)(\d+)', user_query)
        flag = False
        try:
            number = int(number.group(1))
        except AttributeError:
            flag = True
            # number = -2
            number = 2
        if not flag and number == None:
            number = 2
            # number = -2


        # ! Under Price range
        if price_match and 'under ' in user_query or 'below ' in user_query or 'less than ' in user_query:
            max_price = int(price_match.group(1))
            relevant_products = merged_df[merged_df['Price'] <= max_price]
            
            if not relevant_products.empty:
                
                # Sort products by seller score
                if 'seller wise' in user_query.lower() or 'seller score' in user_query.lower():
                    if 'worst' in user_query.lower() or 'bad' in user_query.lower() or 'not good' in user_query.lower() or 'terrible' in user_query.lower():
                        relevant_products = relevant_products.sort_values(by='Seller Score', ascending=True)
                    else:
                        relevant_products = relevant_products.sort_values(by='Seller Score', ascending=False)

                # Sort products by review count
                elif 'review count' in user_query.lower():
                    if 'worst' in user_query.lower() or 'bad' in user_query.lower() or 'not good' in user_query.lower() or 'terrible' in user_query.lower() or 'least' in user_query.lower() or 'minimum' in user_query.lower() or 'less' in user_query.lower():
                        relevant_products = relevant_products.sort_values(by='Total Reviews', ascending=True)
                    else:
                        relevant_products = relevant_products.sort_values(by='Total Reviews', ascending=False)

                 # Sort products by price
                elif 'sort by price' in user_query.lower() or 'based on price' in user_query.lower() or 'sorted by price' in user_query.lower():
                    if 'worst' in user_query.lower() or 'bad' in user_query.lower() or 'not good' in user_query.lower() or 'terrible' in user_query.lower() or 'least' in user_query.lower() or 'minimum' in user_query.lower() or 'less' in user_query.lower() or 'ascending' in user_query.lower() or 'low to high' in user_query.lower():
                        relevant_products = relevant_products.sort_values(by='Price', ascending=True)
                    else:
                        relevant_products = relevant_products.sort_values(by='Price', ascending=False)
                
                # Sort products by product score 
                else:
                    # relevant_products = relevant_products.sort_values(by='Score', ascending=False)
                    if 'worst' in user_query.lower() or 'bad' in user_query.lower() or 'not good' in user_query.lower() or 'terrible' in user_query.lower():
                        relevant_products = relevant_products.sort_values(by='Score', ascending=True)
                    else:
                        relevant_products = relevant_products.sort_values(by='Score', ascending=False)
                
                # Extract product names
                # product_names = relevant_products['Name'].tolist()

                # product_names = [name for name in relevant_products['Name'].tolist() if brand.lower() in name.lower() and color.lower() in name.lower()]

                # product_names = [(row['Name'], row['Url']) for index, row in relevant_products.iterrows() if brand.lower() in row['Name'].lower() and color.lower() in row['Name'].lower() and ( ram_input.lower() in row['Name'].lower() or ram_input.lower() in row['Specs'].lower()  or  ram_input2.lower() in row['Name'].lower() or ram_input2.lower() in row['Specs'].lower() )]

                if equalRating == -1:
                    product_names = [(row['Name'], row['Url']) for index, row in relevant_products.iterrows() if brand.lower() in row['Name'].lower() and color.lower() in row['Name'].lower() and ( ram_input.lower() in row['Name'].lower() or ram_input.lower() in row['Specs'].lower()  or  ram_input2.lower() in row['Name'].lower() or ram_input2.lower() in row['Specs'].lower() or any(element in row['Name'] for element in ram_range_input) or any(element in row['Specs'] for element in ram_range_input) )
                                    and ( rom_input.lower() in row['Name'].lower() or rom_input.lower() in row['Specs'].lower()  or  rom_input2.lower() in row['Name'].lower() or rom_input2.lower() in row['Specs'].lower() )
                                    and ( mp_input in row['Name'].lower() or mp_input in row['Specs'].lower() or mp_input2 in row['Name'].lower() or mp_input2 in row['Specs'].lower() or any(element in row['Name'].lower() for element in mp_above_input) or any(element in row['Specs'].lower() for element in mp_above_input) or any(element in row['Name'].lower() for element in mp_above_input2) or any(element in row['Specs'].lower() for element in mp_above_input2)   or   any(element in row['Name'].lower() for element in mp_below_input) or any(element in row['Specs'].lower() for element in mp_below_input) or any(element in row['Name'].lower() for element in mp_below_input2) or any(element in row['Specs'].lower() for element in mp_below_input2)  ) 
                                    #   and ( mp_input in row['Name'].lower() or mp_input in row['Specs'].lower() or mp_input2 in row['Name'].lower() or mp_input2 in row['Specs'].lower() ) 
                                    and overRating < row['Score'] and underRating > row['Score']  and name_input in row['Name'].lower() ]
                else:
                    product_names = [(row['Name'], row['Url']) for index, row in relevant_products.iterrows() if brand.lower() in row['Name'].lower() and color.lower() in row['Name'].lower() and ( ram_input.lower() in row['Name'].lower() or ram_input.lower() in row['Specs'].lower()  or  ram_input2.lower() in row['Name'].lower() or ram_input2.lower() in row['Specs'].lower() or any(element in row['Name'] for element in ram_range_input) or any(element in row['Specs'] for element in ram_range_input) )
                                    and ( rom_input.lower() in row['Name'].lower() or rom_input.lower() in row['Specs'].lower()  or  rom_input2.lower() in row['Name'].lower() or rom_input2.lower() in row['Specs'].lower() )
                                    and ( mp_input in row['Name'].lower() or mp_input in row['Specs'].lower() or mp_input2 in row['Name'].lower() or mp_input2 in row['Specs'].lower() or any(element in row['Name'].lower() for element in mp_above_input) or any(element in row['Specs'].lower() for element in mp_above_input) or any(element in row['Name'].lower() for element in mp_above_input2) or any(element in row['Specs'].lower() for element in mp_above_input2)   or   any(element in row['Name'].lower() for element in mp_below_input) or any(element in row['Specs'].lower() for element in mp_below_input) or any(element in row['Name'].lower() for element in mp_below_input2) or any(element in row['Specs'].lower() for element in mp_below_input2)  ) 
                                    #   and ( mp_input in row['Name'].lower() or mp_input in row['Specs'].lower() or mp_input2 in row['Name'].lower() or mp_input2 in row['Specs'].lower() ) 
                                    and overRating < row['Score'] and underRating > row['Score']  and name_input in row['Name'].lower() and equalRating == row['Score'] ]


                if product_names != []:
                    # product_names_str = ' \n '.join(product_names)

                    product_names_str = ''
                    for index, name in enumerate(product_names):
                        if index == number:
                            break
                        # product_names_str += f'<br /> {index+1} : {name}.\n '
                        # product_names_str += f'<br /> {index+1} : <a href="{name}">{name}.</a>\n '
                        product_names_str += f'<br /> {index+1} : <a href="{name[1]}">{name[0]}.</a>\n '

                    # return f"Based on user ratings and price, the best {brand} phones under ${max_price} are {', '.join(product_names)}."
                    return f"Based on user ratings and price, the best {brand} phones under ${max_price} are : \n {(product_names_str)}"
                else:
                    return f"No {brand} products found under ${max_price}."

            else:
                return f"No {brand} products found under ${max_price}."
            
        # ! Above price range
        elif price_match and 'above ' in user_query.lower() or 'more than ' in user_query.lower() or 'over ' in user_query.lower():
            min_price = int(price_match.group(1))
            relevant_products = merged_df[merged_df['Price'] >= min_price]
            
            if not relevant_products.empty:
                
                 # Sort products by seller score
                if 'seller wise' in user_query.lower() or 'seller score' in user_query.lower():
                    if 'worst' in user_query.lower() or 'bad' in user_query.lower() or 'not good' in user_query.lower() or 'terrible' in user_query.lower():
                        relevant_products = relevant_products.sort_values(by='Seller Score', ascending=True)
                    else:
                        relevant_products = relevant_products.sort_values(by='Seller Score', ascending=False)
                
                # Sort product by review count
                elif 'review count' in user_query.lower():
                    if 'worst' in user_query.lower() or 'bad' in user_query.lower() or 'not good' in user_query.lower() or 'terrible' in user_query.lower() or 'least' in user_query.lower() or 'minimum' in user_query.lower() or 'less' in user_query.lower():
                        relevant_products = relevant_products.sort_values(by='Total Reviews', ascending=True)
                    else:
                        relevant_products = relevant_products.sort_values(by='Total Reviews', ascending=False)

                 # Sort products by price
                elif 'sort by price' in user_query.lower() or 'based on price' in user_query.lower() or 'sorted by price' in user_query.lower():
                    if 'worst' in user_query.lower() or 'bad' in user_query.lower() or 'not good' in user_query.lower() or 'terrible' in user_query.lower() or 'least' in user_query.lower() or 'minimum' in user_query.lower() or 'less' in user_query.lower() or 'ascending' in user_query.lower() or 'low to high' in user_query.lower():
                        relevant_products = relevant_products.sort_values(by='Price', ascending=True)
                    else:
                        relevant_products = relevant_products.sort_values(by='Price', ascending=False)

                # Sort products by product score 
                else:
                    # relevant_products = relevant_products.sort_values(by='Score', ascending=False)
                    if 'worst' in user_query.lower() or 'bad' in user_query.lower() or 'not good' in user_query.lower() or 'terrible' in user_query.lower():
                        relevant_products = relevant_products.sort_values(by='Score', ascending=True)
                    else:
                        relevant_products = relevant_products.sort_values(by='Score', ascending=False)
                
                # Extract product names
                # product_names = relevant_products['Name'].tolist()
                # product_names = [name for name in relevant_products['Name'].tolist() if brand.lower() in name.lower() and color.lower() in name.lower()]
                
                # product_names = [(row['Name'], row['Url']) for index, row in relevant_products.iterrows() if brand.lower() in row['Name'].lower() and color.lower() in row['Name'].lower()  and ( ram_input.lower() in row['Name'].lower() or ram_input.lower() in row['Specs'].lower()  or  ram_input2.lower() in row['Name'].lower() or ram_input2.lower() in row['Specs'].lower() )]

                if equalRating == -1:
                    product_names = [(row['Name'], row['Url']) for index, row in relevant_products.iterrows() if brand.lower() in row['Name'].lower() and color.lower() in row['Name'].lower() and ( ram_input.lower() in row['Name'].lower() or ram_input.lower() in row['Specs'].lower()  or  ram_input2.lower() in row['Name'].lower() or ram_input2.lower() in row['Specs'].lower() or any(element in row['Name'] for element in ram_range_input) or any(element in row['Specs'] for element in ram_range_input) )
                                    and ( rom_input.lower() in row['Name'].lower() or rom_input.lower() in row['Specs'].lower()  or  rom_input2.lower() in row['Name'].lower() or rom_input2.lower() in row['Specs'].lower() )
                                    and ( mp_input in row['Name'].lower() or mp_input in row['Specs'].lower() or mp_input2 in row['Name'].lower() or mp_input2 in row['Specs'].lower() or any(element in row['Name'].lower() for element in mp_above_input) or any(element in row['Specs'].lower() for element in mp_above_input) or any(element in row['Name'].lower() for element in mp_above_input2) or any(element in row['Specs'].lower() for element in mp_above_input2)   or   any(element in row['Name'].lower() for element in mp_below_input) or any(element in row['Specs'].lower() for element in mp_below_input) or any(element in row['Name'].lower() for element in mp_below_input2) or any(element in row['Specs'].lower() for element in mp_below_input2)  ) 
                                    #   and ( mp_input in row['Name'].lower() or mp_input in row['Specs'].lower() or mp_input2 in row['Name'].lower() or mp_input2 in row['Specs'].lower() ) 
                                    and overRating < row['Score'] and underRating > row['Score']  and name_input in row['Name'].lower() ]
                else:
                    product_names = [(row['Name'], row['Url']) for index, row in relevant_products.iterrows() if brand.lower() in row['Name'].lower() and color.lower() in row['Name'].lower() and ( ram_input.lower() in row['Name'].lower() or ram_input.lower() in row['Specs'].lower()  or  ram_input2.lower() in row['Name'].lower() or ram_input2.lower() in row['Specs'].lower() or any(element in row['Name'] for element in ram_range_input) or any(element in row['Specs'] for element in ram_range_input) )
                                    and ( rom_input.lower() in row['Name'].lower() or rom_input.lower() in row['Specs'].lower()  or  rom_input2.lower() in row['Name'].lower() or rom_input2.lower() in row['Specs'].lower() )
                                    and ( mp_input in row['Name'].lower() or mp_input in row['Specs'].lower() or mp_input2 in row['Name'].lower() or mp_input2 in row['Specs'].lower() or any(element in row['Name'].lower() for element in mp_above_input) or any(element in row['Specs'].lower() for element in mp_above_input) or any(element in row['Name'].lower() for element in mp_above_input2) or any(element in row['Specs'].lower() for element in mp_above_input2)   or   any(element in row['Name'].lower() for element in mp_below_input) or any(element in row['Specs'].lower() for element in mp_below_input) or any(element in row['Name'].lower() for element in mp_below_input2) or any(element in row['Specs'].lower() for element in mp_below_input2)  ) 
                                    #   and ( mp_input in row['Name'].lower() or mp_input in row['Specs'].lower() or mp_input2 in row['Name'].lower() or mp_input2 in row['Specs'].lower() ) 
                                    and overRating < row['Score'] and underRating > row['Score']  and name_input in row['Name'].lower() and equalRating == row['Score'] ]

                if product_names != []:
                    # product_names_str = ' \n '.join(product_names)

                    product_names_str = ''
                    for index, name in enumerate(product_names):
                        if index == number:
                            break
                        # product_names_str += f'<br /> {index+1} : {name}.\n '
                        # product_names_str += f'<br /> {index+1} : <a href="{name}">{name}.</a>\n '
                        product_names_str += f'<br /> {index+1} : <a href="{name[1]}">{name[0]}.</a>\n '

                    # return f"Based on user ratings and price, the best {brand} phones above ${min_price} are {', '.join(product_names)}."
                    return f"Based on user ratings and price, the best {brand} phones above ${min_price} are : \n {(product_names_str)}"
                else:
                    return f"No {brand} products found above ${min_price}."

            else:
                return f"No {brand} products found above ${min_price}."
            
        # ! Equal to price range
        elif price_match and 'equal to ' in user_query or 'with price ' in user_query.lower():
            equal_price = int(price_match.group(1))
            relevant_products = merged_df[merged_df['Price'] == equal_price]
            
            if not relevant_products.empty:

                 # Sort products by seller score
                if 'seller wise' in user_query.lower() or 'seller score' in user_query.lower():
                    if 'worst' in user_query.lower() or 'bad' in user_query.lower() or 'not good' in user_query.lower() or 'terrible' in user_query.lower():
                        relevant_products = relevant_products.sort_values(by='Seller Score', ascending=True)
                    else:
                        relevant_products = relevant_products.sort_values(by='Seller Score', ascending=False)

                # Sort products by review count
                elif 'review count' in user_query.lower():
                    if 'worst' in user_query.lower() or 'bad' in user_query.lower() or 'not good' in user_query.lower() or 'terrible' in user_query.lower() or 'least' in user_query.lower() or 'minimum' in user_query.lower() or 'less' in user_query.lower():
                        relevant_products = relevant_products.sort_values(by='Total Reviews', ascending=True)
                    else:
                        relevant_products = relevant_products.sort_values(by='Total Reviews', ascending=False)

                 # Sort products by price
                elif 'sort by price' in user_query.lower() or 'based on price' in user_query.lower() or 'sorted by price' in user_query.lower():
                    if 'worst' in user_query.lower() or 'bad' in user_query.lower() or 'not good' in user_query.lower() or 'terrible' in user_query.lower() or 'least' in user_query.lower() or 'minimum' in user_query.lower() or 'less' in user_query.lower() or 'ascending' in user_query.lower() or 'low to high' in user_query.lower():
                        relevant_products = relevant_products.sort_values(by='Price', ascending=True)
                    else:
                        relevant_products = relevant_products.sort_values(by='Price', ascending=False)
                
                # Sort products by product score 
                else:
                    # relevant_products = relevant_products.sort_values(by='Score', ascending=False)
                    if 'worst' in user_query.lower() or 'bad' in user_query.lower() or 'not good' in user_query.lower() or 'terrible' in user_query.lower():
                        relevant_products = relevant_products.sort_values(by='Score', ascending=True)
                    else:
                        relevant_products = relevant_products.sort_values(by='Score', ascending=False)
                
                # Extract product names
                # product_names = relevant_products['Name'].tolist()
                # product_names = [name for name in relevant_products['Name'].tolist() if brand.lower() in name.lower() and color.lower() in name.lower()]
                # product_names = [name for name in relevant_products['Name'].tolist() if brand.lower() in name.lower() and color.lower() in name.lower()]
                # product_names = [(row['Name'], row['Url']) for index, row in relevant_products.iterrows() if brand.lower() in row['Name'].lower() and color.lower() in row['Name'].lower() and ( ram_input.lower() in row['Name'].lower() or ram_input.lower() in row['Specs'].lower()  or  ram_input2.lower() in row['Name'].lower() or ram_input2.lower() in row['Specs'].lower() )]

                if equalRating == -1:
                    product_names = [(row['Name'], row['Url']) for index, row in relevant_products.iterrows() if brand.lower() in row['Name'].lower() and color.lower() in row['Name'].lower() and ( ram_input.lower() in row['Name'].lower() or ram_input.lower() in row['Specs'].lower()  or  ram_input2.lower() in row['Name'].lower() or ram_input2.lower() in row['Specs'].lower() or any(element in row['Name'] for element in ram_range_input) or any(element in row['Specs'] for element in ram_range_input) )
                                    and ( rom_input.lower() in row['Name'].lower() or rom_input.lower() in row['Specs'].lower()  or  rom_input2.lower() in row['Name'].lower() or rom_input2.lower() in row['Specs'].lower() )
                                    and ( mp_input in row['Name'].lower() or mp_input in row['Specs'].lower() or mp_input2 in row['Name'].lower() or mp_input2 in row['Specs'].lower() or any(element in row['Name'].lower() for element in mp_above_input) or any(element in row['Specs'].lower() for element in mp_above_input) or any(element in row['Name'].lower() for element in mp_above_input2) or any(element in row['Specs'].lower() for element in mp_above_input2)   or   any(element in row['Name'].lower() for element in mp_below_input) or any(element in row['Specs'].lower() for element in mp_below_input) or any(element in row['Name'].lower() for element in mp_below_input2) or any(element in row['Specs'].lower() for element in mp_below_input2)  ) 
                                    #   and ( mp_input in row['Name'].lower() or mp_input in row['Specs'].lower() or mp_input2 in row['Name'].lower() or mp_input2 in row['Specs'].lower() ) 
                                    and overRating < row['Score'] and underRating > row['Score']  and name_input in row['Name'].lower() ]
                else:
                    product_names = [(row['Name'], row['Url']) for index, row in relevant_products.iterrows() if brand.lower() in row['Name'].lower() and color.lower() in row['Name'].lower() and ( ram_input.lower() in row['Name'].lower() or ram_input.lower() in row['Specs'].lower()  or  ram_input2.lower() in row['Name'].lower() or ram_input2.lower() in row['Specs'].lower() or any(element in row['Name'] for element in ram_range_input) or any(element in row['Specs'] for element in ram_range_input) )
                                    and ( rom_input.lower() in row['Name'].lower() or rom_input.lower() in row['Specs'].lower()  or  rom_input2.lower() in row['Name'].lower() or rom_input2.lower() in row['Specs'].lower() )
                                    and ( mp_input in row['Name'].lower() or mp_input in row['Specs'].lower() or mp_input2 in row['Name'].lower() or mp_input2 in row['Specs'].lower() or any(element in row['Name'].lower() for element in mp_above_input) or any(element in row['Specs'].lower() for element in mp_above_input) or any(element in row['Name'].lower() for element in mp_above_input2) or any(element in row['Specs'].lower() for element in mp_above_input2)   or   any(element in row['Name'].lower() for element in mp_below_input) or any(element in row['Specs'].lower() for element in mp_below_input) or any(element in row['Name'].lower() for element in mp_below_input2) or any(element in row['Specs'].lower() for element in mp_below_input2)  ) 
                                    #   and ( mp_input in row['Name'].lower() or mp_input in row['Specs'].lower() or mp_input2 in row['Name'].lower() or mp_input2 in row['Specs'].lower() ) 
                                    and overRating < row['Score'] and underRating > row['Score']  and name_input in row['Name'].lower() and equalRating == row['Score'] ]


                if product_names != []:
                    # product_names_str = ' \n '.join(product_names)

                    product_names_str = ''
                    for index, name in enumerate(product_names):
                        if index == number:
                            break
                        # product_names_str += f'<br /> {index+1} : {name}.\n '
                        # product_names_str += f'<br /> {index+1} : <a href="{name}">{name}.</a>\n '
                        product_names_str += f'<br /> {index+1} : <a href="{name[1]}">{name[0]}.</a>\n '

                    # return f"Based on user ratings and price, the best {brand} phones equal to ${equal_price} are {', '.join(product_names)}."
                    return f"Based on user ratings and price, the best {brand} phones equal to ${equal_price} are : \n {(product_names_str)}"
                else:
                    return f"No {brand} products found equal to ${equal_price}."
            else:
                return f"No {brand} products found equal to ${equal_price}."
            
        # ! No price range but Brand included
        elif brand != '' and price_match == None:
            relevant_products = merged_df

            # Sort products by seller score
            if 'seller wise' in user_query.lower() or 'seller score' in user_query.lower():
                if 'worst' in user_query.lower() or 'bad' in user_query.lower() or 'not good' in user_query.lower() or 'terrible' in user_query.lower():
                    relevant_products = relevant_products.sort_values(by='Seller Score', ascending=True)
                else:
                    relevant_products = relevant_products.sort_values(by='Seller Score', ascending=False)

            # Sort products by review count
            elif 'review count' in user_query.lower():
                if 'worst' in user_query.lower() or 'bad' in user_query.lower() or 'not good' in user_query.lower() or 'terrible' in user_query.lower() or 'least' in user_query.lower() or 'minimum' in user_query.lower() or 'less' in user_query.lower():
                    relevant_products = relevant_products.sort_values(by='Total Reviews', ascending=True)
                else:
                    relevant_products = relevant_products.sort_values(by='Total Reviews', ascending=False)

             # Sort products by price
            elif 'sort by price' in user_query.lower() or 'based on price' in user_query.lower() or 'sorted by price' in user_query.lower():
                if 'worst' in user_query.lower() or 'bad' in user_query.lower() or 'not good' in user_query.lower() or 'terrible' in user_query.lower() or 'least' in user_query.lower() or 'minimum' in user_query.lower() or 'less' in user_query.lower() or 'ascending' in user_query.lower() or 'low to high' in user_query.lower():
                    relevant_products = relevant_products.sort_values(by='Price', ascending=True)
                else:
                    relevant_products = relevant_products.sort_values(by='Price', ascending=False)
            
            # Sort products by product score 
            else:
                # relevant_products = relevant_products.sort_values(by='Score', ascending=False)
                if 'worst' in user_query.lower() or 'bad' in user_query.lower() or 'not good' in user_query.lower() or 'terrible' in user_query.lower():
                    relevant_products = relevant_products.sort_values(by='Score', ascending=True)
                else:
                    relevant_products = relevant_products.sort_values(by='Score', ascending=False)
            
            # Extract product names
            # product_names = relevant_products['Name'].tolist()
            # product_names = [name for name in relevant_products['Name'].tolist() if brand in name and color in name]
            # product_names = [name for name in relevant_products['Name'].tolist() if brand.lower() in name.lower() and color.lower() in name.lower()]
            
            # product_names = [(row['Name'], row['Url']) for index, row in relevant_products.iterrows() if brand.lower() in row['Name'].lower() and color.lower() in row['Name'].lower() and ( ram_input.lower() in row['Name'].lower() or ram_input.lower() in row['Specs'].lower()  or  ram_input2.lower() in row['Name'].lower() or ram_input2.lower() in row['Specs'].lower() ) 
                            #  and name_input in row['Name'].lower()]

            if equalRating == -1:
                product_names = [(row['Name'], row['Url']) for index, row in relevant_products.iterrows() if brand.lower() in row['Name'].lower() and color.lower() in row['Name'].lower() and ( ram_input.lower() in row['Name'].lower() or ram_input.lower() in row['Specs'].lower()  or  ram_input2.lower() in row['Name'].lower() or ram_input2.lower() in row['Specs'].lower() or any(element in row['Name'] for element in ram_range_input) or any(element in row['Specs'] for element in ram_range_input) )
                                and ( rom_input.lower() in row['Name'].lower() or rom_input.lower() in row['Specs'].lower()  or  rom_input2.lower() in row['Name'].lower() or rom_input2.lower() in row['Specs'].lower() )
                                and ( mp_input in row['Name'].lower() or mp_input in row['Specs'].lower() or mp_input2 in row['Name'].lower() or mp_input2 in row['Specs'].lower() or any(element in row['Name'].lower() for element in mp_above_input) or any(element in row['Specs'].lower() for element in mp_above_input) or any(element in row['Name'].lower() for element in mp_above_input2) or any(element in row['Specs'].lower() for element in mp_above_input2)   or   any(element in row['Name'].lower() for element in mp_below_input) or any(element in row['Specs'].lower() for element in mp_below_input) or any(element in row['Name'].lower() for element in mp_below_input2) or any(element in row['Specs'].lower() for element in mp_below_input2)  ) 
                                #   and ( mp_input in row['Name'].lower() or mp_input in row['Specs'].lower() or mp_input2 in row['Name'].lower() or mp_input2 in row['Specs'].lower() ) 
                                and overRating < row['Score'] and underRating > row['Score']  and name_input in row['Name'].lower() ]
            else:
                product_names = [(row['Name'], row['Url']) for index, row in relevant_products.iterrows() if brand.lower() in row['Name'].lower() and color.lower() in row['Name'].lower() and ( ram_input.lower() in row['Name'].lower() or ram_input.lower() in row['Specs'].lower()  or  ram_input2.lower() in row['Name'].lower() or ram_input2.lower() in row['Specs'].lower() or any(element in row['Name'] for element in ram_range_input) or any(element in row['Specs'] for element in ram_range_input) )
                                and ( rom_input.lower() in row['Name'].lower() or rom_input.lower() in row['Specs'].lower()  or  rom_input2.lower() in row['Name'].lower() or rom_input2.lower() in row['Specs'].lower() )
                                and ( mp_input in row['Name'].lower() or mp_input in row['Specs'].lower() or mp_input2 in row['Name'].lower() or mp_input2 in row['Specs'].lower() or any(element in row['Name'].lower() for element in mp_above_input) or any(element in row['Specs'].lower() for element in mp_above_input) or any(element in row['Name'].lower() for element in mp_above_input2) or any(element in row['Specs'].lower() for element in mp_above_input2)   or   any(element in row['Name'].lower() for element in mp_below_input) or any(element in row['Specs'].lower() for element in mp_below_input) or any(element in row['Name'].lower() for element in mp_below_input2) or any(element in row['Specs'].lower() for element in mp_below_input2)  ) 
                                #   and ( mp_input in row['Name'].lower() or mp_input in row['Specs'].lower() or mp_input2 in row['Name'].lower() or mp_input2 in row['Specs'].lower() ) 
                                and overRating < row['Score'] and underRating > row['Score']  and name_input in row['Name'].lower() and equalRating == row['Score'] ]
            

            if product_names != []:
                # product_names_str = ' \n '.join(product_names)

                product_names_str = ''
                for index, name in enumerate(product_names):
                    if index == number:
                            break
                    # product_names_str += f'<br /> {index+1} : {name}.\n '
                    # product_names_str += f'<br /> {index+1} : <a href="{name}">{name}.</a>\n '
                    product_names_str += f'<br /> {index+1} : <a href="{name[1]}">{name[0]}.</a>\n '

                # return f"Based on user ratings and price, the best {brand} phones are {', '.join(product_names)}."
                return f"Based on user ratings and price, the best {brand} phones are : \n {(product_names_str)}"
            else:
                return f"No {brand} products found."
        
        # ! No Price or Brand
        # elif brand == '' and price_match == None and 'best' in user_query.lower() and 'phone' in user_query.lower():
        elif brand == '' and price_match == None and ('phone' in user_query.lower() or 'product' in user_query.lower() ):
            relevant_products = merged_df

            # Sort products by seller score
            if 'seller wise' in user_query.lower() or 'seller score' in user_query.lower():
                if 'worst' in user_query.lower() or 'bad' in user_query.lower() or 'not good' in user_query.lower() or 'terrible' in user_query.lower():
                    relevant_products = relevant_products.sort_values(by='Seller Score', ascending=True)
                else:
                    relevant_products = relevant_products.sort_values(by='Seller Score', ascending=False)

            # Sort products by review count
            elif 'review count' in user_query.lower():
                if 'worst' in user_query.lower() or 'bad' in user_query.lower() or 'not good' in user_query.lower() or 'terrible' in user_query.lower() or 'least' in user_query.lower() or 'minimum' in user_query.lower() or 'less' in user_query.lower():
                    relevant_products = relevant_products.sort_values(by='Total Reviews', ascending=True)
                else:
                    relevant_products = relevant_products.sort_values(by='Total Reviews', ascending=False)

            # Sort products by price
            elif 'sort by price' in user_query.lower() or 'based on price' in user_query.lower() or 'sorted by price' in user_query.lower():
                if 'worst' in user_query.lower() or 'bad' in user_query.lower() or 'not good' in user_query.lower() or 'terrible' in user_query.lower() or 'least' in user_query.lower() or 'minimum' in user_query.lower() or 'less' in user_query.lower() or 'ascending' in user_query.lower() or 'low to high' in user_query.lower():
                    relevant_products = relevant_products.sort_values(by='Price', ascending=True)
                else:
                    relevant_products = relevant_products.sort_values(by='Price', ascending=False)    
            
            # Sort products by product score 
            else:
                if 'worst' in user_query.lower() or 'bad' in user_query.lower() or 'not good' in user_query.lower() or 'terrible' in user_query.lower():
                    relevant_products = relevant_products.sort_values(by='Score', ascending=True)
                else:
                    relevant_products = relevant_products.sort_values(by='Score', ascending=False)
            
                
            # product_names = relevant_products['Name'].tolist()
            # product_urls = relevant_products['Url'].tolist()

            if equalRating == -1:
                product_names = [(row['Name'], row['Url']) for index, row in relevant_products.iterrows() if brand.lower() in row['Name'].lower() and color.lower() in row['Name'].lower() and ( ram_input.lower() in row['Name'].lower() or ram_input.lower() in row['Specs'].lower()  or  ram_input2.lower() in row['Name'].lower() or ram_input2.lower() in row['Specs'].lower() or any(element in row['Name'] for element in ram_range_input) or any(element in row['Specs'] for element in ram_range_input) )
                                and ( rom_input.lower() in row['Name'].lower() or rom_input.lower() in row['Specs'].lower()  or  rom_input2.lower() in row['Name'].lower() or rom_input2.lower() in row['Specs'].lower() )
                                and ( mp_input in row['Name'].lower() or mp_input in row['Specs'].lower() or mp_input2 in row['Name'].lower() or mp_input2 in row['Specs'].lower() or any(element in row['Name'].lower() for element in mp_above_input) or any(element in row['Specs'].lower() for element in mp_above_input) or any(element in row['Name'].lower() for element in mp_above_input2) or any(element in row['Specs'].lower() for element in mp_above_input2)   or   any(element in row['Name'].lower() for element in mp_below_input) or any(element in row['Specs'].lower() for element in mp_below_input) or any(element in row['Name'].lower() for element in mp_below_input2) or any(element in row['Specs'].lower() for element in mp_below_input2)  ) 
                                #   and ( mp_input in row['Name'].lower() or mp_input in row['Specs'].lower() or mp_input2 in row['Name'].lower() or mp_input2 in row['Specs'].lower() ) 
                                and overRating < row['Score'] and underRating > row['Score']  and name_input in row['Name'].lower() ]
            else:
                product_names = [(row['Name'], row['Url']) for index, row in relevant_products.iterrows() if brand.lower() in row['Name'].lower() and color.lower() in row['Name'].lower() and ( ram_input.lower() in row['Name'].lower() or ram_input.lower() in row['Specs'].lower()  or  ram_input2.lower() in row['Name'].lower() or ram_input2.lower() in row['Specs'].lower() or any(element in row['Name'] for element in ram_range_input) or any(element in row['Specs'] for element in ram_range_input) )
                                and ( rom_input.lower() in row['Name'].lower() or rom_input.lower() in row['Specs'].lower()  or  rom_input2.lower() in row['Name'].lower() or rom_input2.lower() in row['Specs'].lower() )
                                and ( mp_input in row['Name'].lower() or mp_input in row['Specs'].lower() or mp_input2 in row['Name'].lower() or mp_input2 in row['Specs'].lower() or any(element in row['Name'].lower() for element in mp_above_input) or any(element in row['Specs'].lower() for element in mp_above_input) or any(element in row['Name'].lower() for element in mp_above_input2) or any(element in row['Specs'].lower() for element in mp_above_input2)   or   any(element in row['Name'].lower() for element in mp_below_input) or any(element in row['Specs'].lower() for element in mp_below_input) or any(element in row['Name'].lower() for element in mp_below_input2) or any(element in row['Specs'].lower() for element in mp_below_input2)  ) 
                                #   and ( mp_input in row['Name'].lower() or mp_input in row['Specs'].lower() or mp_input2 in row['Name'].lower() or mp_input2 in row['Specs'].lower() ) 
                                and overRating < row['Score'] and underRating > row['Score']  and name_input in row['Name'].lower() and equalRating == row['Score'] ]

            
            if not relevant_products.empty:
                
                # Use the string in the f-string
                if product_names != []:

                    # Create the string to join
                    # product_names_str = ' \n '.join(product_names)

                    product_names_str = ''
                    for index, name in enumerate(product_names):
                        if index == number:
                            break
                        # product_names_str += f'<br /> {index+1} : {name}.\n '
                        # product_names_str += f'<br /> {index+1} : <a href="{product_urls[index]}">{name}.</a>\n '
                        product_names_str += f'<br /> {index+1} : <a href="{name[1]}">{name[0]}.</a>\n '

                    # return f"Based on user ratings, the best phones are {', '.join(product_names)}."
                    return f"Based on user ratings, the recommended phones are : \n {product_names_str}"
                else:
                    return f"No products found."
            else:
                return f"No products found."

        # ! Averages
        elif 'average ' in user_query.lower() and 'price' in user_query.lower():
            avg = 0
            avg = (merged_df['Price'].sum()) / len(merged_df['Price'])

            return f'Average Price per Product: ${avg} \n'

        elif 'average ' in user_query.lower() and 'rating' in user_query.lower():
            avg = 0
            avg = (merged_df['Score'].sum()) / len(merged_df['Score'])

            return f'Average Rating per Product: {avg} \n'

        elif 'average ' in user_query.lower() and 'review count' in user_query.lower():
            avg = 0
            avg = (merged_df['Total Reviews'].sum()) / len(merged_df['Total Reviews'])

            return f'Average Review Count per Product: {avg} \n'

        elif 'average ' in user_query.lower() and 'questions asked' in user_query.lower():
            avg = 0
            avg = (merged_df['Questions Asked'].sum()) / len(merged_df['Questions Asked'])

            return f'Average Questions asked per Product: {avg} \n'
        
        elif 'total ' in user_query.lower() and 'questions asked' in user_query.lower():
            sum = (merged_df['Questions Asked'].sum()) 

            return f'Total Questions asked per Product: {sum} \n'


        elif 'hello' in user_query.lower():
            return f'Hello, I am DarazBot! <br> I provide phones recommendations.'
        
        elif 'bye' in user_query.lower():
            return f'Goodbye, come back soon!'
    

        else:
            return "Sorry, I couldn't understand your query."


app = Flask(__name__)

df = merged_df

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
        

# * Define Product and Review models
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    price = db.Column(db.Float, nullable=True)
    score = db.Column(db.Float, nullable=True)
    url = db.Column(db.String(255), nullable=True)
    questions_asked = db.Column(db.Integer)  
    total_reviews = db.Column(db.Integer)
    seller_score = db.Column(db.Integer)
    company = db.Column(db.String(255), nullable=True) 
    reviews = db.relationship('Review', backref='product', lazy=True)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)


# * Function to convert DataFrame to database records
def convert_df_to_db():
    # * Drop and recreate all tables
    db.drop_all()
    db.create_all()

    # * Iterate through each row in the DataFrame and add records to the database
    for _, row in merged_df.iterrows():
        product = Product(name=row['Name'], price=row['Price'], score=row['Score'], url=row['Url'], questions_asked=row['Questions Asked'], seller_score=row['Seller Score'], total_reviews=row['Total Reviews'], company=row['Company'])
        db.session.add(product)
        db.session.commit()

        # * Add reviews for the product
        for review_content in row['Review']:
            review = Review(content=review_content, product=product)
            db.session.add(review)
            db.session.commit()


# comment this
@app.route('/search', methods=['POST', 'GET']) 
def search():
    if request.method == 'POST':
        user_input = request.form['nm']
        return f'<p style="white-space: pre;">{chatbot(user_input)}</p>'
    else:
        return render_template('search.html')
    

@app.route("/process", methods=["POST"])
def process():
    user_message = request.form.get('user_message', ' ')
    bot_response = chatbot(user_message)
    return {'bot_response': bot_response, 'user_input': user_message}

# ? For DataFrame
# @app.route('/')
# def dashboard1():
#     avg_price = np.mean(df['Price'].astype(float).tolist())
#     avg_rating = np.mean(df['Score'].astype(float).tolist())
#     review_counts = [len(reviews) for reviews in df['Review']]
#     avg_reviews = np.mean(review_counts)
#     total_listing = len(merged_df)
#     total_questions_asked = np.sum(df['Questions Asked'])

#     relevant_products = merged_df
#     relevant_products = relevant_products.sort_values(by='Score', ascending=False)

#     # product_names = relevant_products['Name'].tolist()
#     product_names = [(row['Name'], row['Score'], row['Price'], row['Url']) for index, row in relevant_products.iterrows()][:5]
        

#     return render_template('chat.html', total_listing=total_listing, price=avg_price, rating=avg_rating, reviews=avg_reviews, questions=total_questions_asked, products_list=product_names)

# ? For DataBase
@app.route('/')
def dashboard1():
    avg_price = round(db.session.query(db.func.avg(Product.price)).scalar(), 2)
    avg_rating = round(db.session.query(db.func.avg(Product.score)).scalar(), 2)
    review_counts = [len(product.reviews) for product in Product.query.all()]
    avg_reviews = round(np.mean(review_counts), 2)
    total_listing = Product.query.count()
    total_questions_asked = db.session.query(db.func.sum(Product.questions_asked)).scalar()

    relevant_products = Product.query.order_by(Product.score.desc()).limit(5).all()
    product_names = [(product.name, product.score, product.price, product.url) for product in relevant_products]

    return render_template('chat.html', total_listing=total_listing, price=avg_price,
                           rating=avg_rating, reviews=avg_reviews, questions=total_questions_asked,
                           products_list=product_names)


if __name__ == '__main__':

    # * Database creation
    with app.app_context():
        db.create_all()
        convert_df_to_db()

    app.run(debug=True)
