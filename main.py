import pandas as pd
import ast

campaign_file_one = pd.read_csv('df1.csv')
campaign_file_two = pd.read_csv('df2.csv')

# 1. what is the total spent against people with purple hair?
# can insert a hair color (purple, blue), state (AL, NY), or age range (18-23, 63-68)
def totalSpentByDemographic(demo):
    # 1. query df1 and get all the campaign_ids with audience with "purple" in the ValueError
    campaign_demographics = []

    for demographics in campaign_file_one.audience:
        if demo in demographics.split("_"):
            campaign_demographics.append(True)
        else:
            campaign_demographics.append(False)

    campaign_ids = pd.Series(campaign_demographics)
    # 2. With these IDs, query the df2 and get the spend columns and aggregate
    spends = campaign_file_two[campaign_ids].spend
    # 3. return the amount
    return reduce(lambda x, y: x+y, spends)

# print totalSpentByDemographic("purple") # 512986


#  2. how many campaigns spent on more than 14 total days?
def campaignMoreThanXDays(days):
    # 1. query df2 and group campaign_ids together
    grouped_by_id = campaign_file_two.groupby("campaign_id")
    # 2. now that they are grouped by campaign_ids do a count of unique date. ex fb6385ea-e679-4f16-99af-fc3b11fb665f has count of 11 but has 5/7/2017 on twice. so only really 10

    more_than_x_days = 0
    for campaigns in grouped_by_id.date.nunique():
        if campaigns > days:
            more_than_x_days += 1

    # 3. return campaign ids that have count > 14
    return more_than_x_days

# print campaignMoreThanXDays(14) # 61 campaigns

# 3. what was the total cost per view for all video ads, truncated to two decimal places?
def costPerViewVideos():
    # ** there are actions with just empty arrays so account for this
    # 1. query df2 and select all rows with ad_type = video
    videos_campaigns = campaign_file_two["ad_type"] == "video"

    # 2. with the rows, go through the actions (which is an array of objects) and find the values for key "source1" where {action: views, source1: xxxx}
    # 3. keep track of the total number of views

    total_video_views = 0

    for video_campaigns in campaign_file_two[videos_campaigns].actions:
        # converts string into list again
        video_campaigns = ast.literal_eval(video_campaigns)
        # gets rid of the [] empty actions
        if video_campaigns:
            for array in video_campaigns:
                if array["action"] == "views" and ("source1" in array.keys()):
                    total_video_views += array["source1"]

    # 4. at the same time aggregate the spend column (total =2266983)
    total_spend = campaign_file_two[videos_campaigns].spend
    total_spend = reduce(lambda x, y: x+y, total_spend)
    # 5. return the average rounded to 2 places $14.626451687829049
    return round(float(total_spend) / total_video_views, 2)

# print costPerViewVideos()

# 4. what combination of state and haircolor had the best cost per conversion?

def bestStateAndHaircolorConversion():

    # 1. merge the two files together so that the audience is in df2.
    merged = campaign_file_two.merge(campaign_file_one, on="campaign_id").drop_duplicates()

    # 2. make hair color and state their own columns
    states = []
    hair_color = []
    for row in merged["audience"]:
        states.append(row.split("_")[0])
        hair_color.append(row.split("_")[1])

    merged["state"] = states
    merged["hair_color"] = hair_color

    # 3. create dictionary where it holds all the state/color combination and spends and # of conversions
    dictionary = {}

    for index, row in merged.iterrows():
        actions = ast.literal_eval(row["actions"])

        if len(actions) != 0:
            for obj in actions:
                if not(row["state"]+"_"+row["hair_color"] in dictionary.keys()):
                     dictionary[row["state"]+"_"+row["hair_color"]] = {"conversions": 0, "spend": 0}

                if obj["action"] == "conversions" and ("source1" in obj.keys()):
                    dictionary[row["state"]+"_"+row["hair_color"]]["conversions"] += obj["source1"]
                    dictionary[row["state"]+"_"+row["hair_color"]]["spend"] += row["spend"]

    # 4. iterate through the dictionary and calculate average with spend / conversions and reassign everytime it is greater than the last amount
    best_combination = dictionary.keys()[0]
    best_value =  round(float(dictionary[best_combination]["spend"]) / dictionary[best_combination]["conversions"],2)

    for key, value in dictionary.items():
        if value["conversions"] > 0 and (round(float(value["spend"]) / value["conversions"],2) <  best_value):
            best_value = round(float(value["spend"]) / value["conversions"],2)
            best_combination = key

    return best_combination # Washington brown hair. Spent $0 for 148 conversions

print bestStateAndHaircolorConversion()
