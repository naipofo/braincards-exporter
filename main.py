import json
import requests
from os import getenv
import argparse
import markdown2


braincards_userid = getenv("BRAINCARDS_USERID")
braincards_apikey = getenv("BRAINCARDS_APIKEY")
braincards_name = getenv("BRAINCARDS_NAME")


def generate_text_export(cards_data):
    deck_name = f"{cards_data['pack']['name']}::{cards_data['deck']['name']}"

    cards_text = []
    for card in cards_data['cards']:
        def md_field(key):
            converted_text = markdown2.markdown(card[key]) if card[key] else ""
            escaped_quotes = converted_text.replace('"', '""')
            return f'"{escaped_quotes}"'

        def img_field(key):
            return f"\"<img src=\"\"{card[key]}\"\">\"" if key in card and card[key] else ""

        cards_text.append('\t'.join([
            deck_name,
            str(card["cardId"]),
            md_field("qMdBody"),
            md_field("qMdClarifier"),
            md_field("qMdFootnote"),
            md_field("qMdPrompt"),
            img_field("qOriginalImageUrl"),
            md_field("aMdBody"),
            md_field("aMdClarifier"),
            md_field("aMdFootnote"),
            md_field("aMdPrompt"),
            img_field("aOriginalImageUrl"),
        ]))

    return '\n'.join(cards_text)


def get_cards(pack_id, deck_id):

    url = f"https://api.{braincards_name}.com/api/v2/packs/{pack_id}/decks/{deck_id}/cards"
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "pragma": "no-cache",
        f"x-{braincards_name}-userid": braincards_userid,
        f"x-{braincards_name}-apikey": braincards_apikey,
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        cards_data = response.json()
        return generate_text_export(cards_data)
    else:
        print(f"Error fetching cards: {response.status_code}")


def get_cards_for_pack(pack_id):

    url = f"https://api.{braincards_name}.com/api/v2/market/packs/{pack_id}/decks"
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "pragma": "no-cache",
        f"x-{braincards_name}-userid": braincards_userid,
        f"x-{braincards_name}-apikey": braincards_apikey,
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Extract decks data from JSON
        decks_data = response.json()

        full_text = ""

        # Retrieve cards data for each deck
        for deck in decks_data:
            deck_id = deck["deckId"]
            # print(f"Processing deck: {deck_id}")
            full_text += get_cards(pack_id, deck_id) + "\n"

        return full_text
    else:
        print(
            f"Error fetching decks for pack ID {pack_id}: {response.status_code}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack", type=int, default=None, help="Pack ID")
    parser.add_argument("--deck", type=int, default=None, help="Deck ID")
    parser.add_argument("--full-pack", action="store_true",
                        help="Fetch cards for all decks in the pack")

    args = parser.parse_args()

    pack_id = args.pack
    deck_id = args.deck

    full_txt = ""

    if args.full_pack:
        full_txt = get_cards_for_pack(pack_id)
    else:
        if pack_id and deck_id:
            full_txt = get_cards(pack_id, deck_id)
        else:
            # Prompt user for pack ID and deck ID if not provided as arguments
            pack_id = input("Enter pack ID: ")
            deck_id = input("Enter deck ID: ")

            full_txt = get_cards(pack_id, deck_id)

    print(f"#separator:tab\n#html:true\n#deck column:1\n{full_txt}")
