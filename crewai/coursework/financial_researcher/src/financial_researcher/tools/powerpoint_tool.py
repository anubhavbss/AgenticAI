from crewai_tools import tool
from pptx import Presentation


@tool("Create PowerPoint")
def create_powerpoint(title: str, slides: str) -> str:
    """
    Create a PowerPoint presentation from structured slide content.

    Args:
        title: Presentation title.
        slides: Structured slide content provided by the Presentation Agent.

    Returns:
        Path of the generated PowerPoint file.
    """

    prs = Presentation()

    # Title slide
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = title

    # Content slide
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Research Findings"
    slide.placeholders[1].text = slides

    filename = "company_report.pptx"
    prs.save(filename)

    return f"PowerPoint created successfully: {filename}"