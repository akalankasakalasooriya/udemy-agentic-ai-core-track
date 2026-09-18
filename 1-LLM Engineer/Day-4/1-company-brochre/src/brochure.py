import json

from IPython.display import Markdown, display

from .llm import call_llm
from .scraper import fetch_website_contents, fetch_website_links

link_system_prompt = """
You are provided with a list of links found on a webpage.
Decide which links are most relevant for a brochure about the company,
such as About, Company, or Careers/Jobs pages.
Skip Terms of Service, Privacy and email links.


Respond in JSON as in this example:
{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page", "url": "https://another.full.url/careers"}
    ]
}
"""

brochure_system_prompt = """
You are an assistant that analyzes the contents of several relevant pages from a company website
and creates a short brochure about the company for prospective customers, investors and recruits.
Respond in markdown without code blocks.
Include details of company culture, customers and careers/jobs if you have the information.
"""


def select_relevant_links(url):
    user_prompt = (
        f"Here is the list of links on the website {url} - "
        "respond with the full https URL in JSON format. "
        "Some links might be relative.\n\n"
    )
    user_prompt += "\n".join(fetch_website_links(url))
    result = call_llm(
        [
            {"role": "system", "content": link_system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        json_mode=True,
    )
    return json.loads(result)


def fetch_all_relevant_contents(url):
    result = f"## Landing Page:\n\n{fetch_website_contents(url)}\n## Relevant Links:\n"
    for link in select_relevant_links(url)["links"]:
        result += f"\n\n### Link: {link['type']}\n"
        result += fetch_website_contents(link["url"])
    return result


def create_brochure(company_name, url):
    user_prompt = (
        f"You are looking at a company called: {company_name}\n"
        "Here are the contents of its landing page and other relevant pages; "
        "use this information to build a short brochure in markdown without code blocks.\n\n"
    )
    user_prompt += fetch_all_relevant_contents(url)
    brochure = call_llm(
        [
            {"role": "system", "content": brochure_system_prompt},
            {"role": "user", "content": user_prompt[:5000]},
        ]
    )
    display(Markdown(brochure))
