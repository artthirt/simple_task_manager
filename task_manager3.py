import gradio as gr
from datetime import datetime
import os
import glob

def get_task_files():
    """Get sorted list of task files by modification time"""
    files = glob.glob("task_*.txt")
    files.sort(key=os.path.getmtime, reverse=False)
    return files

def save_task(text: str):
    """Save text to a new task file with current timestamp"""
    if not text.strip():
        return gr.update(), ""
        
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"task_{timestamp}.txt"
    
    with open(filename, "wb") as f:
        f.write(text.encode(encoding="utf-8"))
    
    return gr.update(choices=get_task_files()), ""

def show_task_content(file):
    """Display content of selected task file as Markdown"""
    if file and os.path.exists(file):
        with open(file, "rb") as f:
            content = str(f.read(), encoding='utf-8')
        return content, content  # Return both markdown and raw text
    return "", ""

def save_edited_task(file, content: str):
    """Save edited content back to the file"""
    if file and os.path.exists(file):
        with open(file, "wb") as f:
            f.write(content.encode(encoding="utf-8"))
        return gr.update(choices=get_task_files()), content, "Changes saved successfully!"
    return gr.update(), gr.update(), "Error saving changes!"

def cancel_edit(file):
    """Cancel editing and revert to original content"""
    if file and os.path.exists(file):
        with open(file, "rb") as f:
            content = str(f.read(), encoding='utf-8')
        return content, content, gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)
    return "", "", gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)

css="""
.radio-group .wrap {
    display: grid !important;
    grid-template-columns: 1fr;
}
.brdcol{
    boder: 1px solid #aaa;
}
"""

with gr.Blocks(title="Task Manager", css=css) as app:
    gr.Markdown("## 📝 Task Management System")
    
    with gr.Row():
        with gr.Column(scale=1):            
            # Task list section
            task_list = gr.Radio(
                label="Saved Tasks",
                choices=get_task_files(),
                type="value",
                elem_classes="radio-group"
            )
            
        with gr.Column(scale=3):
            # Current Date display
            current_date = datetime.now().strftime("%Y-%m-%d")
            gr.Markdown(f"### Today's Date: **{current_date}**")
            
            # Task input section
            task_input = gr.Textbox(label="New Task", lines=5, placeholder="Enter your task here...")
            submit_btn = gr.Button("Save Task", variant="primary")

            # Markdown display
            markdown_display = gr.Markdown(
                label="Selected Task Content", 
                min_height='200px',
                elem_classes="brdcol",
                show_copy_button=True,
                container=True
            )
            
            # Hidden editor components
            with gr.Group(visible=False) as edit_group:
                edit_textbox = gr.Textbox(
                    label="Editing Task Content",
                    lines=15,
                    interactive=True
                )
                with gr.Row():
                    save_btn = gr.Button("💾 Save", variant="primary")
                    cancel_btn = gr.Button("🚫 Cancel", variant="stop")
            
            edit_btn = gr.Button("✏️ Edit", variant="secondary")
            status = gr.Markdown()
    
    # Event handlers
    submit_btn.click(
        save_task,
        inputs=task_input,
        outputs=[task_list, task_input]
    )
    
    task_list.change(
        show_task_content,
        inputs=task_list,
        outputs=[markdown_display, edit_textbox]
    )
    
    edit_btn.click(
        lambda: [
            gr.update(visible=True),  # Show edit group
            gr.update(visible=False)  # Hide edit button
        ],
        outputs=[edit_group, edit_btn]
    )
    
    save_btn.click(
        save_edited_task,
        inputs=[task_list, edit_textbox],
        outputs=[task_list, markdown_display, status]
    ).then(
        lambda: [
            gr.update(visible=False),  # Hide edit group
            gr.update(visible=True)   # Show edit button
        ],
        outputs=[edit_group, edit_btn]
    )
    
    cancel_btn.click(
        cancel_edit,
        inputs=task_list,
        outputs=[markdown_display, edit_textbox, edit_group, cancel_btn, edit_btn]
    )

if __name__ == "__main__":
    app.launch()