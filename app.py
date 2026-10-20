import random
import streamlit as st

# --- DATOVÉ TŘÍDY ---
CATEGORIES = {
    "tazaci_zajmena": {"name": "Tázací zájmena", "color": "černá"},
    "koncovky": {"name": "Koncovky podstatných jmen", "color": "červená"},
    "predlozky": {"name": "Předložky", "color": "modrá"},
    "spojky": {"name": "Spojky", "color": "zelená"},
    "slovesa": {"name": "Slovesa", "color": "sloveso"},
    "podstatna_jmena": {"name": "Podstatná jména", "color": "podstatné jméno"},
    "pridavna_jmena": {"name": "Přídavná jména", "color": "přídavné jméno"}
}

class Card:
    def __init__(self, word, category, is_blank=False):
        self.word = word
        self.category = category
        self.is_blank = is_blank
        self.color = CATEGORIES.get(category, {}).get("color", "bílá")

class Deck:
    def __init__(self):
        self.cards = []
        sample_words = {
            "tazaci_zajmena": ["Kdo", "Proč", "Jaký", "Kde", "Kdy"],
            "koncovky": ["-y", "-i", "-ech", "-ami", "-ovi"],
            "predlozky": ["do", "na", "za", "v", "s"],
            "spojky": ["a", "ale", "nebo", "protože", "i"],
            "slovesa": ["běhat", "dělat", "chodit", "mluvit", "skočit"],
            "podstatna_jmena": ["dům", "les", "okno", "tabule", "dveře"],
            "pridavna_jmena": ["rychlý", "velký", "český", "nový", "starý"]
        }
        for cat, words in sample_words.items():
            for w in words:
                self.cards.append(Card(w, cat))
        for _ in range(15):
            self.cards.append(Card("", "blank", is_blank=True))
        random.shuffle(self.cards)

    def draw(self):
        return self.cards.pop() if self.cards else None

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.score = 0

    def draw_starting_cards(self, deck):
        for _ in range(10):
            card = deck.draw()
            if card:
                self.hand.append(card)

# --- INICIALIZACE HRY ---
st.set_page_config(page_title="Slovní Domino", layout="wide")
st.title("🔤 Slovní domino v češtině")

if "game_initialized" not in st.session_state:
    st.session_state.deck = Deck()
    st.session_state.player = Player("Uživatel")
    st.session_state.ai = Player("Stroj (AI)")
    
    st.session_state.player.draw_starting_cards(st.session_state.deck)
    st.session_state.ai.draw_starting_cards(st.session_state.deck)
    
    # Výchozí slovo na stole
    initial_card = Card("běhat", "slovesa")
    st.session_state.board = [initial_card]
    st.session_state.turn = "player" # 'player' nebo 'ai'
    st.session_state.message = "Hra začala!"
    st.session_state.game_initialized = True

# --- POSTranní panel: Stav balíčku a kniha ---
with st.sidebar:
    st.header("📚 Lístky")
    st.write(An := f"Zbývá lístků v pytlíku: **{len(st.session_state.deck.cards)}**")
    
    if st.button("Vzít lístek z balíčku (+1 do ruky)"):
        card = st.session_state.deck.draw()
        if card:
            st.session_state.player.hand.append(card)
            st.success("Lístek byl přidán do ruky!")
            st.rerun()
        else:
            st.warning("Pytlík je prázdný!")

    st.divider()
    st.subheader("Vypsat nové slovo z knihy")
    book_word = st.text_input("Zadejte slovo nalezené v knize:")
    book_cat = st.selectbox("Kategorie slova:", list(CATEGORIES.keys()))
    if st.button("Přidat slovo z knihy do ruky"):
        if book_word.strip():
            st.session_state.player.hand.append(Card(book_word.strip(), book_cat))
            st.success(f"Slovo '{book_word}' přidáno do ruky!")
            st.rerun()

# --- HLAVNÍ HERNÍ PLCHA ---
col1, col2 = st.columns(2)
with col1:
    st.metric(label="👤 Tvé skóre", value=st.session_state.player.score)
with col2:
    st.metric(label="🤖 Skóre stroje", value=st.session_state.ai.score)

#st.subheader("Aktuální řetězec na stole:")
board_display = " ➔ ".join([f"**{c.word}** *({c.color})*" for c in st.session_state.board])
st.markdown(f"> {board_display}")

st.info(st.session_state.message)

# --- TAH HRÁČE ---
if st.session_state.turn == "player":
    st.subheader("Tvůj tah")
    last_card = st.session_state.board[-1]
   #st.write(An := f"Poslední slovo na stole je **{last_card.word}**. Můžeš přiložit slovo začínající/končící na písmeno, nebo stejný slovní druh.")

    # Výběr karty z ruky
    hand_options = {f"{c.word} ({c.color})" if not c.is_blank else "[Prázdný lístek]": i for i, c in enumerate(st.session_state.player.hand)}
    
    if hand_options:
        selected_card_label = st.selectbox("Vyber lístek ze své ruky k zahrání:", list(hand_options.keys()))
        card_idx = hand_options[selected_card_label]
        chosen_card = st.session_state.player.hand[card_idx]

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            if st.button("Zahrát lístek (1 bod - shoda písmen / základní tah)"):
                # Základní pravidlo: shoda prvního nebo posledního písmena
                last_w = last_card.word.lower()
                new_w = chosen_card.word.lower()
                if not chosen_card.is_blank and (new_w.startswith(last_w[0]) or new_w.startswith(last_w[-1]) or new_w.endswith(last_w[0]) or new_w.endswith(last_w[-1])):
                    st.session_state.board.append(chosen_card)
                    st.session_state.player.hand.pop(card_idx)
                    st.session_state.player.score += 1
                    st.session_state.message = f"Zahrál jsi '{chosen_card.word}' (+1 bod)."
                    st.session_state.turn = "ai"
                    st.rerun()
                else:
                    st.warning("Slovo nesplňuje pravidlo navázání na první/poslední písmeno posledního slova!")
        with col_p2:
            if st.button("Zahrát jako stejný slovní druh (2 body)"):
                if not chosen_card.is_blank and chosen_card.category == last_card.category:
                    st.session_state.board.append(chosen_card)
                    st.session_state.player.hand.pop(card_idx)
                    st.session_state.player.score += 2
                    st.session_state.message = f"Zahrál jsi '{chosen_card.word}' jako stejný slovní druh (+2 body)."
                    st.session_state.turn = "ai"
                    st.rerun()
                else:
                    st.warning("Slovo není stejného slovního druhu jako poslední slovo na stole!")
    else:
        st.warning("Nemáš v ruce žádné lístky! Musíš si vzít lístek z balíčku.")

    if st.button("Přeskočit kolo (hledám v knize / nemohu hrát)"):
        st.session_state.message = "Předal jsi tah stroji (0 bodů)."
        st.session_state.turn = "ai"
        st.rerun()

# --- TAH STROJE (AI maximalizující body) ---
elif st.session_state.turn == "ai":
    st.subheader("Tah stroje (AI)...")
    last_card = st.session_state.board[-1]
    
    # AI hledá v ruce nejvýhodnější tah (maximalizace bodů: zkusí najít shodu slovního druhu = 2 body, jinak shodu písmen = 1 bod)
    best_move_idx = None
    best_move_score = 0
    best_move_type = None

    for idx, card in enumerate(st.session_state.ai.hand):
        if card.is_blank:
            continue
        last_w = last_card.word.lower()
        new_w = card.word.lower()
        
        # Priorita 2: Stejný slovní druh
        if card.category == last_card.category:
            best_move_idx = idx
            best_move_score = 2
            best_move_type = "slovní druh"
            break  # Našel optimální tah za 2 body, bere ho
        
        # Priorita 1: Shoda písmen
        elif (new_w.startswith(last_w[0]) or new_w.startswith(last_w[-1]) or 
              new_w.endswith(last_w[0]) or new_w.endswith(last_w[-1])):
            if best_move_score < 1:
                best_move_idx = idx
                best_move_score = 1
                best_move_type = "písmeno"

    if best_move_idx is not None:
        played_card = st.session_state.ai.hand.pop(best_move_idx)
        st.session_state.board.append(played_card)
        st.session_state.ai.score += best_move_score
        st.session_state.message = f"Stroj zahrál '{played_card.word}' ({best_move_type}) a získal {best_move_score} bodů."
    else:
        # Pokud AI nemá platný tah, vezme si kartu z balíčku
        card_drawn = st.session_state.deck.draw()
        if card_drawn:
            st.session_state.ai.hand.append(card_drawn)
        st.session_state.message = "Stroj nemohl zahrát, tak si lízl kartu z balíčku."

    st.session_state.turn = "player"
    st.rerun()

# Zobrazení aktuální ruky hráče pod hrou
st.divider()
st.subheader("Tvá ruka (lístky):")
cols = st.columns(min(len(st.session_state.player.hand), 10) if st.session_state.player.hand else 1)
for i, card in enumerate(st.session_state.player.hand):
    with cols[i % len(cols)]:
        st.info(f"**{card.word if not card.is_blank else 'Prázdný'}**\n\n*{card.color}*")
