# football_tactics_viewer
Python desktop app, written using MVVM design pattern, for visualizing json data describing football events. 
Presentation video: https://youtu.be/leJww2ytKNQ

# Main modules used:
- Visualization  (GUI)          - PyQt5
- Json dataset transformations  - pandas, json, concurrent

# Source Data
Source data - 3 types of json files for every football match - comes from StatsBomb open data repository: https://github.com/statsbomb/open-data.
There are 3 types of files:
- "event" - describing current event on a football pitch witch relevant: football team and player, timestamp, location etc... assigned
- "three-sixty" (which are called 'frames' in the code) - describing current video camera frame captured during particular event (it includes locations of every player) that is currently available on screen
- "lineups" - describing teams taking part in given game with their lineup details.

Relevant objects from json file types mentioned above can be paired using following json attributes:
- "event" ("id")        <-> ("event_uuid") "three-sixty"
- "lineups" ("team_id") <-> ("team"."id") "event".

# Application features
So far, application supports following:
- multiple objects representing json datasets (sets of 3 types of files mentioned above) - can be added/deleted to/from a list on app GUI,
- all of them can have the data calculated and they can be changed in the fly during data visualization,
- location of each player (included in current set of data from "three-sixty" file type) is displayed for chosen number of frame (chosen match's event)
- some common data regarding event details is presented

![My Image](/Resources/img/sample_screen.PNG)

# Limitations caused by source data
- Particular players cannot be easily distinguished for every data frame. There is no such information provided in json files. So there is only a division into players of one and another team. 
- Not all player data is included for particular frame, so not always 22 players are presented. Basically, presented are only those who have been inside video frame which the data was originally collected from - limitation of data source.
- Ball location is not provided and ball is not presented in app so far.
- Referees locations are not provided thus not presented.

# Ideas for development
- Algorithm that will allow to track the ball location.
- Algorithm that will allow to track the identity of players.
- Solution to track current score and present it.
- Solution to save and read data already calculated from json files - to save time during future re-usage of it.
- Solution to implement custom changes in player positions (drawing on pitch view) and saving changes to the disk for future re-usage.