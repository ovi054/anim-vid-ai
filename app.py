import gradio as gr
import subprocess
import os
import tempfile
import shutil
from pathlib import Path
import time
import sys
import re
import manim
import requests
import json

API_KEY = os.environ.get("API_KEY")


def extract_manim_code(ai_text):
    """
    Extract Manim Python code from AI text.
    - If a ```python block exists, extract it.
    - Otherwise, remove any leading text before 'import' or 'class Scene'.
    """
    # Try Markdown-style Python block first
    match = re.search(r"```python\s*(.*?)```", ai_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Otherwise, try to find the first line that looks like Python code
    lines = ai_text.splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith(("from ", "import ", "class ")):
            return "\n".join(lines[i:]).strip()
    
    # fallback: return entire text
    return ai_text.strip()


def generate_code_from_prompt(prompt, progress=gr.Progress()):
    """
    Calls the Fal AI Any LLM API to generate Python Manim code.
    """
    progress(0, desc="Sending request to AI API...")

    api_url = "https://fal.run/fal-ai/any-llm"
    
    payload = {
        "prompt": prompt,
        "priority": "latency",
        "model": "google/gemini-2.5-flash",
        "system_prompt": f"""
Write a Manim script that's in Python to visualize: {prompt}. FOCUS on producing working code. Always use Manim Community version 0.19 syntax. When creating an Axes object, do not use axis_color directly as a keyword argument. Instead, use axis_config= 'color': ... The class should be MyScene and end with self.wait(). Class name should be MyScene. End with self.wait() Only give me the python code so that I can directly put this into the manim project input. 
Avoid using deprecated or unavailable ManimCE methods like get_tangent_line. Construct tangent lines manually using slope and Line(...).
You are a senior math educator and Manim Community v0.19 expert.
Always ensure visuals are well spaced, readable, never overlapping.
make sure video scene doesn't overlap and shown inside the canvas.
Text should be placed carefully using `.animate.to_edge()`, `.next_to()`, or `.shift()`.
Only include coordinate axes, graphs, tangent lines, or shapes if necessary.
Always conclude with `self.wait()`.
Use ManimCE v0.19 syntax.
The scene class should always be named `MyScene`.
"""
    }

    try:
        headers = {
        "Content-Type": "application/json",
        "Authorization": f"Key {API_KEY}"
        }
        response = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=60)
        response.raise_for_status()
        result = response.json()
        
        # Extract generated text
        generated_text = result.get("output", "")
        if not generated_text:
            return "", "❌ No code generated from AI."

        # Extract Python code block safely
        cleaned_code = extract_manim_code(generated_text)

        progress(1.0, desc="✅ AI code generation complete!")
        return cleaned_code, f"✅ AI code generated successfully for: '{prompt}'"

    except Exception as e:
        return "", f"❌ Failed to generate code: {str(e)}"


def edit_code_with_instruction(existing_code, instruction, progress=gr.Progress()):
    """
    Takes existing Manim code and a user instruction (like 'move the text to the left'),
    and uses the AI model to modify the code accordingly.
    """
    progress(0, desc="Sending edit request to AI API...")

    api_url = "https://fal.run/fal-ai/any-llm"

    system_prompt = f"""
You are a Manim expert. You will receive existing Manim code and an instruction on how to modify it.
Follow these rules:
- Only modify what’s necessary.
- Maintain compatibility with Manim Community v0.19.
- Always return full corrected Python code in a ```python``` block.
- The class name must remain unchanged.
- Always end with self.wait().
"""

    payload = {
        "prompt": f"Instruction: {instruction}\n\nOriginal Code:\n```python\n{existing_code}\n```",
        "priority": "latency",
        "model": "google/gemini-2.5-flash",
        "system_prompt": system_prompt
    }

    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Key {API_KEY}"
        }
        response = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=60)
        response.raise_for_status()
        result = response.json()

        ai_text = result.get("output", "")
        if not ai_text:
            return "", "❌ No edited code returned by AI."

        cleaned_code = extract_manim_code(ai_text)

        progress(1.0, desc="✅ Code edited successfully!")
        return cleaned_code, "✅ Code updated based on your instruction."

    except Exception as e:
        return "", f"❌ Failed to edit code: {str(e)}"





class ManimAnimationGenerator:
    def __init__(self):
        self.temp_dir = None
        self.output_dir = None
    
    def setup_directories(self):
        """Setup temporary directories for Manim execution"""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.temp_dir, "media", "videos", "480p15")
        os.makedirs(self.output_dir, exist_ok=True)
        return self.temp_dir
    
    def cleanup_directories(self):
        """Clean up temporary directories"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None
            self.output_dir = None
    
    def validate_manim_code(self, code):
        """Basic validation of Manim code"""
        required_imports = ["from manim import *", "import manim"]
        has_import = any(imp in code for imp in required_imports)
        
        if not has_import:
            return False, "Code must include 'from manim import *' or 'import manim'"
        
        if "class" not in code:
            return False, "Code must contain at least one class definition"
        
        if "Scene" not in code:
            return False, "Class must inherit from Scene or a Scene subclass"
        
        return True, "Code validation passed"
    
    # def install_manim(self):
    #     """Try to install Manim if not available"""
    #     try:
    #         print("Manim not found. Attempting installation...")
    #         subprocess.check_call([
    #             sys.executable, "-m", "pip", "install", "manim", "--quiet"
    #         ])
    #         global MANIM_AVAILABLE
    #         MANIM_AVAILABLE = True
    #         return True, "Manim installed successfully"
    #     except subprocess.CalledProcessError as e:
    #         return False, f"Failed to install Manim: {str(e)}"

    def execute_manim_code(self, code, quality="low", format_type="gif"):
        """Execute Manim code and return the generated animation"""
        # if not MANIM_AVAILABLE:
        #     success, message = self.install_manim()
        #     if not success:
        #         return None, f"❌ Manim Installation Error: {message}", ""

        code  = extract_manim_code(code)

        try:
            is_valid, message = self.validate_manim_code(code)
            if not is_valid:
                return None, f"❌ Validation Error: {message}", ""
            
            temp_dir = self.setup_directories()
            python_file = os.path.join(temp_dir, "animation.py")
            with open(python_file, "w") as f:
                f.write(code)

        # try:
        #     is_valid, message = self.validate_manim_code(code)
        #     if not is_valid:
        #         return None, f"❌ Validation Error: {message}", ""
            
        #     # Dynamically inject portrait (9:16) config
        #     portrait_config = (
        #         "from manim import config\n"
        #         "# Maintain chosen quality while forcing 9:16 aspect ratio\n"
        #         "if config.pixel_height == 480:\n"
        #         "    config.pixel_height = 854  # low\n"
        #         "    config.pixel_width = 480\n"
        #         "elif config.pixel_height == 720:\n"
        #         "    config.pixel_height = 1280  # medium\n"
        #         "    config.pixel_width = 720\n"
        #         "elif config.pixel_height == 1080:\n"
        #         "    config.pixel_height = 1920  # high\n"
        #         "    config.pixel_width = 1080\n"
        #         "else:\n"
        #         "    config.pixel_height = 854\n"
        #         "    config.pixel_width = 480\n"
        #         "config.frame_height = 16\n"
        #         "config.frame_width = 9\n"
        #     )

        
        #     code = portrait_config + "\n" + code
        
        #     temp_dir = self.setup_directories()
        #     python_file = os.path.join(temp_dir, "animation.py")
        #     with open(python_file, "w") as f:
        #         f.write(code)
            #end
            
            class_name = self.extract_class_name(code)
            if not class_name:
                self.cleanup_directories()
                return None, "❌ Error: Could not find a valid Scene class in the code", ""
            
            quality_map = {"low": "-ql", "medium": "-qm", "high": "-qh"}
            quality_flag = quality_map.get(quality, "-ql")
            format_flag = "--format=gif" if format_type == "gif" else ""
            
            # cmd = [sys.executable, "-m", "manim", quality_flag, python_file, class_name]
            cmd = [
                sys.executable, "-m", "manim", 
                "-ql",            # Low Quality (480p)
                "--fps", "15",    # Lower FPS (Standard is 30 or 60, 15 is much lighter)
                "--disable_caching", # CRITICAL: Prevents cache lock freezes
                "--flush_cache",     # CRITICAL: Clears memory
                python_file, 
                class_name
            ]
            if format_flag:
                cmd.append(format_flag)
            
            result = subprocess.run(
                cmd,
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=120,
            )
            
            if result.returncode != 0:
                error_msg = f"❌ Manim execution failed:\n{result.stderr}"
                self.cleanup_directories()
                return None, error_msg, result.stdout
            
            output_file = self.find_output_file(temp_dir, class_name, format_type)
            if not output_file:
                self.cleanup_directories()
                return None, "❌ Error: Could not find generated animation file", result.stdout
            
            permanent_file = f"/tmp/{class_name}_{int(time.time())}.{format_type}"
            shutil.copy2(output_file, permanent_file)
            
            success_msg = f"✅ Animation generated successfully!"
            self.cleanup_directories()
            return permanent_file, success_msg, result.stdout
            
        except subprocess.TimeoutExpired:
            self.cleanup_directories()
            return None, "❌ Error: Animation generation timed out (2 minutes)", ""
        except Exception as e:
            self.cleanup_directories()
            return None, f"❌ An unexpected error occurred: {str(e)}", ""
    
    def extract_class_name(self, code):
        lines = code.split('\n')
        for line in lines:
            if line.strip().startswith('class ') and 'Scene' in line:
                return line.strip().split('class ')[1].split('(')[0].strip()
        return None

    def find_output_file(self, temp_dir, class_name, format_type):
        for root, _, files in os.walk(temp_dir):
            for file in files:
                if file.startswith(class_name) and file.endswith(f".{format_type}"):
                    return os.path.join(root, file)
        return None

# --- GRADIO APP FUNCTIONS ---

generator = ManimAnimationGenerator()

example_codes = {
    "Simple Square": '''from manim import *
class CreateSquare(Scene):
    def construct(self):
        square = Square(side_length=2).set_fill(BLUE, opacity=0.5)
        self.play(Create(square))
        self.play(square.animate.rotate(PI/2))
        self.wait()''',
    
    "Moving Circle": '''from manim import *
class MovingCircle(Scene):
    def construct(self):
        circle = Circle().set_fill(RED, opacity=0.5)
        self.play(Create(circle))
        self.play(circle.animate.shift(RIGHT * 2))
        self.wait()''',
    
    "Text Animation": '''from manim import *
class TextAnimation(Scene):
    def construct(self):
        text = Text("Hello, Manim!", font_size=48)
        self.play(Write(text))
        self.wait()'''
}


def generate_animation(code, quality, format_type, progress=gr.Progress()):
    """Main function to generate animation from code."""
    if not code.strip():
        return None, "❌ Please enter or generate some Manim code.", ""
    
    progress(0.1, desc="Starting animation generation...")
    
    progress(0.3, desc="Executing Manim code...")
    result_path, status_msg, logs = generator.execute_manim_code(code, quality, format_type)
    
    if result_path:
        progress(1.0, desc="Animation Ready!")
        return result_path, status_msg, logs
    else:
        return None, status_msg, logs
        

def generate_full_process(prompt, quality, format_type):
    """Generate Manim code and render video with live, user-friendly updates."""

    # Step 0: Initial notice
    yield None, "🤖 Thinking... generating Manim code based on your prompt.", "", ""

    # Step 1: Generate AI code
    code, msg = generate_code_from_prompt(prompt)
    if not code:
        yield None, f"⚠️ Couldn't generate code. {msg}", "", ""
        return

    # Step 2: Display the code immediately and prepare rendering
    yield None, "🧠 Manim code ready — preparing render environment.", code, ""

    # Step 3: Rendering phase
    yield None, "🎬 Rendering animation... this may take a moment.", code, ""
    result_path, status_msg, logs = generator.execute_manim_code(code, quality, format_type)

    # Step 4: Final stage
    if result_path:
        yield result_path, "✅ Rendering complete! Previewing your animation...", code, logs
    else:
        yield None, f"❌ Something went wrong while rendering. Details: {status_msg}", code, logs

def edit_and_render(existing_code, instruction, quality, format_type, progress=gr.Progress()):
    edited_code, status = edit_code_with_instruction(existing_code, instruction, progress)
    if not edited_code.strip():
        return None, status, existing_code, ""
    result_path, render_status, logs = generator.execute_manim_code(edited_code, quality, format_type)
    return result_path, f"{status}\n{render_status}", edited_code, logs




def load_example(example_name):
    """Load example code into the code editor."""
    return example_codes.get(example_name, "")

# --- GRADIO INTERFACE ---

css = """
    /* Fix the height of the code input and add scrollbar */
    .code-input textarea {
        height: 400px !important;
        max-height: 400px !important;
        min-height: 400px !important;
        overflow-y: auto !important;
        resize: none !important;
    }
    
    /* Ensure the parent container doesn't expand */
    .code-input {
        height: 400px !important;
        max-height: 400px !important;
    }
    
    /* Style the scrollbar for better visibility */
    .code-input textarea::-webkit-scrollbar {
        width: 8px;
    }
    
    .code-input textarea::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    .code-input textarea::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }
    
    .code-input textarea::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
"""

with gr.Blocks(theme=gr.themes.Soft(), 
               css=css,
               title="AI Math Animation Generator") as app:
    gr.Markdown("# 🎬 AI-Powered Manim Animation Generator")
    gr.Markdown("Describe the animation you want, generate the code with AI, and render the video!")
    gr.Markdown("<small>Powered by Gemini 3</small>")

    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("### 1. Generate Code with AI")
            prompt_input = gr.Textbox(
                label="Describe your animation",
                placeholder="e.g., explain bubble sort algorithm",
                lines=2
            )
            # generate_code_btn = gr.Button("🤖 Generate Code from Prompt", variant="secondary")

            generate_anim_btn = gr.Button("🎬 Generate & Render Animation", variant="primary")

            gr.Examples(
                    examples=["explain (a+b)^2", "sum of 1 to n", "explain bubble sort algorithm", "explain dfs", "a guy shaking hands with a horse"],
                    inputs=[prompt_input],
                )
            
            gr.Markdown("### 2. Edit & Render Code")
            code_input = gr.Code(
                label="Manim Code",
                language="python",
                lines=15,
                value=example_codes["Simple Square"],
                elem_classes=["code-input"]
            )

            edit_instruction = gr.Textbox(
            label="Describe what you want to fix or change",
            placeholder="e.g., move the circle to the left, make text smaller",
            lines=2
            )
            edit_code_btn = gr.Button("✏️ Edit Code with AI", variant="secondary")

            with gr.Row():
                quality = gr.Dropdown(choices=["low", "medium", "high"], value="low", label="Quality",visible=False)
                format_type = gr.Dropdown(choices=["gif", "mp4"], value="mp4", label="Format", visible=False)

            # generate_anim_btn = gr.Button("🎬 Generate & Render Animation", variant="primary")
            rerender_btn = gr.Button("🎥 Re-render Animation")
            
            # gr.Markdown("### 📚 Or Load an Example")
            # with gr.Row():
            #     example_dropdown = gr.Dropdown(choices=list(example_codes.keys()), label="Load Example")
            #     load_example_btn = gr.Button("📂 Load")
        
        with gr.Column(scale=2):
            gr.Markdown("### 3. View Your Animation")
            output_video = gr.Video(label="Generated Animation")
            status_output = gr.Textbox(label="Status", lines=2, max_lines=5)
            logs_output = gr.Textbox(label="Manim Logs", lines=10, max_lines=9, visible=False)
            
            with gr.Row():
                show_logs_btn = gr.Button("Show Logs", size="sm")
                hide_logs_btn = gr.Button("Hide Logs", size="sm")

    # Event Handlers
    # generate_code_btn.click(
    #     fn=generate_code_from_prompt,
    #     inputs=[prompt_input],
    #     outputs=[code_input, status_output]
    # )
    
    # generate_anim_btn.click(
    #     fn=generate_animation,
    #     inputs=[code_input, quality, format_type],
    #     outputs=[output_video, status_output, logs_output]
    # )

    generate_anim_btn.click(
    fn=generate_full_process,
    inputs=[prompt_input, quality, format_type],
    outputs=[output_video, status_output, code_input, logs_output],
    )

    rerender_btn.click(
    fn=generate_animation,
    inputs=[code_input, quality, format_type],
    outputs=[output_video, status_output, logs_output]
    )

    # edit_code_btn.click(
    #     fn=edit_code_with_instruction,
    #     inputs=[code_input, edit_instruction],
    #     outputs=[code_input, status_output]
    # )

    edit_code_btn.click(
        fn=edit_and_render,
        inputs=[code_input, edit_instruction, quality, format_type],
        outputs=[output_video, status_output, code_input, logs_output]
    )
    
    # load_example_btn.click(
    #     fn=load_example,
    #     inputs=[example_dropdown],
    #     outputs=[code_input]
    # )
    
    show_logs_btn.click(fn=lambda: gr.update(visible=True), outputs=[logs_output])
    hide_logs_btn.click(fn=lambda: gr.update(visible=False), outputs=[logs_output])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    app.launch(server_name="0.0.0.0", server_port=port)
