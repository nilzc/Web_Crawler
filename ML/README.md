# Objectives
Represent documents as numerical features and apply machine learning to obtain retrieval ranked lists.

# Features
* Build a query-doc static feature matrix:

| query id | doc id | feature 1 | feature 2 | ... | label |
|---|---|---|---|---|---|
* The features can be all the scores from the previous retrieval models or other info (cosine, proximity, etc.).
* The label is the QREL relevance value (0 or 1).
* My understanding about this: use ML algorithm to "learn" from the previous IR models' scores so that we can 
take advantage of all the models and get better results.

# Cross Validation
It's required to use cross validation in this assignment. Each time choose 5 out of 25 queries as the test queries and the rest 
as the training queries. Repeat the process until all queries have been used as test queries.
 
# Test the model
1. Run the ML model to obtain scores.
2. Treat the scores as coming from an IR function and rank the documents.
3. Format the results as in HW1
4. Run ```trec_eval.pl``` and compare the results to the previous IR models.
