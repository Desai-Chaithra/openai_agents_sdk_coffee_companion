# app.py
import gradio as gr
from orchestrator import Runner

def launch_app():
    async def pipeline_mediator(user_mood_input: str):
        orchestrator_engine = Runner()
        return await orchestrator_engine.execute_workflow(user_mood_input)

    interface = gr.Interface(
        fn=pipeline_mediator,
        inputs=[
            gr.Textbox(label="How are you feeling right now?", placeholder="e.g., Anxious and tired, Happy and energetic...")
        ],
        outputs=[
            gr.Textbox(label="Agent 1: Barista Selection (Structured Drink Data)", interactive=False),
            gr.Textbox(label="Agent 2: Companion Plan (Structured Activity Data)", interactive=False),
            gr.Code(label="Async Execution Telemetry Logs (Pipeline Trace Record)", language="text")
        ],
        title="Customized Tool-Driven Modular Companion",
        description="A lightweight multi-file multi-agent pipeline using explicit parameter injection during tool conversion calls."
    )
    interface.launch(inline=False, share=False)

if __name__ == "__main__":
    launch_app()