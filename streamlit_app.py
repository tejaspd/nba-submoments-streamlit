from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st

"""
# Buzzer NBA Insights App

Input a player and select what specifics you want to see to get more insights on them
"""

@st.cache()
def load_datasets():
    game_summary_df = pd.read_csv('nba-submoments-streamlit/21_22_season_results.csv')
    player_summary_df = pd.read_csv('nba-submoments-streamlit/y21_player_historical.csv')
    unique_players = player_summary_df['full_name'].unique().tolist()
    unique_team_aliases = game_summary_df['home_alias'].unique().tolist()
    
    return game_summary_df, player_summary_df, unique_players, unique_team_aliases
game_summary_df, player_summary_df, unique_players_list, unique_team_aliases_list = load_datasets()

col1, col2 = st.columns(2)

with col1:
    player_option = st.selectbox(
        'Player selected:',
        unique_players_list)
    player_active = st.selectbox(
        'Player played:',
        [True, False]
    )

with col2:
    stats_in_overall_context_option = st.selectbox(
        '2021-2022 Counting Statistics in:',
        ['all games', 'wins', 'losses'])

    season_type = st.selectbox(
        'Season Type:',
        ['regular season', 'post-season', 'all games'])

    against_teams = st.multiselect(
        'Against Team(s):',
        unique_team_aliases_list)

if 'regular' in season_type:
    is_playoff = [False]
elif 'post' in season_type:
    is_playoff = [True]
else:
    is_playoff = [True, False]

if player_option != '' and player_active == True:
    first_name, last_name = player_option.split(' ')
    url = "https://www.basketball-reference.com/req/202106291/images/players/{}01.jpg".format((last_name[0:5]+first_name[0:2]).lower())
    
    
    curr_player_df = player_summary_df.query("full_name == '{}' & active == {}".format(player_option, player_active))
    historical_curr_player_df = pd.merge(game_summary_df, curr_player_df, left_on='id', right_on='game_id')
    historical_curr_player_df.drop(historical_curr_player_df.filter(regex='_y$').columns, axis=1, inplace=True)
    historical_curr_player_df.query('is_playoff_x in {}'.format(is_playoff), inplace=True)
    wins = len(historical_curr_player_df[historical_curr_player_df['home_or_away'] == historical_curr_player_df['winner_home_away_x']])
    losses = len(historical_curr_player_df[historical_curr_player_df['home_or_away'] != historical_curr_player_df['winner_home_away_x']])
    if len(against_teams) != 0:
        historical_curr_player_df = historical_curr_player_df[historical_curr_player_df['home_alias'].isin(against_teams) | historical_curr_player_df['away_alias'].isin(against_teams)]
    st.write(historical_curr_player_df[['full_name','title_x','home_or_away','winner_name_x', 'statistics_points', 'statistics_rebounds', 'statistics_assists', 'statistics_field_goals_pct', 'statistics_three_points_pct', 'statistics_minutes', 'statistics_pls_min']])
    if stats_in_overall_context_option == 'all games':
        ppg_val = historical_curr_player_df['statistics_points'].mean()
        rpg_val = historical_curr_player_df['statistics_rebounds'].mean()
        apg_val = historical_curr_player_df['statistics_assists'].mean()
        threept_pct_val = historical_curr_player_df['statistics_three_points_pct'].mean()
        ft_pct_val = historical_curr_player_df['statistics_free_throws_pct'].mean()
        fg_pct_val = historical_curr_player_df['statistics_field_goals_pct'].mean()
    
    st.header("{} Statistics in {}".format(player_option ,season_type))
    st.metric("Team's record when {} did play is ".format(player_option), str(wins) + "-" + str(losses))
    player_image, stats_col0, stats_col1, stats_col2, stats_col3 = st.columns(5)
    
    
    with player_image:
        st.image(url)
    with stats_col0:
        st.metric("Games Played: ", len(historical_curr_player_df))
    with stats_col1:
        st.metric("PPG", round(ppg_val, 1), delta=None, delta_color="normal")
        st.metric("FG%", str(round(fg_pct_val, 1)) + "%", delta=None, delta_color="normal")
    with stats_col2:    
        st.metric("APG", round(apg_val, 1), delta=None, delta_color="normal")
        st.metric("3P%", str(round(threept_pct_val, 1)) + "%", delta=None, delta_color="normal")
    with stats_col3:
        st.metric("RPG", round(rpg_val, 1), delta=None, delta_color="normal")
        st.metric("FT%", str(round(ft_pct_val, 1)) + "%", delta=None, delta_color="normal")
