from parser import get_estates_info
from eda_cleaner import clean_data

get_estates_info("./dataset/pronajem", "estates_info_rent.csv")
get_estates_info("./dataset/prodej", "estates_info_sale.csv")  

clean_data("estates_info_rent.csv")
clean_data("estates_info_sale.csv")