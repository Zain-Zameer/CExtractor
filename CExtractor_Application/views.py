from django.shortcuts import render
import pandas as pd
from django.core.files.storage import FileSystemStorage

# Create your views here.
def index(request):
    return render(request,"index.html")

def filter_duplicate_courses(duplicate_courses):
    filtered_courses = {}
    
    # Iterate through the duplicate_courses dictionary
    for course_code, courses in duplicate_courses.items():
        theory_section = None
        labs = []

        # Separate theory and lab courses
        for course in courses:
            if 'Theory' in course[1]:  # Check if it's a theory course
                theory_section = course[3]  # Store the section of the theory course
            elif 'Lab' in course[1]:  # Check if it's a lab course
                labs.append(course)

        # Filter labs to match the theory section
        filtered_labs = [lab for lab in labs if lab[3] == theory_section]

        # If a theory course was found, store the filtered theory and matching lab
        if theory_section:
            filtered_courses[course_code] = [
                course for course in courses if 'Theory' in course[1]
            ] + filtered_labs

    return filtered_courses

# Django view function
def upload_and_process_file(request):
    if request.method == 'POST' and request.FILES.get('uploaded_file'):
        # Handle file upload
        uploaded_file = request.FILES['uploaded_file']
        fs = FileSystemStorage()
        file_path = fs.save(uploaded_file.name, uploaded_file)
        file_url = fs.url(file_path)  # Not needed but can be useful for reference

        # Load the Excel sheet into a pandas DataFrame
        dataframe = pd.read_excel(fs.path(file_path))

        # Drop duplicates in the dataset
        dataframe.drop_duplicates(inplace=True)

        # Process the dataframe into a dictionary of courses
        courses = {}
        for i in range(len(dataframe)):
            code = dataframe["Course Code"][i]
            title=dataframe["Course Title"][i]
            Cr_Hrs=dataframe["Cr Hrs"][i]
            section = dataframe["Section"][i]
            dept = dataframe["Dept."][i]
            time = dataframe["Time Table"][i]
            cdn_pass = i
            courses[cdn_pass] = code,title,Cr_Hrs,section,dept,time

        # Handle unique courses logic
        unique_courses = {}
        seen_timings = set()
        for key, value in courses.items():
            timing = value[5][:15]  # Get the first 15 characters of the time (for comparison)

            if timing not in seen_timings:
                unique_courses[key] = value
                seen_timings.add(timing)

        # Title handling logic
        unqiue_courses_2 = {}
        seen_titles = set()
        for key, value in unique_courses.items():
            title = value[1]
            if title.endswith("(Lab)"):
                unqiue_courses_2[key] = value
            else:
                if title not in seen_titles:
                    unqiue_courses_2[key] = value
                    seen_titles.add(title)

        # Lab handling logic (group courses by course code)
        grouped_courses = {}
        for key, value in unqiue_courses_2.items():
            course_code = value[0]
            if course_code in grouped_courses:
                grouped_courses[course_code].append(value)
            else:
                grouped_courses[course_code] = [value]

        # Identify duplicate courses
        duplicate_courses = {code: details for code, details in grouped_courses.items() if len(details) > 1}

        # Remove duplicate courses from unqiue_courses_2
        for course_code, courses in duplicate_courses.items():
            for course in courses:
                keys_to_remove = [key for key, value in unqiue_courses_2.items() if value == course]
                for key in keys_to_remove:
                    unqiue_courses_2.pop(key)

        # Apply filter_duplicate_courses function
        filtered_duplicate_courses = filter_duplicate_courses(duplicate_courses)

        # Add filtered duplicate courses back to unqiue_courses_2
        next_key = max(unqiue_courses_2.keys(), default=0) + 1  # Find the next available key
        for course_code, courses in filtered_duplicate_courses.items():
            for course in courses:
                unqiue_courses_2[next_key] = course
                next_key += 1

        # Pass the processed data to the template
        context = {'courses': unqiue_courses_2}
        return render(request, 'index.html', context)

    return render(request, 'index.html')