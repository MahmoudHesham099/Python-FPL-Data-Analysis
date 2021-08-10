import operator
import seaborn as sns
import matplotlib.pyplot as plt
from fpl import FPL
import asyncio
import aiohttp

sns.set()


def positions_calc(players, first_attr, second_attr=None):
    positions = ['GK', 'DEF', 'MID', 'FWD']
    first_dict = dict({(position, 0) for position in positions})
    second_dict = dict({(position, 0) for position in positions})
    for player in players:
        position = positions[player.element_type-1]
        if first_attr == 'now_cost':
            first_dict[position] += getattr(player, first_attr) / 10
        else:
            first_dict[position] += getattr(player, first_attr)
        if second_attr == 'now_cost':
            second_dict[position] += getattr(player, second_attr) / 10
        else:
            second_dict[position] += 1
    avg_dict = dict({(position, first_dict[position]/second_dict[position]) for position in positions})
    ordered_avg_dict = dict(sorted(avg_dict.items(), key=operator.itemgetter(1), reverse=True))
    return ordered_avg_dict


def draw_bar(the_dictionary, x_label, y_label):
    keys = the_dictionary.keys()
    values = the_dictionary.values()
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.tick_params(axis='x', labelsize=8)
    for index, data in enumerate(values):
        plt.text(x=index-0.1, y=data+0.1, s="%.1f" % round(data, 2), fontdict=dict(fontsize=10))
    plt.bar(keys, values, color=['#38003b'])
    plt.show()


def get_top_dict(players, n):
    top_performance = sorted(players, key=lambda x: x.total_points, reverse=True)
    ret_dict = dict()
    for player in top_performance[:n]:
        ret_dict[player.web_name] = player.total_points
    return ret_dict


def get_costs(players, n):
    top_performance = sorted(players, key=lambda x: x.total_points, reverse=True)
    ret_dict = dict()
    for player in top_performance[:n]:
        ret_dict[player.web_name] = player.now_cost / 10
    return ret_dict


async def main():
    async with aiohttp.ClientSession() as session:
        fpl = FPL(session)
        players = await fpl.get_players()

        # average points per player in each position
        positions_avg_points = positions_calc(players, first_attr='total_points')
        draw_bar(positions_avg_points, 'Positions', 'Points / Player')
        # from this chart, the best formation is 3-4-3

        # average price per player in each position
        positions_avg_prices = positions_calc(players, first_attr='now_cost')
        draw_bar(positions_avg_prices, 'Positions', '$Millions / Player')
        # we will use this to get the bench players budget (1 GK, 2 DEF, 1 MID) = 20 Millions

        # average points per price in each position
        points_per_million = positions_calc(players, first_attr='total_points', second_attr='now_cost')
        draw_bar(points_per_million, 'Positions', 'Points / Million')
        # from this we can say that each million bring equal amount of points in each position (10 points per million)
        # so Budgets => FWD:(80/11)*3 = 22 million , DEF: (80/11)*3 = 22 million , MID = (80/11)*4 = 30 million , GK = 6 million

        # --------------------------------

        # get all players in each position
        GK_players = [player for player in players if player.element_type == 1]
        DEF_players = [player for player in players if player.element_type == 2]
        MID_players = [player for player in players if player.element_type == 3]
        FWD_players = [player for player in players if player.element_type == 4]

        # GK Budget = 6 Millions
        # top 5 GK with total_points
        # Choose 1 player
        top_GK = get_top_dict(GK_players, 5)
        GK_costs = get_costs(GK_players, 5)
        draw_bar(top_GK, 'GK Players', 'Total Points')
        draw_bar(GK_costs, 'GK Players', 'Cost')
        # from 2 charts the best GK is Martinez from Aston Villa cost = 5.5m
        # put remaining 0.5m in DEF Budget

        # DEF Budget = 22 + 0.5 = 22.5 Millions
        # top 5 DEF with total_points
        # Choose 3 players
        top_DEF = get_top_dict(DEF_players, 5)
        DEF_costs = get_costs(DEF_players, 5)
        draw_bar(top_DEF, 'DEF Players', 'Total Points')
        draw_bar(DEF_costs, 'DEF Players', 'Cost')
        # from 2 charts the best 3 DEF:
        # Arnold from Liverpool cost = 7.5m, Cresswell from West Ham cost = 5.5m, Wan-Bissaka from Man Utd cost = 5.5m
        # Robertson is injured so we don't choose him
        # put remaining 4m in MID Budget

        # MID Budget = 30 + 4 = 34 Millions
        # top 5 MID with total_points
        # Choose 4 players
        top_MID = get_top_dict(MID_players, 10)
        MID_costs = get_costs(MID_players, 10)
        draw_bar(top_MID, 'MID Players', 'Total Points')
        draw_bar(MID_costs, 'MID Players', 'Cost')
        # from 2 charts the best 4 MID:
        # Fernandes from Man Utd cost = 12m, Son from Spurs cost = 10m, Dallas from Leeds cost = 5.5m, Harrison from Leeds cost = 6m
        # put remaining 0.5m in FWD Budget

        # FWD Budget = 22 + 0.5 = 22.5 Millions
        # top 5 FWD with total_points
        # Choose 3 players
        top_FWD = get_top_dict(FWD_players, 10)
        FWD_costs = get_costs(FWD_players, 10)
        draw_bar(top_FWD, 'FWD Players', 'Total Points')
        draw_bar(FWD_costs, 'FWD Players', 'Cost')
        # from 2 charts the best 3 FWD:
        # Bamford from Leeds cost = 8m, Wood from Burnley cost = 7m, Adams from Southampton cost = 7m
        # Watkins is injured so we don't choose him
        # put remaining 0.5m in Bench Budget

        # Bench Budget = 20 + 0.5 = 20.5 Millions
        # 3 players with cost 5m and 1 player with 5.5m
        GK_costs = get_costs(GK_players, 10)
        draw_bar(GK_costs, 'GK Players', 'Cost')
        DEF_costs = get_costs(DEF_players, 10)
        draw_bar(DEF_costs, 'DEF Players', 'Cost')
        MID_costs = get_costs(MID_players, 40)
        draw_bar(MID_costs, 'MID Players', 'Cost')
        # Fabianski from West Ham cost = 5m, Dunk from Brighton cost = 5m
        # Targett from Aston Villa cost = 5m, Westwood from Burnley cost = 5.5m


asyncio.run(main())