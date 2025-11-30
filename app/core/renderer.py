import tkinter as tk
from tkinter import font
from html.parser import HTMLParser
import markdown2

class MarkdownRenderParser(HTMLParser):
    def __init__(self, text_widget: tk.Text):
        super().__init__()
        self.text_widget = text_widget
        self.current_tags = []
        self.configure_styles()
        
    def configure_styles(self):
        # Fonts
        available_fonts = font.families()
        base_font_family = "Helvetica"
        if "Segoe UI" in available_fonts:
            base_font_family = "Segoe UI"
        elif "Roboto" in available_fonts:
            base_font_family = "Roboto"
        elif "Arial" in available_fonts:
            base_font_family = "Arial"
            
        code_font_family = "Courier"
        if "Consolas" in available_fonts:
            code_font_family = "Consolas"
        elif "Courier New" in available_fonts:
            code_font_family = "Courier New"

        base_font = (base_font_family, 11)
        code_font = (code_font_family, 10)
        
        # Configure Tags
        self.text_widget.tag_configure("h1", font=(base_font_family, 24, "bold"), spacing1=20, spacing3=10, foreground="#2c3e50")
        self.text_widget.tag_configure("h2", font=(base_font_family, 20, "bold"), spacing1=15, spacing3=8, foreground="#34495e")
        self.text_widget.tag_configure("h3", font=(base_font_family, 16, "bold"), spacing1=12, spacing3=5, foreground="#2c3e50")
        self.text_widget.tag_configure("h4", font=(base_font_family, 14, "bold"), spacing1=10, spacing3=5, foreground="#2c3e50")
        self.text_widget.tag_configure("h5", font=(base_font_family, 12, "bold"), spacing1=10, spacing3=5, foreground="#2c3e50")
        self.text_widget.tag_configure("h6", font=(base_font_family, 11, "bold"), spacing1=10, spacing3=5, foreground="#2c3e50")
        
        self.text_widget.tag_configure("p", font=base_font, spacing1=5, spacing3=5)
        self.text_widget.tag_configure("code", font=code_font, background="#f0f0f0", foreground="#c7254e")
        self.text_widget.tag_configure("pre", font=code_font, background="#f8f9fa", lmargin1=20, lmargin2=20)
        self.text_widget.tag_configure("strong", font=(base_font_family, 11, "bold"))
        self.text_widget.tag_configure("em", font=(base_font_family, 11, "italic"))
        self.text_widget.tag_configure("ul", lmargin1=20, lmargin2=20)
        self.text_widget.tag_configure("li", lmargin1=20, lmargin2=20, spacing1=2)
        self.text_widget.tag_configure("a", foreground="#3498db", underline=True)
        self.text_widget.tag_configure("blockquote", lmargin1=20, lmargin2=20, background="#f9f9f9", foreground="#555")

    def handle_starttag(self, tag, attrs):
        self.current_tags.append(tag)
        if tag == 'li':
            self.text_widget.insert("end", "• ", tuple(self.current_tags))

    def handle_endtag(self, tag):
        # Insert newline after block elements
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'pre', 'div', 'blockquote']:
            self.text_widget.insert("end", "\n")
            
        if tag in self.current_tags:
            for i in range(len(self.current_tags) - 1, -1, -1):
                if self.current_tags[i] == tag:
                    self.current_tags.pop(i)
                    break

    def handle_data(self, data):
        if not self.current_tags:
            if not data.strip():
                return
        
        if 'pre' in self.current_tags:
            self.text_widget.insert("end", data, tuple(self.current_tags))
        else:
            self.text_widget.insert("end", data, tuple(self.current_tags))

def render_markdown(text_widget: tk.Text, md_text: str):
    text_widget.config(state=tk.NORMAL)
    text_widget.delete("1.0", tk.END)
    
    html = markdown2.markdown(md_text, extras=["fenced-code-blocks", "tables"])
    
    parser = MarkdownRenderParser(text_widget)
    parser.feed(html)
    
    text_widget.config(state=tk.DISABLED)
