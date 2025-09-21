import random as rd
import sys
import logging as log
import time
import copy

log.basicConfig(level=log.CRITICAL, format='%(levelname)s -  %(message)s')




RANKS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K', 'A']
SUITS = ['♥', '♠', '♦', '♣']

RANK_VALUES = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 
               9: 9, 10: 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}

HAND_RANKING = {'high card' : 1, 'pair': 2, 'double pair' : 3, 'three of a kind': 4, 
                    'straight': 5, 'flush': 6, 'full house': 7, 'four of a kind': 8, 
                    'straight flush': 9, 'royal flush': 10}

GAME_ROUNDS = {1: 'preflop', 2: 'flop', 3: 'turn', 4: 'river'}



def get_deck():

    global RANKS
    global SUITS

    deck = []

    for rank in RANKS:
        for suit in SUITS:
            deck.append([rank, suit])

    return deck




def get_card(number_of_cards, deck):

    if number_of_cards > len(deck):
        deck = get_deck()

    cards = []

    cards = deck[:number_of_cards]

    log.info(f'card slice from deck: {cards}')

    deck = deck[number_of_cards:]

    log.info(f'There are {len(deck)} cards in the deck')

    return cards, deck




def get_hand_rank(hand):

    log.info(f'Hand : {hand}')

    global RANKS
    global SUITS

    hand_ranks = [0] * len(hand)
    hand_suits = [0] * len(hand)

    log.info(f'Hand ranks length: {hand_ranks}')
    log.info(f'Hand suits length: {hand_suits}')

    for card in range(len(hand)):
        hand_ranks[card] = hand[card][0]
        hand_suits[card] = hand[card][1]

    

    return hand_ranks, hand_suits




def duplicates_checker(hand_ranks):
    
    ranks_counter = {}
    pair_counter = []
    triple_counter = []
    quadruple_counter = []
    duplicate_rank = []

    log.info(f'Hand ranks : {hand_ranks}')

    for card in hand_ranks:
        ranks_counter.setdefault(card, 0)
        ranks_counter[card] = ranks_counter[card] + 1
        
    for duplicate in ranks_counter.keys():
        if ranks_counter[duplicate] == 2:
            pair_counter.append(RANK_VALUES[duplicate])
        if ranks_counter[duplicate] == 3:
            triple_counter.append(RANK_VALUES[duplicate])
        if ranks_counter[duplicate] == 4:
            quadruple_counter.append(RANK_VALUES[duplicate])

    duplicate_rank = [pair_counter] + [triple_counter] + [quadruple_counter]
    
    log.info(f'Ranks counter: {ranks_counter}')
    log.info(f'Duplicate rank: {duplicate_rank}')
    
    return duplicate_rank




def flush_checker(hand_suits, hand):

    global SUITS
    global RANK_VALUES
    flush_rank = 0
    suits_counter = {}
    is_a_flush = False
    suited_hand = copy.copy(hand)

    for suit in hand_suits:
        suits_counter.setdefault(suit, 0)
        suits_counter[suit] = suits_counter[suit] + 1

    if not suits_counter:
        return False, None

    if 5 in suits_counter.values():
        is_a_flush = True
        for suit, counter in suits_counter.items():
            if counter == 5:
                flush_suit = suit

        for i in range(len(suited_hand)):
            if suited_hand[i][1] != flush_suit:
                suited_hand.remove(i)
        for i in range(suited_hand):
            if flush_rank < RANK_VALUES[suited_hand[i][0]]:
                flush_rank = RANK_VALUES[suited_hand[i][0]]

    return is_a_flush, flush_rank, suited_hand




def straight_checker(hand_ranks, hand):
    
    global RANK_VALUES

    count = 1
    straight_rank = None
    is_a_straight = False
    straight_cards = []
    sorted_hand = list(set(hand_ranks))
    sorted_hand = sorted(sorted_hand, key = lambda card: RANK_VALUES[card])

    if len(sorted_hand) < 5:
        return False, None, None

    if {2, 3, 4, 5, 'A'}.issubset(set(sorted_hand)):
        is_a_straight = True
        straight_rank = 5

    values = [RANK_VALUES[c] for c in sorted_hand]

    log.info(f'Hand values: {values}')

    for i in range(1, len(values)):  
        if values[i] == values[i - 1] + 1:
            count += 1
            straight_cards.append(values[i-1])
            straight_cards.append(values[i])
            if count >= 5:
                is_a_straight = True
        else:
            count = 1

    straight_cards = list(set(straight_cards))

    log.info(f'Straight cards: {straight_cards}')

    if is_a_straight != True:
        straight_cards = [0]*5

    return is_a_straight, straight_rank, straight_cards




def get_hand_type(hand):
    
    hand_ranks, hand_suits = get_hand_rank(hand)
    is_a_flush, flush_rank, suited_hand = flush_checker(hand_suits, hand)
    duplicate_rank = duplicates_checker(hand_ranks)
    is_a_straight, straight_rank, straight_hand = straight_checker(hand_ranks, hand)
    
    same_card_counter = 1
    hand_highest_card = None
    hand_type = []

    if duplicate_rank[0] != []:
        hand_type.append('pair')
        hand_highest_card = max(duplicate_rank[0])
        log.info(f'Hand highest card: {hand_highest_card}')
        duplicate_rank[0].remove(hand_highest_card)
        if duplicate_rank[0] != []:
            hand_type.append('double pair')

    if duplicate_rank[1] != []:
        hand_type.append('three of a kind')
        hand_highest_card = max(duplicate_rank[1])

    if duplicate_rank[2] != []:
        hand_type = ['four of a kind']
        hand_highest_card = max(duplicate_rank[2])

    if 'pair' in hand_type and 'three of a kind' in hand_type:
        hand_type = ['full house']

    if is_a_straight == True:
        hand_type.append('straight')
        hand_highest_card = straight_rank

    if is_a_flush == True:
        hand_type.append('flush')
        hand_highest_card = flush_rank

    if is_a_flush == True and is_a_straight == True :
        for i in range(suited_hand):
            if suited_hand[i][0] == straight_hand[i]:
                same_card_counter += 1
        if same_card_counter == 5:
            hand_type.append('straight flush')

    if 'straight flush' in hand_type and 'A' in hand_ranks:
        hand_type = ['royal flush']
    
    log.info(f'Hand type: {hand_type}')

    return hand_type, hand_highest_card




def get_hand_strength(hand_type):

    global HAND_RANKING

    hand_strength = 0
    for type in hand_type:
        if hand_strength <= HAND_RANKING[type]:
            hand_strength = HAND_RANKING[type]
    
    log.info(f'Hand strength: {hand_strength}')

    return hand_strength



# Automates the get_hand_strength process
def auto_get_hand_strength(hand):

    hand_ranks, hand_suits = get_hand_rank(hand)

    log.info(f'Player hand length: {len(hand)}')

    hand_type, highest_card = get_hand_type(hand)
    
    hand_strength = get_hand_strength(hand_type)
    

    return {'hand strength': hand_strength, 'hand type': hand_type, 'hand highest card': highest_card}




def balance_update(amount, balances, bet_issuer):

    betted_amount = 0

    if bet_issuer == player:
        if balances.get(player, 0) >= amount:
            balances[player] -= amount
            betted_amount = amount
        else:
            print('You do not have sufficient balance. Please enter a lower bet.')
 
    if bet_issuer == bot:
        if balances.get(bot, 0) >= amount:
            balances[bot] -= amount
            betted_amount = amount
        else:
            log.info(f'The bot doesn\'t have enough money to bet: {balances[bot]}')
            

    return balances, betted_amount




def big_blind_mechanic(balances, button_bet_issuer):

    betting_pool = 0
    who_bets = ''

    if button_bet_issuer == player:
        player_bet = big_blind
        balances, betted_amount = balance_update(player_bet, balances, player)
        who_bets = bot
    else:
        bot_bet = big_blind
        balances, betted_amount = balance_update(bot_bet, balances, bot)
        who_bets = player
    betting_pool += betted_amount
    
    return balances, betting_pool, who_bets


def player_bet_mechanic(balances, betting_pool, bot_total_bet, player_total_bet, player):
    
    player_action = ''

    while True:
        if player_total_bet > bot_total_bet:
            player_betting_amount = 0
            player_action = None
            break

        if player_total_bet <= bot_total_bet:
            print(f'Do you wish to raise (r), call (c), or fold (f) ? Your balance is {balances[player]}.')
            player_input = input('> ')

            if player_input == 'r':
                print('Please input the raise amount.')
                try:
                    player_bet = int(input('> '))
                    balances, player_betting_amount = balance_update(player_bet, balances, player)   
                    player_action = 'raise'
                    betting_pool += player_betting_amount
                    player_total_bet  += player_betting_amount
                    if player_betting_amount != 0:
                        break

                except TypeError:
                    print('Please enter a correct number.')
                    

            elif player_input == 'c':
                player_betting_amount = bot_total_bet - player_total_bet
                balances, player_total_bet = balance_update(player_betting_amount, balances, player)
                player_action = 'call'
                betting_pool += player_betting_amount
                break

            elif player_input == 'f':
                player_action = 'fold'
                player_betting_amount = 0
                break 

            else:
                print('Please type a correct input please.')    
        
        
    return betting_pool, player_action, player_betting_amount, player_total_bet




def bot_bet_sizing(balances, player_betting_amount, betting_pool):

    bet_size = 0

    if any(balances[bot] > amount for amount in (3*big_blind, 
                                                 1.2*player_betting_amount, 
                                                 0.2*betting_pool)):
        bet_size = max(3*big_blind, 1.2*player_betting_amount, 0.2*betting_pool)
    elif balances[bot] == 0:
        return bet_size
    else:
        bet_size = balances[bot]/4

    return bet_size




def bot_round_strategy(balances, bot_hand_info, which_round, betting_pool, big_blind, player_betting_amount, bot_betting_amount, bot_total_bet):
    
    global RANKS
    global SUITS
    global RANK_VALUES

    bet_issuer = 'bot'
    bot_action = ''
    
    bot_hand_strength = bot_hand_info['bot hand strength']
    bot_hand_type = bot_hand_info['bot hand type']
    bot_hand = bot_hand_info['bot hand']
    bot_hand_ranks, bot_hand_suits = get_hand_rank(bot_hand)
    log.info(f'Bot hand ranks: {bot_hand_ranks}')
    close_strong_hand = False

    bot_call = player_betting_amount

    bluffing_opportunity = rd.random()

    close_hand = []

    strong_hand_threshold = range(which_round+1, 11)
    medium_hand_threshold = [which_round-1, which_round]


    if bot_hand_strength in strong_hand_threshold:
        bot_bet_size = min(bot_bet_sizing(balances, player_betting_amount, betting_pool), balances[bot]/2)
    elif bot_hand_strength in medium_hand_threshold:
        bot_bet_size = min(bot_bet_sizing(balances, player_betting_amount, betting_pool), balances[bot]/4)
    else :
        bot_bet_size = min(bot_bet_sizing(balances, player_betting_amount, betting_pool), balances[bot]/10)
    
    if bot_bet_size == 0:
        bot_action = 'fold'
        return balances, betting_pool, bot_betting_amount, bot_total_bet, bot_action


    for rank in RANKS:
        for suit in SUITS:
            close_hand = auto_get_hand_strength(bot_hand + [[rank, suit]])['hand strength']
            if close_hand in strong_hand_threshold:
                close_strong_hand = True
                break

    if which_round == 1: 
        if bot_hand_strength in strong_hand_threshold:
            balances, bot_betting_amount =  balance_update(bot_bet_size, balances, bet_issuer)
            bot_action = 'raise' 

        elif bot_hand_strength in medium_hand_threshold:
            if bluffing_opportunity <= 0.6:
            # If the hand has 2 cards of the same color or they follow each other (8 and 9 for ex)
                if bot_hand[0][1] == bot_hand[1][1] or abs(RANK_VALUES[bot_hand_ranks[0]]-RANK_VALUES[bot_hand_ranks[1]]) == 1:
                    balances, bot_betting_amount = balance_update(bot_bet_size, balances, bet_issuer)
                    bot_action = 'raise'

                else:
                    balances, bot_betting_amount = balance_update(bot_call, balances, bet_issuer)
                    bot_action = 'call'

        elif bot_hand_strength == 0:
            if bluffing_opportunity <= 0.5:
                balances, bot_betting_amount = balance_update(bot_call, balances, bet_issuer)
                bot_action = 'call'

            else:
                bot_action = 'fold'
                
        else:
            bot_action = 'fold'

    elif which_round in [2, 3, 4]:
        # Raises
        if bot_hand_strength in strong_hand_threshold:
            balances, bot_betting_amount = balance_update(bot_bet_size, balances, bet_issuer)
            bot_action = 'raise'

        # Bluffs raise
        elif close_strong_hand == True:
            if bluffing_opportunity <= 0.7:
                balances, bot_betting_amount = balance_update(bot_bet_size, balances, bet_issuer)
                bot_action = 'raise'

            else:
                balances, bot_betting_amount = balance_update(bot_call, balances, bet_issuer)
                bot_action = 'call'

        # Calls
        elif bot_hand_strength in medium_hand_threshold:
            balances, bot_betting_amount = balance_update(bot_call, balances, bet_issuer)
            bot_action = 'call'

        # Folds
        else:
            bot_action = 'fold'
    
    # In case which_round doesn't work as intended or for some reason bot_action = ''
    else:
            bot_action = 'fold'
    
    # Preventing the bot from raising to the moon by either all-in, calling or folding
    if 2*bot_total_bet >= balances[bot]:
        balances[bot] += bot_betting_amount
        # Undoing the bet
        if bot_hand_strength in strong_hand_threshold:
            if bluffing_opportunity <= 0.2:
                balances, bot_betting_amount =  balance_update(balances[bot], balances, bet_issuer)
                bot_action = 'all in' 
            else:
                balances, bot_betting_amount = balance_update(bot_call, balances, bet_issuer)
                bot_action = 'call'
        elif bot_hand_strength in medium_hand_threshold and bot_action == 'raise':
            bot_action = 'call'
        else:
            bot_action = 'fold'

    time.sleep(delay)

    print(f'The bot has choosen to {bot_action}.')

    betting_pool = betting_pool + bot_betting_amount

    bot_total_bet += bot_betting_amount

    log.info(f'Bot hand: {bot_hand}')
    log.info(f'Bot total bet: {bot_total_bet}')
    log.info(f'Betting pool: {betting_pool}')
    log.info(f'bot_betting_amount {bot_betting_amount}')

    return balances, betting_pool, bot_betting_amount, bot_total_bet, bot_action


def who_wins(round_info):

    winner = ''
    tie = 'tie'
    player_hand_duplicates = round_info['player hand duplicates']
    bot_hand_duplicates = round_info['bot hand duplicates']


    if round_info['player hand strength'] > round_info['bot hand strength']:
        winner = player
        return winner
    
    elif round_info['player hand strength'] < round_info['bot hand strength']:
        winner = bot
        return winner
    
    elif round_info['player hand strength'] == round_info['bot hand strength']:
        if player_highest_card == None and bot_highest_card == None:
            winner = tie
            return winner

        elif player_highest_card > bot_highest_card:
            winner = player
            return winner

        elif player_highest_card < bot_highest_card:
            winner = bot
            return winner

    else:
        for i in reversed(range(3)):
            player_max_dup = max(player_hand_duplicates[i], default =0)
            bot_max_dup = max(bot_hand_duplicates[i], default = 0)
            if player_max_dup > bot_max_dup:
                winner = player
                break
            elif player_max_dup < bot_max_dup:
                winner = bot
                break
        else:
            winner = tie 
        
    return winner




def game_round_info(which_round, deck, poker_board, player_hand, bot_hand):

    global GAME_ROUNDS

    new_board_cards = []

    if GAME_ROUNDS[which_round] == 'preflop':
        
        player_hand, deck = get_card(2, deck)

        log.info(f'Deck length: {len(deck)}')

        bot_hand, deck = get_card(2, deck)


    elif GAME_ROUNDS[which_round] == 'flop':

        new_board_cards, deck = get_card(3, deck)
        
        log.info(f'Flop round new board cards: {new_board_cards}')

        log.info(f'Deck length: {len(deck)}')
       
    elif GAME_ROUNDS[which_round] == 'turn':

        new_board_cards, deck = get_card(1, deck)
        log.info(f'Deck length: {len(deck)}')

    elif GAME_ROUNDS[which_round] == 'river':

        new_board_cards, deck = get_card(1, deck)
        log.info(f'Deck length: {len(deck)}')
    
    assert GAME_ROUNDS[which_round] in ['preflop', 'flop', 'turn', 'river']

    poker_board.extend(new_board_cards)
    
    log.info(f'Poker board: {poker_board}')

    print(f'The {GAME_ROUNDS[which_round]} is beginning.')
    
    player_hand.extend(new_board_cards)
    bot_hand.extend(new_board_cards)


    log.info(f'Player hand post poker board: {player_hand}')
    

    player_hand_str = ", ".join(f'{num}{suit}' for num, suit in player_hand[0:2])

    if poker_board != []:
        poker_board_str = ", ".join(f'{num}{suit}' for num, suit in poker_board)
        print(f'The board is : {poker_board_str}')
    time.sleep(delay)
    print(f'Your cards are: {player_hand_str}')
    

    player_hand_strength, player_hand_type = auto_get_hand_strength(player_hand)['hand strength'], auto_get_hand_strength(player_hand)['hand type']
    player_hand_highest_card = auto_get_hand_strength(player_hand)['hand highest card']
    bot_hand_strength, bot_hand_type = auto_get_hand_strength(bot_hand)['hand strength'], auto_get_hand_strength(bot_hand)['hand type']
    bot_hand_highest_card = auto_get_hand_strength(bot_hand)['hand highest card']

    player_hand_ranks, player_hand_suits = get_hand_rank(player_hand)
    player_hand_duplicates = duplicates_checker(player_hand_ranks)
    bot_hand_ranks, bot_hand_suits = get_hand_rank(bot_hand)
    bot_hand_duplicates = duplicates_checker(bot_hand_ranks)
    
    
    print(f'The {GAME_ROUNDS[which_round]} round begins. The minimum betting amount is : {big_blind}')

    return {
            'player hand': player_hand,
            'player hand type': player_hand_type,
            'player hand strength' : player_hand_strength,
            'player hand duplicates': player_hand_duplicates,
            'player hand highest card': player_hand_highest_card,
            'bot hand': bot_hand,
            'bot hand type': bot_hand_type,
            'bot hand strength': bot_hand_strength,
            'bot hand duplicates': bot_hand_duplicates,
            'bot hand highest card': bot_hand_highest_card,
            'board cards': poker_board
        }, deck, player_hand, bot_hand



# MAIN LOOP
# Welcoming sequence
print('WELCOME TO THE POKER GAME!')
delay = 0.2
time.sleep(delay)
print('Please enter your name.')
player = input('> ')
betting_pool = 0
betting_round_end = False
which_round = 1
game_end = False

# GAME PARAMETERS
bot = 'bot'
balances = {player: 1000, bot: 1000}
big_blind = 20


while True: 
    while True:
        time.sleep(delay)
        print('Press p to play, q to quit.')
        player_input = input('> ')

        log.info(f'Player input: {player_input}') 
        if player_input == 'p':
            break
        elif player_input == 'q':
            sys.exit()
        else:
            print('Please enter a valid input.')
            continue
          


    while game_end == False:

        # Setting up the button at random, will switch between the player and 
        # the bot for the rest of the game
        poker_board = []
        player_hand = []
        bot_hand = []
        round_info = {}

        round_end = False
        which_round = 1

        button_bet_issuer = rd.choice([player, bot])
        deck = get_deck()
        rd.shuffle(deck)

        who_bets = button_bet_issuer

        bot_total_bet, player_total_bet = 0, 0
        bot_betting_amount, player_betting_amount = 0, 0 
        betting_pool, bot_total_bet, player_total_bet = 0, 0, 0    

        if who_bets == bot: 
            bot_betting_amount = big_blind
            betting_pool += bot_betting_amount 
            bot_total_bet += bot_betting_amount
            bot_betting_amount = 0
            player_betting_amount = 0 
        else: 
            player_betting_amount = big_blind 
            player_total_bet += player_betting_amount 
            balances, betting_pool, who_bets = big_blind_mechanic(balances, button_bet_issuer)
        
        print(f'The button is {who_bets}.')
            

        while round_end == False:

            betting_round_end = False

            # GAME START
            time.sleep(delay)
            
            time.sleep(delay)

            round_info, deck, player_hand, bot_hand = game_round_info(which_round, deck, poker_board, player_hand, bot_hand)
            
            print(f'Your current balance is {balances.get(player, 0)}')

            log.info(f'Round info: {round_info}')
                
            # Giving the bot information before betting 
            
            bot_hand_info = {info: round_info[info] for info in list(round_info.keys())[5:9]}
            
            player_action = ''
            bot_action = ''

            # Display
            player_hand_type, player_highest_card = get_hand_type(player_hand)
            player_hand_type_str = ', '.join(player_hand_type)
            if None not in player_hand_type:
                player_hand_type = ', '.join(f'{hand_type}' for hand_type in player_hand_type)  
            else:
                player_hand_type = ''

            bot_hand_type, bot_highest_card = get_hand_type(bot_hand)
            bot_hand_type_str = ', '.join(bot_hand_type)
            if None not in bot_hand_type:
                bot_hand_type = ', '.join(f'{hand_type}' for hand_type in bot_hand_type)
            else : 
                bot_hand_type = ''

            bot_hand_str = ", ".join(f'{num}{suit}' for num, suit in bot_hand)
            player_hand_str = ", ".join(f'{num}{suit}' for num, suit in player_hand)

            time.sleep(delay)

            while betting_round_end == False: 
                
                log.info(f'Who bets: {who_bets}')
                
                if who_bets == player: 
                    betting_pool, player_action, player_betting_amount, player_total_bet = player_bet_mechanic(balances, betting_pool, bot_total_bet, player_total_bet, player) 
                    who_bets = bot

                    if player_action == 'fold': 
                        betting_round_end = True 
                        round_end = True
                        break
                        
                    elif player_action == 'call': 
                        betting_round_end = True
                        who_bets = bot
                        break 
                     
                    
                elif who_bets == bot: 
                    balances, betting_pool, bot_betting_amount, bot_total_bet, bot_action = bot_round_strategy(balances, bot_hand_info, which_round, betting_pool, big_blind, 
                                                                                                              player_betting_amount, bot_betting_amount, bot_total_bet) 
                    who_bets = player 
                
                    time.sleep(delay)
                    if bot_action == 'fold':
                        round_end = True
                        break  

                    elif bot_action == 'raise':
                        print(f'Bot has raised by {bot_betting_amount}.')
                        continue     
                
                    log.info(f'Bot action: {bot_action}')
                    log.info(f'Player action: {player_action}')
            
            bot_betting_amount, player_betting_amount = 0, 0 
            
            which_round += 1
            
            if which_round == 5 or bot_action == 'fold' or player_action == 'fold':
                winner = who_wins(round_info)
                if bot_action == 'fold':
                    winner = player
                if player_action == 'fold':
                    winner = bot

                if winner == player:
                    if player_hand_type != '' and bot_hand_type != '':
                        print(f'You win with a {player_hand_type} ! The bot had a {bot_hand_type}. You have earned {betting_pool}!')
                    balances[player] += betting_pool

                elif winner == bot:
                    if bot_hand_type != '':
                        print(f'You lost. The bot has won {betting_pool} with a {bot_hand_type}.')
                    else:
                        print(f'You lost. The bot has won {betting_pool}.')
                    balances[bot] += betting_pool

                elif winner == 'tie':
                    player_earnings = betting_pool / 2
                    if bot_hand_type != '' and player_hand_type != '':
                        print(f'It\'s a tie !. You had {player_hand_type} and the bot hand {player_hand_type}. You both have won {player_earnings}!')
                    else:
                        print(f'It\'s a tie !. You both have won {player_earnings}!')
                    bot_earnings = player_earnings
                    balances[player] += player_earnings
                    balances[bot] += bot_earnings
                
                print(f'Your new balance is {balances.get(player, 0)}')
                if balances[bot] == 0:
                    print('The bot\'s balance is 0. You have won the game !')
                print('Press p to play another round. Press any other key to quit the game.')
                player_input = input('> ')
                if player_input != 'p':
                    sys.exit()
                round_end = True



