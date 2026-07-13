"""
Task: Company sales brochure generator
    - Create a product that can generate marketing brochures about a company
        1. For prospective clients
        2. For investors
        3. For recruitment
    
    - The technology
        1. Use OpenAI API
        2. Use one-shot prompting
        3. Stream back results and show with formatting

    - Input
        1. We shall be provided a company name and their primary website
"""

# import OS so that we can interact with the OS files
import os

import json

# import load_dotenv so that we can fetch the api key from env file
from dotenv import load_dotenv

# the below lib works in notebooks and is being used by ed, however, we need to use rich lib instead for our case
# from IPython.display import Markdown, display, update_display
# importing rich for formatted output
# from rich.markdown import Markdown
# from rich.console import Console

# for scraping websites, we are using scraper code written by ed, built with beautifulsoup
from scraper import fetch_website_links, fetch_website_contents

# to interact with openai API, we are using openai lib
from openai import OpenAI


# load dotenv and assign the value of api key to variable api_key
# override is true so that we can have the fresh pull up of the api key, instead of something that's already loaded
load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

# check if api_key is fine, if not the following statement gets printed
if not api_key or not api_key.startswith('sk-proj-') or len(api_key) < 10:
    print("There is some issue with OpenAI API key. Please check the key.")
    

# assign model to be used
MODEL = 'gpt-5.4-nano'
# assign OpenAI function from openai lib to a varaiable
ai_llm = OpenAI()

# run scraper function to fetch the links
website_to_fetch = 'https://edwarddonner.com'
links = fetch_website_links(website_to_fetch)
print(links)


# our scraping is working fine and we were able to extract all the links from the given website, however, some of the links are not relevant to our document, hence
# now our next task is to filter out the relevant links required for our final output and we shall do this by using LLM.
# for this, we first start by creating a system prompt and giving an output format/example to the LLM
# since we are providing the LLM with one example, this type of prompting is known as single shot prompting, and we show it multiple examples, the prompting type is called as multi shot prompting
# also, since the system prompt will remain same, we have saved the prompt in a variable
link_system_prompt = """
You are provided with a list of links found on a company's website. 
You are able to decide which of the links would be most relevant to include in a brochure about the company, such as links to an About page, a Company or Overview page, or Careers/Jobs pages. Limit the result to 5 or less top most relevant links. 

You should respond in JSON as in this example:

{
    "links": [
        {"type": "About page", "url": "https://full.url/goes/here/about"},
        {"type": "Careers page", "url": "https://another.full.url/careers"}
    ]
}

Include links that are relevant to a company brochure. Good candidates:
- About / About Us, Company / Overview, Our Story, Mission
- Team / Leadership
- Careers / Jobs
- Products / Services
- The company's or founder's own official social media profiles (e.g. LinkedIn, Twitter/X, Facebook, YouTube, GitHub)
- A blog or news index/landing page (e.g. "/blog", "/news", "/posts")

Exclude links that are not useful for a brochure, including:
- Login / signup / account pages, and transactional flows such as upgrade, checkout, cart, subscribe, or "buy now" pages (e.g. "/upgrade?plan=pro", "/checkout") 
- Terms of Service, Privacy Policy, cookie policy
- Email (mailto:) links
- Login / signup pages
- "Share this page" widgets and links to third-party or unrelated people's social media
- Individual blog or news posts, UNLESS a post is clearly a flagship, company-defining piece; routine individual posts should be excluded
- Bare page anchors that start with "#"

When in doubt, include rather than exclude. If a link points to a page on the company's own website (the same domain as the base URL) and it is not clearly one of the excluded types above, include it even if its purpose is not obvious from the URL. Short, non-descriptive slugs (for example "/outsmart", "/connect-four", "/proficient") are often product, project, or company pages, so keep them. It is better to include a borderline same-domain page than to drop a potentially relevant one; the brochure-writing step will make the final selection.

Every URL you return must be a full, absolute URL beginning with the scheme (https:// or http://) and domain. Some links in the list may be relative (for example "/about" or "careers/"). Resolve any relative link into an absolute URL using the website's base URL, which is provided alongside the links. Do not return relative paths.

Do not invent links — only return URLs that appear in the provided list.

Respond with valid JSON only. Do not include any commentary before or after the JSON, and do not wrap it in Markdown code fences.
"""

# next we create a function, that should take in an input of a URL and combine it with the user prompt, so that every time we run it, we will be able to give a new URL as input, thus keeping the things organized and simple

def get_user_prompt(url):
    user_prompt = f"""Here is the list of links found on the website {url}.

Decide which of these links are relevant for a company brochure, following the rules you have been given. Respond with the full/absolute URL for each, in the required JSON format. If any links are relative, resolve them against the base URL above.

Links:
"""
    links = fetch_website_links(url)
    user_prompt += "\n".join(str(link) for link in links)
    return user_prompt

print(get_user_prompt('https://edwarddonner.com'))


# now we have our system and user prompts ready. now using these two, we create another function, that we will use to send the response to the LLM
def get_relevant_links(url):
    response = ai_llm.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": link_system_prompt},
            {"role": "user", "content": get_user_prompt(url)}
        ],
        response_format={"type": "json_object"}
    )
    result = response.choices[0].message.content
    links = json.loads(result) if result else {}
    return links


def get_content_and_links(url):
    page_content = fetch_website_contents(url)
    page_links = get_relevant_links(url)
    fetch_result = f"## Landing Page:\n\n{page_content}\n ##Links:\n"
    for link in page_links['links']:
        fetch_result += f"\n\n### Link: {link['type']}"
        fetch_result += fetch_website_contents(link['url'])
    return fetch_result


# now we move on to the creation of the brochure. we keep two system prompts, one is warm + proffesional, second is entertaining. 

brochure_system_prompt_pro = """
You are an assistant that analyzes the contents of several relevant pages from a company's website and creates a brochure about the company for prospective customers, investors, and potential recruits. Respond in Markdown.

Write a medium-length brochure. Where the provided content supports it, include sections such as:
- A short overview of the company and what it does
- Products / services
- Who they serve (customers or users)
- Company culture and values
- Careers / jobs

Use a professional but warm tone: polished, credible, and clear, with a touch of personality. Base the brochure only on the information in the provided page contents — do not invent facts, figures, or offerings. If there is not enough information for a section, leave that section out. Use short Markdown headings for each section.

Do not state specific numbers, statistics, or figures (e.g. counts of models, users, or customers) unless they appear verbatim in the provided content.
"""

brochure_system_prompt_fun = """
You are an assistant that analyzes the contents of several relevant pages from a company's website and creates a brochure about the company for prospective customers, investors, and potential recruits. Respond in Markdown.

Write a medium-length brochure. Where the provided content supports it, include sections such as:
- A short overview of the company and what it does
- Products / services
- Who they serve (customers or users)
- Company culture and values
- Careers / jobs

Use a light, humorous, entertaining tone — make it fun and engaging wherever the content allows, without misrepresenting the company. Base the brochure only on the information in the provided page contents — do not invent facts, figures, or offerings. If there is not enough information for a section, leave that section out. Use short Markdown headings for each section.

Do not state specific numbers, statistics, or figures (e.g. counts of models, users, or customers) unless they appear verbatim in the provided content.
"""

def get_brochure_user_prompt(company_name, url):
    user_prompt = f"""You are an assistant working on creating the brochure for the company: {company_name}.
You are provided with the main web pages of the website along with the content present in those pages.
Please write the brochure text as per the given instructions.

"""
    user_prompt += get_content_and_links(url)
    user_prompt = user_prompt[:5000]
    return user_prompt


def create_brochure(company_name, url):
    response = ai_llm.chat.completions.create(
        model='gpt-4.1-mini',
        messages=[
            {"role": "system", "content": brochure_system_prompt_fun},
            {"role": "user", "content": get_brochure_user_prompt(company_name, url)}
        ]
    )
    result = response.choices[0].message.content
    return result

print(create_brochure('SquadStack', 'https://www.squadstack.ai/'))

"""
Response for Pro:
# Hugging Face Brochure

---

## Overview

**Hugging Face** is the pioneering AI community building the future of machine learning. Serving as a collaborative platform, Hugging Face empowers developers, researchers, and enterprises worldwide to create, discover, and share machine learning models, datasets, and applications. It’s a vibrant ecosystem where innovation thrives, fueled by the world’s largest open library of models and datasets.

---

## Products & Services

- **Models**  
  Access over **2 million pre-trained machine learning models** spanning multiple AI modalities such as text, speech, and image. These models are continuously updated by contributors worldwide, enabling rapid experimentation and deployment.

- **Datasets**  
  Explore and contribute to a vast repository with **over 500,000 datasets**, curated to accelerate machine learning research and applications.

- **Spaces**  
  Host and interact with **machine learning applications** via Spaces, an environment optimized for running AI apps including speech-to-speech voice chat, image editing, optical character recognition (OCR), video generation, and more.

- **Inference Endpoints**  
  Deploy machine learning models seamlessly at scale with **Inference Endpoints**, a managed service tailored for enterprise-grade AI inference needs.

- **Storage Buckets**  
  Facilitate scalable storage solutions for hosting datasets, models, and other artifacts essential for machine learning workflows.

- **Hugging Face PRO and Enterprise Solutions**  
  Tailored plans offering advanced support, security, and integration options for teams and enterprises aiming to leverage Hugging Face at scale.

---

## Who We Serve

Our platform serves a diverse audience including:

- **Machine Learning Practitioners & Researchers**  
  Empowering the AI community with tools and resources to collaborate and innovate effortlessly.

- **Developers & AI Enthusiasts**  
  Providing easy access to models and datasets to build cutting-edge AI applications.

- **Enterprises & Teams**  
  Offering scalable, secure AI infrastructure and support to integrate AI capabilities into business operations.

---

## Company Culture & Values

At Hugging Face, the spirit of **community collaboration** is central. We believe in openness, transparency, and collective intelligence to accelerate AI innovation. By fostering an inclusive and supportive environment, we enable contributors from across the globe to share knowledge and build the AI future together.

Our platform exemplifies:

- **Openness**: Host and collaborate on unlimited public models, datasets, and applications leveraging an open-source stack.
- **Innovation**: Constantly evolving with the latest AI research and technological breakthroughs.
- **Accessibility**: Democratizing AI by making powerful tools and resources available to all skill levels.

---

## Careers

Join Hugging Face and be part of the AI revolution. We offer opportunities to work with a world-class team dedicated to transforming the way people interact with artificial intelligence. If you arepassionate about open source, machine learning, and community-driven innovation, Hugging Face is the place to grow your career.

*Explore job openings and learn more about our team culture on our website.*

---

## Connect & Learn

Stay engaged with the AI community through Hugging Face’s:

- Active forums and Discord channels  
- In-depth documentation and tutorials  
- Research blog and daily AI paper discussions  
- Open repositories on GitHub

---

**Hugging Face** — The AI community building the future, one model at a time.

Explore the platform: [huggingface.co](https://huggingface.co)

---

*Empower your AI journey with Hugging Face — where collaboration meets innovation.*
"""

"""
Response from fun:
# Hugging Face Brochure  
*The AI Community Building the Future — And Having Fun Doing It!*

---

## Who is Hugging Face?

Hugging Face is not just another tech company — it’s *the* vibrant, bustling community where the magic of machine learning (ML) happens. Consider it your AI playground, library, and workshop all rolled into one sleek platform. Here, brilliant minds from around the world collaborate on everything from models and datasets to full-blown AI applications. If AI were a party, Hugging Face would be the house everyone wants to crash (with invite, of course).  

---

## What Does Hugging Face Do?  

At its heart, Hugging Face offers a sprawling platform to **Create, Discover, and Collaborate** on machine learning projects — whether you’re building the next state-of-the-art chatbot, creating datasets that teach computers new tricks, or hosting applications that thrill users. The crown jewels of their platform include:

- **2+ million Models:** From natural language to computer vision and beyond, an enormous library of ready-to-use, open-source ML models awaits you.  
- **500,000+ Datasets:** Need data to fuel your AI? They’ve got a ginormous collection covering all kinds of domains.  
- **Spaces:** The playground for AI apps, hosting over a million applications where you can see ML in action or deploy your own with ease.  
- **Inference Endpoints:** Plug-and-play hosted APIs that make deploying your models at scale as easy as pie — no rocket science needed.  
- **Open Source Magic:** An open source stack that lets developers move faster, test ideas, and innovate without roadblocks.  

---

## Who Benefits from Hugging Face?  

This is the community platform for:  

- **Machine Learning Researchers & Data Scientists:** Share your models, datasets, experiments, and get feedback from peers.  
- **Developers & AI Engineers:** Deploy models efficiently, integrate AI features, or build dazzling new applications without reinventing the wheel.  
- **Enterprises & Teams:** Take advantage of specialized enterprise plans and PRO support to scale AI projects quickly and securely.  
- **AI Enthusiasts & Learners:** Dive into the community forums, blogs, daily research papers, and a friendly Discord to learn and connect.  

Simply put, if AI is your passion or profession, Hugging Face is your happy place.  

---

## Company Culture & Values  

Hugging Face champions an inclusive, collaborative, and open approach to building AI’s future. They believe great innovation happens when people share openly, build together, and support one another (bonus points for good humor and curiosity!). Their metaphorical motto? “Better together.”  

From hosting massive open-source repositories to maintaining a community buzzing with knowledge and creativity, Hugging Face embraces transparency, accessibility, and the joy of creation. Your git repo never felt so loved.  

---

## Join the Team & Careers  

Love AI? Love community? Hugging Face is on the lookout for passionate people ready to shape the future of machine learning. Whether you’re a researcher, engineer, or advocate, the company offers a playground to grow your skills, collaborate with world-class talent, and make a real impact.  

Being part of Hugging Face means:  

- Working at the forefront of open-source AI  
- Contributing to a global community that values your voice  
- Being part of a culture that mixes brilliance with a dash of fun and lots of coffee (or tea)  
- Growing professionally while helping shape the tools that *everyone* will use tomorrow  

Are you ready to Hug the future?  

---

## Ready to Explore?  

- **Browse over 2 million models**  
- **Dive into 500k+ datasets**  
- **Check out apps running on Hugging Face Spaces**  
- **Try deploying with Inference Endpoints**  

Join the AI community that’s building tomorrow — today. Where else can you say “I’m part of the team powering the future of machine learning” with a grin?  

---

# Hugging Face  
*AI is better shared*  

Explore more at [huggingface.co](https://huggingface.co)  

---  

*Disclaimer: No actual hugging required, but highly encouraged.* 🤗
"""