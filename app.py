from flask import Flask, render_template, request, send_file
import os
from src.pipeline import clean_dataset

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")

        if not file or file.filename == "":
            return render_template("index.html", error="Please select a file")

        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in [".csv", ".pdf"]:
            return render_template("index.html", error="Only CSV or PDF files are supported")

        input_path = os.path.join(UPLOAD_FOLDER, file.filename)
        output_path = os.path.join(OUTPUT_FOLDER, f"cleaned_{file.filename}.csv")

        file.save(input_path)

        df, dqi_before, dqi_after, plots, nlg_summary = clean_dataset(input_path)
        df.to_csv(output_path, index=False)

        return render_template(
            "index.html",
            dqi_before=dqi_before,
            dqi_after=dqi_after,
            plots=plots,
            nlg_summary=nlg_summary,
            download_file=output_path
        )

    return render_template("index.html")


@app.route("/download")
def download():
    file_path = request.args.get("file")
    if file_path and os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
