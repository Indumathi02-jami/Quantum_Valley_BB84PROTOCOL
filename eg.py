from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import re
import io
import pypdf
from docx import Document

app = Flask(__name__)
CORS(app)

# Mock internship dataset
INTERNSHIPS_DATA = [
    {"id": 1, "title": "Digital Marketing Intern", "company": "TechCorp India", "sector": "Technology",
     "skills_required": ["digital marketing", "social media", "content writing", "analytics"],
     "location": "Delhi", "description": "Learn digital marketing strategies for tech products",
     "duration": "3 months", "stipend": "₹15,000/month"},
    {"id": 2, "title": "Finance Analyst Intern", "company": "HDFC Bank", "sector": "Banking & Finance",
     "skills_required": ["accounting", "excel", "financial analysis", "data analysis"],
     "location": "Mumbai", "description": "Assist in financial planning and analysis",
     "duration": "6 months", "stipend": "₹20,000/month"},
    {"id": 3, "title": "Software Development Intern", "company": "Infosys", "sector": "IT Services",
     "skills_required": ["python", "web development", "database", "programming"],
     "location": "Bangalore", "description": "Develop web applications and learn software engineering",
     "duration": "4 months", "stipend": "₹25,000/month"},
    # Add more internships as needed
]

# --------------- Recommendation Logic ---------------
def calculate_similarity(candidate_profile, internship):
    candidate_skills = [s.strip().lower() for s in candidate_profile.get('skills', '').split(',')]
    candidate_sector = candidate_profile.get('sector', '').lower()
    candidate_location = candidate_profile.get('location', '').lower()

    internship_skills = [s.lower() for s in internship['skills_required']]
    internship_sector = internship['sector'].lower()
    internship_location = internship['location'].lower()

    skill_matches = len(set(candidate_skills) & set(internship_skills))
    total_skills = len(set(candidate_skills + internship_skills))
    skill_similarity = (skill_matches / max(total_skills, 1)) if total_skills > 0 else 0

    sector_similarity = 1.0 if candidate_sector in internship_sector or internship_sector in candidate_sector else 0.0
    location_similarity = 1.0 if candidate_location in internship_location or internship_location in candidate_location else 0.0

    similarity = (skill_similarity * 0.6) + (sector_similarity * 0.25) + (location_similarity * 0.15)
    return similarity, skill_matches, len(candidate_skills), len(internship_skills)

def get_recommendation_level(similarity_score):
    if similarity_score >= 0.8:
        return {"level": "Best Fit", "icon": "✅", "bg": "#d4edda"}
    elif similarity_score >= 0.6:
        return {"level": "OK", "icon": "🙂", "bg": "#d1ecf1"}
    elif similarity_score >= 0.4:
        return {"level": "Wait", "icon": "⏳", "bg": "#fff3cd"}
    else:
        return {"level": "Skip", "icon": "❌", "bg": "#f8d7da"}

def generate_explanation(candidate_profile, internship, skill_matches, total_candidate_skills, total_internship_skills):
    candidate_skills = [s.strip().lower() for s in candidate_profile.get('skills', '').split(',')]
    internship_skills = [s.lower() for s in internship['skills_required']]
    matched_skills = list(set(candidate_skills) & set(internship_skills))

    explanation = f"🎯 **{internship['title']}** at {internship['company']}\n"
    if matched_skills:
        explanation += f"✅ Skills Match: {', '.join(matched_skills[:3]).title()}\n"
    if candidate_profile.get('sector', '').lower() in internship['sector'].lower():
        explanation += f"🏢 Sector Match: {internship['sector']}\n"
    if candidate_profile.get('location', '').lower() in internship['location'].lower():
        explanation += f"📍 Location Match: {internship['location']}\n"
    explanation += f"⏱️ Duration: {internship['duration']}\n💰 Stipend: {internship['stipend']}"
    return explanation

# ------------------- Routes -------------------
@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Internship Recommendation</title>
<style>
body {font-family: Arial, sans-serif; margin:20px; background:#f7f7f7;}
h1,h2 {color:#333;}
form {margin-bottom:20px; padding:15px; background:#fff; border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,0.1);}
input[type=text], input[type=file] {width:95%; padding:8px; margin:5px 0 15px 0; border:1px solid #ccc; border-radius:4px;}
button {background-color:#4CAF50; color:white; padding:10px 18px; border:none; border-radius:4px; cursor:pointer;}
button:hover {background-color:#45a049;}
#recommendations div {border:1px solid #ccc; margin:10px 0; padding:15px; border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,0.1);}
</style>
</head>
<body>
<h1>Upload Resume</h1>
<form id="resumeForm">
  <input type="file" id="resume" name="resume" accept=".pdf,.docx,.txt" required>
  <button type="submit">Upload Resume</button>
</form>

<h2>Candidate Profile</h2>
<form id="profileForm">
  <label>Skills:</label><br>
  <input type="text" id="skills" name="skills"><br>
  <label>Sector:</label><br>
  <input type="text" id="sector" name="sector"><br>
  <label>Location:</label><br>
  <input type="text" id="location" name="location"><br>
  <label>Education:</label><br>
  <input type="text" id="education" name="education"><br>
  <button type="submit">Get Recommendations</button>
</form>

<h2>Top Recommendations</h2>
<div id="recommendations"></div>

<script>
document.getElementById("resumeForm").addEventListener("submit", async function(e){
    e.preventDefault();
    const formData = new FormData();
    formData.append("resume", document.getElementById("resume").files[0]);
    const res = await fetch("/api/extract-resume", {method:"POST", body: formData});
    const data = await res.json();
    if(data.success){
        document.getElementById("skills").value = data.extracted_data.skills;
        document.getElementById("education").value = data.extracted_data.education;
    } else {
        alert("Error: "+data.error);
    }
});

document.getElementById("profileForm").addEventListener("submit", async function(e){
    e.preventDefault();
    const profile = {
        skills: document.getElementById("skills").value,
        sector: document.getElementById("sector").value,
        location: document.getElementById("location").value,
        education: document.getElementById("education").value
    };
    const res = await fetch("/api/recommend", { 
        method:"POST", 
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify(profile)
    });
    const data = await res.json();
    const recDiv = document.getElementById("recommendations");
    recDiv.innerHTML="";
    if(data.success){
        data.recommendations.forEach(rec=>{
            const box = document.createElement("div");
            box.style.background=rec.recommendation.bg;
            box.innerHTML = `<h3>${rec.internship.title} (${rec.recommendation.icon} ${rec.recommendation.level})</h3>
            <p><b>Company:</b> ${rec.internship.company}</p>
            <p>${rec.explanation.replace(/\\n/g,'<br>')}</p>`;
            recDiv.appendChild(box);
        });
    } else { recDiv.innerHTML="<p style='color:red;'>"+data.error+"</p>"; }
});
</script>
</body>
</html>
''')

@app.route('/api/extract-resume', methods=['POST'])
def extract_resume():
    try:
        if 'resume' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        file = request.files['resume']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        text = ""
        if file.filename.endswith('.pdf'):
            pdf_reader = pypdf.PdfReader(io.BytesIO(file.read()))
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        elif file.filename.endswith('.docx'):
            doc = Document(io.BytesIO(file.read()))
            for para in doc.paragraphs:
                text += para.text + "\n"
        else:
            text = file.read().decode('utf-8', errors='ignore')

        # Skills extraction
        common_skills = ['python','java','javascript','html','css','react','angular','node.js','data analysis','machine learning','sql','excel','powerpoint','word','communication','teamwork','leadership','problem solving','creativity','accounting','finance','marketing','sales','research','writing','photoshop','illustrator','cad','autocad','design','project management']
        text_lower = text.lower()
        found_skills = [s for s in common_skills if s in text_lower]

        # Education extraction
        education_patterns = [r'b\.?tech|bachelor.*technology|engineering',r'b\.?sc|bachelor.*science',r'b\.?com|bachelor.*commerce',
                              r'b\.?a|bachelor.*arts',r'm\.?tech|master.*technology',r'm\.?sc|master.*science',r'mba|master.*business',
                              r'diploma',r'12th|intermediate|higher.*secondary',r'10th|matriculation|secondary']
        education = "Not specified"
        for pattern in education_patterns:
            if re.search(pattern,text_lower):
                if 'tech' in pattern: education="B.Tech/Engineering"
                elif 'mba' in pattern: education="MBA"
                elif 'master' in pattern: education="Post Graduate"
                elif 'bachelor' in pattern: education="Graduate"
                elif 'diploma' in pattern: education="Diploma"
                elif '12th' in pattern: education="12th Pass"
                break

        return jsonify({'success': True, 'extracted_data': {'skills': ', '.join(found_skills[:10]), 'education': education}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/recommend', methods=['POST'])
def recommend():
    try:
        candidate_profile = request.json
        recommendations=[]
        for internship in INTERNSHIPS_DATA:
            similarity, skill_matches, c_skills, i_skills = calculate_similarity(candidate_profile, internship)
            recommendation_level = get_recommendation_level(similarity)
            explanation = generate_explanation(candidate_profile, internship, skill_matches, c_skills, i_skills)
            recommendations.append({'internship': internship, 'similarity_score': similarity, 'recommendation': recommendation_level, 'explanation': explanation})
        recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)
        return jsonify({'success': True, 'recommendations': recommendations[:5]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
