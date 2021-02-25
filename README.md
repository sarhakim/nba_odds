# nba_odds

Project to predict NBA championship winner before NBA season and also before the playoffs when regular season is over.

## Run

To run the project in an environment with all the dependencies, use the shell scripts :
- **build_features.sh**
- **build_model.sh**

## Structure

Project modules are in the folder nba_odds. 

#### application
Scripts to combine all the other modules and run the project. 
- **build_features.py** : Module to build features and save its into .csv file. Paths can be changed in the config part.  
- **build_models.py** :  Module to build a model and save predictions into .csv file. 

#### config
This folder is not properly used yet. 
It contains all the configurations that can be used in the project : paths, model parameters, data schemas.

#### preprocessing

- **GamesPerTeam** : Creates a dataframe with one row per team per game.  
- **Labels** : Creates a dataframe with the winner per season.  
- **PlayersData** : Creates a dataframe with players by season with associated team. And one with players, season and associated stats.
- **SplitOnPlayoffs** : Class with playoff dates, regular season dates and a method to keep only regular season data from games_per_team dataframe.

#### features
Classes to build features.
- **EloRating**
The method `compute` creates a dataframe with the elo ratings of each team, for each games date. The elo of a game is the elo of the team before this game.  
The method `get_first_elo_season` gets the first elo value for each team of each season. Applied to a dataframe that contains only the playoff elo ratings, it provides the elo rating of each team before the playoff season.

- **PER** : player efficiency rating
The method `previous_season_per` uses previous season player performances and next season team compositions to get PER by team for next season.
The method `preplayoff_season_per` uses regular season player performances and team compositions to get PER by team for the playoff season.

- **TeamStats**
The method `compute_aggregated_features` is used to compute the season performances. Used to get regular season performances before the playoff season.
The method `compute_previous_season_features` is used to compute previous season performances for preseason analysis.

#### model

- **ModelBuilder** : Build and evaluate a model.  
Train dataset is the dataset before 2018. Test is 2018 season. 
Returns a dataframe with predictions and odds for each team, for 2018 season.


## Install

### Install poetry

```
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

To make sure virtual env is created in project. 

```
poetry config virtualenvs.in-project=true
```

## Install environment 

```
poetry install --no-root
```

A `requirements.txt` file is also available. (not tested)

### Virtual environment in jupyter notebooks 

```
python -m ipykernel install --user --name=nba-odds-env
```

# References 

https://towardsdatascience.com/predicting-the-outcome-of-nba-games-with-machine-learning-a810bb768f20

