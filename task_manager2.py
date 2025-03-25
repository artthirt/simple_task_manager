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

def save_edited_task(file, content):
    """Save edited content back to the file"""
    if file and os.path.exists(file):
        with open(file, "w") as f:
            f.write(content)
        return gr.update(choices=get_task_files()), "Changes saved successfully!"
    return gr.update(), "Error saving changes!"

def cancel_edit(file):
    """Cancel editing and revert to original content"""
    if file and os.path.exists(file):
        with open(file, "rb") as f:
            content = str(f.read(), encoding='utf-8')
        return content, gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)
    return "", gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)

css="""
.radio-group .wrap {
    display: grid !important;
    grid-template-columns: 1fr;
}
"""

with gr.Blocks(title="Task Manager", css=css) as app:
    gr.Markdown("## 📝 Task Management System")
    
    with gr.Row():
        with gr.Column():
            # Current Date display
            current_date = datetime.now().strftime("%Y-%m-%d")
            gr.Markdown(f"### Today's Date: **{current_date}**")
            
            # Task input section
            task_input = gr.Textbox(label="New Task", lines=5, placeholder="Enter your task here...")
            submit_btn = gr.Button("Save Task", variant="primary")
            
            with gr.Blocks(css=css) as sel:
                with gr.Row():
                    # Task list section
                    task_list = gr.Radio(
                        label="Saved Tasks",
                        choices=get_task_files(),
                        type="value",
                        elem_classes="radio-group"
                    )
            
        with gr.Column():
            # Task content display and editing
            task_display = gr.Textbox(
                label="Selected Task Content",
                lines=15,
                interactive=False
            )
            with gr.Row():
                edit_btn = gr.Button("✏️ Edit", variant="secondary")
                save_btn = gr.Button("💾 Save", variant="primary", visible=False)
                cancel_btn = gr.Button("🚫 Cancel", variant="stop", visible=False)
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
        outputs=task_display
    )
    
    edit_btn.click(
        lambda: [
            gr.update(interactive=True),
            gr.update(visible=True),
            gr.update(visible=True),
            gr.update(visible=False)
        ],
        outputs=[task_display, save_btn, cancel_btn, edit_btn]
    )
    
    save_btn.click(
        save_edited_task,
        inputs=[task_list, task_display],
        outputs=[task_list, status]
    )
    
    cancel_btn.click(
        cancel_edit,
        inputs=task_list,
        outputs=[task_display, save_btn, cancel_btn, edit_btn]
    )
    
    # Handle cancel edit when selecting new file
    task_list.change(
        lambda: [
            gr.update(interactive=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=True)
        ],
        outputs=[task_display, save_btn, cancel_btn, edit_btn]
    )

if __name__ == "__main__":
    app.launch()