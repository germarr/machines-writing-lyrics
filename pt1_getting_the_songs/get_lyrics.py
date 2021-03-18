from urllib.parse import urlencode
import requests
import json
import pandas as pd
from requests_html import HTML
import re

ar = input("Name of artist: ")
lang_ = input("Main Language (ES or EN): ")


def main(artist=ar):
    client_access_token = "_jnouQXAL5mt8OAZg4Ge93aoxSJKxLPWymm1wk57a4lnO4oPKrCp5bbc6dCu0KKY"

    artist_id = search_artist_id(search_term=artist, token=client_access_token)

    print(f"artist_id: {artist_id}")

    full_df_clean = all_artist_songs(
        id_of_artist=artist_id, token=client_access_token)

    print(f"\nThe artists has: {len(full_df_clean)} songs")

    sentences_list = lyrics_list(
        all_artist_songs=full_df_clean.url.tolist()[0:100])

    all_sentences, sentences_df = combine_all_sentences(
        list_of_sentences=sentences_list)

    save_to_txt(sentences=all_sentences, artist=artist, lang=lang_)


def search_artist_id(search_term, token):

    headers = {"Authorization": f"Bearer {token}"}
    search = search_term
    endpoint_search = "https://api.genius.com/search"
    data_search = urlencode({"q": f"{search}"})
    lookup_url_search = f"{endpoint_search}?{data_search}"

    r_search = requests.get(lookup_url_search, headers=headers).json()

    base_search = r_search["response"]["hits"][0]["result"]["primary_artist"]
    artist_id = base_search.get("id")

    return artist_id


def all_artist_songs(id_of_artist, token):
    songs_urls = []
    next_page = 1
    headers = {"Authorization": f"Bearer {token}"}
    while True:
        r_songs = requests.get(
            f"https://api.genius.com/artists/{id_of_artist}/songs?per_page=50&page={next_page}&sort=popularity", headers=headers).json()

        amount_of_songs = range(len(r_songs["response"]["songs"]))
        print(next_page, end=', ')
        for i in amount_of_songs:
            url_base = r_songs["response"]["songs"][i]
            songs_urls.append({
                "song_id": url_base.get("id"),
                "url": url_base.get("url"),
                "song": url_base["title_with_featured"],
                "full_title": url_base["full_title"],
                "primary_artist_id": url_base["primary_artist"]["id"],
                "primary_artist_name": url_base["primary_artist"]["name"],
                "hot": url_base["stats"].get("hot")
            })

            next_page = r_songs["response"].get("next_page")

        if not next_page:
            break

    full_df = pd.DataFrame.from_dict(songs_urls)
    full_df_clean = full_df.query(f'primary_artist_id == {id_of_artist}')

    return full_df_clean


def words_from_song(url):
    r = requests.get(url).text
    r_html = HTML(html=r)

    try:
        lyrics = r_html.find("p")[0].text.lower()
    except IndexError:
        lyrics = "null"

    lst = [lyrics]
    word_list = lst[0].split()

    try:
        df = pd.DataFrame(word_list).rename(columns={0: "words"}).groupby(
            "words").size().reset_index().sort_values(by=0, ascending=False)
    except KeyError:
        df = "null"

    sentences = lyrics.split('\n')
    sentences_list = []

    for i in range(len(sentences)):
        varOne = re.sub(r'\[[^()]*\]', '', sentences[i])
        if varOne != "":
            sentences_list.append(varOne)

    while(" " in sentences):
        sentences.remove(" ")

    return lyrics, word_list, df, sentences_list
    

def lyrics_list(all_artist_songs):
    lyrics_list = []
    word_list_ = []
    sentences_list = []
    df_list = []

    for i in range(len(all_artist_songs)):
        url = all_artist_songs[i]
        lyrics, word_list, df, sentences = words_from_song(url)
        lyrics_list.append(lyrics)
        word_list_.append(word_list)
        df_list.append(df)
        sentences_list.append(sentences)
        print(i+1, end=", ")

    return sentences_list


def combine_all_sentences(list_of_sentences):
    all_sentences = []

    for i in range(len(list_of_sentences)):
        for si in range(len(list_of_sentences[i])):
            all_sentences.append(list_of_sentences[i][si])

    sentences_df = pd.DataFrame(all_sentences)

    return all_sentences, sentences_df


def save_to_txt(sentences, artist, lang):
    list_to_convert = sentences
    artist_ = artist.replace(" ", "").lower()

    with open(f'../lyrics/{lang}/{artist_}.txt', 'w', encoding="utf-8") as filehandle:
        for listitem in list_to_convert:
            filehandle.write('%s\n' % listitem)

    print(f"\nFile '{artist_}.txt' Created!")


if __name__ == "__main__":
    # execute only if run as a script
    main()
