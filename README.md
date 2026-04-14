# CIS-376-SmartBudget-AI-Powered-Personal-Finance-Manager



SmartBudget is a personal finance application that helps users track their expenses and income, set budgets and generate analytics and reports. It uses SQLite for local data storage and includes automated reporting and budget analysis features. 



**Features of SmartBudget:**



1. Transaction Management:

   * Add income and expense transactions
   * Store description, category, payment method, and date
   * Retrieve transactions by type, category, or month
   * Support recurring transactions
   * Delete transaction records





2\. Financial Analytics:

   * Total income and total expenses per month
   * Savings rate calculation
   * Average daily spending based on active spending days
   * Spending breakdown by category
   * Top expense categories
   * Period-over-period comparison between months



3\. Budget Tracking:



* Create budgets for specific categories
* Track total spending per category
* Calculate remaining budget
* Determine if spending exceeds budget limits





4\. Reporting System:



* It generates structured monthly reports including:

  * Monthly income and expenses
  * Net savings calculation
  * Savings rate percentage
  * Average daily spending
  * Top spending categories
  * Month-over-month comparison
  * Rule-based financial recommendations  



&#x20;                

5\. Local Database 

* Uses SQLite(SmartBudget.db)
* Stores transactions, budgets and categories







6\. Machine Learning Components

The system includes lightweight ML functionality:



a. Transaction Categorization (TransactionCategorizer)

* Uses a Naive Bayes-style word frequency model
* Trained on labeled transaction descriptions
* Predicts category based on transaction text input
* Supports saving and loading trained models using pickle



b. Spending Prediction (SpendingPredictor)

* Uses linear regression per category
* Predicts next-month spending based on historical values
* Handles single-month edge cases safely





**Prerequisites:**



The following must be installed on the system:

1. Python 3.8 or higher 
2. Python's package manager (pip)







**Installation Steps:**



1. Clone repository from GitHub using the following link:

&#x09;

&#x09;https://github.com/jalloul-design/CIS-376-SmartBudget-AI-Powered-Personal-Finance-Manager#



2\. Repository can be downloaded by clicking the green downward arrow button near 'Code'. 



3\. Select desired method either via GitHub Desktop or as a ZIP file to the system



4\. Open the project folder, right-click to open command prompt



5\. Using the command prompt, install dependencies mentioned in the requirements.txt file using the following command:


	py -m pip install -r requirements.txt







**Running the program:**



1. Open the project folder 
2. Open main.py file in python to run the program 
3. Use SmartBudget app as desired





**Testing:**



In the testing folder, there are three types of tests: 



1. Integration tests using test\_integration.py 

   * Tests the full system functionality:

     * Transaction workflow
     * Budget tracking
     * Analytics calculations
     * Edge cases such as empty database, invalid input





2\. Machine Learning Tests using test\_models.py



   * Tests AI Components:

     * Transaction Categorisation models
     * Spending prediction model
     * Model Saving and Loading
     * Prediction Validations





3\. Unit Testing Using test\_unit\_models.py



* Tests to ensure Transaction, Budget and Category Models works correctly on its own



* **Transaction Tests**

  * Create and store transactions
  * Retrieve by type, category, or month
  * Delete transactions
  * Handle recurring transactions	





* Budget Tests

  * Create budgets
  * Compute spending per category
  * Calculate remaining budget
  * Detect budget overflow conditions





* Category Tests

  * Create and retrieve categories
  * Get category by ID or name
  * Delete and update operations





