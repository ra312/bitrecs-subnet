import ast
import json
import re
import os
import pandas as pd
import bittensor as bt


class PromptFactory:
    """
    Creates a bitrecs prompt for a given SKU and context.

    Args:
        sku (str): The SKU to generate recommendations for.
        context (str): The context to generate recommendations from.
        num_recs (int): The number of recommendations to generate.
        load_catalog (bool): Whether to load the catalog from a file.
        debug (bool): Whether to trace write the prompts.
    
    """
    def __init__(self, sku, context, num_recs=5, load_catalog=False, debug=False):        
        self.sku = sku
        self.context = context
        self.num_recs = num_recs
        if self.num_recs < 1 or self.num_recs > 20:
            raise ValueError("num_recs must be between 1 and 20")        
        self.load_catalog = load_catalog
        self.debug = debug
        self.catalog = []

    
    def generate_prompt(self) -> str:

        bt.logging.info("PROMPT generating prompt: {}".format(self.sku))

        return_type1 = ExampleRecs.rt1()

        season = "fall/winter"
        persona = "Ecommerce Store Manager"        
      
        prompt = """
        # PERSONA:

        <persona>{}</persona>

        You are a {} with 20 years of experience providing product recommendations to customers.
        You are goal oriented and your goal is to increase average order value and conversion rate for the store.
        You have a deep understanding of the full product catalog in the store.
        When a customer buys X you recommended Y because they are often bought together or in succession.
        You have deep knowledge of the products in the store and know each product attribute and can provide accurate recommendations.
        You never show multiple colors or sizes of the same product in a set of recommendations.
        You produce a fair distribution of skus in the final list of recommendations.
        You also think outside the box and provide creative recommendations during different seasons or events.
        The current season is: <season>{}</season>.\n
        
        # INSTRUCTIONS

        Given the <query> make a list of {} product recommendations that compliment the query. 
        Return only products from the <context> provided.
    
        Consider your <persona> before making your list of {} recommendations. 
        Only return products that exist in the <context> provided.
        Very important you must return products that exist in the context only. 
        Do not hallucinate.

        Here is the user query:
        <query>
        {}
        </query>        
        """.format(persona, persona, season, self.num_recs, self.num_recs, self.sku)

        if self.context and len(self.context) > 10:
            prompt += """Here is the list of products you can select your recommendations from:
        <context>{}</context>        
        **Important** Only return products from the <context> provided.
        
        """.format(self.context)
        
        if 1==2:
            prompt += """

            # Example Result Format:
            {}        
            """.format(return_type1)

        #   prompt += """
        #     # FINAL INSTRUCTIONS
            
        #     1) Observe the user <query>.
        #     2) Find recommended products in the <context> provided and make a list of {} recommendations that compliment the query.
        #     3) The products recommended should be products a customer would buy before, along with, or after they have purchased the product from <query>.
        #     4) Return recommendations in a JSON array.
        #     5) The order of the recommendations is important. The first few recommendations should be the most relevant to the query.
        #     6) Be diverse in your recommendations. Do not recommend the same product multiple times or from the same class of products.
        #     7) Double check the potential return data structure for empty fields, invalid values or errors.
        #     8) Never explain yourself, no small talk, just return the final data in the correct array format. 
        #     9) Your final response should only be an array of recommendations in JSON format.
        #     10) Never say 'Based on the provided query' or 'I have determined'. 
        #     11) Never explain yourself.
        #     12) Return in JSON.

        # prompt += """
        #     # FINAL INSTRUCTIONS
            
        #     1) Observe the user <query>.
        #     2) Find recommended products in the <context> provided and make a list of {} recommendations that compliment the query.
        #     3) The products recommended should be products a customer would buy after they have purchased the product from <query>.
        #     4) Return recommendations in a JSON array.
        #     5) The order of the recommendations is important. The first recommendation should be the most relevant to the query.
        #     6) Double check the potential return data structure for empty fields, invalid values or errors or invalid string quotes or characters.
        #     7) Never explain yourself, no small talk, just return the final data in the correct array format. 
        #     8) Your final response should only be an array of recommendations in JSON format.
        #     9) Never say 'Based on the provided query' or 'I have determined'. 
        #     10) Never explain yourself.
        #     11) Return in JSON.

        # prompt += """\n
        #     # FINAL INSTRUCTIONS
            
        #     1) Load <persona> and <context> into your memory.
        #     2) Observe the user <query>.
        #     3) Find recommended products in the <context> and make a list of {} recommended products that compliment the query.
        #     4) The products recommended could be products a customer would buy after they have purchased the product from <query>.
        #     5) The products recommended could also be products the customer would buy before they purchased the product from <query>.
        #     6) Think step by step and consider the customer journey.
        #     7) Return recommendations in a JSON array.
        #     8) The order of the recommendations is important. The first recommendation should be the most relevant to the <query>.
        #     9) Double check the potential return array for empty fields, invalid values or syntax errors or invalid string quotes or invalid characters.
        #     10) Never explain yourself, no small talk, just return the final data in the correct array format. 
        #     11) Your final response should only be an array of recommendations in JSON format.                        
        #     12) Do not alter the context JSON, return all fields as they are.
        #     13) Each recommendation should have a 'sku', 'name' and 'price' field.
        #     14) Never say 'Based on the provided query' or 'I have determined'. 
        #     15) Never explain yourself.
        #     16) You must return a JSON array with exacty {} elements, remember arrays are 0 indexed.
        #     17) Ensure all skus are unique in the final return JSON. My life depends on this. VERY IMPORTANT.
        #     18) Return in JSON.

        prompt += """\n
        # FINAL INSTRUCTIONS
        
        1) Load <persona> and <context> into your memory.
        2) Observe the user <query>.
        3) Find {} unique recommended products in the <context> that compliment the <query and return a unique set.
        4) The products recommended could be products a customer would buy **after** they have purchased the product from <query>.
        5) The products recommended could also be products the customer would buy **before** they purchased the product from <query>.
        6) Think step by step and consider the entire customer journey.        
        7) The order of the recommendations is important. The first recommendation should be the most relevant to the <query>.
        8) Double check the potential return array for empty fields, invalid values or syntax errors or invalid string quotes or invalid characters.
        9) Never explain yourself, no small talk, just return the final data in the correct array format. 
        10) Your final response should be a single JSON array of the recommendations.
        11) Do not alter the context JSON, return all fields as they are.
        12) Each recommendation should have a 'sku', 'name' and 'price' field.
        13) Each recommendation should be unique (use 'sku' as the key field for uniqueness).
        14) Never say 'Based on the provided query' or 'I have determined'. 
        15) Never explain yourself.
        16) assert each recommendation is unique ('sku' is the key).
        17) assert len(recommendations) == {}. If not, start over until it matches.
        18) Return in JSON.
            
            
        """.format(self.num_recs, self.num_recs)

        #print(prompt)
        #bt.logging.info("generated prompt: {}".format(prompt))
        prompt_length = len(prompt)
        bt.logging.info(f"LLM QUERY Prompt length: {prompt_length}")

        if self.debug:
            bt.logging.debug("Prompt: {}".format(prompt))

        return prompt
    

    @staticmethod
    def tryload_catalog(file_path: str, max_rows=10000) -> list:
        try:
            df = pd.read_csv(file_path)
            #WooCommerce Format
            columns = ["ID", "Type", "SKU", "Name", "Published", "Description", "In stock?", "Stock", "Categories"]            
            #Take only certain columns
            df = df[[c for c in columns if c in df.columns]]            
            #Clean HTML
            df['Description'] = df['Description'].str.replace(r'<[^<>]*>', '', regex=True)
            #Only take simple and variable products
            product_types = ["simple", "variable"]
            df = df[df['Type'].isin(product_types)]            
            #Final renaming of columns
            df = df.rename(columns={'In stock?': 'InStock', 'Stock': 'OnHand'})
            #Remove NaN
            df.fillna('', inplace=True)
            df = df.head(max_rows)
            df = df.to_dict(orient='records')
            return df
        except Exception as e:            
            bt.logging.error(str(e))
            return []
        

    @staticmethod
    def tryparse_llm(input_str: str) -> list:
        try:
            pattern = r'\[.*?\]'
            regex = re.compile(pattern, re.DOTALL)
            match = regex.findall(input_str)        
            for array in match:
                try:
                    llm_result = array.strip()
                    return json.loads(llm_result)
                except json.JSONDecodeError:                    
                    bt.logging.error(f"Invalid JSON in prompt factory: {array}")
            return []
        except Exception as e:
            bt.logging.error(str(e))
            return []
        

    # @staticmethod
    # def parse_llm(input_str: str) -> list:
    #     final_results = PromptFactory.tryparse_llm(input_str)
    #     for item in final_results:
    #         cleaned_item = str(item).replace("\\'", "'")  # Fix escaped single quotes            
    #         dictionary_item = ast.literal_eval(cleaned_item)
    #         if "name" in dictionary_item:
    #             dictionary_item["name"] = dictionary_item["name"].replace("'", "-")  # Remove single quotes
    #         recommendation = str(dictionary_item)
    #         final_results.append(recommendation)
    #     return final_results


    def catalog_to_json(self) -> str:
        if len(self.catalog) == 0:
            return "[]"
        return json.dumps(self.catalog, indent=2)



class ExampleRecs:
    
    def example_recs() -> str:
        e = """"
        
        #  Example Queries:
        
        - <query>MH01-S-Orange</query>
        - <query>MH01-XL-Black</query>
        - <query>Chaz Kangeroo Hoodie - XL, Black</query>
        - <query>Chaz Kangeroo Hoodie - S, Orange</query>
        - <query>MS04-XL-Red</query>
        - <query>MS04-XS-Black</query>
        - <query>MS07-XL-Black</query>
        - <query>MS12</query>
        - <query>MT02-L-White</query>
        - <query>WS09-S-Red</query>
        - <query>WS09-S-White</query>
        - <query>WSH04-32-Green</query>
        - <query>WSH04-32-Orange</query>
        - <query>Breathe-Easy Tank</query>
        - <query>Breathe-Easy Tank - L, Purple</query>    
        - <query>Sprite Foam Yoga Brick</query>
        - <query>24-WG084</query>
        - <query>24-UG03</query>
        \n
        """
        return e
    
    
    def rt1() -> str:
        return """ 
        [
            {
                "sku": "MH01-S-Orange",         
                "name": "Chaz Kangeroo Hoodie - S, Orange",                
                "price" 52.00
            },
            {
                "sku": "MH01-XL-Black",         
                "name": "Chaz Kangeroo Hoodie - XL, Black",                
                "price" 52.00        
            },
            {
                "sku": "MS04-XL-Red",         
                "name": "Gobi HeatTec&reg; Tee - XL, Red",                
                "price" 29.00        
            },
            {
                "sku": "MS04-XS-Black",         
                "name": "Gobi HeatTec&reg; Tee - XS, Black",                
                "price" 29.00        
            },
            {
                "sku": "MS12",         
                "name": "Atomic Endurance Running Tee (Crew-Neck)",                
                "price" 29.00        
            },
            {
                "sku": "MT02-L-White",         
                "name": "Tristan Endurance Tank - L, White",                
                "price" 29.00           
            },
            {
                "sku": "WS09-S-Red",         
                "name": "Tiffany Fitness Tee - S, Red",                
                "price" 28.00           
            },
            {
                "sku": "WSH04-32-Green",         
                "name": "Artemis Running Short - 32, Green",                
                "price" 45.00           
            },
            {
                "sku": "WT09",         
                "name": "Breathe-Easy TanK",                
                "price" 34.00           
            },
            {
                "sku": "WT09-L-Purple",         
                "name": "Breathe-Easy Tank - L, Purple",                
                "price" 34.00           
            },
            {
                "sku": "24-WG084",         
                "name": "Sprite Foam Yoga Brick",                
                "price" 5.00           
            },
            {
                "sku": "24-UG03",         
                "name": "Harmony Lumaflex&trade; Strength Band Kit",                
                "price" 22.00           
            }

        ]"""