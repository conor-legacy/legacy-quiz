from flask import Flask, render_template, request, redirect, url_for, session, make_response
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from xhtml2pdf import pisa # type: ignore
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

sections = [
    {
        "name": "Exit Readiness",
        "questions": [
            {
                "question": "How would the business perform if you and/ or the other owners working in the company spent time away for 3 months?",
                "options": [
                    {"text": "Operations would continue unchanged", "points": 5},
                    {"text": "Operations would be affected but not critically", "points": 3},
                    {"text": "Operations would be majorly impacted but the company would survive", "points": 1},
                    {"text": "Operations would likely not be able to continue", "points": 0}
                ]
            },
            {
                "question": "How active are the owners in the day to day running of the business? (days per week)",
                "options": [
                    {"text": "The owners work 0-1 days per week", "points": 5},
                    {"text": "The owners work 2-3 days per week", "points": 2},
                    {"text": "The owners work > 4 days per week", "points": 0}
                ]
            },
            {
                "question": "A leadership team capable of independently leading the company without you …",
                "options": [
                    {"text": "already exists", "points": 5},
                    {"text": "is currently being developed", "points": 4},
                    {"text": "would be possible to construct with the existing staff", "points": 2},
                    {"text": "would be hardly possible with the existing staff", "points": 1},
                    {"text": "is currently unrealistic due to the size of the company", "points": 0}
                ]
            },
            {
                "question": "Ideally, when would you like to exit the company?",
                "options": [
                    {"text": "As soon as possible", "points": 5},
                    {"text": "In the next 1-2 years", "points": 3},
                    {"text": "In the next 3-5 years", "points": 2},
                    {"text": "I am currently not looking to sell", "points": 0}
                ]
            },
            {
                "question": "How prepared are the company’s financial records for due diligence by potential buyers?",
                "options": [
                    {"text": "Our financial records are well-organized and ready for due diligence at any time", "points": 5},
                    {"text": "Our financial records are generally organized but may require some preparation for due diligence", "points": 3},
                    {"text": "Our financial records are somewhat disorganized and would need significant work to be ready for due diligence", "points": 1},
                    {"text": "Our financial records are not ready for due diligence and would require a complete overhaul", "points": 0}
                ]
            },
            {
                "question": "Is there a documented succession plan in place for key roles within the company?",
                "options": [
                    {"text": "Yes, there is a detailed and documented succession plan for all key roles", "points": 5},
                    {"text": "Yes, there is a documented succession plan, but it needs updating", "points": 3},
                    {"text": "There is an informal succession plan, but it is not documented", "points": 2},
                    {"text": "No, there is no succession plan in place", "points": 0}
                ]
            }
        ]
    },
    {
        "name": "Fundamentals",
        "questions": [
            {
                "question": "The business Profit and Loss accounts are reviewed …",
                "options": [
                    {"text": "Weekly", "points": 5},
                    {"text": "Monthly", "points": 4},
                    {"text": "Quarterly", "points": 2},
                    {"text": "Annually", "points": 1},
                    {"text": "My external accountant is in charge of reviewing accounts", "points": 0}
                ]
            },
            {
                "question": "What is the customer/ client concentration of the company?",
                "options": [
                    {"text": "We have a diverse mix of customers/ clients ensuring no client accounts for more than 5% of total sales", "points": 5},
                    {"text": "We have a diverse mix of customers/ clients ensuring no client accounts for more than 20% of total sales", "points": 3},
                    {"text": "We have customers/ clients that account for more than 20% of total sales", "points": 1},
                    {"text": "One customer accounts for the majority of sales", "points": 0}
                ]
            },
            {
                "question": "What is the nature of the company's revenue?",
                "options": [
                    {"text": "The majority of our revenue is recurring and comes from long-term contracts or subscriptions", "points": 5},
                    {"text": "We have a mix of recurring and one-time revenue, with a significant portion being recurring", "points": 4},
                    {"text": "Most of our revenue is one-time, but we are working on increasing our recurring revenue streams", "points": 2},
                    {"text": "Our revenue is primarily one-time sales without significant recurring revenue streams", "points": 0}
                ]
            },
            {
                "question": "How often does the company update its strategic business plan?",
                "options": [
                    {"text": "Annually", "points": 5},
                    {"text": "Every 2-3 years", "points": 3},
                    {"text": "Only when significant changes occur", "points": 1},
                    {"text": "We do not have a formal strategic business plan", "points": 0}
                ]
            },
            {
                "question": "How does the company handle financial forecasting and budgeting?",
                "options": [
                    {"text": "We have a comprehensive annual forecasting and budgeting process", "points": 5},
                    {"text": "We create budgets and forecasts, but they are not updated regularly", "points": 3},
                    {"text": "Financial forecasting and budgeting are done informally or as needed", "points": 1},
                    {"text": "We do not have a formal process for financial forecasting and budgeting", "points": 0}
                ]
            },
            {
                "question": "What is the company’s approach to investment in technology and innovation?",
                "options": [
                    {"text": "We regularly invest in new technologies and innovation to stay competitive", "points": 5},
                    {"text": "We invest in technology and innovation sporadically, as needed", "points": 3},
                    {"text": "We invest minimally in technology and innovation", "points": 1},
                    {"text": "We do not prioritize investment in technology and innovation", "points": 0}
                ]
            }
        ]
    },
    {
        "name": "Operations",
        "questions": [
            {
                "question": "Are there Standard Operating Procedures (SPO’s) in place in the company?",
                "options": [
                    {"text": "There are very clear and defined SPO’s in place that the staff have received extensive training in and are monitored continuously", "points": 5},
                    {"text": "There are SPO’s in place, but their implementation is not regularly monitored", "points": 3},
                    {"text": "There are SOPs in place, but they are currently being updated or revised", "points": 1},
                    {"text": "There are no SPO’s in place, individual staff members have their own way of carrying out the company operations", "points": 0}
                ]
            },
            {
                "question": "Are there Key Performance Indicators (KPI’s) in place in the company?",
                "options": [
                    {"text": "Each department within the company have clear KPI’s in place with specific timelines that are regularly assessed, and progress monitored", "points": 5},
                    {"text": "The company have some KPI’s in place with clear/ approximate timelines and we assess whether they were met after the timeline", "points": 4},
                    {"text": "The company is currently developing KPI’s", "points": 1},
                    {"text": "The company does not have KPI’s in place", "points": 0}
                ]
            },
            {
                "question": "How efficient are the company's supply chain and logistics operations?",
                "options": [
                    {"text": "Our supply chain and logistics operations are highly efficient, with minimal delays and optimized costs", "points": 5},
                    {"text": "Our supply chain and logistics operations are generally efficient, but there are occasional delays and areas for cost optimization", "points": 3},
                    {"text": "Our supply chain and logistics operations face frequent delays and inefficiencies, and there is significant room for improvement", "points": 1},
                    {"text": "We do not have a well-defined supply chain and logistics strategy, leading to frequent disruptions and high costs", "points": 0}
                ]
            },
            {
                "question": "Should the company grow, how easily could the necessary staff be recruited?",
                "options": [
                    {"text": "Recruiting and training staff for further growth is smooth", "points": 5},
                    {"text": "We have a system in place for recruiting and training staff, making it manageable", "points": 3},
                    {"text": "Recruiting and training staff for further growth is a significant challenge, yet doable", "points": 1},
                    {"text": "Recruiting and training staff for further growth is very difficult", "points": 0}
                ]
            },
            {
                "question": "What is your current assessment of the labour market for company-relevant staff?",
                "options": [
                    {"text": "There is no shortage of skilled workers on the labour market for company-relevant staff", "points": 5},
                    {"text": "There is noticeable competition on the labour market for company-relevant staff", "points": 3},
                    {"text": "There is a high shortage on the labour market for company-relevant staff and this is a major challenge for the company", "points": 0}
                ]
            },
            {
                "question": "How would you rate the company's internal communication?",
                "options": [
                    {"text": "Internal communication is clear, transparent, and frequent", "points": 5},
                    {"text": "Internal communication is generally good but could be improved", "points": 3},
                    {"text": "Internal communication is inconsistent and often unclear", "points": 1},
                    {"text": "Internal communication is poor and lacks transparency", "points": 0}
                ]
            }
        ]
    },
    {
        "name": "Growth",
        "questions": [
            {
                "question": "How would you describe the current marketing strategy of the company?",
                "options": [
                    {"text": "We have a clear and effective strategy in place to identify various clients and to target them with the right offer", "points": 5},
                    {"text": "We have a basic strategy that we follow but it needs improving", "points": 3},
                    {"text": "We are currently developing a comprehensive marketing strategy", "points": 1},
                    {"text": "We rely primarily on word-of-mouth and referrals without a formal marketing strategy", "points": 0}
                ]
            },
            {
                "question": "What is the company's strategy for product or service innovation?",
                "options": [
                    {"text": "We have a dedicated team and budget for continuous innovation and development", "points": 5},
                    {"text": "We occasionally invest in innovation when opportunities arise", "points": 3},
                    {"text": "Innovation is not a primary focus, but we make improvements as needed", "points": 2},
                    {"text": "We have no formal strategy for innovation", "points": 0}
                ]
            },
            {
                "question": "How would you describe the current online marketing strategy of the company?",
                "options": [
                    {"text": "We have a comprehensive online marketing strategy that includes active methods such as social media engagement, targeted email campaigns, and SEO optimization", "points": 5},
                    {"text": "We have a solid online marketing strategy with active social media and email marketing, but our efforts lack consistency and a clear direction.", "points": 3},
                    {"text": "Our online marketing strategy is in the early stages of development, with some social media and email activities being implemented.", "points": 2},
                    {"text": "We do not have a formal online marketing strategy and rely primarily on traditional marketing methods with minimal online presence.", "points": 0}
                ]
            },
            {
                "question": "How scalable are the company’s operations to support growth?",
                "options": [
                    {"text": "Our operations are highly scalable and can support significant growth without major changes", "points": 5},
                    {"text": "Our operations are somewhat scalable but would require some adjustments to support significant growth", "points": 3},
                    {"text": "Our operations have limited scalability and would need major changes to support significant growth", "points": 1},
                    {"text": "Our operations are not scalable and would struggle to support growth", "points": 0}
                ]
            },
            {
                "question": "How strong is the company's competitive position in the market?",
                "options": [
                    {"text": "We are a market leader with a strong competitive position", "points": 5},
                    {"text": "We have a solid competitive position but face significant competition", "points": 4},
                    {"text": "Our competitive position is moderate, and we are working to strengthen it", "points": 2},
                    {"text": "Our competitive position is weak, and we struggle to compete effectively", "points": 0}
                ]
            },
            {
                "question": "How well does the company understand its target market and customer needs?",
                "options": [
                    {"text": "We have a deep understanding of our target market and customer needs, which drives our growth strategy", "points": 5},
                    {"text": "We have a good understanding of our target market but could improve our insights into customer needs", "points": 3},
                    {"text": "Our understanding of the target market and customer needs is limited and needs improvement", "points": 1},
                    {"text": "We have minimal understanding of our target market and customer needs", "points": 0}
                ]
            }
        ]
    }
]

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_USERNAME = 'legacytest2024@gmail.com'
EMAIL_PASSWORD = 'rijtdcjfyhpuffht'
RECIPIENT_EMAIL = 'conorpower357@gmail.com'

@app.route('/')
def index():
    return render_template('index.html', sections=sections, enumerate=enumerate)

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        answers = request.form.to_dict()
        section_scores = {}
        total_score = 0

        for section_index, section in enumerate(sections):
            section_score = 0
            for question_index, question in enumerate(section["questions"]):
                key = f"section{section_index}_question{question_index}"
                value = answers.get(key)
                if value:
                    for option in question["options"]:
                        if option["text"] == value:
                            section_score += option["points"]
                            total_score += option["points"]
            section_scores[section["name"]] = section_score

        # Store the scores in the session
        session['total_score'] = total_score
        session['section_scores'] = section_scores
        session['answers'] = answers

        return redirect(url_for('result'))

@app.route('/result')
def result():
    total_score = session.get('total_score', 0)
    section_scores = session.get('section_scores', {})
    answers = session.get('answers', {})

    # Calculate percentage scores for each section based on a fixed max score of 30
    section_percentages = {section: (score / 30 * 100) for section, score in section_scores.items()}

    # Calculate the overall percentage score
    overall_percentage = total_score / (30 * len(section_scores)) * 100

    # Generate colors based on score
    def get_color(percentage):
        if percentage > 80:
            return '#4ACD3F'  # Darker green
        elif 50 <= percentage <= 80:
            return '#FF8000'  # Orange
        else:
            return '#B22222'  # Darker red

    labels = list(section_percentages.keys())
    sizes = list(section_percentages.values())
    colors = [get_color(pct) for pct in sizes]  # Assign colors based on percentage

    def make_autopct(values):
        def my_autopct(pct):
            total = sum(values)
            val = int(round(pct * total / 100.0))
            return f'{val:.0f}%'
        return my_autopct

    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, autopct=make_autopct(sizes),
        startangle=90, textprops=dict(color="w"), wedgeprops=dict(width=0.5, edgecolor='white', linewidth=3)
    )

    # Improve label visibility and position
    for text in texts:
        text.set_color('black')
        text.set_fontsize(10)
        text.set_weight('bold')

    for autotext, wedge in zip(autotexts, wedges):
        autotext.set_color('white')
        autotext.set_fontsize(10)
        autotext.set_weight('bold')
        # Position the text closer to the outer edge
        angle = (wedge.theta2 - wedge.theta1) / 2.0 + wedge.theta1
        x = wedge.r * 0.75 * np.cos(np.deg2rad(angle))
        y = wedge.r * 0.75 * np.sin(np.deg2rad(angle))
        autotext.set_position((x, y))

    # Add a smaller circle at the center to make it look like a donut chart
    centre_circle = plt.Circle((0, 0), 0.5, fc='white')
    fig.gca().add_artist(centre_circle)

    # Add overall percentage in the center of the donut chart
    plt.text(0, 0.1, 'Your overall score is:', ha='center', va='center', fontsize=10, color='black', weight='bold')
    plt.text(0, -0.1, f'{overall_percentage:.0f}%', ha='center', va='center', fontsize=14, color='black', weight='bold')

    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    chart_url = base64.b64encode(img.getvalue()).decode()

    # Render the HTML result page to a string
    result_html = render_template('result.html', chart_url=chart_url, total_score=total_score, section_scores=section_scores, section_percentages=section_percentages)

    # Convert HTML to PDF
    pdf_file = convert_html_to_pdf(result_html)

    # Send email with the results
    send_email(total_score, section_scores, answers, pdf_file)

    return render_template('result.html', chart_url=chart_url)

def convert_html_to_pdf(source_html):
    result_file = io.BytesIO()

    # Convert HTML to PDF
    pisa_status = pisa.CreatePDF(
        source_html,                   # the HTML to convert
        dest=result_file)              # file handle to receive result

    # If the conversion is successful, pisa_status.err will be False
    if not pisa_status.err:
        result_file.seek(0)  # Rewind the file handle to the beginning
        return result_file
    return None

def send_email(total_score, section_scores, answers, pdf_file):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USERNAME
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = 'Quiz Results'

    body = f"Total Score: {total_score}\n\nSection Scores:\n"
    for section, score in section_scores.items():
        body += f"{section}: {score}\n"
    
    body += "\nAnswers:\n"
    for question, answer in answers.items():
        body += f"{question}: {answer}\n"

    msg.attach(MIMEText(body, 'plain'))

    # Attach the PDF file
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(pdf_file.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= result.pdf")
    msg.attach(part)

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_USERNAME, RECIPIENT_EMAIL, text)
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == '__main__':
    app.run(debug=True)