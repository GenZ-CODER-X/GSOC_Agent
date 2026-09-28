import time
from bs4 import BeautifulSoup
import requests

def org_gsoc_page(org_name:str):
    url=f"https://www.gsocorganizations.dev/organization/{org_name}/"
    start_time=time.perf_counter()

    #1. Web Ingestion
    response=requests.get(
        url,
        timeout=20,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    response.raise_for_status()
    ingestion_end=time.perf_counter()
    #2 parse HTML
    soup=BeautifulSoup(response.text,"html.parser")
    print(type(soup))
    text=soup.get_text(separator="\n",strip=False)
    print(text)
    parsing_end=time.perf_counter()
    

if __name__ == "__main__":
    org_gsoc_page("3dtk")

    