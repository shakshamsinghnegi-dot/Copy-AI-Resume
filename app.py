# step 1 load modules 
import os
import time
import langchain
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
import pytesseract as pyt
from tavily import TavilyClient
from langchain.messages import SystemMessage, HumanMessage
import numpy as np
import streamlit as st

#Step2:
st.title("Agentic PPT Generator")
st.header("User can generate,PPT,Image,and latest new")
st.slidebar.title("Give All API Key")

GOOGLE_API_KEY=st.sidebar.text_input("GOOGLE_API_KEY",type="password")
TAVILY_API_KEY = st.sidebar.text_input("TAVILY_API_KEY", type = "password")


ALL_API = [GOOGLE_API_KEY,TAVILY_API_KEY]

if not all(ALL_API):
  st.sidebar.error("MUST PASS ALL API KEYS")

  url="https://aistudio.google.com/api-keys"
  st.markdown(f"Get Google API key -{url}")

  url="https://app.tavily.com/playground"
  st.markdown(f"Get Tavily API key-{url}")
elif all(ALL_API):
  st.sidebar.success("API_KEY loaded")
  #MODEL LOAD 
  model = ChatGoogleGenerativeAI(
    google_api_key = GOOGLE_API_KEY,
    model = st.sidebar.selectbox("Gemini-Model-Name",
                                 options = ["gemini-2.5-flash","gemini-2.5-flash-lite",
                                            "gemini-3.5-flash","gemini-3.5-flash-lite"])
  selected_model=st.selectbox("Select-Model",options=options)
  model=ChatGoogleGenerativeAI(
    model=selected_model,
    google_api_key=GOOGLE_API_KEY)
else:
  st.sidebar.info("check api keys")

#========================STEP 3================================
#Search_Latest_using_tavily
def serch_latest_info(query):
   """This function helps to fetch latest news or jobs rerlated article
  using tavily """

  client = TavilyClient(
      api_key = TAVILY_API )
  response = client.search(query)
  return response

def generate_image(img_prompt,slide_no = 1):
  """this function helps user generate
  image using free api key with given
  image_prompt"""
  url = f"https://image.pollinations.ai/{img_prompt}"

import requests as r
content=r.get(url).content
with open(f"ai_image_{slide_no}.jpeg",'wb') as f:
  f.write(content)
return url

def run_agent(leader_agent, query):
  prompt = f"""Based on Below given Query, your task is to call specific tool,
  first to promptify user prompt, than call image tool, or latest search if
  required.give slide dynamic, ui ux, with creative design, keep help of
  function to generate image based on given topic, Generate image using
  with no of slide asked and embed that in same html ppt and using file handling embed this in
  output html, use java script function to generate image using async
  func and threading and give output in HTML user query given below:"""
  prompt = prompt+ query
  response = leader_agent.invoke({'messages': [{'role': 'user', 'content': prompt}]})
  code = response['messages'] [-1].content[-1]['text']
  return code


#Leader_agent creation
if all(API_KEY): 
    leader_agent = create_agent(
        model= model,
        tools = [search_latest_info,#generate image]
    )
    leader_agent
else:
  st.info("Give API KEY to load agent")




#=====================Step 4 Stremlit Navbars===========================
tab1,tab2,tab3=st.tabs(["Generate Image",
                        "Fetch News"
                        "Generate PPT"])

user_input=st.text_area("Write Prompt & CLick Agent")
if (user_input)&(Leader_agent):
  with tab1:
    if st.button("Click to generate image",key="Image-button"):
      with st.spinner("Running Agent"):
        try:
          url=generate_image(user_input)
          import request as r
          img_data=r.get(url)
          st.image(url)
        except Exception as err:
          st.error("Error Code:",err)

  with tab2:
    if st.button("Fetch Latest News",key="News-button"):
      with st.spinner("Running Agent"):
        try:
          prompt="""Give Latest News Related to given user Query 
          in Dynamic HTML,Output with cards design format.
          Strict HTML Output, No any markdown Response
          User Query:"""+user_input

          response = leader_agent.invoke({'messages': [{'role': 'user', 'content': prompt}]})
          code = response['messages'] [-1].content[-1]['text']
          st.html(code,width="stretch",unsafe_allow_javascript=True)


        except Exception as err:
          st.error("Error Code:",err)

with tab3:
  if st.button("Click to Generate PPT", key="PPT-Button"):
    with st.spinner("Running Agent"):
      try:
        code=run_agent(leader_agent,user_input)
        st.html(code,width="stretch",unsafe_allow_javascript=True)

        if st.downloaded_button(label="DOWNLOAD PPT",
                                data=code,
                                file_name='ppt.html',
                                mime='text/html'):
           st.success("PPT Downloded Successfully !!!")

      except Exception as err:
        st.error("ERROR CODE:",err)


