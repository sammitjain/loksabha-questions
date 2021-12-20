# loksabha-questions

<p align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/2/2c/Indian_Parliament.svg" alt="A graphic of the Parliament of India, Courtesy: Suthir, Wikipedia"/>
</p>

Questions asked in the Lok Sabha - collection and analysis of trends. Creating the dataset from scratch. Check out [this link](https://youthincmag.com/explained-question-hour-and-zero-hour-parliamentary-proceedings) for a quick explanation of how the Question Hour works in the Lok Sabha.

The eventual goal of this repo is a complete analysis of the questions asked in the Lok Sabha (House of the People - lower house of the Indian Parliament). As of writing this readme, the December 2021 session is in progress, and the dataset I've put together has 4250 questions from 1st December 2021 to 23rd December 2021.

Each question has the following information:
| Field | Description |
| ---: | --- |
| Question ID | The official question number |
| Question Type | Type of question, starred/unstarred |
| Question Date | Session Date in which question was presented |
| Question From | Asking Member(s) of Parliament |
| Question To | Ministry / Department sought in the question |
| Question Topic | Topic of the question |
| Question Contents | Question body |
| Member Party | Political affiliation of the Asking Member |
| Member State | Asking Member's state |
| Member Constituency | Asking Member's constituency |
| Member Constituency Type | Asking Member's constituency type |


The goal of this project is to be able to answer the following questions (work in progress):
* What are the questions that were asked by an MP?
* What are the questions being asked from a particular state?
* How many questions were asked around a particular topic?
* And many more combinations of these...
  
## Origins
* This dataset was compiled by parsing PDFs of session questions. Typical Oral and Written questions look like:

<p align="center">
  <img src="/doc/img/sample_oral.png" alt="Sample Page from List of Oral Questions in a Session" width=450/>
  <img src="/doc/img/sample_written.png" alt="Sample Page from List of Oral Questions in a Session" width=450/>
</p>

* These PDFs can be found on the [Official Lok Sabha Website](http://loksabhaph.nic.in/Questions/questionlist.aspx).
* As a starting point for this Dataset, I'm using the Seventeenth (17th) Session of the Lok Sabha. Will continue to add more sessions regularly.
* Parsing these PDFs is truly a challenge - a staggering amount of data to scrape, and an even more daunting number of typing inconsistencies to consider.
* Mapping the Asking Member to an actual Member of Parliament was also a difficult task. For e.g., consider the following names:
  - Shri Sunil Kumar Singh
  - Shri S.K. Singh
  - Shri Sunil Singh
  - *Singh, Shri Sunil Kumar*
  - Singh, Sunil Kumar
  - Singh, Sunil K.
* These are all valid ways to write a name. Which one do we stick to? I choose to go with the full name approach with Last Name, First Name. Fuzzy-matching of Indian names was a difficult task, but it worked out well, thanks mostly to [thefuzz](https://github.com/seatgeek/thefuzz).
* Btw, interestingly, we currently have *FIVE* Shri Sunil Kumar's as MPs:


| Member Name | Party | Constituency |
| --- | --- | --- |
| Mondal, Shri Sunil Kumar | All India Trinamool Congress	| Bardhaman Purba (SC)(West Bengal) |
| Singh, Shri Sunil Kumar	| Bharatiya Janata Party	| Chatra (Jharkhand) |
| Soni, Shri Sunil Kumar	| Bharatiya Janata Party	| Raipur (Chhattisgarh) |
| Sunil Kumar Pintu, Shri	| Janata Dal (United)	| Sitamarhi (Bihar) |
| Kumar, Shri Sunil	| Janata Dal (United)	| Valmiki Nagar (Bihar) |


## Why are there TWO .csv files in this dataset?

* Sometimes, questions are clubbed, and therefore may list multiple asking members. For example, consider Q. 362 and Q. 4142 in the above screenshots.
* Therefore, Multiple Members may ask a Single Question, and a Single Member may ask Multiple Questions.
* This makes it harder to analyze questions - specifically operations like grouping / aggregating in a dataset.
* This Many-to-Many relationship is typically addressed in Databases by means of a bridging table.
* However, considering the scale of the problem, I decided to ship an augmented version of this database as well which is called `questions_flattened.csv` in addition to the `questions.csv` database. 
* A quick look into the number of questions will better demonstrate the above explanation.
  - Each session has 250 questions on record (20 starred + 230 unstarred).
  - For 17 sessions, the total comes to **4250 questions**. This is why `questions.csv` has 4250 entries as of now.
  - Some questions were asked by multiple members, so I replicated these questions for each asking Member of Parliament.
  - This results in **7050 questions** after *flattening out* the questions - Hence, `questions_flattened.csv`


## NOTE: 
* I do not own any of the associated data and is publicly available at http://loksabhaph.nic.in/Questions/questionlist.aspx as on December 15th, 2021. 
* Any information presented is merely an interpretation and should not be used as a substitute for real data.
* Since this project involves a lot of text analytics, natural language processing, semantic parsing of really messy data, it is prone to errors.
