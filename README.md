# About project
A self-implemented project that is a small copy of a Takeaway. It mainly focuses on showing the experience of an building api.
The project allows us to order food from a restaurant of our choice and see the orders that are already created.
All restaurants are imaginated, also created orders are not real.
I didn't do a demo because I'm not familiar with front-end and a frameworks like react.
Here is an [API documentation](https://restaurantapp.mateuszk.site/docs).
If there is something I should correct, please let me know about it.

# Counting delivery time
One idea was to count the delivery time based on the restaurant address and the order address.
When creating the order, the server communicated with [Distancematrix.ai](https://distancematrix.ai/)'s Matrix API
where restaurant addresses as well as orders were sent, and delivery time was taken.
I gave up on the idea because it is an unnecessary cost for me and the trial versions end after a month.
The code that was supposed to be used for this is [here](https://github.com/mateuszklusowski/restaurantapp/tree/main/counting_time_code).

# Libraries and technologies used in project
Django\
djangorestframework\
django-crispy-forms\
social-auth-app-django\
django-oauth-toolkit\
drf_social_oauth2\
PostgresSQL\
psycopg2\
celery\
redis\
httpx
## Documentation

[Documentation](https://restaurantapp.mateuszk.site/docs)
