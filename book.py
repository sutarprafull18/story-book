import os
import streamlit as st
from openai import OpenAI
from PIL import Image
import requests
from fpdf import FPDF
import base64
import zipfile

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("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"))  # Add your API key

# Streamlit UI
st.title("🧙♂️ Auto-Book Generator")
title = st.text_input("Enter your book title:")

def generate_story(title):
    """Generate story content using GPT-4"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a children's story writer. Generate a 3-chapter story in markdown format."},
            {"role": "user", "content": f"Title: {title}. Include characters, dialogue, and a moral lesson."}
        ]
    )
    return response.choices[0].message.content

def generate_image(prompt):
    """Generate image using DALL-E 3"""
    response = client.images.generate(
        model="dall-e-3",
        prompt=f"Children's book illustration, colorful, cartoon style. Scene: {prompt}",
        size="1024x1024",
        quality="standard",
        n=1,
    )
    return response.data[0].url

def create_pdf(title, content, images):
    """Convert text + images to PDF"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    
    for page in content.split('\n\n'):
        pdf.multi_cell(0, 10, txt=page)
        if images:
            img_url = images.pop(0)
            img_data = requests.get(img_url).content
            with open("temp_img.jpg", "wb") as f:
                f.write(img_data)
            pdf.image("temp_img.jpg", x=10, w=180)
    pdf.output("book.pdf")
    return "book.pdf"

if title and st.button("Generate Book"):
    # Step 1: Generate story
    story = generate_story(title)
    st.markdown("### Generated Story:")
    st.markdown(story)
    
    # Step 2: Generate images for chapters
    chapters = story.split('## Chapter')[1:]
    image_urls = []
    for chap in chapters:
        prompt = chap.split('\n')[0]  # Use chapter heading as image prompt
        image_urls.append(generate_image(prompt))
    
    # Step 3: Create PDF/ZIP with content
    pdf_path = create_pdf(title, story, image_urls.copy())
    
    # Step 4: Provide download link
    with open(pdf_path, "rb") as f:
        pdf_data = f.read()
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{title}_book.pdf">Download Book</a>'
    st.markdown(href, unsafe_allow_html=True)
