from tests.main import main, read_card
import card_reader_cli

if __name__ == "__main__":
    # main()
    # card_data = read_card()
    card_data = card_reader_cli.auto_read_card()
    print(card_data)