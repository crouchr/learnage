# free tier is 1000 calls per day
# make a call every 10 minutes = 600 seconds
# num locations = 6
num_locations = 6
api_calls = num_locations * (24 * 60 * 60) / 600

print(api_calls)
