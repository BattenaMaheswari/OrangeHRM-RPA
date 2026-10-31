\# OrangeHRM Employee Management RPA



\## Project Overview



OrangeHRM Employee Management RPA is a web automation project developed using Python, Selenium WebDriver, and Flask.



The application automates employee management tasks in OrangeHRM through a simple web dashboard. Users can enter their login credentials and employee details, trigger the automation, and view the execution status and exported employee records.



\## Features



\- Flask-based web dashboard

\- Login using OrangeHRM credentials

\- Automated login using Selenium WebDriver

\- Navigation to the PIM module

\- Employee search and verification

\- Automated employee creation

\- Employee list extraction

\- Pagination handling

\- CSV export of employee records

\- Explicit waits and exception handling

\- Automation logging

\- Automated logout

\- Execution status displayed on the dashboard



\## Technologies Used



| Technology | Purpose |

|---|---|

| Python | Automation logic |

| Selenium WebDriver | Browser automation |

| Flask | Web dashboard and backend |

| HTML | Dashboard structure |

| CSS | Dashboard styling |

| CSV | Employee data export |

| ChromeDriver | Chrome browser automation |



\## Project Structure



```text

OrangeHRM-RPA/

│

├── app.py

├── automation.py

├── requirements.txt

├── README.md

├── .gitignore

│

├── templates/

│   └── index.html

│

└── static/

&#x20;   ├── style.css

&#x20;   └── screenshots/

```



\## Installation and Setup



\### 1. Clone the repository



```bash

git clone https://github.com/BattenaMaheswari/OrangeHRM-RPA.git

```



\### 2. Navigate to the project folder



```bash

cd OrangeHRM-RPA

```



\### 3. Create a virtual environment



```bash

python -m venv venv

```



\### 4. Activate the virtual environment



Windows:



```bash

venv\\Scripts\\activate

```



\### 5. Install dependencies



```bash

pip install -r requirements.txt

```



\## Run the Application



Start the Flask application:



```bash

python app.py

```



Open your browser and visit:



```text

http://127.0.0.1:5000

```



\## Automation Workflow



1\. Open the Flask dashboard.

2\. Enter OrangeHRM login credentials.

3\. Enter employee details.

4\. Submit the form to start automation.

5\. Selenium launches Chrome and logs in to OrangeHRM.

6\. Navigate to the PIM module.

7\. Search for the employee ID.

8\. If the employee does not exist, open the Add Employee page.

9\. Enter employee details and create the employee.

10\. Verify employee creation.

11\. Extract employee records from the employee list.

12\. Handle pagination and export records to CSV.

13\. Log out of OrangeHRM.

14\. Display the automation result on the Flask dashboard.



\## Output



The application displays:



\- Automation execution status

\- Employee details

\- Success or failure message

\- Total exported employee records

\- CSV export file location



\## Error Handling and Logging



The automation uses explicit waits, exception handling, and logging to handle browser interactions and unexpected execution errors.



\## GitHub Repository



\[OrangeHRM-RPA](https://github.com/BattenaMaheswari/OrangeHRM-RPA)



\## Author



\*\*Battena Maheswari\*\*



