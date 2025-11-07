# DataEngineerCertification
this is the repository for the project I completed in order to get my Data Engineering Certification from DataCamp

# Data Engineer Certification - Practical Exam - Supplement Experiments

1001-Experiments makes personalized supplements tailored to individual health needs.

1001-Experiments aims to enhance personal health by using data from wearable devices and health apps.

This data, combined with user feedback and habits, is used to analyze and refine the effectiveness of the supplements provided to the user through multiple small experiments.

The data engineering team at 1001-Experiments plays a crucial role in ensuring the collected health and activity data from thousands of users is accurately organized and integrated with the data from supplement usage. 

This integration helps 1001-Experiments provide more targeted health and wellness recommendations and improve supplement formulations.


~~~~~~~~~~~~~~~~~~~~

# Data Cleaning and Integration Pipeline

This project demonstrates the process of merging and cleaning data from multiple CSV files into a single, analysis-ready dataset. The pipeline reads four datasets related to user health, supplement usage, experiment metadata, and user profiles, performs necessary data transformations, and outputs a unified DataFrame.

### Datasets Used:
1. `user_health_data.csv` – Contains health metrics (heart rate, glucose, sleep, activity).
2. `supplement_usage.csv` – Lists supplement intake details (dosage, experiment ID).
3. `experiments.csv` – Contains experiment names and descriptions.
4. `user_profiles.csv` – Includes user demographic information (email, age).

### Key Operations:
- Merging datasets based on common columns (user_id, date).
- Cleaning categorical and text data (e.g., normalizing supplement names and emails).
- Handling missing values and ensuring data integrity.
- Converting between data types (e.g., parsing dates, extracting numeric values from text).
- Exporting the final dataset to CSV and Excel formats.

### Tools Used:
- Python 3.8
- Pandas
- Regular Expressions for text extraction and cleaning

### Output:
The cleaned and merged dataset is saved as:
- `merged_output.csv`
- `merged_output.xlsx` (if Excel is available)

