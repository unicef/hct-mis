from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

default_url = "http://localhost:8080"
url = input(f"Url of page (default is {default_url}):")
if not url:
    url = default_url

driver = Chrome()

driver.get(url)
label = input("Choose the label (default it data-cy):")
if not label:
    label = "data-cy"


def printing(what: str) -> None:
    for ii in ids:
        data_cy_attribute = ii.get_attribute("data-cy")  # type: ignore
        var_name = [i.capitalize() for i in data_cy_attribute.lower().replace("-", " ").split(" ")]
        method_name = "get" + "".join(var_name)
        var_name[0] = var_name[0].lower()
        var_name = "".join(var_name)  # type: ignore
        if what == "Labels":
            print(f"{var_name} = '{ii.tag_name}[data-cy=\"{data_cy_attribute}\"]'")
        if what == "Methods":
            print(f"def {method_name}(self) -> WebElement: \n\treturn self.wait_for(self.{var_name})\n")


while 1:
    input("Open the page and press Enter")
    ids = driver.find_elements(By.XPATH, f"//*[@{label}]")
    printing("Labels")
    print("\n")
    printing("Methods")
