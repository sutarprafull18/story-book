import streamlit as st
from PIL import Image
import requests
from fpdf import FPDF
import base64
import random
import lorem  # for generating placeholder text

# Streamlit UI
st.title("📚 Free Auto-Book Generator")
title = st.text_input("Enter your book title:")

def generate_story(title):
    """Generate a simple story using lorem ipsum"""
    story = f"# {title}\n\n"
    
    for i in range(1, 4):
        chapter_title = str(lorem.sentence())  # Convert generator to string
        story += f"## Chapter {i}: {chapter_title}\n\n"
        # Generate 3 paragraphs per chapter and convert to string
        paragraphs = [str(lorem.paragraph()) for _ in range(3)]
        story += "\n\n".join(paragraphs)
        story += "\n\n"
    
    return story

def get_placeholder_image(width=1024, height=1024):
    """Get a placeholder image from picsum.photos"""
    url = f"https://picsum.photos/{width}/{height}"
    response = requests.get(url)
    image_url = response.url
    return image_url

def create_pdf(title, content, images):
    """Convert text + images to PDF"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    
    # Split content into pages
    for page in content.split('\n\n'):
        if page.strip():  # Only process non-empty pages
            try:
                pdf.multi_cell(0, 10, txt=page)
                if images:
                    img_url = images.pop(0)
                    try:
                        img_data = requests.get(img_url).content
                        with open("temp_img.jpg", "wb") as f:
                            f.write(img_data)
                        pdf.image("temp_img.jpg", x=10, w=180)
                    except Exception as e:
                        st.warning(f"Failed to add image: {e}")
            except Exception as e:
                st.warning(f"Failed to add text: {e}")
    
    pdf.output("book.pdf")
    return "book.pdf"

if title and st.button("Generate Book"):
    try:
        # Step 1: Generate story
        story = generate_story(title)
        st.markdown("### Generated Story:")
        st.markdown(story)
        
        # Step 2: Get placeholder images for chapters
        image_urls = [get_placeholder_image() for _ in range(3)]
        
        # Step 3: Create PDF
        pdf_path = create_pdf(title, story, image_urls.copy())
        
        # Step 4: Provide download link
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()
        b64 = base64.b64encode(pdf_data).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="{title}_book.pdf">Download Book</a>'
        st.markdown(href, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"An error occurred: {e}")
