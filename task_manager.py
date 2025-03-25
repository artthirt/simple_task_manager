import gradio as gr
from datetime import datetime
import os
import glob

def get_task_files():
    """Get sorted list of task files by modification time"""
    files = glob.glob("task_*.txt")
    files.sort(key=os.path.getmtime, reverse=False)
    return files

def save_task(text):
    """Save text to a new task file with current timestamp"""
    if not text.strip():
        return gr.update(), ""
        
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"task_{timestamp}.txt"
    
    with open(filename, "w") as f:
        f.write(text)
    
    return gr.update(choices=get_task_files()), ""

def show_task_content(file):
    """Display content of selected task file"""
    if file and os.path.exists(file):
        with open(file, "rb") as f:
            return str(f.read(), encoding='utf-8')
    return ""

with gr.Blocks(title="Task Manager") as app:
    gr.Markdown("## 📝 Task Management System")
    
    with gr.Row():
        with gr.Column():
            # Task input section
            task_input = gr.Textbox(label="New Task", lines=5, placeholder="Enter your task here...")
            submit_btn = gr.Button("Save Task", variant="primary")
            
            # Task list section
            task_list = gr.Radio(
                label="Saved Tasks",
                choices=get_task_files(),
                type="value"
            )
            
        with gr.Column():
            # Task content display
            task_display = gr.Textbox(
                label="Selected Task Content",
                lines=15,
                interactive=False
            )
    
    # Event handlers
    submit_btn.click(
        save_task,
        inputs=task_input,
        outputs=[task_list, task_input]
    )
    
    task_list.change(
        show_task_content,
        inputs=task_list,
        outputs=task_display
    )

if __name__ == "__main__":
    app.launch()