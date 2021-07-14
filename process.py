def kinda_next(x):
    try:
        return next(x)
    except:
        return None

def process(data):
    players = []
    for round in data:
        for song in round['songs']:
            submitter = song['submitter']
            if not submitter in players:
                players.append(submitter)

    print(";".join(players))

    for i, round in enumerate(data):
        # Sort by players
        songs = round['songs']
        songs = [kinda_next(song for song in songs if song['submitter'] == player) for player in players]
        for song_i, (song, submitter) in enumerate(zip(songs, players)):
            round_name = round['name']
            tab = ';'
            if song is None:
                song_name = '~No submission~😭'
                votes = [0 for player in players]
            else:
                song_name = song['name']
                votes = [song['votes'].get(player, 0) for player in players]
            print(f'{round_name if song_i == 0 else ""};{submitter};{song_name};{tab.join([str(vote) for vote in votes])}')

if __name__=='__main__':
    import json
    with open('data.json', 'r') as f:
        data = json.load(f)
    process(data)

# import matplotlib.pyplot as plt
# import numpy as np
# poi = 'Someone'
# vote_totals = np.array([0]*len(players))
# for songs in data:
#     for song in songs:
#         if song['submitter'] == poi:
#             votes = [song['votes'].get(player, 0) for player in players]
#             vote_totals += votes
# plt.bar(players, vote_totals)
# plt.title(f'Votes for {poi}')
# plt.show()