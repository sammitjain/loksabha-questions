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
  
## Origins + Observations
* Sometimes, questions are clubbed, and therefore may list multiple asking members.


## NOTE: 
* I do not own any of the associated data and is publicly available at http://loksabhaph.nic.in/Questions/questionlist.aspx as on December 15th, 2021. 
* Any information presented is merely an interpretation and should not be used as a substitute for real data.
* Since this project involves a lot of text analytics, natural language processing, semantic parsing of really messy data, it is prone to errors.
