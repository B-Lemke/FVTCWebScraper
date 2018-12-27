import requests
import time
import json
from bs4 import BeautifulSoup


def get_clusters():
    '''
    Gets a list of the clusters at FVTC, along with each of the programs in the clusters
    '''

    clustersURl = "https://fvtc.edu/programs/all-programs"
    clusterList = []

    #make a connection to the page and parse it into a readable format
    clusterSite = requests.get(clustersURl, headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'})
    clusterHtml = BeautifulSoup(clusterSite.text, 'html.parser')

    #If connected to the page, parse out the information
    while clusterSite.status_code == 200:
    
        try: 
             clusters = clusterHtml.findAll('dd')

             for cluster in clusters:
                 clusterTitle = "None"
                 programs = []

                 clusterTitle = cluster.span.text
                 print("\n Retrieving Cluster: " + clusterTitle + "...")

                 rawProgramData = cluster.findAll("a", {"class":"programLink"})
                 for program in rawProgramData:
                    
                    #get the URL to the program
                    programUrl = program['href']
                    fullProgramUrl = "https://fvtc.edu" + programUrl

                    #get the program info
                    programInfo = get_program(fullProgramUrl)
                    programs.append(programInfo)

                    print("     " + programInfo.get("ProgramTitle") + " added")

                    cluster_dict = {'ClusterTitle': clusterTitle, 'Programs' : programs}
                    #wait a second so we don't spam the server
                    time.sleep(1)

                 clusterList.append(cluster_dict)
                 
                    
                    
        except: 
            pass

       
        return clusterList
    
    

def get_program(programUrl):
    '''
    '''
    #List of properties
    programTitle = 'None'
    programDescription = 'None'
    programID = 'None'  
    degreeType = 'None'
    numberOfCredits = 'None' 
    financialAidAvailable = False
    careerOpportunities = []
    tuitionAndFees = 0.00
    additionalMaterials = 0.00
    textbookCost = 0.00
    programCourses = []
    
    #make a connection to the page and parse it into a readable format
    programSite = requests.get(programUrl, headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'})
    programHtml = BeautifulSoup(programSite.text, 'html.parser')
    
    #If connected to the page, parse out the information
    while programSite.status_code == 200:
    
        try: 
             programTitle = programHtml.find('span', id="dnn_ctr11976_View_lblProgramTitle").text
        except: 
            pass

        try: 
             programDescription = programHtml.find('span', id="dnn_ctr11976_View_lblProgramDescription").text
        except: 
            pass
    
        try: 
            programID = programHtml.find('span', id="dnn_ctr11976_View_lblProgramNumber").text
        except:
            pass

        try: 
            degreeType = programHtml.find('span', id="dnn_ctr11976_View_lblProgramDegreeType").text
        except:
            pass

        try: 
            numberOfCredits = programHtml.find('span', id="dnn_ctr11976_View_lblProgramCredits").text 
            #remove the word credits
            numberOfCredits = numberOfCredits.lower().replace('credits', '').strip()

        except:
            pass
        try: 
            financialAidAvailable = programHtml.find('span', id="dnn_ctr11976_View_lblProgramSpecsAid").text
            if financialAidAvailable == "Financial Aid Eligible":
                financialAidAvailable = True
            else:
                financialAidAvailable = False

        except:
            pass

        #come back, needs a loop
        try: 
            careers = programHtml.findAll('span', {"class":"fvtc-mod-pospl-job-title"})
            #Loop through and replace the tags with the name of the career opportunities
            for career in careers:
                careerName = career.text
                careerOpportunities.append(careerName)
        except:
            pass

        try: 
            tuitionAndFees = programHtml.find('span', id="dnn_ctr11976_View_lblCostEstimate").text
        except:
            pass

        try: 
            additionalMaterials = programHtml.find('span', id="dnn_ctr11976_View_lblAdditionalCost").text
        except:
            pass

        try: 
            textbookCost = programHtml.find('span', id="dnn_ctr11976_View_lblEstTextbookCost").text
        except:
            pass

        try:
            #get the URL to the courses for this program
            coursesUrl = programHtml.find('a', id="dnn_ctr11976_View_hypExplore")['href']
            fullCourseUrl = "https://fvtc.edu" + coursesUrl

            #get the program courses
            programCourses = get_courses(fullCourseUrl)

        except:
            pass
    
        program_dict = {'ProgramTitle' : programTitle, 'ProgramDescription' : programDescription, 'ProgramID' : programID, 'DegreeType' : degreeType, 'NumberOfCredits' : numberOfCredits, 'FinancialAidAvailable' : financialAidAvailable, 'CareerOpportunities' : careerOpportunities, 'TuitionAndFees' : tuitionAndFees, 'AdditionalMaterials' : additionalMaterials, 'TextbookCost' : textbookCost, 'ProgramCourses' : programCourses}
        return program_dict




def get_courses(fullCoursesUrl):
    '''
    A function that scapes the information on the page that displays the courses required for a program

    Requires: A url to the page that it will scrape the information from
    Returns: A data dictionary with the courses for the program and the number of credits for each area


    Going to maybe cause issues with non AAS degrees with the general credits and elective credits
    '''

    #List of properties
    numberTechnicalCredits = 0
    technicalStudies = []

    numberGeneralCredits = 0
    generalStudies = []

    numberElectiveCredits = 0
    suggestedElectives = []

    #bool for certificates
    isCertificate = False

    #make a connection to the page and parse it into a readable format
    coursesSite = requests.get(fullCoursesUrl, headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'})
    coursesHtml = BeautifulSoup(coursesSite.text, 'html.parser')

    #If connected to the page, parse out the information
    while coursesSite.status_code == 200:
    

        ### Get the number of credits needed for each type

        try: 
             #see if there is a section with this id used for technical courses. If not, it is a certificate and needs to be handled differently
             numberTechnicalCredits = coursesHtml.select_one("#dnn_ctr11979_View_rptCourseGroups_lblCourseGroupCredits_0").text                 
        except: 
            pass

        #If there are courses listed, then we got them already and this is not a certificate
        if numberTechnicalCredits != 0:
            #clean up the information
            numberTechnicalCredits = numberTechnicalCredits.lower().replace("(","").replace(")","").replace("credits","").strip()
        else:
            try: 
              #This is a certificate, and we need to grab a different container
              numberTechnicalCredits = coursesHtml.find('span', id="dnn_ctr11979_View_lblProgramCredits").text
              numberTechnicalCredits = numberTechnicalCredits.lower().replace('credits', '').strip()

              isCertificate = True

            except: 
                pass
           



        try: 
             numberGeneralCredits = coursesHtml.find('span', id="dnn_ctr11979_View_rptCourseGroups_lblCourseGroupCredits_1").text

             #clean up the information
             numberGeneralCredits = numberGeneralCredits.lower().replace("(","").replace(")","").replace("credits","").strip()
        except: 
            pass

        try: 
             numberElectiveCredits = coursesHtml.find('span', id="dnn_ctr11979_View_rptCourseGroups_lblCourseGroupCredits_2").text

             #clean up the information
             numberElectiveCredits = numberElectiveCredits.lower().replace("(","").replace(")","").replace("credits","").strip()
        except: 
            pass

        ### Get the courses for each type

        try: 
             technicalStudiesSection = coursesHtml.find('h3', id="dnn_ctr11979_View_rptCourseGroups_hCourseGroupHeading_0").parent
             technicalCourses = technicalStudiesSection.findAll('dd')

             for course in technicalCourses:
                 new_course_dict = extract_course_info(course)
                 technicalStudies.append(new_course_dict)
        except: 
            pass

        
        try: 
             generalStudiesSection = coursesHtml.find('h3', id="dnn_ctr11979_View_rptCourseGroups_hCourseGroupHeading_1").parent
             generalCourses = generalStudiesSection.findAll('dd')

             for course in generalCourses:
                 new_course_dict = extract_course_info(course)
                 generalStudies.append(new_course_dict)

        except: 
            pass

        try: 
             electiveSection = coursesHtml.find('h3', id="dnn_ctr11979_View_rptCourseGroups_hCourseGroupHeading_2").parent
             electiveCourses = electiveSection.findAll('dd')

             for course in electiveCourses:
                 new_course_dict = extract_course_info(course)
                 suggestedElectives.append(new_course_dict)

        except: 
            pass
      

        ###Exception for certificates

        if isCertificate:
            try: 
                 technicalStudiesSection = coursesHtml.find('dl', {"class":"fvtc-mod-posclst-accordion"})
                 technicalCourses = technicalStudiesSection.findAll('dd')

                 for course in technicalCourses:
                     new_course_dict = extract_course_info(course)
                     technicalStudies.append(new_course_dict)
            except: 
                pass


        course_dict = {'NumberTechnicalCredits' : numberTechnicalCredits, 'TechnicalStudies' : technicalStudies, 'NumberGeneralCredits' : numberGeneralCredits, 'GeneralStudies' : generalStudies, 'NumberElectiveCredits' : numberElectiveCredits, 'SuggestedElectives' : suggestedElectives}

        

        return course_dict


def extract_course_info(course):
    '''
    Function that when given a course will return a dictionary wit hthe name ID, number of credits, hour estimate and description for the course.
    '''

    courseName = "None"
    courseID = "None"
    courseNumberOfCredits = 0
    courseHourEstimate = "None"
    courseDescription = "None"


    try: 
        courseName = course.find('span', {"class" : "fvtc-mod-posclst-course-name" }).text
    except: 
        pass


     ####### NOTE : There is no class for course ID or number of credits or description , we must use selectors and travel through the DOM to get the elements out


    try: 
        courseID = course.a.select('div > div')[1].text.strip()
    except: 
        pass

    try: 
        courseNumberOfCredits = course.a.select('div > div')[2].span.text.strip()
    except: 
        pass

    try: 
        courseHourEstimate = course.find("div", {"class":"content"}).span.text.strip()
    except: 
        pass
                
    try: 
        courseDescription = course.find("div", {"class":"content"}).select_one("span:nth-of-type(2)").text.strip()
    except: 
        pass

    #Make a new dictionary for this course, and add it to the technical studie list
    new_course_dict = {'CourseName':courseName, 'CourseID':courseID, 'CourseNumberOfCredits': courseNumberOfCredits, 'CourseHourEstimate': courseHourEstimate, 'CourseDescription' : courseDescription}
    return new_course_dict

print("Retrieving Program Information!")


clusters = get_clusters()


with open('clusterInfo.txt', 'w') as f:
  json.dump(clusters, f, ensure_ascii=False)

print("\n\n JSON written to the file: 'clusterInfo.txt' ")
