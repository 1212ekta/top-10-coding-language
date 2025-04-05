from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__, static_folder="static")
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the base directory
CSV_FILE = os.path.join(BASE_DIR, "data", "stackoverflow_questions_2022-2025.csv")

# 🔥 Print the CSV file path to check where it's looking for the file
print(f"Looking for CSV file at: {CSV_FILE}")

# 🔥 Check if the file exists
if not os.path.exists(CSV_FILE):
    print("❌ CSV file not found!")
else:
    print("✅ CSV file found!")



# 🎨 Fixed colors for tags
TAG_COLORS = {
    "python": "#377eb8", "java": "#ff7f00", "javascript": "#4daf4a", 
    "c++": "#984ea3", "c#": "#e41a1c", "html": "#f781bf", 
    "css": "#a65628", "react": "#fdae61", "angular": "#66c2a5", 
    "flutter": "#d73027"
}
@app.route('/')
def serve_homepage():
    return send_from_directory('static', 'data.html')

@app.route('/data', methods=['GET'])
def get_json_data():
    """Return JSON data of tag trends."""
    try:
        if not os.path.exists(CSV_FILE):
            return jsonify({"error": "CSV file not found!"}), 404

        df = pd.read_csv(CSV_FILE, encoding="utf-8")
        df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
        df["Year"] = df["Time"].dt.year
        df = df.dropna(subset=["Year"])

        tag_counts = df.groupby(["Year", "Tag"]).size().reset_index(name="Count")
        total_tags_per_year = tag_counts.groupby("Year")["Count"].transform("sum")
        tag_counts["Normalized_Count"] = (tag_counts["Count"] / total_tags_per_year) * 100  # %

        top_tags = tag_counts.groupby("Tag")["Normalized_Count"].sum().nlargest(10).index.tolist()
        tag_counts = tag_counts[tag_counts["Tag"].isin(top_tags)]

        result = {}
        for tag in top_tags:
            tag_data = tag_counts[tag_counts["Tag"] == tag][["Year", "Normalized_Count"]].to_dict(orient="records")
            result[tag] = tag_data

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/data.html')
def serve_data_html():
    """Serve the data.html page from the static folder."""
    return send_from_directory("static", "data.html")


if __name__ == '__main__':
    app.run(debug=True)
