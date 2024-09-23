import fitz  # PyMuPDF
import re
from pprint import pprint


# Method to extract text from PDF.
def extract_text_from_pdf(pdf_path):
    # Open the PDF file
    doc = fitz.open(pdf_path)
    text = ""
    # Iterate through the pages and extract text
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text("text")
    return text


# Method to see how many credits are left in a user's degree.
def parse_credits_info(text):
    # Original regex pattern
    pattern = r"(NO|OK)\s+TOTAL CREDITS for the DEGREE\s+EARNED:\s+(\d+\.\d+)\s+CREDITS\s+IN-PROGRESS\s+(\d+\.\d+)\s+CREDITS\s+-->\s+NEEDS:\s+(\d+\.\d+)\s+CREDITS"

    match = re.search(pattern, text)
    if match:
        status = match.group(1)  # "NO" or "OK"
        earned_credits = float(match.group(2))
        in_progress_credits = float(match.group(3))
        needed_credits = float(match.group(4))
    else:
        # Fallback: Calculate credits using extract_courses_and_credits
        parsed_courses = extract_courses_and_credits(text)
        school_and_major = extract_requested_major(text)
        school = school_and_major["school"]
        major = school_and_major["major"]
        earned_credits = sum(
            course["credits"] for course in parsed_courses if course["status"] != "CR"
        )
        in_progress_credits = sum(
            course["credits"] for course in parsed_courses if "INP" in course["status"]
        )
        total_credits = earned_credits + in_progress_credits

        if "NURSING" in school:
            print(major)
            if major == "ACCELERATED PROGRAM":
                needed_credits = max(49 - total_credits, 0)
                status = "OK" if total_credits >= 49 else "NO"
            else:
                print("test")
                needed_credits = max(124 - total_credits, 0)
                print(needed_credits)
                status = "OK" if total_credits >= 124 else "NO"
        else:
            needed_credits = max(120 - total_credits, 0)
            status = "OK" if total_credits >= 120 else "NO"

    return {
        "status": status,
        "earned_credits": round(earned_credits, 2),
        "in_progress_credits": round(in_progress_credits, 2),
        "needed_credits": round(needed_credits, 2),
    }


# Method to see a user's courses in progress, using regex parsing.
def old_extract_in_progress_courses(text):
    # Define the regex pattern to match in-progress courses
    pattern = r"IP\s+(Fall|Spring|Summer)\s+(\d{4})\s+\(\w+\)\s*(\d+\.\d+)\s+CREDITS ADDED\s*((?:.*?(?:INP|IP).*?\n)+)"

    # Find all matches of the pattern
    matches = re.findall(pattern, text, re.DOTALL)

    courses = {}

    # Iterate over all matched groups
    for match in matches:
        semester, year, total_credits, course_block = match
        # Extract individual courses from the block
        course_pattern = (
            r"\s*(?:\w+\s+)?([A-Z]+\s*[A-Z]*\d+)\s+(\d+\.\d+)\s+(INP|IP)\s+(.*?)\s*$"
        )
        course_matches = re.findall(course_pattern, course_block, re.MULTILINE)

        for course_code, credits, status, course_name in course_matches:
            # Create a unique key for each course
            course_key = (course_code.strip(), course_name.strip())

            # Only add the course if it's not already in the dictionary
            if course_key not in courses:
                courses[course_key] = {
                    "semester": f"{semester} {year}",
                    "course_code": course_code.strip(),
                    "credits": float(credits),
                    "status": status,
                    "course_name": course_name.strip(),
                }

    # Convert the dictionary values back to a list
    return list(courses.values())


# Method to see a user's courses in progress, using status codes from extract_courses_and_credits().
def extract_in_progress_courses(text):
    all_courses = extract_courses_and_credits(text)
    in_progress_courses = [
        course for course in all_courses if "INP" in course["status"]
    ]
    return in_progress_courses


def extract_courses_and_credits(text):
    # Updated regular expression to match course info including 4-digit course numbers
    course_pattern = r"([A-Z ]+\d{3,4})\s+(\d+\.\d{2})\s+([A-Z]+)\s+(.*?)(?=\n|$)"

    matches = re.findall(course_pattern, text)
    courses = {}

    for match in matches:
        # Remove all spaces from course_code
        course_code = "".join(match[0].split())

        # Add a space between the last alphabetical character and the first number
        course_code = re.sub(r"([A-Z])(\d)", r"\1 \2", course_code)

        credits = float(match[1])
        status = match[2]
        course_name = match[3].strip()

        if re.match(r"^E \d{3,4}$", course_code):
            course_code = "MS&E " + course_code.split()[1]

        if "Statics" in course_name:
            credits = 3.00

        # Use course_code as key to handle duplicates
        if course_code in courses:
            # If the course already exists, update the status if it's different
            existing_statuses = set(courses[course_code]["status"].split("/"))
            existing_statuses.add(status)
            courses[course_code]["status"] = "/".join(sorted(existing_statuses))
        else:
            courses[course_code] = {
                "course_code": course_code,
                "credits": credits,
                "status": status,
                "course_name": course_name,
            }

    return list(courses.values())


def extract_student_name(text):
    # Regular expression to match the student's name on the second line
    pattern = r"(?m)^.*\n([\w,]+)"

    match = re.search(pattern, text)
    if match:
        return match.group(1)
    else:
        return None


def extract_requested_major(text):
    # Regular expression to find the DARS line and capture the following two lines
    pattern = r"DEGREE AUDIT REPORTING SYSTEM \(DARS\)\s*\n\s*(.*?)\s*\n\s*(.*?)\s*\n"

    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        school = match.group(1).strip()
        major = match.group(2).strip()
        return {"school": school, "major": major}
    else:
        return None


def extract_majors_and_certificates(text):
    # Regular expressions for majors and certificates, case-insensitive
    major_pattern = r"(?i)major:\s+\d{2}/\d{2}/\d{2}\s+\d+\s+(.*?)\s{3,}$"
    certif_pattern = r"(?i)certif:\s+\d{2}/\d{2}/\d{2}\s+\d+\s+(.*?)\s{3,}$"

    # Find all matches
    majors = [m.strip() for m in re.findall(major_pattern, text, re.MULTILINE)]
    certificates = [c.strip() for c in re.findall(certif_pattern, text, re.MULTILINE)]

    return {"majors": majors, "certificates": certificates}


def extract_preparation_date(text):
    # Regular expression to match the date in the format MM/DD/YY
    pattern = r"Prepared:\s+(\d{2}/\d{2}/\d{2})"

    match = re.search(pattern, text)
    if match:
        return match.group(1)
    else:
        return None


def extract_completed_requirements(text):
    pattern = r"OK\s+(.*?)(?=\n(?:OK|NO|\n|$))"

    matches = re.findall(pattern, text, re.DOTALL)

    completed_requirements = []

    for match in matches:
        lines = match.strip().split("\n")
        requirement = {"category": lines[0].strip(), "earned": None, "details": []}

        if requirement["category"] == "= requirement complete":
            continue

        # Find the index of the dashed line
        dash_line_index = next(
            (i for i, line in enumerate(lines) if re.match(r"^-+$", line)), len(lines)
        )

        # Capture all lines between category and dashed line as details
        requirement["details"] = [
            line.strip() for line in lines[1:dash_line_index] if line.strip()
        ]

        # Extract 'EARNED:' from details if present
        for line in requirement["details"]:
            if line.startswith("EARNED:"):
                requirement["earned"] = line.split("EARNED:")[1].strip()
                break

        completed_requirements.append(requirement)

    return completed_requirements


def extract_unfulfilled_requirements(text):
    pattern = r"NO\s+(.*?)(?=\n(?:OK|NO|\n|$))"

    matches = re.findall(pattern, text, re.DOTALL)

    unfulfilled_requirements = []

    for match in matches[:-1]:  # Exclude the last match
        lines = match.strip().split("\n")
        requirement = {
            "category": lines[0].strip(),
            "needs": None,
            "earned": None,
            "details": [],
        }

        # Find the index of the dashed line
        dash_line_index = next(
            (i for i, line in enumerate(lines) if re.match(r"^-+$", line)), len(lines)
        )

        # Capture all lines between category and dashed line as details
        requirement["details"] = [
            line.strip() for line in lines[1:dash_line_index] if line.strip()
        ]

        # Extract 'NEEDS:' and 'EARNED:' from details if present
        for line in requirement["details"]:
            if line.startswith("NEEDS:"):
                requirement["needs"] = line.split("NEEDS:")[1].strip()
            elif line.startswith("EARNED:"):
                requirement["earned"] = line.split("EARNED:")[1].strip()

        unfulfilled_requirements.append(requirement)

    return unfulfilled_requirements


# Method to extract certificate credits
def extract_certificate_credits(text, certificate_name):
    # Dynamic patterns to match different formats of credit information
    patterns = {
        "needs": r"NEEDS:\s+(\d+\.\d+)\s+CREDITS",
        "in_progress": r"IN-PROGRESS\s+(\d+\.\d+)\s+CREDITS",
        "earned": r"(?:EARNED:\s+(\d+\.\d+)\s+CREDITS|GPA CREDITS EARNED\s+(\d+\.\d+))",
    }

    results = {
        "certificate_name": certificate_name,
        "needed_credits": 0.0,
        "in_progress_credits": 0.0,
        "earned_credits": 0.0,
    }

    # Search for each pattern
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            # Handle different group capturing for 'earned'
            if key == "earned":
                results[key] = float(match.group(1) or match.group(2))
            else:
                results[key] = float(match.group(1))

    return results


def extract_all_data(pdf_path):

    if not pdf_path.endswith(".pdf"):
        return False

    # Extract raw text from PDF
    raw_text = extract_text_from_pdf(pdf_path)

    # Check if the first line contains "Prepared:"
    if not raw_text.strip().startswith("Prepared:"):
        raise ValueError("The provided PDF does not appear to be a valid DARS report.")

    # Extract all data using existing methods
    student_name = extract_student_name(raw_text)
    preparation_date = extract_preparation_date(raw_text)
    requested = extract_requested_major(raw_text)

    if "Certificate" in requested["major"]:
        raise ValueError("Certificates are not accepted.")

    majors_and_certificates = extract_majors_and_certificates(raw_text)
    credits_info = parse_credits_info(raw_text)
    in_progress_courses = extract_in_progress_courses(raw_text)
    all_courses = extract_courses_and_credits(raw_text)
    completed_requirements = extract_completed_requirements(raw_text)
    unfulfilled_requirements = extract_unfulfilled_requirements(raw_text)
    gpa = extract_student_gpa(raw_text)

    # Compile all data into a single object
    all_data = {
        "student_name": student_name,
        "preparation_date": preparation_date,
        "requested_school": requested["school"] if requested else None,
        "requested_major": requested["major"] if requested else None,
        "majors": majors_and_certificates["majors"],
        "certificates": majors_and_certificates["certificates"],
        "credits": credits_info,
        "in_progress_courses": in_progress_courses,
        "all_courses": all_courses,
        "completed_requirements": completed_requirements,
        "unfulfilled_requirements": unfulfilled_requirements,
        "gpa": gpa,
    }

    return all_data


# all_data = extract_all_data('./assets/cals.pdf')

# pprint(all_data)


def extract_student_gpa(text):
    print('extract_student_gpa called')
    # Pattern to match GPA lines
    gpa_patterns = [
        r"(\d+\.\d+)\s+GPA\s*$",
        r"(\d+\.\d+)\s+GPA\s+for\s+Advising",
        r"(\d+\.\d+)\s+GPA\s*$",
        r"(\d+\.\d+)\s+UW-Madison\s+Cumulative\s+GPA"
    ]
    
    # Search for GPA using each pattern
    for pattern in gpa_patterns:
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            return str(float(match.group(1)))
    
    # If no match found, return None
    return None

# Example usage:
# gpa = extract_student_gpa(text)
# if gpa is not None:
#     print(f"Student's GPA: {gpa}")
# else:
#     print("GPA not found in the text")
