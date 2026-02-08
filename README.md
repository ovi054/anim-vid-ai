# 🎬 Anim-Vid-AI: The Algorithmic Storyteller

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Manim](https://img.shields.io/badge/Engine-Manim_Community-green)
![AI](https://img.shields.io/badge/Model-Gemini_3_Flash-purple)
![Docker](https://img.shields.io/badge/Deployment-Docker-blue)
 
> *Theme: Educational Tools & Platforms / Artificial Intelligence*

## 🚀 Vision & Purpose
Complex logic is hard to explain with just text. Whether it's the swapping logic of **Bubble Sort**, the traversal path of **DFS (Depth First Search)**, or abstract **Mathematical proofs**, static images often fail to convey the *movement* of logic.

**Anim-Vid-AI** is an AI-powered visualization engine that turns natural language descriptions into high-quality, programmatic animations. It democratizes the power of the **Manim** engine (used by 3Blue1Brown), allowing developers, educators, and content creators to generate complex algorithm visualizations in seconds without writing a single line of Python code.

## ✨ Key Features
*   **Algorithm Visualization:** specialized in rendering sorting algorithms, graph traversals, and data structures.
*   **Logic-to-Code:** Converts prompts like "Show a binary search tree balancing itself" into precise Manim Python code.
*   **Smart Iteration:** Use the chat interface to refine animations (e.g., "Slow down the sorting step" or "Highlight the pivot element").
*   **Dual View:** targeted at developers—view the generated Python code alongside the rendered video to learn Manim syntax.
*   **Production Ready:** Dockerized architecture solving the complex dependency issues of FFmpeg, LaTeX, and Cairo.

## 🎥 Demo
**Live URL:** https://anim-vid-ai.onrender.com

**Demo Video:** https://youtu.be/JwwYcg1Bcvg


## 🧠 How It Works
1.  **Intent Parsing:** The AI analyzes the prompt to identify if the request is Mathematical (Graphs, Calculus) or Algorithmic (Arrays, Nodes, Pointers).
2.  **Code Synthesis:** It generates a `MyScene` class in Python, utilizing Manim's `VGroup`, `Arrow`, and `.animate` methods to represent logic flows.
3.  **Compilation:** The code is executed in an ephemeral sandbox to render the `.mp4` output.
4.  **Error Correction:** If the code fails (e.g., overlapping nodes), the "Edit" feature allows the AI to self-correct the spatial arrangement.


## 🛠️ Tech Stack
*   **Core Engine:** Python, Manim Community (v0.19.0)
*   **Intelligence:** Gemini 3 Flash with custom prompting for algorithmic logic.
*   **Interface:** Gradio (Web UI).
*   **Infrastructure:** Docker & Render (Cloud Deployment).

## ⚙️ Installation & Setup

### Option 1: Docker (Recommended)
This project requires system-level dependencies (FFmpeg, Pango, LaTeX) that are difficult to install manually. We recommend using the Docker container.

1.  **Clone the Repo**
    ```bash
    git clone https://github.com/YOUR_USERNAME/anim-vid-ai.git
    cd anim-vid-ai
    ```

2.  **Build**
    ```bash
    docker build -t anim-vid-ai .
    ```

3.  **Run**
    ```bash
    docker run -p 7860:7860 -e API_KEY=your_fal_ai_key anim-vid-ai
    ```
    Access the app at `http://localhost:7860`.

### Option 2: Cloud Deployment (Render)
1.  Fork this repository.
2.  Create a **New Web Service** on Render.
3.  Select **Docker** as the runtime.
4.  Add your `API_KEY` in the Environment Variables.

## 👥 Team Members
*   **Avi Pal**

---
