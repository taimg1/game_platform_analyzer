import re
import asyncio
from datetime import datetime, timezone
from typing import Annotated, Set, List
from fastapi import Depends
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup, Tag
from untils.gemini_api import GeminiApiDependency
import json


class WebScraper:
    def __init__(self, gemini_api: GeminiApiDependency):
        self.gemini_api = gemini_api

    async def get_page_html(self, url: str) -> str:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=90000)

            try:
                await page.wait_for_selector(
                    "button.button--big.age-gate__button", timeout=10000
                )
                await page.click("button.button--big.age-gate__button")
                await page.wait_for_load_state("networkidle")
            except Exception as e:
                print(f"Age gate button not found or error clicking: {e}")

            html = await page.content()
            await browser.close()
            return html

    def delete_trash_data_from_html(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup.find_all(
            ["script", "style", "header", "footer", "aside", "form"]
        ):
            tag.decompose()

        for nav in soup.find_all("nav"):
            if not isinstance(nav, Tag):
                continue

            is_pagination = False
            nav_attributes = f"{nav.get('class', '')} {nav.get('id', '')} {nav.get('aria-label', '')} {nav.get('role', '')}".lower()
            if any(keyword in nav_attributes for keyword in ["pagination", "pager"]):
                is_pagination = True
            if not is_pagination:
                links = nav.find_all("a")
                if 0 < len(links) < 20:
                    for link in links:
                        if not isinstance(link, Tag):
                            continue
                        link_text = link.get_text(strip=True).lower()
                        aria_label_value = link.get("aria-label", "")
                        link_aria_label = (
                            " ".join(aria_label_value)
                            if isinstance(aria_label_value, list)
                            else str(aria_label_value)
                        ).lower()

                        pagination_keywords = [
                            "next",
                            "previous",
                            "back",
                            "last",
                            "first",
                            ">",
                            "»",
                            "<",
                            "«",
                        ]
                        if (
                            any(keyword in link_text for keyword in pagination_keywords)
                            or any(
                                keyword in link_aria_label
                                for keyword in ["next page", "previous page"]
                            )
                            or link_text.isdigit()
                        ):
                            is_pagination = True
                            break
            if not is_pagination:
                nav.decompose()

        return str(soup)

    def __clean_json_markdown(self, text: str) -> str:
        pattern = r"```(?:json)?(.*?)```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()

    def clean_json(self, obj):
        if isinstance(obj, dict):
            return {k: self.clean_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.clean_json(v) for v in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return obj

    async def extract_game_links_with_gemini(
        self,
        clean_html: str,
        target_count: int,
        current_url: str,
    ) -> dict:
        prompt = f"""
You are a highly intelligent web scraping assistant. Your task is to analyze the provided HTML of a game store's category page and extract two things: all direct links to individual game detail pages and a way to navigate to the next page of results.

Instructions:
1.  Identify and return a list of **ALL** game detail URLs found on the page. A game URL typically leads to a page dedicated to a single game.
    -   Do not include links to news, DLCs without a base game, or developer pages.
    -   Return as many game URLs as you can find on the page, up to a maximum of {target_count}.
    -   IMPORTANT: If an extracted URL is a relative path (e.g., starts with '/'), you MUST combine it with the base URL of the current page to form an absolute URL. The current page URL is: {current_url}
2.  Find the pagination element to go to the NEXT page or 'Load More'. Provide a unique and reliable CSS selector for it.
    -   Prioritize elements with text like 'Next', '>', '>>', `aria-label="Next page"`, or especially 'Load More'.
    -   If there's no 'Next' button but there are numbered pages, provide the selector for the next available page number.
    -   If you cannot find a way to get to the next page, return null.

Return a single, valid JSON object with the following keys:
-   "game_urls": (list[str]) A list of all game URLs found.
-   "next_page_selector": (str or null) The CSS selector for the next page/load more element, or null if not found.

Cleaned HTML:
{clean_html}
"""

        response_text = await self.gemini_api.generate_response(prompt)
        if not response_text:
            raise ValueError("Failed to get a valid response from Gemini API.")
        response_text = self.__clean_json_markdown(response_text)
        try:
            response_json = json.loads(response_text)
            return {
                "game_urls": response_json.get("game_urls", []),
                "next_page_selector": response_json.get("next_page_selector"),
            }
        except json.JSONDecodeError:
            print("Failed to parse Gemini response as JSON:", response_text)
            return {"game_urls": [], "next_page_selector": None}

    async def collect_game_urls(self, start_url: str, limit: int = 50) -> list[str]:
        collected_urls: List[str] = []
        seen_urls: Set[str] = set()

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            await page.goto(start_url, timeout=90000)
            await page.evaluate("""
                const scrollHeight = document.body.scrollHeight;
                window.scrollTo(0, scrollHeight * 0.35);
            """)
            while len(collected_urls) < limit:
                try:
                    await page.evaluate("""
                        const scrollHeight = document.body.scrollHeight;
                        window.scrollTo(0, scrollHeight * 0.35);
                    """)
                    await asyncio.sleep(3)
                    await page.evaluate(
                        "window.scrollBy(0, document.body.scrollHeight)"
                    )
                except Exception as e:
                    print(
                        f"Page did not reach network idle state, proceeding anyway: {e}"
                    )

                html = await page.content()
                current_page_url = page.url
                cleaned_html = self.delete_trash_data_from_html(html)

                result = await self.extract_game_links_with_gemini(
                    cleaned_html,
                    limit,
                    current_page_url,
                )

                all_found_urls = result.get("game_urls", [])

                if not all_found_urls and not result.get("next_page_selector"):
                    print("LLM returned no URLs and no next page selector. Stopping.")
                    break

                for url in all_found_urls:
                    if url not in seen_urls:
                        seen_urls.add(url)
                        collected_urls.append(url)
                        if len(collected_urls) >= limit:
                            break

                print(f"Collected {len(collected_urls)} URLs so far (target: {limit}).")

                if not result["next_page_selector"] or len(collected_urls) >= limit:
                    if not result["next_page_selector"]:
                        print("No 'next page' button found. Stopping.")
                    break

                try:
                    next_page_selector = result["next_page_selector"]
                    await page.locator(next_page_selector).scroll_into_view_if_needed(
                        timeout=5000
                    )
                    await page.click(next_page_selector, timeout=10000)
                    print(f"Clicked '{next_page_selector}'. Waiting for new content.")

                except Exception as e:
                    print(
                        f"Pagination failed or element '{result.get('next_page_selector')}' not found: {e}"
                    )
                    break

            await browser.close()

        return collected_urls[:limit]

    async def extract_game_data_from_url(self, game_url: str) -> dict:
        html = await self.get_page_html(game_url)
        cleaned_html = self.delete_trash_data_from_html(html)

        prompt = f"""
Analyze the HTML from a game detail page ({game_url}) and extract the information into a single, valid JSON object.
If a piece of information is not found or applicable, use null for its value.
**Do not omit any fields. Always include all fields, even if the value is null.**

Current Date: {datetime.now(timezone.utc).isoformat()}

HTML Content:
{cleaned_html}

JSON Output Structure and Instructions:
{{
  "name": "(string) The full name of the game as displayed on the platform. Required.",
  "description": "(string or null) A detailed description of the game, usually a few paragraphs long. Extract the main descriptive text.",
  "price": "(float) The current price. For free games, use 0.0. If the price is unknown or cannot be determined, use -1.0. This field is required and must never be null.",
  "currency": "(string or null) The currency code, such as 'USD', 'EUR', 'UAH'. Extract the currency **as shown on the page**. If not found, use null. Do not guess or convert.",
  "price_in_usd": "(float) The price converted to USD. If 'currency' is not USD, convert 'price' to USD. If 'currency' is already USD, use the same value as 'price'. If 'price' is -1.0 or null, this field should also be -1.0 or null respectively. This field is required and must never be null.",
  "availability_status": "(string) Must be one of: 'available', 'out_of_stock', 'coming_soon', 'preorder', 'free', 'unavailable', 'early_access', 'beta', 'region_locked', 'unknown'. Required.",
  "url_on_platform": "(string) The full URL of the page being analyzed. Use this value: {game_url}",
  "rating": "(float or null) The game's average score. Normalize all ratings to a 5-point scale. Example: '9/10' or '90%' becomes 4.5.",
  "reviews_count": "(integer or null) Total number of user reviews. Convert text like '1.2K' to 1200.",
  "special_content_json": "(JSON object or null) Info about DLCs, bundles. Example: {{\"dlcs\": [\"DLC Name 1\"], \"season_pass_available\": true}}. If nothing found, use null.",
  "discount_info_json": "(JSON object or null) Info about discounts. Example: {{\"original_price\": 29.99, \"discounted_price\": 26.99, \"sale_end_date\": \"2025-06-13T23:59:59Z\"}}. Use null if not on sale.",
  "metadata_json": "(JSON object or null) Other game metadata like genres, tags, developer, publisher, release date, system requirements. If metadata is not available, use null."
}}

Important Notes:
- Always return a complete JSON object with all fields present.
- If a value is not found, return null for that field.
- Strictly follow the requested data types and formats.
- If the sale end date is given as a relative phrase (e.g., "ends in 14 days"), you **must** compute and return the exact absolute date in ISO 8601 format using the current date provided. Never leave `sale_end_date` null if any time reference is available.
- For `metadata_json`, include as many details as possible. If a subfield like `developer` or `tags` is missing, include it with null or omit inside the nested object — but the field `metadata_json` itself must be present.
- **For 'price_in_usd' conversion:**
    - If 'currency' is 'USD', 'price_in_usd' should be the same as 'price'.
    - If 'currency' is not 'USD', you **must** use an **up-to-date exchange rate** (which Gemini will obtain independently) to convert 'price' to USD.
    - If 'price' is -1.0 or null, 'price_in_usd' should also be -1.0 or null respectively.
    - If the currency is unknown or conversion is impossible due to missing 'price' or 'currency', use -1.0 for 'price_in_usd'.

JSON Response:
"""
        response_text = await self.gemini_api.generate_response(prompt) 
        if not response_text:
            raise ValueError("Failed to get a valid response from Gemini API.")
        cleaned_response_text = self.__clean_json_markdown(response_text)

        try:
            data = json.loads(cleaned_response_text)
            required_fields = [
                "name",
                "price",
                "price_in_usd", 
                "availability_status",
            ]
            for field in required_fields:
                if field not in data or data[field] is None:
                    print(
                        f"Warning: Required field '{field}' missing or null in LLM response for {game_url}. Raw: {cleaned_response_text}"
                    )
            return data
        except json.JSONDecodeError as e:
            print(
                f"Failed to parse Gemini response for {game_url} as JSON: {cleaned_response_text}. Error: {e}"
            )
            return {
                "name": None,
                "description": None,
                "price": -1.0,
                "currency": None,
                "price_in_usd": -1.0,
                "availability_status": "unknown",
                "url_on_platform": game_url,
                "rating": None,
                "reviews_count": None,
                "special_content_json": None,
                "discount_info_json": None,
                "metadata_json": None,
            }
        except Exception as e:
            print(
                f"An unexpected error occurred while processing game data for {game_url}: {e}. Raw: {cleaned_response_text}"
            )
            return {
                "name": None,
                "description": None,
                "price": -1.0,
                "currency": None,
                "price_in_usd": -1.0,
                "availability_status": "unknown",
                "url_on_platform": game_url,
                "rating": None,
                "reviews_count": None,
                "special_content_json": None,
                "discount_info_json": None,
                "metadata_json": None,
            }


WebScraperDependency = Annotated[WebScraper, Depends(WebScraper)]
