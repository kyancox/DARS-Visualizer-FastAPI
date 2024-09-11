import extract

'''
Testing output of methods.
'''

# Example usage of extract_text_from_pdf()
pdf_path = "./assets/compsci.pdf"
raw_text = extract.extract_text_from_pdf(pdf_path)
# print(raw_text)  # Print the first 1000 characters for inspection

# Example usage of extract_student_name()
student_name = extract.extract_student_name(raw_text)
print('Student Name:')
print(student_name)
print()

# Example usage of extract_preparation_date()
preparation_date = extract.extract_preparation_date(raw_text)
print('Preparation Date:')
print(preparation_date)
print()

# Example usage of extract_school_and_major()
school_and_major = extract.extract_requested_major(raw_text)
print('School and Major:')
print(school_and_major)
print()

# Example usage of extract_majors_and_certificates()
result = extract.extract_majors_and_certificates(raw_text)
print('Majors and Certificates:')
print(result)
print()


# Example usage of parse_credits_info()
# raw_text = """
# NO TOTAL CREDITS for the DEGREE
# EARNED: 73.00 CREDITS
# IN-PROGRESS 16.00 CREDITS
# --> NEEDS: 31.00 CREDITS
# """
parsed_data = extract.parse_credits_info(raw_text)
print('Credits:')
print(parsed_data)
print()

# Example usage of extract_in_progress_courses()
text = """
IP      Fall 2024 (FA24)                                         
           16.00 CREDITS ADDED                                    
       FA24 ASIAN    236  3.00 INP    Asia Enchanted               
       FA24 ASIAN    371  3.00 INP    Journey West & Gods' Creation
       FA24 COMP SCI240  3.00 INP    Intro to Discrete Mathematics
       FA24 COMP SCI354  3.00 INP    Machine Organizatn&Progrmng  
       FA24 STAT    303  1.00 INP    R for Statistics I           
       FA24 STAT    309  3.00 INP    Intro to Prob & Math Stat    
"""
in_progress_courses = extract.extract_in_progress_courses(text)
print('In progress courses:')
for course in in_progress_courses:
    print(course)
print()

# Example usage of extract_courses_and_credits()
print('parsed_courses:')
parsed_courses = extract.extract_courses_and_credits(text)
for course in parsed_courses:
    print(course)
print()

# After extracting the raw_text from the PDF
completed_requirements = extract.extract_completed_requirements(text)
print('Completed requirements:')
for req in completed_requirements:
    print(req)
print()

# Example usage of extract_unfulfilled_requirements()
unfulfilled_reqs = extract.extract_unfulfilled_requirements(text)
print('Incomplete requirements:')
for req in unfulfilled_reqs:
    # print(req)
    print(f"Category: {req['category']}")
    if req['needs']:
        print(f"Needs: {req['needs']}")
    if req['earned']:
        print(f"Earned: {req['earned']}")
    if req['details']:
        print("Details:")
        for detail in req['details']:
            print(f"  - {detail}")
    print()    

# Example usage on text for each certificate
# pdf_text = extract_text_from_pdf("./assets/bcert.pdf")
# accounting_credits = extract_certificate_credits(pdf_text, "Certificate in Accounting")
# print(accounting_credits)

# pdf_text = extract_text_from_pdf("./assets/cscert.pdf")
# cs_credits = extract_certificate_credits(pdf_text, "Certificate in Computer Science")
# print(cs_credits)

# pdf_text = extract_text_from_pdf("./assets/chinese.pdf")
# chinese_credits = extract_certificate_credits(pdf_text, "Certificate in Chinese Professional Communication")
# print(chinese_credits)

# pdf_text = extract_text_from_pdf('./assets/bsn.pdf')
# bsn_name = extract_requested_major(pdf_text)
# print(bsn_name)

# pdf_text = extract_text_from_pdf('./assets/prebsn.pdf')
# prebsn_name = extract_requested_major(pdf_text)
# print(prebsn_name)

# pdf_text = extract_text_from_pdf('./assets/nac.pdf')
# nac_name = extract_requested_major(pdf_text)
# print(nac_name)
