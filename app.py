from flask import Flask, render_template, request, redirect, url_for, session, make_response, send_file
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
import plotly.graph_objs as go # type: ignore
import plotly.io as pio # type: ignore


app = Flask(__name__)
app.secret_key = 'your_secret_key'

sections = [
    {
        "name": "General Information",
        "questions": [
            {"question": "What is your name?", "type": "text", "name": "name"},
            {"question": "What is your age?", "type": "number", "name": "age"},
            {"question": "What is your email address?", "type": "email", "name": "email"},
            {"question": "What is your company name?", "type": "text", "name": "company_name"},
            {"question": "What industry does your company operate in?", "type": "select", "name": "industry", "options": [
                {"text": "Automotive and Boat", "suboptions": ["Auto Repair and Service Shops", "Car Dealerships", "Car Washes", "Equipment Rental and Dealers", "Gas Stations", "Junk and Salvage Yards", "Marine/Boat Service and Dealers", "Towing Companies", "Truck Stops"]},
                {"text": "Beauty and Personal Care", "suboptions": ["Hair Salons and Barber Shops", "Massage Businesses", "Nail Salons", "Spas", "Tanning Salons"]},
                {"text": "Building and Construction", "suboptions": ["Building Material and Hardware Stores", "Concrete Businesses", "Electrical and Mechanical Contracting Businesses", "Heavy Construction Businesses", "HVAC Businesses", "Plumbing Businesses"]},
                {"text": "Communication and Media", "suboptions": ["Magazines and Newspapers", "Production Companies"]},
                {"text": "Education and Children", "suboptions": ["Day Care and Child Care Centers", "Preschools", "Schools"]},
                {"text": "Entertainment and Recreation", "suboptions": ["Art Galleries", "Banquet Halls", "Bowling Alleys", "Casinos", "Golf Courses and Services", "Marinas and Fishing", "Nightclubs and Theaters"]},
                {"text": "Financial Services", "suboptions": ["Accounting and Tax Practices", "Banking and Loan Businesses", "Check Cashing Businesses", "Financial Services Businesses", "Insurance Agencies"]},
                {"text": "Food and Restaurants", "suboptions": ["Bakeries", "Bars, Pubs and Taverns", "Breweries", "Coffee Shops and Cafes", "Donut Shops", "Food Trucks", "Ice Cream and Frozen Yogurt Shops", "Juice Bars", "Restaurants"]},
                {"text": "Health Care and Fitness", "suboptions": ["Assisted Living and Nursing Homes", "Dance, Pilates, and Yoga Studios", "Dental Practices", "Gyms and Fitness Centers", "Home Health Care Businesses", "Medical Practices"]},
                {"text": "Manufacturing", "suboptions": ["Auto, Boat and Aircraft Manufacturers", "Chemical and Related Product Manufacturers", "Clothing and Fabric Manufacturers", "Electronic and Electrical Equipment Manufacturers", "Food and Related Product Manufacturers", "Furniture and Fixture Manufacturers", "Glass, Stone, and Concrete Manufacturers", "Industrial and Commercial Machinery Manufacturers", "Lumber and Wood Products Manufacturers", "Machine Shops and Tool Manufacturers", "Medical Device and Product Manufacturers", "Metal Product Manufacturers", "Packaging Businesses", "Paper Manufacturers and Printing Businesses", "Rubber and Plastic Products Manufacturers", "Sign Manufacturers and Businesses"]},
                {"text": "Online and Technology", "suboptions": ["Cell Phone and Computer Repair and Service Businesses", "Graphic and Web Design Businesses", "IT and Software Service Businesses", "Software and App Companies", "Websites and Ecommerce Businesses"]},
                {"text": "Pet Services", "suboptions": ["Dog Daycare and Boarding Businesses", "Pet Grooming Businesses", "Pet Stores and Supply Businesses"]},
                {"text": "Retail", "suboptions": ["Bike Shops", "Clothing and Accessory Stores", "Convenience Stores", "Dollar Stores", "Flower Shops", "Furniture and Furnishings Stores", "Grocery Stores and Supermarkets", "Health Food and Nutrition Businesses", "Jewelry Stores", "Liquor Stores", "Nursery and Garden Centers", "Pawn Shops", "Pharmacies", "Smoke Shops", "Vending Machine Businesses"]},
                {"text": "Service Businesses", "suboptions": ["Architecture and Engineering Firms", "Catering Companies", "Cleaning Businesses", "Commercial Laundry Businesses", "Dry Cleaners", "Funeral Homes", "Landscaping and Yard Service Businesses", "Laundromats and Coin Laundry Businesses", "Legal Services and Law Firms", "Locksmith Businesses", "Medical Billing Businesses", "Pest Control Businesses", "Property Management Businesses", "Security Businesses", "Staffing Agencies", "Waste Management and Recycling Businesses"]},
                {"text": "Transportation and Storage", "suboptions": ["Delivery, Freight and Service Routes", "Limo and Passenger Transportation Businesses", "Moving and Shipping Businesses", "Storage Facilities and Warehouses", "Trucking Companies"]},
                {"text": "Wholesale and Distributors", "suboptions": ["Durable Goods Wholesalers and Distributors", "Nondurable Goods Wholesalers and Distributors"]}
            ]}
        ]
    },
    {
        "name": "Business Health Check",
        "subsections": [
            {
                "name": "Exit Readiness",
                "questions": [
                    {
                        "text": "1. How would the business perform if you and/ or the other owners working in the company spent time away for 3 months?",
                        "options": [
                            {"text": "Operations would continue unchanged", "points": 5},
                            {"text": "Operations would be affected but not critically", "points": 3},
                            {"text": "Operations would be majorly impacted but the company would survive", "points": 1},
                            {"text": "Operations would likely not be able to continue", "points": 0}
                        ]
                    },
                    {
                        "text": "2. How active are the owners in the day to day running of the business? (days per week)",
                        "options": [
                            {"text": "The owners work 0-1 days per week", "points": 5},
                            {"text": "The owners work 2-3 days per week", "points": 2},
                            {"text": "The owners work > 3 days per week", "points": 0}
                        ]
                    },
                    {
                        "text": "3. A leadership team capable of independently leading the company without you …",
                        "options": [
                            {"text": "already exists", "points": 5},
                            {"text": "is currently being developed", "points": 4},
                            {"text": "would be possible to construct with the existing staff", "points": 2},
                            {"text": "would be hardly possible with the existing staff", "points": 1},
                            {"text": "is currently unrealistic due to the size of the company", "points": 0}
                        ]
                    },
                    {
                        "text": "4. Ideally, when would you like to exit the company?",
                        "options": [
                            {"text": "As soon as possible", "points": 5},
                            {"text": "In the next 1-2 years", "points": 3},
                            {"text": "In the next 3-5 years", "points": 2},
                            {"text": "I am currently not looking to sell", "points": 0}
                        ]
                    },
                    {
                        "text": "5. How prepared are the company’s financial records for due diligence by potential buyers?",
                        "options": [
                            {"text": "Our financial records are well-organized and ready for due diligence at any time", "points": 5},
                            {"text": "Our financial records are generally organized but may require some preparation for due diligence", "points": 3},
                            {"text": "Our financial records are somewhat disorganized and would need significant work to be ready for due diligence", "points": 1},
                            {"text": "Our financial records are not ready for due diligence and would require a complete overhaul", "points": 0}
                        ]
                    },
                    {
                        "text": "6. Is there a documented succession plan in place for key roles within the company?",
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
                        "text": "1. The business Profit and Loss accounts are reviewed …",
                        "options": [
                            {"text": "Weekly", "points": 5},
                            {"text": "Monthly", "points": 4},
                            {"text": "Quarterly", "points": 2},
                            {"text": "Annually", "points": 1},
                            {"text": "My external accountant is in charge of reviewing accounts", "points": 0}
                        ]
                    },
                    {
                        "text": "2. What is the customer/ client concentration of the company?",
                        "options": [
                            {"text": "We have a diverse mix of customers/ clients ensuring no client accounts for more than 5% of total sales", "points": 5},
                            {"text": "We have a diverse mix of customers/ clients ensuring no client accounts for more than 20% of total sales", "points": 3},
                            {"text": "We have customers/ clients that account for more than 20% of total sales", "points": 1},
                            {"text": "One customer accounts for the majority of sales", "points": 0}
                        ]
                    },
                    {
                        "text": "3. What is the nature of the company's revenue?",
                        "options": [
                            {"text": "The majority of our revenue is recurring and comes from long-term contracts or subscriptions", "points": 5},
                            {"text": "We have a mix of recurring and one-time revenue, with a significant portion being recurring", "points": 4},
                            {"text": "Most of our revenue is one-time, but we are working on increasing our recurring revenue streams", "points": 2},
                            {"text": "Our revenue is primarily one-time sales without significant recurring revenue streams", "points": 0}
                        ]
                    },
                    {
                        "text": "4. How often does the company update its strategic business plan?",
                        "options": [
                            {"text": "Annually", "points": 5},
                            {"text": "Every 2-3 years", "points": 3},
                            {"text": "Only when significant changes occur", "points": 1},
                            {"text": "We do not have a formal strategic business plan", "points": 0}
                        ]
                    },
                    {
                        "text": "5. How does the company handle financial forecasting and budgeting?",
                        "options": [
                            {"text": "We have a comprehensive annual forecasting and budgeting process", "points": 5},
                            {"text": "We create budgets and forecasts, but they are not updated regularly", "points": 3},
                            {"text": "Financial forecasting and budgeting are done informally or as needed", "points": 1},
                            {"text": "We do not have a formal process for financial forecasting and budgeting", "points": 0}
                        ]
                    },
                    {
                        "text": "6. To what extent has the company adopted digital technology to help with its internal processes?",
                        "options": [
                            {"text": "Fully, we use software for all key internal processes", "points": 5},
                            {"text": "Mostly, we mainly use software for internal processes but we still use some paper records", "points": 3},
                            {"text": "Partially, we still mainly use paper records for most processes", "points": 1},
                            {"text": "Not at all, we use paper records for all processes", "points": 0}
                        ]
                    }
                ]
            },
            {
                "name": "Operations",
                "questions": [
                    {
                        "text": "1. Are there Standard Operating Procedures (SPO’s) in place in the company?",
                        "options": [
                            {"text": "There are very clear and defined SPO’s in place that the staff have received extensive training in and are monitored continuously", "points": 5},
                            {"text": "There are SPO’s in place, but their implementation is not regularly monitored", "points": 3},
                            {"text": "There are SOPs in place, but they are currently being updated or revised", "points": 1},
                            {"text": "There are no SPO’s in place, individual staff members have their own way of carrying out the company operations", "points": 0}
                        ]
                    },
                    {
                        "text": "2. Are there Key Performance Indicators (KPI’s) in place in the company?",
                        "options": [
                            {"text": "Each department within the company have clear KPI’s in place with specific timelines that are regularly assessed, and progress monitored", "points": 5},
                            {"text": "The company have some KPI’s in place with clear/ approximate timelines and we assess whether they were met after the timeline", "points": 4},
                            {"text": "The company is currently developing KPI’s", "points": 1},
                            {"text": "The company does not have KPI’s in place", "points": 0}
                        ]
                    },
                    {
                        "text": "3. How efficient are the company's supply chain and logistics operations?",
                        "options": [
                            {"text": "Our supply chain and logistics operations are highly efficient, with minimal delays and optimized costs", "points": 5},
                            {"text": "Our supply chain and logistics operations are generally efficient, but there are occasional delays and areas for cost optimization", "points": 3},
                            {"text": "Our supply chain and logistics operations face frequent delays and inefficiencies, and there is significant room for improvement", "points": 1},
                            {"text": "We do not have a well-defined supply chain and logistics strategy, leading to frequent disruptions and high costs", "points": 0}
                        ]
                    },
                    {
                        "text": "4. How does the company handle quality control?",
                        "options": [
                            {"text": "We have a comprehensive quality control process that includes regular inspections and corrective actions", "points": 5},
                            {"text": "We have a quality control process in place, but it is not consistently applied", "points": 3},
                            {"text": "Quality control is handled on an ad-hoc basis without a formal process", "points": 1},
                            {"text": "We do not have a quality control process", "points": 0}
                        ]
                    },
                    {
                        "text": "5. What is your current assessment of the labour market for company-relevant staff?",
                        "options": [
                            {"text": "There is no shortage of skilled workers on the labour market for company-relevant staff", "points": 5},
                            {"text": "There is noticeable competition on the labour market for company-relevant staff", "points": 3},
                            {"text": "There is a high shortage on the labour market for company-relevant staff and this is a major challenge for the company", "points": 0}
                        ]
                    },
                    {
                        "text": "6. Do you have a backup supplier for if your most important supplier stopped operating or could not deliver?",
                        "options": [
                            {"text": "We have many options for backup suppliers and this is not a problem for us", "points": 5},
                            {"text": "We have some possible backup suppliers", "points": 3},
                            {"text": "We have no clear backup suppliers however, we could find a way to survive", "points": 1},
                            {"text": "We have no back up option and the company would likely face collapse", "points": 0}
                        ]
                    }
                ]
            },
            {
                "name": "Sales and Marketing",
                "questions": [
                    {
                        "text": "1. How would you describe the current marketing strategy of the company?",
                        "options": [
                            {"text": "We have a clear and effective strategy in place to identify various clients and to target them with the right offer", "points": 5},
                            {"text": "We have a basic strategy that we follow but it needs improving", "points": 3},
                            {"text": "We are currently developing a comprehensive marketing strategy", "points": 1},
                            {"text": "We rely primarily on word-of-mouth and referrals without a formal marketing strategy", "points": 0}
                        ]
                    },
                    {
                        "text": "2. What percentage of the coming year's revenues have already been contractually agreed?",
                        "options": [
                            {"text": "More than 75%", "points": 5},
                            {"text": "51-75%", "points": 3},
                            {"text": "15-50%", "points": 2},
                            {"text": "0-15%", "points": 0}
                        ]
                    },
                    {
                        "text": "3. How would you describe the current online marketing strategy of the company?",
                        "options": [
                            {"text": "We have a comprehensive online marketing strategy that includes active methods such as social media engagement, targeted email campaigns, and SEO optimization", "points": 5},
                            {"text": "We have a solid online marketing strategy with active social media and email marketing, but our efforts lack consistency and a clear direction", "points": 3},
                            {"text": "Our online marketing strategy is in the early stages of development, with some social media and email activities being implemented", "points": 2},
                            {"text": "We do not have a formal online marketing strategy and rely primarily on traditional marketing methods with minimal online presence", "points": 0}
                        ]
                    },
                    {
                        "text": "4. How regularly does your company carry out customer surveys and incorporate Net Promoter Score (NPS) into your marketing strategy?",
                        "options": [
                            {"text": "Regularly (at least once per quarter), we conduct customer surveys regularly and actively use the Net Promoter Score (NPS) to guide our marketing and sales strategies", "points": 5},
                            {"text": "Occasionally (once or twice a year), we conduct customer surveys occasionally and use the Net Promoter Score (NPS) to inform some of our marketing decisions", "points": 3},
                            {"text": "Rarely (less than once a year), we conduct customer surveys infrequently, and the Net Promoter Score (NPS) is only sometimes considered in our marketing strategy", "points": 1},
                            {"text": "Never, we do not conduct customer surveys, and the Net Promoter Score (NPS) is not a part of our marketing strategy", "points": 0}
                        ]
                    },
                    {
                        "text": "5. Do you have a sales person or team in place with clear targets and performance-based incentives?",
                        "options": [
                            {"text": "Yes, we have a dedicated sales team with clear targets and strong performance-based incentives", "points": 5},
                            {"text": "We have a sales team, but targets and incentives need improvement", "points": 4},
                            {"text": "We have a sales team, but no clear targets or performance-based incentives", "points": 2},
                            {"text": "No, we do not have a dedicated sales person or team", "points": 0}
                        ]
                    },
                    {
                        "text": "6. How well does the company understand its target market and customer needs?",
                        "options": [
                            {"text": "We have a deep understanding of our target market and customer needs, which drives our growth strategy", "points": 5},
                            {"text": "We have a good understanding of our target market but could improve our insights into customer needs", "points": 3},
                            {"text": "Our understanding of the target market and customer needs is limited and needs improvement", "points": 1},
                            {"text": "We have minimal understanding of our target market and customer needs", "points": 0}
                        ]
                    }
                ]
            },
            {
                "name": "Growth",
                "questions": [
                    {
                        "text": "1. How much capacity does your company have to take on more customers and demand?",
                        "options": [
                            {"text": "High capacity, we have significant capacity and can easily accommodate a substantial increase in customers and demand", "points": 5},
                            {"text": "Moderate capacity, we have moderate capacity and can handle some additional customers and demand without major adjustments", "points": 3},
                            {"text": "Limited capacity, we have limited capacity and can only take on a small number of additional customers and demand", "points": 1},
                            {"text": "No capacity, we are currently at full capacity and cannot take on any more customers or demand without expanding our resources", "points": 0}
                        ]
                    },
                    {
                        "text": "2. Should the company grow, how easily could the necessary staff be recruited?",
                        "options": [
                            {"text": "Recruiting and training staff for further growth is smooth", "points": 5},
                            {"text": "We have a system in place for recruiting and training staff, making it manageable", "points": 3},
                            {"text": "Recruiting and training staff for further growth is a significant challenge, yet doable", "points": 1},
                            {"text": "Recruiting and training staff for further growth is very difficult", "points": 0}
                        ]
                    },
                    {
                        "text": "3. How easy is it for a customer to find an alternative product or a workaround solution instead of using your company?",
                        "options": [
                            {"text": "Not easily at all, our products, services, or business model are highly unique and protected by strong intellectual property, proprietary processes, or significant competitive advantages", "points": 5},
                            {"text": "With some difficulty, our products, services, or business model have unique aspects that are not readily available", "points": 3},
                            {"text": "Fairly easily, our product is not particularly unique and similar products are readily available", "points": 1},
                            {"text": "Very easily, there is little to no difference between our product and other products on the market", "points": 0}
                        ]
                    },
                    {
                        "text": "4. How strong is the company's competitive position in the market?",
                        "options": [
                            {"text": "We are a market leader with a strong competitive position", "points": 5},
                            {"text": "We have a solid competitive position but face significant competition", "points": 4},
                            {"text": "Our competitive position is moderate, and we are working to strengthen it", "points": 2},
                            {"text": "Our competitive position is weak, and we struggle to compete effectively", "points": 0}
                        ]
                    },
                    {
                        "text": "5. What is the company's strategy for product or service innovation?",
                        "options": [
                            {"text": "We have a dedicated team and budget for continuous innovation and development and we have a strong innovation pipeline", "points": 5},
                            {"text": "We occasionally invest in innovation when opportunities arise", "points": 3},
                            {"text": "Innovation is not a primary focus, but we make improvements as needed", "points": 2},
                            {"text": "We have no formal strategy for innovation", "points": 0}
                        ]
                    },
                    {
                        "text": "6. How recession-proof is your company?",
                        "options": [
                            {"text": "Highly recession-proof, our products or services are essential and needs-based, with stable demand regardless of economic conditions", "points": 5},
                            {"text": "Moderately recession-proof, our products or services are somewhat essential, with demand slightly affected by economic conditions", "points": 3},
                            {"text": "Slightly recession-proof, our products or services are more wants-based, with demand significantly affected by economic conditions", "points": 1},
                            {"text": "Not recession-proof, our products or services are non-essential and wants-based, with demand highly susceptible to economic downturns", "points": 0}
                        ]
                    }
                ]
            }
        ]
    },
    {
        "name": "Owners' Mindset",
        "questions": [
            {
                "text": "1. Do your children currently work in the business?",
                "type": "radio",
                "name": "children_in_business",
                "options": [
                    {"text": "Yes", "value": "yes"},
                    {"text": "No", "value": "no"}
                ]
            },
            {
                "text": "2. What year did you start your business (or take over it)?",
                "type": "text",
                "name": "year_of_start"
            },
            {
                "text": "3. If you could wave a magic wand and fix one problem in your company, what would it be?",
                "type": "text",
                "name": "magic_wand_problem"
            },
            {
                "text": "4. What is your long-term goal for your company?",
                "type": "radio",
                "name": "long_term_goal",
                "options": [
                    {"text": "Sell my business to a third party", "value": "sell_to_third_party"},
                    {"text": "Transition my business to my kids", "value": "transition_to_kids"},
                    {"text": "Transition my business to the next generation of managers", "value": "transition_to_managers"},
                    {"text": "Shut down my business", "value": "shut_down"}
                ]
            },
            {
                "text": "5. Tick any of the below checkboxes that resonate with you when it comes to considering to sell your company (Select all that apply)",
                "type": "checkbox",
                "name": "considerations",
                "options": [
                    {"text": "I am worried that employees will not be taken care of well enough if I go", "value": "employees"},
                    {"text": "I don't have anything to do when I retire", "value": "nothing_to_do"},
                    {"text": "I don't think I will get a good value for my business", "value": "value"},
                    {"text": "No one can run the company as well as I can", "value": "drop_off"},
                    {"text": "My legacy will be changed from what I want it to be", "value": "legacy"}
                ]
            },
            {
                "text": "6. Have you received a valuation before? If so, what was it?",
                "type": "text",
                "name": "previous_valuation"
            }
        ]
    },
    {
        "name": "Business Valuation",
        "subsections": [
            {
                "name": "Financials",
                "questions": [
                    {
                        "question": "Would you like to provide your financial details below to receive an approximate valuation?",
                        "type": "radio",
                        "name": "provide_financial_details",
                        "options": [
                            {"text": "Yes", "value": "yes"},
                            {"text": "No", "value": "no"}
                        ]
                    },
                    {
                        "text": "Sales",
                        "fields": ["2021", "2022", "2023"]
                    },
                    {
                        "text": "Gross Profit",
                        "fields": ["2021", "2022", "2023"]
                    },
                    {
                        "text": "Operating Profit (Profit before Interest and Tax)",
                        "fields": ["2021", "2022", "2023"]
                    },
                    {
                        "text": "Depreciation",
                        "fields": ["2021", "2022", "2023"]
                    },
                    {
                        "text": "Net Profit",
                        "fields": ["2021", "2022", "2023"]
                    },
                    {
                        "text": "Total Current Assets",
                        "fields": ["2021", "2022", "2023"]
                    },
                    {
                        "text": "Stocks",
                        "fields": ["2021", "2022", "2023"]
                    },
                    {
                        "text": "Total Current Liabilities",
                        "fields": ["2021", "2022", "2023"]
                    },
                    {
                        "text": "Long-Term Liabilities",
                        "fields": ["2021", "2022", "2023"]
                    },
                    {
                        "text": "Net Assets",
                        "fields": ["2021", "2022", "2023"]
                    },
                    {
                        "text": "Equity (Shareholders Funds)",
                        "fields": ["2021", "2022", "2023"]
                    },
                    {
                        "text": "Number of Employees",
                        "fields": ["2021", "2022", "2023"]
                    },
                    {
                        "text": "Trade Debtors",
                        "fields": ["2021", "2022", "2023"]
                    },
                    {
                        "text": "Trade Creditors",
                        "fields": ["2021", "2022", "2023"]
                    },
                    {
                        "text": "Purchases",
                        "fields": ["2021", "2022", "2023"]
                    }
                    
                ]
            }
        ]
    }
]

# Routes for the multi-page form
@app.route('/')
def index():
    return redirect(url_for('introduction'))

@app.route('/introduction')
def introduction():
    return render_template('introduction.html')

@app.route('/general_info', methods=['GET', 'POST'])
def general_info():
    if request.method == 'POST':
        form_data = request.form.to_dict()
        print("Form Data:", form_data)  # Debugging line
        session['general_info'] = form_data
        return redirect(url_for('business_health_check'))
    return render_template('general_info.html', section=sections[0])


@app.route('/business_health_check', methods=['GET', 'POST'])
def business_health_check():
    if request.method == 'POST':
        session['business_health_check'] = request.form.to_dict()
        return redirect(url_for('owners_mindset'))
    business_health_check_sections = sections[1]['subsections']
    return render_template('business_health_check.html', sections=business_health_check_sections, enumerate=enumerate)

@app.route('/owners_mindset', methods=['GET', 'POST'])
def owners_mindset():
    if request.method == 'POST':
        session['owners_mindset'] = request.form.to_dict()
        return redirect(url_for('valuation'))
    return render_template('owners_mindset.html', section=sections[2])

@app.route('/valuation', methods=['GET', 'POST'])
def valuation():
    if request.method == 'POST':
        valuation_data = request.form.to_dict()
        session['valuation'] = valuation_data
        
        if valuation_data.get('financial_questions') == 'no':
            session['valuation'] = {'financial_questions': 'no'}
            return redirect(url_for('result'))
        
        return redirect(url_for('result'))
    
    valuation_sections = sections[3]['subsections']
    return render_template('valuation.html', sections=valuation_sections, enumerate=enumerate)


@app.route('/result')
def result():
    general_info = session.get('general_info', {})
    business_health_check = session.get('business_health_check', {})
    valuation = session.get('valuation', {})
    
    # Calculate the scores and render the results page
    section_scores = {}
    total_score = 0
    for section_index, section in enumerate(sections[1]['subsections']):
        section_score = 0
        for question_index, question in enumerate(section["questions"]):
            key = f"section{section_index}_question{question_index}"
            value = business_health_check.get(key)
            if value:
                for option in question["options"]:
                    if option["text"] == value:
                        section_score += option["points"]
                        total_score += option["points"]
        section_scores[section["name"]] = section_score

    # Calculate percentage scores for each section based on a fixed max score of 30
    section_percentages = {section: (score / 30 * 100) for section, score in section_scores.items()}

    # Calculate the overall percentage score
    overall_percentage = total_score / (30 * len(section_scores)) * 100

    # Function to determine the color based on the percentage
    def get_color(percentage):
        if percentage > 79:
            return '#4ACD3F'  # Darker green
        elif 30 <= percentage <= 79:
            return '#FF8000'  # Orange
        else:
            return '#B22222'  # Darker red

    # Determine the color for the overall score
    overall_score_color = get_color(overall_percentage)

    labels = list(section_percentages.keys())
    sizes = [25] * len(labels)  # Equal size for each section
    colors = [get_color(pct) for pct in section_percentages.values()]

    def make_autopct(values):
        def my_autopct(pct):
            return f'{pct:.0f}%'
        return my_autopct

    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, autopct=make_autopct(sizes),
        startangle=90, textprops=dict(color="w"), wedgeprops=dict(width=0.5, edgecolor='white', linewidth=3)
    )

    for text in texts:
        text.set_color('black')
        text.set_fontsize(10)
        text.set_weight('bold')

    for autotext, wedge in zip(autotexts, wedges):
        percentage = section_percentages[wedge.get_label()]
        autotext.set_text(f'{percentage:.0f}%')
        autotext.set_color('white')
        autotext.set_fontsize(10)
        autotext.set_weight('bold')
        angle = (wedge.theta2 - wedge.theta1) / 2.0 + wedge.theta1
        x = wedge.r * 0.75 * np.cos(np.deg2rad(angle))
        y = wedge.r * 0.75 * np.sin(np.deg2rad(angle))
        autotext.set_position((x, y))

    centre_circle = plt.Circle((0, 0), 0.5, fc='white')
    fig.gca().add_artist(centre_circle)

    plt.text(0, 0.1, 'Your Legacy Score is:', ha='center', va='center', fontsize=10, color='black', weight='bold')
    plt.text(0, -0.1, f'{overall_percentage:.0f}%', ha='center', va='center', fontsize=14, color=overall_score_color, weight='bold')

    ax.axis('equal')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    chart_url = base64.b64encode(img.getvalue()).decode()

    gauges = []
    messages = []
    for label, percentage in section_percentages.items():
        color = get_color(percentage)
        gauge = go.Figure(go.Indicator(
            mode="gauge",
            value=percentage,
            title={'text': label},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': color, 'thickness': 0.00001},  # Set bar color dynamically and minimize thickness
                'steps': [
                    {'range': [0, 29], 'color': '#B22222'},
                    {'range': [30, 79], 'color': '#FF8000'},
                    {'range': [80, 100], 'color': '#4ACD3F'}
                ],
                'shape': 'angular',
            }
        ))

        angle = 180 * (abs((100 - percentage)) / 100)

        gauge.add_shape(
            dict(
                type="line",
                x0=0.5,
                y0=0,  # Adjust starting point of the needle
                x1=0.5 + 0.4 * np.cos(np.radians(angle)),  # Shorten the needle length
                y1=np.sin(np.radians(angle)),  # Adjust to match the new length
                line=dict(color="black", width=4)
            )
        )

        gauge.add_annotation(
            x=0.5, y=-0.25,  # Position the percentage score below the gauge
            text=f'{percentage:.0f}%',
            showarrow=False,
            font=dict(size=20, color=color)
        )

        gauge.update_layout(
            margin=dict(l=20, r=20, t=80, b=20),  # Increase top margin and reduce bottom margin
            height=200,
            annotations=[]  # Ensure no default annotations
        )

        gauge_html = pio.to_html(gauge, full_html=False)
        gauges.append(gauge_html)

        # Create messages based on score
        if label == "Exit Readiness":
            if percentage > 79:
                messages.append("Congratulations! Your Exit Readiness score is excellent. Your business is well-prepared for a transition or sale. A high score in Exit Readiness means that your business can operate independently of you, with a solid succession plan and well-documented processes. This makes your business more valuable and attractive to potential buyers.")
            elif 30 <= percentage <= 79:
                messages.append("Your Exit Readiness score is moderate. While there are some good practices in place, there is significant room for improvement. An average score in Exit Readiness suggests that while some systems and plans are in place, they may not be robust enough to ensure a smooth transition or sale. Strengthening these areas will enhance business stability and attractiveness to buyers.")
            else:
                messages.append("Your Exit Readiness score is critically low. Immediate action is required to ensure the stability and continuity of your business. A low score in Exit Readiness indicates that your business is heavily dependent on you, the owner, and lacks a solid succession plan. This puts your business at risk if you are unable to oversee operations, making it less attractive to potential buyers.")
        
        elif label == "Fundamentals":
            if percentage > 79:
                messages.append("Great job! Your Fundamentals score is excellent, indicating a strong foundation for your business. A high score in Fundamentals means your business has solid financial management, diverse customer base, and predictable revenue streams. This stability enhances business value and attractiveness to investors.")
            elif 30 <= percentage <= 79:
                messages.append("Your Fundamentals score is moderate. You have some good practices, but there are key areas that need strengthening. An average score in Fundamentals suggests that while your business is functioning, there are significant areas that need improvement to ensure long-term stability and growth.")
            else:
                messages.append("Your Fundamentals score is critically low. Urgent improvements are needed to establish a stable foundation for your business. A low score in Fundamentals indicates weaknesses in core business operations such as financial management and customer diversification. This can lead to instability and reduced business value.")
        
        elif label == "Operations":
            if percentage > 79:
                messages.append("Excellent! Your Operations score is very high, reflecting efficient and effective business processes. A high score in Operations means your business processes are optimized, leading to minimal delays and costs. This efficiency boosts productivity and profitability.")
            elif 30 <= percentage <= 79:
                messages.append("Your Operations score is moderate. Some processes are working well, but there is room for improvement. An average score in Operations indicates that while some processes are efficient, others may be causing delays or additional costs. Enhancing these areas will improve overall business performance.")
            else:
                messages.append("Your Operations score is critically low. Immediate action is required to improve efficiency and effectiveness. A low score in Operations suggests significant inefficiencies and potential disruptions in your business processes. Addressing these issues is crucial for smooth day-to-day operations and overall business health.")
        
        elif label == "Sales and Marketing":
            if percentage > 79:
                messages.append("Well done! Your Sales and Marketing score is excellent, indicating strong strategies and customer engagement. A high score in Sales and Marketing means your business effectively attracts and retains customers, driving growth and increasing revenue. This strength makes your business more competitive and valuable.")
            elif 30 <= percentage <= 79:
                messages.append("Your Sales and Marketing score is moderate. Some strategies are working, but there is potential for much more. An average score in Sales and Marketing suggests that while some efforts are effective, there is room to strengthen your strategies to achieve better customer engagement and revenue growth.")
            else:
                messages.append("Your Sales and Marketing score is critically low. Significant improvements are needed to drive business growth. A low score in Sales and Marketing indicates weak strategies and poor customer engagement, which can lead to stagnant or declining revenue. Enhancing these areas is crucial for attracting and retaining customers.")
        
        elif label == "Growth":
            if percentage > 79:
                messages.append("Fantastic! Your Growth score is very high, reflecting strong potential for expansion and innovation. A high score in Growth means your business is well-positioned to take advantage of market opportunities, scale effectively, and innovate. This potential enhances your business’s long-term success and value.")
            elif 30 <= percentage <= 79:
                messages.append("Your Growth score is moderate. There are some growth opportunities, but more effort is needed to fully capitalize on them. An average score in Growth suggests that while there are opportunities, your business is not fully leveraging them. Enhancing your growth strategies will help maximize your business’s potential.")
            else:
                messages.append("Your Growth score is critically low. Urgent action is needed to enhance your business’s potential for expansion. A low score in Growth indicates limited opportunities for scaling and innovation, which can hinder long-term success. Focusing on growth strategies is essential to ensure your business remains competitive.")


    # Financial Ratios Calculation
    financial_ratios = {}
    financial_questions = valuation.get('financial_questions')

    if financial_questions == 'yes':
        financial_data = {key: valuation[key] for key in valuation if 'financial' in key}

        for year in ['2021', '2022', '2023']:
            sales = float(financial_data.get(f'financial_sales_{year}', 0))
            gross_profit = float(financial_data.get(f'financial_gross_profit_{year}', 0))
            operating_profit = float(financial_data.get(f'financial_operating_profit_(profit_before_interest_and_tax)_{year}', 0))
            depreciation = float(financial_data.get(f'financial_depreciation_{year}', 0))
            net_profit = float(financial_data.get(f'financial_net_profit_{year}', 0))
            current_assets = float(financial_data.get(f'financial_total_current_assets_{year}', 0))
            current_liabilities = float(financial_data.get(f'financial_total_current_liabilities_{year}', 0))
            long_term_liabilities = float(financial_data.get(f'financial_long-term_liabilities_{year}', 0))
            net_assets = float(financial_data.get(f'financial_net_assets_{year}', 0))
            equity = float(financial_data.get(f'financial_equity_(shareholders_funds)_{year}', 0))
            num_employees = float(financial_data.get(f'financial_number_of_employees_{year}', 0))
            trade_debtors = float(financial_data.get(f'financial_trade_debtors_{year}', 0))
            trade_creditors = float(financial_data.get(f'financial_trade_creditors_{year}', 0))
            purchases = float(financial_data.get(f'financial_purchases_{year}', 0))
            stocks = float(financial_data.get(f'financial_stocks_{year}', 0))

            gross_profit_margin = (gross_profit / sales) * 100 if sales != 0 else 0
            ebitda = operating_profit + abs(depreciation)
            net_profit_margin = (net_profit / sales) * 100 if sales != 0 else 0
            gearing = (abs(long_term_liabilities) / equity) * 100 if equity != 0 else 0
            liquidity_ratio = f"{current_assets / abs(current_liabilities):.1f}:1" if current_liabilities != 0 else "N/A"
            return_on_capital = ((operating_profit) / (equity + abs(long_term_liabilities))) * 100 if equity + abs(long_term_liabilities) != 0 else 0
            revenue_per_head = sales / num_employees if num_employees != 0 else 0
            debtors_turnover_period = (trade_debtors * 365) / sales if sales != 0 else 0
            creditors_turnover_period = (trade_creditors * 365) / purchases if purchases != 0 else 0
            stock_turnover_period = (stocks * 365) / (sales - gross_profit) if (sales - gross_profit) != 0 else 0
            cash_conversion_cycle = stock_turnover_period + debtors_turnover_period - creditors_turnover_period

            financial_ratios[year] = {
                "Gross Profit Margin": f"{gross_profit_margin:.0f}%",
                "Return on Capital Employed": f"{return_on_capital:.0f}%",
                "EBITDA": f"{ebitda:.0f}",
                "Net Profit Margin": f"{net_profit_margin:.0f}%",
                "Gearing": f"{gearing:.0f}%",
                "Liquidity Ratio": liquidity_ratio,
                "Revenue per Head": f"{revenue_per_head:.0f}",
                "Debtors Turnover Period": f"{debtors_turnover_period:.0f} days",
                "Creditors Turnover Period": f"{creditors_turnover_period:.0f} days",
                "Stock Turnover Period": f"{stock_turnover_period:.0f} days",
                "Cash Conversion Cycle": f"{cash_conversion_cycle:.0f} days"
            }

        # Business Valuation Calculation
        net_assets_2023 = float(financial_data.get('financial_net_assets_2023', 0))
        ebitda_2021 = float(financial_ratios['2021']['EBITDA'].replace(',', ''))
        ebitda_2022 = float(financial_ratios['2022']['EBITDA'].replace(',', ''))
        ebitda_2023 = float(financial_ratios['2023']['EBITDA'].replace(',', ''))

        weighted_avg_ebitda = (1/6 * ebitda_2021 + 2/6 * ebitda_2022 + 3/6 * ebitda_2023)
        
        # Determine the multiple based on the criteria
        def get_multiple(ebitda, legacy_score):
            if ebitda <= 200000:
                if legacy_score <= 50:
                    return 1
                elif legacy_score <= 80:
                    return 2
                elif legacy_score <= 95:
                    return 3
                else:
                    return 4
            elif ebitda <= 400000:
                if legacy_score <= 40:
                    return 1
                elif legacy_score <= 80:
                    return 2
                elif legacy_score <= 95:
                    return 3
                else:
                    return 4
            elif ebitda <= 600000:
                if legacy_score <= 35:
                    return 1
                elif legacy_score <= 70:
                    return 2
                elif legacy_score <= 90:
                    return 3
                else:
                    return 4
            elif ebitda <= 800000:
                if legacy_score <= 30:
                    return 1
                elif legacy_score <= 60:
                    return 2
                elif legacy_score <= 85:
                    return 3
                else:
                    return 4
            elif ebitda <= 1000000:
                if legacy_score <= 20:
                    return 1
                elif legacy_score <= 50:
                    return 2
                elif legacy_score <= 80:
                    return 3
                else:
                    return 4
            else:
                if legacy_score <= 20:
                    return 1
                elif legacy_score <= 50:
                    return 2
                elif legacy_score <= 80:
                    return 3
                else:
                    return 4

        multiple = get_multiple(weighted_avg_ebitda, overall_percentage)
        business_valuation = net_assets_2023 + multiple * weighted_avg_ebitda
        business_valuation = round(business_valuation)

    else:
        financial_ratios = {
            '2021': {"Gross Profit Margin": "N/A", "Return on Capital Employed": "N/A", "EBITDA": "N/A", "Net Profit Margin": "N/A", "Gearing": "N/A", "Liquidity Ratio": "N/A", "Revenue per Head": "N/A", "Debtors Turnover Period": "N/A", "Creditors Turnover Period": "N/A", "Stock Turnover Period": "N/A", "Cash Conversion Cycle": "N/A"},
            '2022': {"Gross Profit Margin": "N/A", "Return on Capital Employed": "N/A", "EBITDA": "N/A", "Net Profit Margin": "N/A", "Gearing": "N/A", "Liquidity Ratio": "N/A", "Revenue per Head": "N/A", "Debtors Turnover Period": "N/A", "Creditors Turnover Period": "N/A", "Stock Turnover Period": "N/A", "Cash Conversion Cycle": "N/A"},
            '2023': {"Gross Profit Margin": "N/A", "Return on Capital Employed": "N/A", "EBITDA": "N/A", "Net Profit Margin": "N/A", "Gearing": "N/A", "Liquidity Ratio": "N/A", "Revenue per Head": "N/A", "Debtors Turnover Period": "N/A", "Creditors Turnover Period": "N/A", "Stock Turnover Period": "N/A", "Cash Conversion Cycle": "N/A"},
        }
        business_valuation = "N/A"


    # Define the intervals and scores
    ebitda_intervals = np.arange(200, 1001, 200)
    segment1 = [50, 40, 35, 30, 20]  # First segment
    segment2 = [30, 40, 30, 30, 30]  # Second segment
    segment3 = [15, 15, 20, 20, 30]  # Third segment
    segment4 = [5 , 5, 15, 20, 20]  # Fourth segment

    # Custom tick labels
    tick_labels = ['0-2', '2-4', '4-6', '6-8', '8-10']

    # Plotting the bar chart
    fig, ax = plt.subplots(figsize=(4, 4))

    # Set the width of the bars
    bar_width = 100

    # Plot the first segment
    bars1 = ax.bar(ebitda_intervals, segment1, width=bar_width, color='skyblue', label='1x')

    # Plot the second segment on top of the first segment
    bars2 = ax.bar(ebitda_intervals, segment2, width=bar_width, bottom=segment1, color='lightgreen', label='2x')

    # Calculate the height for the third segment to be stacked correctly
    segment1_2 = [sum(x) for x in zip(segment1, segment2)]
    bars3 = ax.bar(ebitda_intervals, segment3, width=bar_width, bottom=segment1_2, color='tomato', label='3x')

    segment1_2_3 = [sum(x) for x in zip(segment1, segment2, segment3)]
    bars4 = ax.bar(ebitda_intervals, segment4, width=bar_width, bottom=segment1_2_3, color='gold', label='4x')

    # Add text annotations on the bars
    for i in range(len(ebitda_intervals)):
        ax.text(ebitda_intervals[i], segment1[i] / 2, f'{"1x"}', ha='center', va='center', color='white')
        ax.text(ebitda_intervals[i], segment1[i] + segment2[i] / 2, f'{"2x"}', ha='center', va='center', color='white')
        ax.text(ebitda_intervals[i], segment1_2[i] + segment3[i] / 2, f'{"3x"}', ha='center', va='center', color='white')
        ax.text(ebitda_intervals[i], segment1_2_3[i] + segment4[i] / 2, f'{"4x"}', ha='center', va='center', color='white')

    ax.set_xlabel("EBITDA (€100,000s)")
    ax.set_ylabel('Legacy Score')
    ax.set_title('How Multiples are Assigned')
    ax.set_xticks(ebitda_intervals)
    ax.set_xticklabels(tick_labels)
    ax.set_yticks(np.arange(0, 101, 10))
    ax.set_xlim(100, 1100)
    ax.set_ylim(0, 100)

    fig.tight_layout()  # Adjust the layout to fit the page

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    bar_chart_url = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)


    return render_template('result.html', 
                       general_info=general_info, 
                       chart_url=chart_url, 
                       gauges=gauges, 
                       messages=messages, 
                       financial_ratios=financial_ratios, 
                       business_valuation=business_valuation, 
                       bar_chart_url=bar_chart_url, 
                       overall_score_color=overall_score_color, 
                       zip=zip,
                       enumerate=enumerate, sections=sections)  # Add this line



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
