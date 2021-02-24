# nba_odds


## Install

### Install poetry`

```
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

To make sure virtual env is created in project. 

```
poetry config virtualenvs.in-project=true
```

### Install environment 

```
poetry install --no-root
```

### Virtual environment in jupyter notebooks 

```
python -m ipykernel install --user --name=nba-odds-env
```
# Références 

https://towardsdatascience.com/predicting-the-outcome-of-nba-games-with-machine-learning-a810bb768f20

