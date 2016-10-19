# Recommendation-System

This is a recommendation system created in python using the CherryPy and Mako frameworks. 

It uses a database of recipes to give recommendations according to ingredients. In the future, users can add their own recipes and food categories. 

The algorithm used to classify is a simple _nearest neighbours classifier_ that achieves _content based item to item collaborative filtering_. Once users begin to rate the items we can also add user based filtering where we also consider user similarity.

It is currently deployed and can be accessed as a web application from: [here](http://eatit.pythonanywhere.com/)

