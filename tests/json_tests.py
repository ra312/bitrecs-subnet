import json
import json_repair


def test_parsing():
    single_rec = "{'sku': '24-UG01', 'name': 'Quest Lumaflex&trade; Band', 'price': '19'}"
    single_rec2 = "{'sku': '24-UG02', 'name': 'Pursuit Lumaflex&trade; Tone Band', 'price': '16'}"
    single_rec3 = "{'sku': '24-MG05', 'name': 'Cruise Dual Analog Watch', 'price': '55'}"
    multi_rec = [single_rec, single_rec2, single_rec3]

    # final_results = []
    # results = [str(r) for r in multi_rec]
    # for r in results:
    #     r = r.rstrip('"').lstrip('"')
    #     final_results.append(r)

    # print(final_results)
    #json_string = json.dumps(multi_rec, indent=4)

    json_string = [item.replace("'", '"') for item in multi_rec]
    print(json_string)  
    # thing = json.loads(json_string)
    # print(thing)  

    #@results = [eval(item) for item in results]
    final_recs = [json.loads(idx.replace("'", '"')) for idx in multi_rec]
    print(final_recs)
    #results = [literal_eval(item) for item in results]

    #thing = json.loads(final_results)
    # assert thing["sku"] == "24-UG01"
    # assert thing["name"] == "Quest Lumaflex&trade; Band"
    # assert thing["price"] == "19"
    print("Test 1 complete")


def test_parsing2():
    results =  ["{'sku': '24-WG088', 'name': 'Sprite Foam Roller'}",
                 "{'sku': '24-WG084', 'name': 'Sprite Foam Yoga Brick'}",
                   "{'sku': '24-UG01', 'name': 'Quest Lumaflex&trade; Band'}", 
                   '{\'sku\': \'24-UG05\', \'name\': "Go-Get\'r Pushup Grips"}', 
                   "{'sku': '24-UG02', 'name': 'Pursuit Lumaflex&trade; Tone Band'}", 
                   "{'sku': '24-UG07', 'name': 'Dual Handle Cardio Ball'}"]

    final = []
    for idx in results:
        #print(idx)      
        fixed1 = json_repair.repair_json(idx, logging=False)  
        print(f"fixed: {fixed1}")
        product = json_repair.loads(fixed1)
        #fixed = json_repair.loads(idx, logging=False)
        #print(fixed)
        final.append(product)

    #final_recs = [json.loads(idx.replace("'", '"')) for idx in fixed]
    #final_recs = [json.loads(idx.replace("'", '"')) for idx in response.results]

    #print(final_recs)
    print("FINAL RESULTS")
    print(final)

    assert len(results) == len(final)

if __name__ == "__main__":
    #test_parsing()
    test_parsing2()
    print("JSON Tests done.")