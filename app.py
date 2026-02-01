import gradio as gr
from textblob import TextBlob
import pandas as pd
import csv

# 1. THE BRAIN: Logic with Excel-Ready Formatting
def process_data(text, file):
    data_log = []
    
    # Identify Source (File or Text)
    if file is not None:
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file.name)
                input_list = df.iloc[:, 0].astype(str).tolist()
            else:
                with open(file.name, 'r', encoding='utf-8') as f:
                    input_list = f.readlines()
            
            for item in input_list:
                clean_item = item.strip()
                if clean_item:
                    blob = TextBlob(clean_item)
                    p_score = round(blob.sentiment.polarity, 2)
                    label = "Positive" if p_score > 0.1 else "Negative" if p_score < -0.1 else "Neutral"
                    data_log.append({"Feedback_Text": clean_item, "Sentiment_Label": label, "Score": p_score})
        except Exception as e:
            return f"Error: {e}", 0, None
    
    elif text.strip():
        blob = TextBlob(text)
        p_score = round(blob.sentiment.polarity, 2)
        label = "Positive" if p_score > 0.1 else "Negative" if p_score < -0.1 else "Neutral"
        data_log.append({"Feedback_Text": text.strip(), "Sentiment_Label": label, "Score": p_score})
    
    if not data_log:
        return "No data found", 0, None

    # EXCEL OPTIMIZATION:
    output_path = "NeuralDarsh_Final_Report.csv"
    report_df = pd.DataFrame(data_log)
    
    # We use 'utf-8-sig' because Excel specifically needs it to display emojis and columns correctly.
    report_df.to_csv(output_path, index=False, quoting=csv.QUOTE_ALL, encoding='utf-8-sig')

    # Calculate Overall Stats
    avg_score = round(report_df['Score'].mean(), 2)
    final_mood = "Positive 😊" if avg_score > 0.1 else "Negative 😡" if avg_score < -0.1 else "Neutral 😐"
    
    return final_mood, avg_score, output_path

# 2. THE UI: Professional & Interactive
with gr.Blocks(theme=gr.themes.Default(primary_hue="blue")) as demo:
    gr.Markdown("# 💎 NeuralDarsh: Senti-Analyze Pro")
    gr.Markdown("---")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 📥 Input Area")
            user_text = gr.Textbox(label="Type Review", placeholder="Paste here...", lines=3)
            user_file = gr.File(label="Upload Dataset (.txt or .csv)")
            with gr.Row():
                run_btn = gr.Button("🚀 Analyze", variant="primary")
                clear_btn = gr.Button("🔄 Reset")

        with gr.Column():
            gr.Markdown("### 📊 Results & Export")
            res_label = gr.Label(label="Sentiment Summary")
            res_score = gr.Number(label="Average Polarity Score")
            out_file = gr.File(label="📥 Download Excel-Ready Report")

    run_btn.click(fn=process_data, inputs=[user_text, user_file], outputs=[res_label, res_score, out_file])
    clear_btn.click(lambda: [None, None, None, None, None], outputs=[user_text, user_file, res_label, res_score, out_file])

if __name__ == "__main__":
    demo.launch()