import json
import re
import os
import pandas as pd


class PromptFactory:
    def __init__(self, sku, context, num_recs=5, load_catalog=False):        
        self.sku = sku
        self.context = context
        self.num_recs = num_recs
        if self.num_recs < 1 or self.num_recs > 10:
            raise ValueError("num_recs must be between 1 and 10")
        self.catalog = []       

        # if load_catalog:
        #     data_folder = os.path.join(os.path.dirname(__file__), "..", "..", "data")
        #     print(data_folder)
        #     catalog_file = "{}/product_catalog.csv".format(data_folder)
        #     if not os.path.exists(catalog_file):
        #         raise FileNotFoundError("Catalog file not found: {}".format(catalog_file))
        #     df = OpenRouterRec.tryload_catalog(catalog_file)
        #     self.catalog = df

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
            print(str(e))
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
                    print(f"Invalid JSON: {array}")
            return []
        except Exception as e:
            print(e)
            return []


    def catalog_to_json(self) -> str:
        if len(self.catalog) == 0:
            return "[]"
        return json.dumps(self.catalog, indent=2)
    
    
    def prompt(self) -> str:        
        print("generating prompt: {}".format(self.sku))

        return_type1 = ExampleRecs.rt1()     
      
        prompt = """       
        
        # PERSONA:
        
        You are an ecommerce store manager with 20 years of experience providing product
        recommendations to customers. You have a deep understanding of the full product catalog in your store.        
        When a customer buys X you recommended Y because they are often bought together or in succession.
        
        # INSTRUCTIONS

        Given the <query> make a list of {} product recommendations that compliment the query. 
        Return only products from the <context> provided.
    
        Consider your persona before making your list of {} recommendations. 
        Only return products that exist in the <context> provided.

        Here is the user query:        
        <query>
        {}
        </query>        
        """.format(self.num_recs, self.num_recs, self.sku)       

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

        prompt += """
            # FINAL INSTRUCTIONS
            
            1) Observe the user <query>.
            2) Find recommended products in the <context> provided and make a list of {} recommendations that compliment the query.
            3) The products recommended should be products a customer would buy after they have purchased the product from <query>.
            4) Return recommendations in a JSON array similar to the Example Result Format.
            5) Double check the potential return data structure for empty fields, invalid values or errors.
            6) Never explain yourself, no small talk, just return the final data in the correct array format. 
            7) Your final response should only be an array of recommendations in JSON format.
            8) Never say 'Based on the provided query' or 'I have determined'. 
            9) Never explain yourself.
            10) Return in JSON.
            
        """.format(self.num_recs)

        #print(prompt)
        
        return prompt
    

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