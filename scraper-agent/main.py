from portia import PlanBuilderV2, Config, Portia, StepOutput, Input, PlanRun
from bs4 import BeautifulSoup
import httpx
import asyncio
from pydantic import BaseModel

def retrieve_website(url: str) -> str:
    response = httpx.get(url, follow_redirects=True)
    return response.text


def extract_text_from_html(html: str, selectors: list[str] | None = None) -> str:
    soup = BeautifulSoup(html, "html.parser")
    if not selectors:
        return soup.get_text()
    else:
        return "\n".join([soup.select(selector)[0].get_text() for selector in selectors])

def selector_is_in_html(html: str, selector: str) -> bool:
    soup = BeautifulSoup(html, "html.parser")
    return len(soup.select(selector)) > 0

def extract_block_from_wikipedia_page(html: str, selector: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    start_element = soup.select_one(selector).parent # heading id is a child of the mw_heading div
    if not start_element:
        return ""
    extracted_texts = []
    # collect everything until the next heading
    for sibling in start_element.find_next_siblings():
        # Stop if a sibling element with the class 'mw_heading' is encountered
        if 'mw_heading' in sibling.get('class', []):
            break
        # Otherwise, extract its text
        extracted_texts.append(sibling.get_text(separator="\n", strip=True))

    return "\n".join(extracted_texts).strip()


class ScientistProfile(BaseModel):
    name: str
    birth_date: str
    death_date: str | None
    nationality: str
    most_known_for: str
    
    def __str__(self):
        return f"""Name: {self.name}
        Birth Date: {self.birth_date}
        Death Date: {self.death_date}
        Nationality: {self.nationality}
        Most Known For: {self.most_known_for}
        """


class Publication(BaseModel):
    title: str
    year: str | None
    
    def __str__(self):
        return f"""Title: {self.title}
        Year: {self.year}
        """

class Publications(BaseModel):
    publications: list[Publication]
    
    def __str__(self):
        return "\n".join([str(publication) for publication in self.publications])

portia = Portia(Config.from_default(storage_class="memory", default_log_level="CRITICAL"))


plan = (
    PlanBuilderV2("Scientist Scraper")
    .input(name="url", description="The URL of the website to scrape")
    .function_step(
        function=retrieve_website,
        args={"url": Input("url")},
        step_name="Retrieve Website"
        
    ).function_step(
        function=extract_text_from_html,
        args={"html": StepOutput("Retrieve Website")},
        step_name="Extract Text from HTML"
    )
    .if_(condition=selector_is_in_html,
         args={"html": StepOutput("Retrieve Website"), "selector": "#Publications"},
    )
    .function_step(function=extract_block_from_wikipedia_page,
                   args={"html": StepOutput("Retrieve Website"), "selector": "#Publications"},
                   step_name="Retrieve Publications"
    )
    .llm_step(
        task="Determine the publications of the scientist.",
        inputs=[StepOutput("Retrieve Publications")],
        output_schema=Publications,
        step_name="Analyze Publications"
    )
    .endif()
    .llm_step(
        task="Determine the scientist's profile.",
        inputs=[StepOutput("Extract Text from HTML")],
        output_schema=ScientistProfile,
        step_name="Analyze Website"
    )
    .build()
)

async def main() -> list[PlanRun]:
    websites = [
        "https://wikipedia.org/wiki/Ada_Lovelace",
        "https://wikipedia.org/wiki/Nikola_Tesla",
        "https://wikipedia.org/wiki/Albert_Einstein",
        "https://wikipedia.org/wiki/Isaac_Newton",
        "https://wikipedia.org/wiki/Galileo_Galilei",
        "https://wikipedia.org/wiki/Marie_Curie",
        "https://wikipedia.org/wiki/Richard_Feynman",
        "https://en.wikipedia.org/wiki/Brian_Cox_(physicist)",
        ]
    results = await asyncio.gather(*[portia.arun_plan(plan, plan_run_inputs={"url": url}) for url in websites])
    return results

if __name__ == "__main__":
    results = asyncio.run(main())
    for result in results:
        if result.outputs.final_output:
            print("--------------------------------")
            print(result.outputs.final_output.get_value())
            if publications := result.outputs.step_outputs.get("$step_4_output"):
                print(f"Number of publications: {len(publications.get_value().publications)}")
            else:
                print("No publications found")
