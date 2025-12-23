from flask import Flask, render_template, request, send_file
import os
from src.pipeline import clean_dataset

app = Flask(__name__)

# Folders
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")

        if not file or file.filename == "":
            return render_template("index.html", error="No file selected")

        filename = file.filename
        ext = os.path.splitext(filename)[1].lower()

        if ext not in [".csv", ".pdf"]:
            return render_template(
                "index.html",
                error="Only CSV and text-based PDF files are supported"
            )

        input_path = os.path.join(UPLOAD_FOLDER, filename)
        output_path = os.path.join(
            OUTPUT_FOLDER,
            "cleaned_" + os.path.splitext(filename)[0] + ".csv"
        )

        file.save(input_path)

        # Run cleaning pipeline
        df, dqi_before, dqi_after, plots, nlg_summary = clean_dataset(input_path)

        # Save cleaned dataset
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
    return send_file(file_path, as_attachment=True)


# 🔹 REQUIRED FOR DEPLOYMENT (Render / Cloud)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
