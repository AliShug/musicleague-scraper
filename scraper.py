from selenium import webdriver
import pickle
import json
import os
from process import process

def do_login(browser, url):
    browser.get(url)
    cookies = browser.get_cookies()
    with open('cookies.pickle', 'wb') as f:
        pickle.dump(cookies, f)
    input('Login in the browser, then press Enter to continue here...')
    cookies = browser.get_cookies()
    with open('cookies.pickle', 'wb') as f:
        pickle.dump(cookies, f)


def scrape(browser, url):
    if not os.path.isfile('cookies.pickle'):
        do_login(browser, url)
    
    browser.get('https://musicleague.app')
    with open('cookies.pickle', 'rb') as f:
        cookies = pickle.load(f)
    for cookie in cookies:
        browser.add_cookie(cookie)
    print('Logged in')
    browser.get(url)

    # Just get the number of rounds
    round_count = len(browser.find_elements_by_link_text('Round Results'))
    rounds = []
    round_names = [x.text for x in browser.find_elements_by_class_name('round-title')]
    assert(round_count == len(round_names))

    for round_num, round_name in enumerate(round_names):
        browser.get(url)
        browser.find_elements_by_link_text('Round Results')[round_num].click()
        song_names = [x.text for x in browser.find_elements_by_class_name('name') if x.tag_name=='a' and len(x.text) > 0]
        submitters = [x.text[13:] for x in browser.find_elements_by_class_name('submitter') if x.tag_name=='span' and len(x.text) > 0]
        vote_containers = browser.find_elements_by_class_name('vote-breakdown')
        all_voters = []
        all_vote_counts = []
        for vote_container in vote_containers:
            upvotes = vote_container.find_elements_by_class_name('upvote')
            upvotes = upvotes[:len(upvotes)//2] # half are hidden
            all_vote_counts.append([ int(upvote.find_element_by_class_name('vote-count').text) for upvote in upvotes ])
            all_voters.append([ upvote.find_element_by_class_name('voter').text for upvote in upvotes ])
        songs = []
        for song_name, submitter, voters, vote_counts in zip(song_names, submitters, all_voters, all_vote_counts):
            song = {
                'name': song_name,
                'submitter': submitter,
                'votes': {voter:count for voter, count in zip(voters, vote_counts)}
            }
            songs.append(song)
        rounds.append({
            'name': round_name,
            'songs': songs
        })
    with open('data.json', 'w') as f:
        json.dump(rounds, f)
    return rounds

    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='URL for the music league - https://musicleague.app/l/<base64 crap>/')
    parser.add_argument('--login', '-l', action='store_true', help="Login to music league. Try this if the scraper isn't running correctly.")
    parser.add_argument('--process', '-p', action='store_true', help="Immediately process the data to csv (semicolon-separated) and print this.")
    args = parser.parse_args()

    browser = webdriver.Chrome()

    if args.login:
        do_login(browser, args.url)
    data = scrape(browser, args.url)

    if args.process:
        process(data)

    browser.close()
