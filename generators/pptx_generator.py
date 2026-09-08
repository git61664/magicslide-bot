import os
import asyncio
from datetime import datetime
from python_pptx import Presentation
from python_pptx.util import Inches, Pt
from python_pptx.enum.text import PP_ALIGN
from python_pptx.dml.color import RGBColor

async def generate_presentation(data: dict, user_id: int) -> str:
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)
    
    theme_idx = data.get("theme_idx", 0)
    colors = [
        (41, 128, 185, 255, 255, 255),
        (46, 139, 87, 255, 255, 255),
        (192, 57, 43, 255, 255, 255),
        (108, 52, 131, 255, 255, 255),
        (241, 196, 15, 0, 0, 0),
        (52, 73, 94, 255, 255, 255),
        (52, 152, 219, 255, 255, 255),
        (255, 255, 255, 0, 0, 0),
    ]
    
    bg_color = colors[theme_idx][:3]
    text_color = colors[theme_idx][3:]
    
    slide1 = prs.slides.add_slide(prs.slide_layouts[6])
    background = slide1.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(*bg_color)
    
    title_box = slide1.shapes.add_textbox(Inches(1), Inches(2.5), Inches(8), Inches(1.5))
    title_frame = title_box.text_frame
    title_frame.text = data['topic']
    title_frame.paragraphs[0].font.size = Pt(54)
    title_frame.paragraphs[0].font.bold = True
    title_frame.paragraphs[0].font.color.rgb = RGBColor(*text_color)
    title_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    author_box = slide1.shapes.add_textbox(Inches(1), Inches(5), Inches(8), Inches(1))
    author_frame = author_box.text_frame
    author_frame.text = data['author']
    author_frame.paragraphs[0].font.size = Pt(24)
    author_frame.paragraphs[0].font.color.rgb = RGBColor(*text_color)
    author_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    for i in range(1, data['slides']):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(*bg_color)
        
        slide_num_box = slide.shapes.add_textbox(Inches(8.5), Inches(6.8), Inches(1), Inches(0.5))
        slide_num_frame = slide_num_box.text_frame
        slide_num_frame.text = str(i)
        slide_num_frame.paragraphs[0].font.size = Pt(12)
        slide_num_frame.paragraphs[0].font.color.rgb = RGBColor(*text_color)
    
    output_path = f"temp/taqdimot_{user_id}_{int(datetime.now().timestamp())}.pptx"
    os.makedirs("temp", exist_ok=True)
    prs.save(output_path)
    
    return output_path
