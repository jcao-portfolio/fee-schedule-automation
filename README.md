-------------------------------------------------------
Fee Schedule Automation Program Part One and Two Guide
-------------------------------------------------------
Step-by-step process of how to convert Python file to an Executable file

1. First, open the command prompt using the search bar

2. Navigate to your project folder, for this example, it should be located in Fee Schedule Automation folder.

3. Then, create a virtual environment, this environment (env) should be created in Fee Schedule Automation.
        Use the following example code in the command prompt:
        - python -m venv env

4. After that, activate the virtual environment
        Use the following example code to navigate to 'Scripts' and activate the virtual environment, you will now see that the env is in parentheses (env):
        - C:/Fee Schedule Automation/env/Scripts> activate

5. Once your virtual enviroment is created and activated, you'll want to install the necessary packages that were used in the program
        The following commands can be used to install the required packages:
        - pip install pandas
        - pip install numpy
        - pip install xlrd
        - pip install openpyxl
        - pip install pyinstaller

6. At this point, you can now convert the python file (.py) to an executable file (.exe). Use the following command to create the executable: 
    - pyinstaller --onefile Fee_Schedule_Automation_Part_One.py
    - pyinstaller --onefile Fee_Schedule_Automation_Part_Two.py

7. Locate the executable file, this should be located in the 'dist' directory within the directory where the script is located.

8. After that, go into the 'dist' folder and move executable file into the main root 'Fee Schedule Automation' folder. 

9. Run the generated executable to test whether it works as expected.