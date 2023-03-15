from bs4 import BeautifulSoup
from fake_headers import Headers
import requests
import json

HOST = "https://spb.hh.ru"
SEARCH = "/search/vacancy?area=1&area=2&text=python"
MAIN = f"{HOST}{SEARCH}"


vacancies_list = []


def get_headers():
    return Headers(browser="chrome", os="win").generate()


def get_text(url):
    return requests.get(url, headers=get_headers()).text


def scrapping_vacancy():
    soup = BeautifulSoup(get_text(MAIN), "lxml")
    articles_list = soup.find_all("a", class_="serp-item__title")

    for vacancy in articles_list:
        link = vacancy["href"]
        response_link = requests.get(link, headers=get_headers())
        parse_link = BeautifulSoup(response_link.text, "lxml")
        vacancy_title = parse_link.find(attrs={"data-qa": "vacancy-title"}).text
        vacancy_desc = parse_link.find("div", {"data-qa": "vacancy-description"}).text
        if not vacancy_desc:
            continue
        if ("Django" or "Flask") in vacancy_desc:
            link = link

            salary = parse_link.find(
                "span", class_="bloko-header-section-2 bloko-header-section-2_lite"
            ).text
            if not salary:
                continue

            city = parse_link.find("p", {"data-qa": "vacancy-view-location"})
            if not city:
                city = parse_link.find("span", {"data-qa": "vacancy-view-raw-address"})
                if not city:
                    continue

            company_name = parse_link.find(
                "a", {"data-qa": "vacancy-company-name"}
            ).text
            if not company_name:
                continue
            vacancies_list.append(
                {
                    "Название вакансии: ": vacancy_title,
                    "Ссылка на вакансию: ": link,
                    "Зарплата: ": salary,
                    "Название компании: ": company_name,
                    "Город: ": city.text,
                }
            )


if __name__ == "__main__":
    scrapping_vacancy()

    with open("vacancies.json", "w", encoding="utf-8") as json_file:
        json.dump(vacancies_list, json_file, indent=2, ensure_ascii=False)
